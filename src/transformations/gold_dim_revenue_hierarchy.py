"""
Gold Layer - Dimension Revenue Hierarchy
========================================

Builds the Revenue Hierarchy dimension for analytical revenue
classification.

The hierarchy organizes revenue into the following structure:

Revenue
├── Prospecting
├── Renewal
└── Expansion
    ├── Cross-Sell
    └── Up-Sell

For the synthetic environment, Expansion is classified using
the following deterministic business rule:

- Alpha   -> Cross-Sell
- Beta    -> Up-Sell
- Gamma   -> Up-Sell

This rule is intentionally synthetic and does not reproduce
any proprietary production rule.

Responsibilities:

- Read standardized Silver data
- Build the analytical revenue hierarchy
- Apply synthetic business rules
- Validate hierarchy combinations
- Generate deterministic surrogate keys
- Add a standard N/A member
- Persist the Gold dimension

Revenue calculation itself is intentionally excluded from
this dimension and will be implemented in Fact Revenue.
"""

from hashlib import sha256
from pathlib import Path

import pandas as pd


# ----------------------------------------------------------------------
# CONFIGURATION
# ----------------------------------------------------------------------

SILVER_PATH = Path(
    "data/silver/opportunities.parquet"
)

GOLD_PATH = Path(
    "data/gold/dim_revenue_hierarchy.parquet"
)

SOURCE_TABLE = "opportunities"


EXPECTED_COLUMNS = [
    "opportunity_type",
    "brand",
]


# ----------------------------------------------------------------------
# BUSINESS RULES
# ----------------------------------------------------------------------

EXPANSION_BRAND_MAPPING = {
    "Alpha": "Cross-Sell",
    "Beta": "Up-Sell",
    "Gamma": "Up-Sell",
}


NEGOTIATION_TYPE_MAPPING = {
    "Prospecting": "Prospecting",
    "Retention": "Renewal",
    "Expansion": "Expansion",
}


# ----------------------------------------------------------------------
# VALIDATION
# ----------------------------------------------------------------------

def validate_columns(
    df: pd.DataFrame,
) -> None:
    """
    Validate whether the source contains all required columns.
    """

    missing_columns = [
        column
        for column in EXPECTED_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            "Missing expected columns: "
            f"{missing_columns}"
        )


# ----------------------------------------------------------------------
# STANDARDIZATION
# ----------------------------------------------------------------------

def standardize_source_values(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Standardize source values before applying business rules.
    """

    df = df.copy()

    df["opportunity_type"] = (
        df["opportunity_type"]
        .astype("string")
        .str.strip()
        .str.title()
    )

    df["brand"] = (
        df["brand"]
        .astype("string")
        .str.strip()
        .str.title()
    )

    return df


# ----------------------------------------------------------------------
# HIERARCHY GENERATION
# ----------------------------------------------------------------------

def build_revenue_hierarchy(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Build the analytical revenue hierarchy combinations.

    The hierarchy is generated from the distinct combinations
    required by the synthetic business rules.
    """

    source = (
        df[
            [
                "opportunity_type",
                "brand",
            ]
        ]
        .drop_duplicates()
        .reset_index(drop=True)
    )

    source["negotiation_type"] = (
        source["opportunity_type"]
        .map(
            NEGOTIATION_TYPE_MAPPING
        )
    )

    source["revenue_level_1"] = (
        "Revenue"
    )

    source["revenue_level_2"] = (
        source["negotiation_type"]
    )

    source["revenue_level_3"] = (
        source["negotiation_type"]
    )

    expansion_mask = (
        source["negotiation_type"]
        == "Expansion"
    )

    source.loc[
        expansion_mask,
        "revenue_level_3",
    ] = (
        source.loc[
            expansion_mask,
            "brand",
        ]
        .map(
            EXPANSION_BRAND_MAPPING
        )
    )

    return source


# ----------------------------------------------------------------------
# QUALITY RULES
# ----------------------------------------------------------------------

def validate_business_mapping(
    df: pd.DataFrame,
) -> None:
    """
    Validate that all source classifications can be resolved.
    """

    invalid_negotiation_types = (
        df.loc[
            df["negotiation_type"].isna(),
            "opportunity_type",
        ]
        .drop_duplicates()
        .tolist()
    )

    if invalid_negotiation_types:
        raise ValueError(
            "Unmapped opportunity types found: "
            f"{invalid_negotiation_types}"
        )

    expansion_without_level = df[
        (
            df["negotiation_type"]
            == "Expansion"
        )
        & (
            df["revenue_level_3"]
            .isna()
        )
    ]

    if not expansion_without_level.empty:
        invalid_brands = (
            expansion_without_level[
                "brand"
            ]
            .drop_duplicates()
            .tolist()
        )

        raise ValueError(
            "Expansion brands without a "
            "revenue hierarchy mapping: "
            f"{invalid_brands}"
        )


def remove_duplicates(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Keep one record per analytical hierarchy combination.
    """

    hierarchy_columns = [
        "revenue_level_1",
        "revenue_level_2",
        "revenue_level_3",
    ]

    return (
        df[
            hierarchy_columns
        ]
        .drop_duplicates()
        .reset_index(drop=True)
    )


# ----------------------------------------------------------------------
# SURROGATE KEY
# ----------------------------------------------------------------------

def generate_surrogate_key(
    level_1: str,
    level_2: str,
    level_3: str,
) -> str:
    """
    Generate a deterministic surrogate key based on
    the complete hierarchy path.
    """

    hierarchy_path = "|".join(
        [
            str(level_1).strip(),
            str(level_2).strip(),
            str(level_3).strip(),
        ]
    )

    return sha256(
        hierarchy_path
        .upper()
        .encode("utf-8")
    ).hexdigest()


def add_surrogate_key(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Add the revenue hierarchy surrogate key.
    """

    df = df.copy()

    df["revenue_hierarchy_sk"] = (
        df.apply(
            lambda row: generate_surrogate_key(
                row["revenue_level_1"],
                row["revenue_level_2"],
                row["revenue_level_3"],
            ),
            axis=1,
        )
    )

    return df


# ----------------------------------------------------------------------
# STANDARD N/A MEMBER
# ----------------------------------------------------------------------

def add_unknown_member(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Add a standard N/A member used when the revenue hierarchy
    cannot be resolved.
    """

    unknown_record = pd.DataFrame(
        [
            {
                "revenue_hierarchy_sk": (
                    generate_surrogate_key(
                        "N/A",
                        "N/A",
                        "N/A",
                    )
                ),
                "revenue_level_1": "N/A",
                "revenue_level_2": "N/A",
                "revenue_level_3": "N/A",
            }
        ]
    )

    return pd.concat(
        [
            unknown_record,
            df[
                [
                    "revenue_hierarchy_sk",
                    "revenue_level_1",
                    "revenue_level_2",
                    "revenue_level_3",
                ]
            ],
        ],
        ignore_index=True,
    )


# ----------------------------------------------------------------------
# PERSISTENCE
# ----------------------------------------------------------------------

def save_gold(
    df: pd.DataFrame,
) -> None:
    """
    Persist the Gold dimension as Parquet.
    """

    GOLD_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    df.to_parquet(
        GOLD_PATH,
        index=False,
    )

    print(
        f"Gold output: {GOLD_PATH}"
    )


# ----------------------------------------------------------------------
# PIPELINE
# ----------------------------------------------------------------------

def process_dim_revenue_hierarchy() -> pd.DataFrame:
    """
    Execute the complete Gold transformation
    for the Revenue Hierarchy dimension.
    """

    if not SILVER_PATH.exists():
        raise FileNotFoundError(
            f"Silver dataset not found: "
            f"{SILVER_PATH}"
        )

    df = pd.read_parquet(
        SILVER_PATH
    )

    if df.empty:
        raise ValueError(
            "Silver opportunity dataset is empty."
        )

    print(
        f"Silver records: {len(df)}"
    )

    validate_columns(
        df
    )

    df = standardize_source_values(
        df
    )

    hierarchy = (
        build_revenue_hierarchy(
            df
        )
    )

    validate_business_mapping(
        hierarchy
    )

    hierarchy = remove_duplicates(
        hierarchy
    )

    hierarchy = add_surrogate_key(
        hierarchy
    )

    hierarchy = add_unknown_member(
        hierarchy
    )

    hierarchy = hierarchy[
        [
            "revenue_hierarchy_sk",
            "revenue_level_1",
            "revenue_level_2",
            "revenue_level_3",
        ]
    ]

    save_gold(
        hierarchy
    )

    print(
        f"Gold records: {len(hierarchy)}"
    )

    return hierarchy


# ----------------------------------------------------------------------
# MAIN
# ----------------------------------------------------------------------

if __name__ == "__main__":

    print(
        "Gold Layer - "
        "Dimension Revenue Hierarchy"
    )

    print(
        "============================"
    )

    process_dim_revenue_hierarchy()

    print(
        "\nRevenue Hierarchy dimension "
        "created successfully."
    )

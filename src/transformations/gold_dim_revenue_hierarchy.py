"""
Gold Layer - Revenue Hierarchy Dimension
========================================

Builds the Revenue Hierarchy dimension from the Silver opportunity dataset.

The hierarchy supports both aggregated analytical classifications
and detailed revenue classifications.

Hierarchy:

Revenue
├── Prospecting
│   └── Prospecting
├── Renewal
│   └── Renewal
└── Expansion
    ├── Expansion
    ├── Cross-Sell
    └── Up-Sell

The aggregated Expansion member is required so that target data can
reference the Expansion level, while revenue data can reference the
more detailed Cross-Sell and Up-Sell levels.

Responsibilities:

- Read standardized Silver data
- Validate the source structure
- Standardize analytical classifications
- Apply synthetic hierarchy rules
- Include aggregated and detailed hierarchy members
- Generate deterministic surrogate keys
- Add a standard N/A member
- Persist the Gold dimension

The implementation uses synthetic business rules and does not contain
proprietary production information.
"""

from hashlib import sha256
from pathlib import Path

import pandas as pd


SILVER_PATH = Path("data/silver/opportunities.parquet")
GOLD_PATH = Path("data/gold/dim_revenue_hierarchy.parquet")

EXPECTED_COLUMNS = [
    "opportunity_type",
    "brand",
]


OPPORTUNITY_TYPE_MAPPING = {
    "Prospecting": "Prospecting",
    "Retention": "Renewal",
    "Expansion": "Expansion",
}


EXPANSION_BRAND_MAPPING = {
    "Alpha": "Cross-Sell",
    "Beta": "Up-Sell",
    "Gamma": "Up-Sell",
}


def validate_columns(df):
    """Validate the required source columns."""
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


def standardize_source(df):
    """Standardize source values used by the hierarchy."""
    df = df.copy()

    for column in EXPECTED_COLUMNS:
        df[column] = (
            df[column]
            .astype("string")
            .str.strip()
            .str.title()
        )

    return df


def map_opportunity_type(df):
    """Map source opportunity types to analytical negotiation types."""
    df = df.copy()

    df["negotiation_type"] = df["opportunity_type"].map(
        OPPORTUNITY_TYPE_MAPPING
    )

    unmapped_values = (
        df.loc[
            df["negotiation_type"].isna(),
            "opportunity_type",
        ]
        .dropna()
        .unique()
        .tolist()
    )

    if unmapped_values:
        raise ValueError(
            "Unmapped opportunity types found: "
            f"{unmapped_values}"
        )

    return df


def build_hierarchy_records(df):
    """
    Build the hierarchy members required by the analytical model.

    The aggregated Expansion member is created explicitly because
    targets are analyzed at the Expansion level, while revenue can
    be analyzed at Cross-Sell or Up-Sell level.
    """

    records = []

    for negotiation_type in sorted(
        df["negotiation_type"].dropna().unique()
    ):
        if negotiation_type == "Expansion":
            records.append(
                {
                    "revenue_level_1": "Revenue",
                    "revenue_level_2": "Expansion",
                    "revenue_level_3": "Expansion",
                }
            )

            expansion_brands = sorted(
                df.loc[
                    df["negotiation_type"] == "Expansion",
                    "brand",
                ]
                .dropna()
                .unique()
            )

            for brand in expansion_brands:
                detailed_level = EXPANSION_BRAND_MAPPING.get(
                    brand
                )

                if detailed_level is None:
                    raise ValueError(
                        "No synthetic hierarchy mapping found "
                        f"for Expansion brand: {brand}"
                    )

                records.append(
                    {
                        "revenue_level_1": "Revenue",
                        "revenue_level_2": "Expansion",
                        "revenue_level_3": detailed_level,
                    }
                )

        else:
            records.append(
                {
                    "revenue_level_1": "Revenue",
                    "revenue_level_2": negotiation_type,
                    "revenue_level_3": negotiation_type,
                }
            )

    hierarchy = pd.DataFrame(records)

    if hierarchy.empty:
        raise ValueError(
            "No revenue hierarchy records were generated."
        )

    hierarchy = hierarchy.drop_duplicates(
        subset=[
            "revenue_level_1",
            "revenue_level_2",
            "revenue_level_3",
        ]
    ).reset_index(drop=True)

    return hierarchy


def generate_surrogate_key(level_1, level_2, level_3):
    """Generate a deterministic SHA-256 surrogate key."""
    normalized_value = "|".join(
        [
            str(level_1).strip().upper(),
            str(level_2).strip().upper(),
            str(level_3).strip().upper(),
        ]
    )

    return sha256(
        normalized_value.encode("utf-8")
    ).hexdigest()


def add_surrogate_key(df):
    """Add the deterministic hierarchy surrogate key."""
    df = df.copy()

    df["revenue_hierarchy_sk"] = df.apply(
        lambda row: generate_surrogate_key(
            row["revenue_level_1"],
            row["revenue_level_2"],
            row["revenue_level_3"],
        ),
        axis=1,
    )

    return df


def add_unknown_member(df):
    """Add the standard unknown member."""
    unknown_record = pd.DataFrame(
        [
            {
                "revenue_hierarchy_sk": generate_surrogate_key(
                    "N/A",
                    "N/A",
                    "N/A",
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


def validate_hierarchy(df):
    """Validate the final hierarchy structure."""
    required_members = {
        (
            "Revenue",
            "Prospecting",
            "Prospecting",
        ),
        (
            "Revenue",
            "Renewal",
            "Renewal",
        ),
        (
            "Revenue",
            "Expansion",
            "Expansion",
        ),
        (
            "Revenue",
            "Expansion",
            "Cross-Sell",
        ),
        (
            "Revenue",
            "Expansion",
            "Up-Sell",
        ),
    }

    actual_members = set(
        zip(
            df["revenue_level_1"],
            df["revenue_level_2"],
            df["revenue_level_3"],
        )
    )

    missing_members = required_members - actual_members

    if missing_members:
        raise ValueError(
            "Required revenue hierarchy members are missing: "
            f"{sorted(missing_members)}"
        )


def save_gold(df):
    """Persist the Gold dimension."""
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


def process_dim_revenue_hierarchy():
    """Build the Revenue Hierarchy Gold dimension."""

    if not SILVER_PATH.exists():
        raise FileNotFoundError(
            f"Silver dataset not found: {SILVER_PATH}"
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

    validate_columns(df)

    df = standardize_source(df)

    df = df[
        df["opportunity_type"].notna()
        & (df["opportunity_type"] != "")
        & df["brand"].notna()
        & (df["brand"] != "")
    ]

    df = map_opportunity_type(df)

    hierarchy = build_hierarchy_records(df)

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

    validate_hierarchy(
        hierarchy
    )

    save_gold(
        hierarchy
    )

    print(
        f"Gold records: {len(hierarchy)}"
    )

    print(
        "\nRevenue hierarchy:"
    )

    print(
        hierarchy.to_string(
            index=False
        )
    )

    return hierarchy


if __name__ == "__main__":
    print(
        "Gold Layer - Revenue Hierarchy Dimension"
    )

    print(
        "========================================="
    )

    process_dim_revenue_hierarchy()

    print(
        "\nRevenue hierarchy dimension "
        "created successfully."
    )

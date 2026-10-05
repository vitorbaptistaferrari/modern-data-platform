"""
Gold Layer - Dimension Negotiation Type
=======================================

Builds the Negotiation Type dimension from the Silver
opportunity dataset.

This dimension introduces the first business-rule transformation
of the Gold layer by translating operational opportunity types
into standardized analytical negotiation types.

Source classification:

- Prospecting
- Retention
- Expansion

Analytical classification:

- Prospecting
- Renewal
- Expansion

Cross-Sell and Up-Sell are intentionally handled later in the
Revenue Hierarchy dimension because they represent a lower-level
classification of Expansion.

Responsibilities:

- Read standardized Silver data
- Validate the source structure
- Apply analytical business rules
- Generate a deterministic surrogate key
- Add a standard N/A member
- Persist the Gold dimension
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
    "data/gold/dim_negotiation_type.parquet"
)

SOURCE_TABLE = "opportunities"


EXPECTED_COLUMNS = [
    "opportunity_type",
]


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
# BUSINESS RULES
# ----------------------------------------------------------------------

NEGOTIATION_TYPE_MAPPING = {
    "Prospecting": "Prospecting",
    "Retention": "Renewal",
    "Expansion": "Expansion",
}


def standardize_source_values(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Standardize source opportunity type values before
    applying analytical business rules.
    """

    df = df.copy()

    df["opportunity_type"] = (
        df["opportunity_type"]
        .astype("string")
        .str.strip()
        .str.title()
    )

    return df


def apply_negotiation_rules(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Translate operational opportunity types into
    analytical negotiation types.
    """

    df = df.copy()

    df["negotiation_type"] = (
        df["opportunity_type"]
        .map(
            NEGOTIATION_TYPE_MAPPING
        )
    )

    return df


# ----------------------------------------------------------------------
# QUALITY RULES
# ----------------------------------------------------------------------

def remove_invalid_values(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Remove records where the source classification
    cannot be resolved.
    """

    return df[
        df["opportunity_type"].notna()
        & (df["opportunity_type"] != "")
    ].copy()


def validate_business_mapping(
    df: pd.DataFrame,
) -> None:
    """
    Validate that every source opportunity type has
    a corresponding analytical classification.
    """

    unmapped_values = (
        df.loc[
            df["negotiation_type"].isna(),
            "opportunity_type",
        ]
        .drop_duplicates()
        .tolist()
    )

    if unmapped_values:
        raise ValueError(
            "Unmapped opportunity types found: "
            f"{unmapped_values}"
        )


def remove_duplicates(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Keep one record per analytical negotiation type.
    """

    return (
        df[
            [
                "negotiation_type",
            ]
        ]
        .drop_duplicates()
        .reset_index(drop=True)
    )


# ----------------------------------------------------------------------
# SURROGATE KEY
# ----------------------------------------------------------------------

def generate_surrogate_key(
    negotiation_type: str,
) -> str:
    """
    Generate a deterministic surrogate key based on
    the analytical negotiation type.
    """

    normalized_value = (
        str(negotiation_type)
        .strip()
        .upper()
    )

    return sha256(
        normalized_value.encode("utf-8")
    ).hexdigest()


def add_surrogate_key(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Add the negotiation type surrogate key.
    """

    df = df.copy()

    df["negotiation_type_sk"] = (
        df["negotiation_type"]
        .apply(
            generate_surrogate_key
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
    Add a standard N/A member used when the analytical
    negotiation type cannot be resolved.
    """

    unknown_record = pd.DataFrame(
        [
            {
                "negotiation_type_sk": (
                    generate_surrogate_key(
                        "N/A"
                    )
                ),
                "negotiation_type": "N/A",
            }
        ]
    )

    return pd.concat(
        [
            unknown_record,
            df[
                [
                    "negotiation_type_sk",
                    "negotiation_type",
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

def process_dim_negotiation_type() -> pd.DataFrame:
    """
    Execute the complete Gold transformation
    for the Negotiation Type dimension.
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

    df = remove_invalid_values(
        df
    )

    df = apply_negotiation_rules(
        df
    )

    validate_business_mapping(
        df
    )

    df = remove_duplicates(
        df
    )

    df = add_surrogate_key(
        df
    )

    df = add_unknown_member(
        df
    )

    df = df[
        [
            "negotiation_type_sk",
            "negotiation_type",
        ]
    ]

    save_gold(
        df
    )

    print(
        f"Gold records: {len(df)}"
    )

    return df


# ----------------------------------------------------------------------
# MAIN
# ----------------------------------------------------------------------

if __name__ == "__main__":

    print(
        "Gold Layer - "
        "Dimension Negotiation Type"
    )

    print(
        "==========================="
    )

    process_dim_negotiation_type()

    print(
        "\nNegotiation Type dimension "
        "created successfully."
    )

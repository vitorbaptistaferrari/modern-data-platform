"""
Gold Layer - Dimension Target Type
==================================

Builds the Target Type dimension from the Silver target dataset.

This dimension standardizes operational target classifications
into the analytical terminology used by the Gold model.

Source classification:

- Prospecting
- Retention
- Expansion

Analytical classification:

- Prospecting
- Renewal
- Expansion

Responsibilities:

- Read standardized Silver data
- Validate the source structure
- Standardize target classifications
- Apply analytical business rules
- Validate the business mapping
- Remove duplicates
- Generate a deterministic surrogate key
- Add a standard N/A member
- Persist the Gold dimension

Business rules related to revenue calculation are intentionally
excluded from this dimension.
"""

from hashlib import sha256
from pathlib import Path

import pandas as pd


# ----------------------------------------------------------------------
# CONFIGURATION
# ----------------------------------------------------------------------

SILVER_PATH = Path(
    "data/silver/targets.parquet"
)

GOLD_PATH = Path(
    "data/gold/dim_target_type.parquet"
)

SOURCE_TABLE = "targets"


EXPECTED_COLUMNS = [
    "target_type",
]


# ----------------------------------------------------------------------
# BUSINESS RULES
# ----------------------------------------------------------------------

TARGET_TYPE_MAPPING = {
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

def standardize_target_types(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Standardize target type values before applying
    analytical business rules.
    """

    df = df.copy()

    df["target_type"] = (
        df["target_type"]
        .astype("string")
        .str.strip()
        .str.title()
    )

    return df


# ----------------------------------------------------------------------
# BUSINESS TRANSFORMATION
# ----------------------------------------------------------------------

def apply_target_type_rules(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Translate operational target types into analytical
    target types.
    """

    df = df.copy()

    df["analytical_target_type"] = (
        df["target_type"]
        .map(
            TARGET_TYPE_MAPPING
        )
    )

    return df


def validate_business_mapping(
    df: pd.DataFrame,
) -> None:
    """
    Validate that every source target type has a
    corresponding analytical classification.
    """

    unmapped_values = (
        df.loc[
            df["analytical_target_type"].isna(),
            "target_type",
        ]
        .drop_duplicates()
        .tolist()
    )

    if unmapped_values:
        raise ValueError(
            "Unmapped target types found: "
            f"{unmapped_values}"
        )


# ----------------------------------------------------------------------
# QUALITY RULES
# ----------------------------------------------------------------------

def remove_invalid_values(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Remove records where the source target type
    is null or empty.
    """

    return df[
        df["target_type"].notna()
        & (df["target_type"] != "")
    ].copy()


def remove_duplicates(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Keep one record per analytical target type.
    """

    return (
        df[
            [
                "analytical_target_type",
            ]
        ]
        .drop_duplicates()
        .reset_index(drop=True)
    )


# ----------------------------------------------------------------------
# SURROGATE KEY
# ----------------------------------------------------------------------

def generate_surrogate_key(
    target_type: str,
) -> str:
    """
    Generate a deterministic surrogate key based on
    the analytical target type.
    """

    normalized_value = (
        str(target_type)
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
    Add the target type surrogate key.
    """

    df = df.copy()

    df["target_type_sk"] = (
        df["analytical_target_type"]
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
    Add a standard N/A member used when the target type
    cannot be resolved.
    """

    unknown_record = pd.DataFrame(
        [
            {
                "target_type_sk": (
                    generate_surrogate_key(
                        "N/A"
                    )
                ),
                "target_type": "N/A",
            }
        ]
    )

    return pd.concat(
        [
            unknown_record,
            df[
                [
                    "target_type_sk",
                    "analytical_target_type",
                ]
            ].rename(
                columns={
                    "analytical_target_type": (
                        "target_type"
                    )
                }
            ),
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

def process_dim_target_type() -> pd.DataFrame:
    """
    Execute the complete Gold transformation
    for the Target Type dimension.
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
            "Silver target dataset is empty."
        )

    print(
        f"Silver records: {len(df)}"
    )

    validate_columns(
        df
    )

    df = standardize_target_types(
        df
    )

    df = remove_invalid_values(
        df
    )

    df = apply_target_type_rules(
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
            "target_type_sk",
            "target_type",
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
        "Dimension Target Type"
    )

    print(
        "======================"
    )

    process_dim_target_type()

    print(
        "\nTarget Type dimension "
        "created successfully."
    )

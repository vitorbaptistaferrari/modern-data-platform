"""
Gold Layer - Dimension Brand
============================

Builds the Brand dimension from the Silver opportunity dataset.

Responsibilities:

- Read standardized Silver data
- Validate the source structure
- Standardize brand values
- Remove invalid brand values
- Generate a deterministic surrogate key
- Add a standard N/A member
- Persist the Gold dimension

Business rules that classify revenue are intentionally excluded
from this dimension.
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
    "data/gold/dim_brand.parquet"
)

SOURCE_TABLE = "opportunities"

EXPECTED_COLUMNS = [
    "brand",
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
# STANDARDIZATION
# ----------------------------------------------------------------------

def standardize_brand(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Standardize brand values.
    """

    df = df.copy()

    df["brand"] = (
        df["brand"]
        .astype("string")
        .str.strip()
        .str.title()
    )

    return df


# ----------------------------------------------------------------------
# QUALITY RULES
# ----------------------------------------------------------------------

def remove_invalid_brands(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Remove records with null or empty brand values.
    """

    df = df[
        df["brand"].notna()
        & (df["brand"] != "")
    ]

    return df


def remove_duplicates(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Keep one record per distinct brand.
    """

    return (
        df[
            ["brand"]
        ]
        .drop_duplicates()
        .reset_index(drop=True)
    )


# ----------------------------------------------------------------------
# SURROGATE KEY
# ----------------------------------------------------------------------

def generate_surrogate_key(
    brand: str,
) -> str:
    """
    Generate a deterministic surrogate key for a brand.

    The key is based on a normalized business value and SHA-256.
    """

    normalized_value = (
        str(brand)
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
    Add the brand surrogate key.
    """

    df = df.copy()

    df["brand_sk"] = (
        df["brand"]
        .apply(generate_surrogate_key)
    )

    return df


# ----------------------------------------------------------------------
# STANDARD N/A MEMBER
# ----------------------------------------------------------------------

def add_unknown_member(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Add a standard N/A member used when a brand cannot
    be resolved during analytical processing.
    """

    unknown_record = pd.DataFrame(
        [
            {
                "brand_sk": generate_surrogate_key(
                    "N/A"
                ),
                "brand": "N/A",
            }
        ]
    )

    df = pd.concat(
        [
            unknown_record,
            df[
                [
                    "brand_sk",
                    "brand",
                ]
            ],
        ],
        ignore_index=True,
    )

    return df


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

def process_dim_brand() -> pd.DataFrame:
    """
    Execute the complete Gold transformation
    for the Brand dimension.
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

    df = standardize_brand(
        df
    )

    df = remove_invalid_brands(
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
            "brand_sk",
            "brand",
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

    print("Gold Layer - Dimension Brand")
    print("============================")

    process_dim_brand()

    print(
        "\nBrand dimension created successfully."
    )

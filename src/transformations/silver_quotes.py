"""
Silver Layer - Quotes
=====================

Transforms the Bronze quote dataset into a standardized
Silver representation.

Responsibilities:

- Validate source structure
- Standardize text fields
- Apply data types
- Validate primary and foreign keys
- Deduplicate quotes
- Add Silver technical metadata

Business rules are intentionally excluded from this layer.
"""

from pathlib import Path

import pandas as pd

from silver_utils import (
    add_silver_metadata,
    deduplicate,
    remove_invalid_keys,
    save_silver,
    standardize_text_columns,
    validate_columns,
)


# ----------------------------------------------------------------------
# CONFIGURATION
# ----------------------------------------------------------------------

BRONZE_PATH = Path(
    "data/bronze/quotes.parquet"
)

SILVER_PATH = Path(
    "data/silver/quotes.parquet"
)

SOURCE_TABLE = "quotes"


EXPECTED_COLUMNS = [
    "quote_id",
    "opportunity_id",
    "quote_status",
    "quote_date",
    "quoted_amount",
    "dt_ingestao",
]


# ----------------------------------------------------------------------
# STANDARDIZATION
# ----------------------------------------------------------------------

def standardize_quotes(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Apply quote-specific standardization.
    """

    df = standardize_text_columns(
        df,
        [
            "quote_id",
            "opportunity_id",
            "quote_status",
        ],
    )

    df["quote_status"] = (
        df["quote_status"]
        .str.title()
    )

    df["quote_date"] = (
        pd.to_datetime(
            df["quote_date"],
            errors="coerce",
        )
    )

    df["quoted_amount"] = (
        pd.to_numeric(
            df["quoted_amount"],
            errors="coerce",
        )
    )

    return df


# ----------------------------------------------------------------------
# QUALITY
# ----------------------------------------------------------------------

def apply_quality_rules(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Apply technical data quality rules.
    """

    df = remove_invalid_keys(
        df,
        ["quote_id"],
    )

    df = deduplicate(
        df,
        ["quote_id"],
    )

    return df


# ----------------------------------------------------------------------
# FOREIGN KEY VALIDATION
# ----------------------------------------------------------------------

def validate_foreign_keys(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Validate required foreign key fields.
    """

    invalid_count = (
        df["opportunity_id"].isna()
        | (df["opportunity_id"] == "")
    ).sum()

    if invalid_count > 0:

        raise ValueError(
            "Foreign key column "
            "'opportunity_id' contains "
            f"{invalid_count} invalid records."
        )

    return df


# ----------------------------------------------------------------------
# PIPELINE
# ----------------------------------------------------------------------

def process_quotes() -> pd.DataFrame:
    """
    Execute the complete Silver transformation
    for the quote dataset.
    """

    if not BRONZE_PATH.exists():
        raise FileNotFoundError(
            f"Bronze dataset not found: "
            f"{BRONZE_PATH}"
        )

    df = pd.read_parquet(
        BRONZE_PATH
    )

    if df.empty:
        raise ValueError(
            "Bronze quote dataset is empty."
        )

    print(
        f"Bronze records: {len(df)}"
    )

    # --------------------------------------------------------------
    # 1. Validate structure
    # --------------------------------------------------------------

    validate_columns(
        df,
        EXPECTED_COLUMNS,
    )

    # --------------------------------------------------------------
    # 2. Standardize fields
    # --------------------------------------------------------------

    df = standardize_quotes(df)

    # --------------------------------------------------------------
    # 3. Validate primary key
    # --------------------------------------------------------------

    df = apply_quality_rules(df)

    # --------------------------------------------------------------
    # 4. Validate foreign key
    # --------------------------------------------------------------

    df = validate_foreign_keys(df)

    # --------------------------------------------------------------
    # 5. Add Silver metadata
    # --------------------------------------------------------------

    df = add_silver_metadata(
        df,
        SOURCE_TABLE,
    )

    # --------------------------------------------------------------
    # 6. Persist Silver
    # --------------------------------------------------------------

    save_silver(
        df,
        SILVER_PATH,
    )

    print(
        f"Silver records: {len(df)}"
    )

    return df


# ----------------------------------------------------------------------
# MAIN
# ----------------------------------------------------------------------

if __name__ == "__main__":

    print("Silver Layer - Quotes")
    print("=====================")

    process_quotes()

    print(
        "\nQuote Silver transformation "
        "completed successfully."
    )

"""
Silver Layer - Customers
========================

Transforms the Bronze customer dataset into a standardized
Silver representation.

The transformation reuses common Silver utilities for:

- Validation
- Text standardization
- Key validation
- Deduplication
- Silver metadata
- Persistence

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
    "data/bronze/customers.parquet"
)

SILVER_PATH = Path(
    "data/silver/customers.parquet"
)

SOURCE_TABLE = "customers"


EXPECTED_COLUMNS = [
    "customer_id",
    "customer_name",
    "tax_id",
    "city",
    "state",
    "segment",
    "status",
    "dt_ingestao",
]


# ----------------------------------------------------------------------
# CUSTOMER-SPECIFIC STANDARDIZATION
# ----------------------------------------------------------------------

def standardize_customers(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Apply customer-specific standardization.

    Generic text cleaning is delegated to the Silver utilities.
    """

    df = standardize_text_columns(
        df,
        [
            "customer_id",
            "customer_name",
            "tax_id",
            "city",
            "state",
            "segment",
            "status",
        ],
    )

    df["state"] = (
        df["state"]
        .str.upper()
    )

    df["segment"] = (
        df["segment"]
        .str.title()
    )

    df["status"] = (
        df["status"]
        .str.title()
    )

    return df


# ----------------------------------------------------------------------
# PIPELINE
# ----------------------------------------------------------------------

def process_customers() -> pd.DataFrame:
    """
    Execute the complete Silver transformation
    for the customer dataset.
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
            "Bronze customer dataset is empty."
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

    df = standardize_customers(df)

    # --------------------------------------------------------------
    # 3. Validate primary key
    # --------------------------------------------------------------

    df = remove_invalid_keys(
        df,
        ["customer_id"],
    )

    # --------------------------------------------------------------
    # 4. Deduplicate
    # --------------------------------------------------------------

    df = deduplicate(
        df,
        ["customer_id"],
    )

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

    print("Silver Layer - Customers")
    print("=========================")

    process_customers()

    print(
        "\nCustomer Silver transformation "
        "completed successfully."
    )

"""
Silver Layer - Contracts
========================

Transforms the Bronze contract dataset into a standardized
Silver representation.

Responsibilities:

- Validate source structure
- Standardize text fields
- Apply data types
- Validate primary and foreign keys
- Deduplicate contracts
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
    "data/bronze/contracts.parquet"
)

SILVER_PATH = Path(
    "data/silver/contracts.parquet"
)

SOURCE_TABLE = "contracts"


EXPECTED_COLUMNS = [
    "contract_id",
    "opportunity_id",
    "contract_status",
    "contract_start_date",
    "contract_end_date",
    "contract_value",
    "dt_ingestao",
]


# ----------------------------------------------------------------------
# STANDARDIZATION
# ----------------------------------------------------------------------

def standardize_contracts(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Apply contract-specific standardization.
    """

    df = standardize_text_columns(
        df,
        [
            "contract_id",
            "opportunity_id",
            "contract_status",
        ],
    )

    df["contract_status"] = (
        df["contract_status"]
        .str.title()
    )

    df["contract_start_date"] = (
        pd.to_datetime(
            df["contract_start_date"],
            errors="coerce",
        )
    )

    df["contract_end_date"] = (
        pd.to_datetime(
            df["contract_end_date"],
            errors="coerce",
        )
    )

    df["contract_value"] = (
        pd.to_numeric(
            df["contract_value"],
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
        ["contract_id"],
    )

    df = deduplicate(
        df,
        ["contract_id"],
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

def process_contracts() -> pd.DataFrame:
    """
    Execute the complete Silver transformation
    for the contract dataset.
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
            "Bronze contract dataset is empty."
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

    df = standardize_contracts(df)

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

    print("Silver Layer - Contracts")
    print("=========================")

    process_contracts()

    print(
        "\nContract Silver transformation "
        "completed successfully."
    )

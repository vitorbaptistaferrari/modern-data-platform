"""
Silver Layer - Record Types
===========================

Transforms the Bronze record type dataset into a standardized
Silver representation.

Responsibilities:

- Validate source structure
- Standardize text fields
- Remove invalid primary keys
- Deduplicate records
- Add Silver technical metadata

Business rules are intentionally excluded from this layer.
"""

from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


# ----------------------------------------------------------------------
# CONFIGURATION
# ----------------------------------------------------------------------

BRONZE_PATH = Path(
    "data/bronze/record_types.parquet"
)

SILVER_PATH = Path(
    "data/silver/record_types.parquet"
)


EXPECTED_COLUMNS = [
    "record_type_id",
    "record_type_name",
    "dt_ingestao",
]


# ----------------------------------------------------------------------
# VALIDATION
# ----------------------------------------------------------------------

def validate_columns(
    df: pd.DataFrame,
) -> None:
    """
    Validate whether the source contains the expected columns.
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

def standardize_record_types(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Standardize record type fields.
    """

    df = df.copy()

    df["record_type_id"] = (
        df["record_type_id"]
        .astype("string")
        .str.strip()
    )

    df["record_type_name"] = (
        df["record_type_name"]
        .astype("string")
        .str.strip()
        .str.title()
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

    Records without a record type identifier are removed.
    Duplicate identifiers are reduced to one record.
    """

    df = df.copy()

    df = df[
        df["record_type_id"].notna()
        & (df["record_type_id"] != "")
    ]

    df = (
        df.sort_values(
            by="dt_ingestao"
        )
        .drop_duplicates(
            subset=["record_type_id"],
            keep="last",
        )
    )

    return df


# ----------------------------------------------------------------------
# SILVER METADATA
# ----------------------------------------------------------------------

def add_silver_metadata(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Add technical metadata related to Silver processing.
    """

    df = df.copy()

    df["dt_processamento_silver"] = (
        datetime.now(timezone.utc)
    )

    df["nm_camada_origem"] = (
        "bronze"
    )

    df["nm_tabela_origem"] = (
        "record_types"
    )

    return df


# ----------------------------------------------------------------------
# PIPELINE
# ----------------------------------------------------------------------

def process_record_types() -> pd.DataFrame:
    """
    Execute the complete Silver transformation
    for the record type dataset.
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
            "Bronze record type dataset is empty."
        )

    print(
        f"Bronze records: {len(df)}"
    )

    # --------------------------------------------------------------
    # 1. Validate structure
    # --------------------------------------------------------------

    validate_columns(df)

    # --------------------------------------------------------------
    # 2. Standardize fields
    # --------------------------------------------------------------

    df = standardize_record_types(df)

    # --------------------------------------------------------------
    # 3. Apply quality rules
    # --------------------------------------------------------------

    df = apply_quality_rules(df)

    # --------------------------------------------------------------
    # 4. Add Silver metadata
    # --------------------------------------------------------------

    df = add_silver_metadata(df)

    # --------------------------------------------------------------
    # 5. Persist Silver
    # --------------------------------------------------------------

    SILVER_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    df.to_parquet(
        SILVER_PATH,
        index=False,
    )

    print(
        f"Silver records: {len(df)}"
    )

    print(
        f"Silver output: {SILVER_PATH}"
    )

    return df


# ----------------------------------------------------------------------
# MAIN
# ----------------------------------------------------------------------

if __name__ == "__main__":

    print("Silver Layer - Record Types")
    print("============================")

    process_record_types()

    print(
        "\nRecord Type Silver transformation "
        "completed successfully."
    )

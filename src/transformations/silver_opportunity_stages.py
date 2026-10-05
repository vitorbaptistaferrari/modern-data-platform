"""
Silver Layer - Opportunity Stages
=================================

Transforms the Bronze opportunity stage dataset into a
standardized Silver representation.

Responsibilities:

- Validate source structure
- Standardize text fields
- Apply data types
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
    "data/bronze/opportunity_stages.parquet"
)

SILVER_PATH = Path(
    "data/silver/opportunity_stages.parquet"
)


EXPECTED_COLUMNS = [
    "stage_id",
    "stage_name",
    "stage_order",
    "is_closed",
    "is_won",
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

def standardize_stages(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Standardize opportunity stage fields.
    """

    df = df.copy()

    df["stage_id"] = (
        df["stage_id"]
        .astype("string")
        .str.strip()
    )

    df["stage_name"] = (
        df["stage_name"]
        .astype("string")
        .str.strip()
        .str.title()
    )

    df["stage_order"] = (
        pd.to_numeric(
            df["stage_order"],
            errors="coerce",
        )
        .astype("Int64")
    )

    df["is_closed"] = (
        df["is_closed"]
        .astype("boolean")
    )

    df["is_won"] = (
        df["is_won"]
        .astype("boolean")
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

    Records without a stage identifier are removed.
    Duplicate stage identifiers are reduced to one record.
    """

    df = df.copy()

    df = df[
        df["stage_id"].notna()
        & (df["stage_id"] != "")
    ]

    df = (
        df.sort_values(
            by="dt_ingestao"
        )
        .drop_duplicates(
            subset=["stage_id"],
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
        "opportunity_stages"
    )

    return df


# ----------------------------------------------------------------------
# PIPELINE
# ----------------------------------------------------------------------

def process_opportunity_stages() -> pd.DataFrame:
    """
    Execute the complete Silver transformation
    for the opportunity stage dataset.
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
            "Bronze opportunity stage "
            "dataset is empty."
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

    df = standardize_stages(df)

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

    print(
        "Silver Layer - Opportunity Stages"
    )

    print(
        "================================="
    )

    process_opportunity_stages()

    print(
        "\nOpportunity Stage Silver "
        "transformation completed successfully."
    )

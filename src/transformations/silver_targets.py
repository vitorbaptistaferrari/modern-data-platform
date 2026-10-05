"""
Silver Layer - Targets
======================

Transforms the Bronze target dataset into a standardized
Silver representation.

Responsibilities:

- Validate source structure
- Standardize text fields
- Apply data types
- Validate primary keys
- Deduplicate records
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
    "data/bronze/targets.parquet"
)

SILVER_PATH = Path(
    "data/silver/targets.parquet"
)

SOURCE_TABLE = "targets"


EXPECTED_COLUMNS = [
    "target_id",
    "period",
    "brand",
    "target_type",
    "nature",
    "target_value",
    "dt_ingestao",
]


# ----------------------------------------------------------------------
# STANDARDIZATION
# ----------------------------------------------------------------------

def standardize_targets(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Apply target-specific standardization.
    """

    df = standardize_text_columns(
        df,
        [
            "target_id",
            "brand",
            "target_type",
            "nature",
        ],
    )

    df["brand"] = (
        df["brand"]
        .str.title()
    )

    df["target_type"] = (
        df["target_type"]
        .str.title()
    )

    df["nature"] = (
        df["nature"]
        .str.title()
    )

    df["period"] = (
        pd.to_datetime(
            df["period"],
            errors="coerce",
        )
    )

    df["target_value"] = (
        pd.to_numeric(
            df["target_value"],
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

    Records without a target identifier are removed.
    Duplicate target identifiers are reduced to one record.
    """

    df = remove_invalid_keys(
        df,
        ["target_id"],
    )

    df = deduplicate(
        df,
        ["target_id"],
    )

    return df


# ----------------------------------------------------------------------
# PIPELINE
# ----------------------------------------------------------------------

def process_targets() -> pd.DataFrame:
    """
    Execute the complete Silver transformation
    for the target dataset.
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
            "Bronze target dataset is empty."
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

    df = standardize_targets(df)

    # --------------------------------------------------------------
    # 3. Validate primary key
    # --------------------------------------------------------------

    df = apply_quality_rules(df)

    # --------------------------------------------------------------
    # 4. Add Silver metadata
    # --------------------------------------------------------------

    df = add_silver_metadata(
        df,
        SOURCE_TABLE,
    )

    # --------------------------------------------------------------
    # 5. Persist Silver
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

    print("Silver Layer - Targets")
    print("======================")

    process_targets()

    print(
        "\nTarget Silver transformation "
        "completed successfully."
    )

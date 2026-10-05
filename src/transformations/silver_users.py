"""
Silver Layer - Users
====================

Transforms the Bronze user dataset into a standardized
Silver representation.

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
    "data/bronze/users.parquet"
)

SILVER_PATH = Path(
    "data/silver/users.parquet"
)


EXPECTED_COLUMNS = [
    "user_id",
    "user_name",
    "department",
    "role",
    "active",
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

def standardize_users(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Standardize user fields.
    """

    df = df.copy()

    text_columns = [
        "user_id",
        "user_name",
        "department",
        "role",
    ]

    for column in text_columns:

        df[column] = (
            df[column]
            .astype("string")
            .str.strip()
        )

    df["department"] = (
        df["department"]
        .str.title()
    )

    df["role"] = (
        df["role"]
        .str.title()
    )

    df["active"] = (
        df["active"]
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

    Records without a user identifier are removed.
    Duplicate user identifiers are reduced to one record.
    """

    df = df.copy()

    df = df[
        df["user_id"].notna()
        & (df["user_id"] != "")
    ]

    df = (
        df.sort_values(
            by="dt_ingestao"
        )
        .drop_duplicates(
            subset=["user_id"],
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
        "users"
    )

    return df


# ----------------------------------------------------------------------
# PIPELINE
# ----------------------------------------------------------------------

def process_users() -> pd.DataFrame:
    """
    Execute the complete Silver transformation
    for the user dataset.
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
            "Bronze user dataset is empty."
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

    df = standardize_users(df)

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

    print("Silver Layer - Users")
    print("====================")

    process_users()

    print(
        "\nUser Silver transformation "
        "completed successfully."
    )

"""
Silver Layer - Users
====================

Transforms the Bronze user dataset into a standardized
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
    "data/bronze/users.parquet"
)

SILVER_PATH = Path(
    "data/silver/users.parquet"
)

SOURCE_TABLE = "users"


EXPECTED_COLUMNS = [
    "user_id",
    "user_name",
    "department",
    "role",
    "active",
    "dt_ingestao",
]


# ----------------------------------------------------------------------
# USER-SPECIFIC STANDARDIZATION
# ----------------------------------------------------------------------

def standardize_users(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Apply user-specific standardization.

    Generic text cleaning is delegated to the Silver utilities.
    """

    df = standardize_text_columns(
        df,
        [
            "user_id",
            "user_name",
            "department",
            "role",
        ],
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

    validate_columns(
        df,
        EXPECTED_COLUMNS,
    )

    # --------------------------------------------------------------
    # 2. Standardize fields
    # --------------------------------------------------------------

    df = standardize_users(df)

    # --------------------------------------------------------------
    # 3. Validate primary key
    # --------------------------------------------------------------

    df = remove_invalid_keys(
        df,
        ["user_id"],
    )

    # --------------------------------------------------------------
    # 4. Deduplicate
    # --------------------------------------------------------------

    df = deduplicate(
        df,
        ["user_id"],
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

    print("Silver Layer - Users")
    print("====================")

    process_users()

    print(
        "\nUser Silver transformation "
        "completed successfully."
    )

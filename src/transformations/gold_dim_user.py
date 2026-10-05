"""
Gold Layer - Dimension User
===========================

Builds the User dimension from the Silver user dataset.

Responsibilities:

- Read standardized Silver data
- Validate the source structure
- Standardize analytical attributes
- Remove invalid user identifiers
- Deduplicate users
- Generate a deterministic surrogate key
- Add a standard N/A member
- Persist the Gold dimension

Business rules are intentionally excluded from this dimension.
"""

from hashlib import sha256
from pathlib import Path

import pandas as pd


# ----------------------------------------------------------------------
# CONFIGURATION
# ----------------------------------------------------------------------

SILVER_PATH = Path(
    "data/silver/users.parquet"
)

GOLD_PATH = Path(
    "data/gold/dim_user.parquet"
)

SOURCE_TABLE = "users"


EXPECTED_COLUMNS = [
    "user_id",
    "user_name",
    "department",
    "role",
    "active",
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

def standardize_users(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Standardize user attributes for analytical consumption.
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

    df["user_name"] = (
        df["user_name"]
        .str.title()
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
# QUALITY RULES
# ----------------------------------------------------------------------

def remove_invalid_users(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Remove records with null or empty user identifiers.
    """

    return df[
        df["user_id"].notna()
        & (df["user_id"] != "")
    ].copy()


def remove_duplicates(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Keep one analytical record per user.
    """

    return (
        df[
            EXPECTED_COLUMNS
        ]
        .drop_duplicates(
            subset=["user_id"],
            keep="last",
        )
        .reset_index(drop=True)
    )


# ----------------------------------------------------------------------
# SURROGATE KEY
# ----------------------------------------------------------------------

def generate_surrogate_key(
    user_id: str,
) -> str:
    """
    Generate a deterministic surrogate key based on
    the source user identifier.
    """

    normalized_value = (
        str(user_id)
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
    Add the user surrogate key.
    """

    df = df.copy()

    df["user_sk"] = (
        df["user_id"]
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
    Add a standard N/A member used when a user cannot
    be resolved during analytical processing.
    """

    unknown_record = pd.DataFrame(
        [
            {
                "user_sk": generate_surrogate_key(
                    "N/A"
                ),
                "user_id": "N/A",
                "user_name": "N/A",
                "department": "N/A",
                "role": "N/A",
                "active": pd.NA,
            }
        ]
    )

    return pd.concat(
        [
            unknown_record,
            df[
                [
                    "user_sk",
                    "user_id",
                    "user_name",
                    "department",
                    "role",
                    "active",
                ]
            ],
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

def process_dim_user() -> pd.DataFrame:
    """
    Execute the complete Gold transformation
    for the User dimension.
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
            "Silver user dataset is empty."
        )

    print(
        f"Silver records: {len(df)}"
    )

    validate_columns(
        df
    )

    df = standardize_users(
        df
    )

    df = remove_invalid_users(
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
            "user_sk",
            "user_id",
            "user_name",
            "department",
            "role",
            "active",
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

    print("Gold Layer - Dimension User")
    print("===========================")

    process_dim_user()

    print(
        "\nUser dimension created successfully."
    )

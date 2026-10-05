"""
Gold Layer - Dimension Opportunity Stage
========================================

Builds the Opportunity Stage dimension from the Silver
opportunity stage dataset.

Responsibilities:

- Read standardized Silver data
- Validate the source structure
- Standardize analytical attributes
- Validate stage identifiers
- Deduplicate stages
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
    "data/silver/opportunity_stages.parquet"
)

GOLD_PATH = Path(
    "data/gold/dim_opportunity_stage.parquet"
)

SOURCE_TABLE = "opportunity_stages"


EXPECTED_COLUMNS = [
    "stage_id",
    "stage_name",
    "stage_order",
    "is_closed",
    "is_won",
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

def standardize_stages(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Standardize opportunity stage attributes.
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
# QUALITY RULES
# ----------------------------------------------------------------------

def remove_invalid_stages(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Remove records with null or empty stage identifiers.
    """

    return df[
        df["stage_id"].notna()
        & (df["stage_id"] != "")
    ].copy()


def validate_stage_names(
    df: pd.DataFrame,
) -> None:
    """
    Validate that stage names are populated.
    """

    invalid_count = (
        df["stage_name"].isna()
        | (df["stage_name"] == "")
    ).sum()

    if invalid_count > 0:
        raise ValueError(
            "Stage name contains "
            f"{invalid_count} invalid records."
        )


def remove_duplicates(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Keep one record per stage identifier.
    """

    return (
        df[
            EXPECTED_COLUMNS
        ]
        .drop_duplicates(
            subset=["stage_id"],
            keep="last",
        )
        .reset_index(drop=True)
    )


# ----------------------------------------------------------------------
# SURROGATE KEY
# ----------------------------------------------------------------------

def generate_surrogate_key(
    stage_id: str,
) -> str:
    """
    Generate a deterministic surrogate key based on
    the source stage identifier.
    """

    normalized_value = (
        str(stage_id)
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
    Add the opportunity stage surrogate key.
    """

    df = df.copy()

    df["opportunity_stage_sk"] = (
        df["stage_id"]
        .apply(
            generate_surrogate_key
        )
    )

    return df


# ----------------------------------------------------------------------
# STANDARD N/A MEMBER
# ----------------------------------------------------------------------

def add_unknown_member(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Add a standard N/A member used when an opportunity
    stage cannot be resolved.
    """

    unknown_record = pd.DataFrame(
        [
            {
                "opportunity_stage_sk": (
                    generate_surrogate_key(
                        "N/A"
                    )
                ),
                "stage_id": "N/A",
                "stage_name": "N/A",
                "stage_order": pd.NA,
                "is_closed": pd.NA,
                "is_won": pd.NA,
            }
        ]
    )

    return pd.concat(
        [
            unknown_record,
            df[
                [
                    "opportunity_stage_sk",
                    "stage_id",
                    "stage_name",
                    "stage_order",
                    "is_closed",
                    "is_won",
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

def process_dim_opportunity_stage() -> pd.DataFrame:
    """
    Execute the complete Gold transformation
    for the Opportunity Stage dimension.
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
            "Silver opportunity stage dataset "
            "is empty."
        )

    print(
        f"Silver records: {len(df)}"
    )

    validate_columns(
        df
    )

    df = standardize_stages(
        df
    )

    df = remove_invalid_stages(
        df
    )

    validate_stage_names(
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
            "opportunity_stage_sk",
            "stage_id",
            "stage_name",
            "stage_order",
            "is_closed",
            "is_won",
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

    print(
        "Gold Layer - "
        "Dimension Opportunity Stage"
    )

    print(
        "============================"
    )

    process_dim_opportunity_stage()

    print(
        "\nOpportunity Stage dimension "
        "created successfully."
    )

"""
Silver Layer - Opportunities
============================

Transforms the Bronze opportunity dataset into a standardized
Silver representation.

Responsibilities:

- Validate source structure
- Standardize text fields
- Apply data types
- Validate primary and foreign keys
- Deduplicate opportunities
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
    "data/bronze/opportunities.parquet"
)

SILVER_PATH = Path(
    "data/silver/opportunities.parquet"
)

SOURCE_TABLE = "opportunities"


EXPECTED_COLUMNS = [
    "opportunity_id",
    "customer_id",
    "user_id",
    "record_type_id",
    "stage_id",
    "opportunity_type",
    "brand",
    "origin",
    "opportunity_date",
    "close_date",
    "amount",
    "dt_ingestao",
]


# ----------------------------------------------------------------------
# STANDARDIZATION
# ----------------------------------------------------------------------

def standardize_opportunities(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Apply opportunity-specific standardization.
    """

    df = standardize_text_columns(
        df,
        [
            "opportunity_id",
            "customer_id",
            "user_id",
            "record_type_id",
            "stage_id",
            "opportunity_type",
            "brand",
            "origin",
        ],
    )

    df["opportunity_type"] = (
        df["opportunity_type"]
        .str.title()
    )

    df["brand"] = (
        df["brand"]
        .str.title()
    )

    df["origin"] = (
        df["origin"]
        .str.title()
    )

    df["opportunity_date"] = (
        pd.to_datetime(
            df["opportunity_date"],
            errors="coerce",
        )
    )

    df["close_date"] = (
        pd.to_datetime(
            df["close_date"],
            errors="coerce",
        )
    )

    df["amount"] = (
        pd.to_numeric(
            df["amount"],
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

    Records without an opportunity identifier are removed.
    """

    df = remove_invalid_keys(
        df,
        ["opportunity_id"],
    )

    df = deduplicate(
        df,
        ["opportunity_id"],
    )

    return df


# ----------------------------------------------------------------------
# FOREIGN KEY VALIDATION
# ----------------------------------------------------------------------

def validate_foreign_keys(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Validate that required foreign key fields are populated.

    Referential integrity against the dimension datasets will
    be evaluated in a later pipeline stage.
    """

    foreign_key_columns = [
        "customer_id",
        "user_id",
        "record_type_id",
        "stage_id",
    ]

    for column in foreign_key_columns:

        invalid_count = (
            df[column].isna()
            | (df[column] == "")
        ).sum()

        if invalid_count > 0:

            raise ValueError(
                f"Foreign key column "
                f"'{column}' contains "
                f"{invalid_count} invalid records."
            )

    return df


# ----------------------------------------------------------------------
# PIPELINE
# ----------------------------------------------------------------------

def process_opportunities() -> pd.DataFrame:
    """
    Execute the complete Silver transformation
    for the opportunity dataset.
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
            "Bronze opportunity dataset is empty."
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

    df = standardize_opportunities(df)

    # --------------------------------------------------------------
    # 3. Validate primary key
    # --------------------------------------------------------------

    df = apply_quality_rules(df)

    # --------------------------------------------------------------
    # 4. Validate foreign key fields
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

    print("Silver Layer - Opportunities")
    print("============================")

    process_opportunities()

    print(
        "\nOpportunity Silver transformation "
        "completed successfully."
    )"""
Silver Layer - Opportunities
============================

Transforms the Bronze opportunity dataset into a standardized
Silver representation.

Responsibilities:

- Validate source structure
- Standardize text fields
- Apply data types
- Validate primary and foreign keys
- Deduplicate opportunities
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
    "data/bronze/opportunities.parquet"
)

SILVER_PATH = Path(
    "data/silver/opportunities.parquet"
)

SOURCE_TABLE = "opportunities"


EXPECTED_COLUMNS = [
    "opportunity_id",
    "customer_id",
    "user_id",
    "record_type_id",
    "stage_id",
    "opportunity_type",
    "brand",
    "origin",
    "opportunity_date",
    "close_date",
    "amount",
    "dt_ingestao",
]


# ----------------------------------------------------------------------
# STANDARDIZATION
# ----------------------------------------------------------------------

def standardize_opportunities(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Apply opportunity-specific standardization.
    """

    df = standardize_text_columns(
        df,
        [
            "opportunity_id",
            "customer_id",
            "user_id",
            "record_type_id",
            "stage_id",
            "opportunity_type",
            "brand",
            "origin",
        ],
    )

    df["opportunity_type"] = (
        df["opportunity_type"]
        .str.title()
    )

    df["brand"] = (
        df["brand"]
        .str.title()
    )

    df["origin"] = (
        df["origin"]
        .str.title()
    )

    df["opportunity_date"] = (
        pd.to_datetime(
            df["opportunity_date"],
            errors="coerce",
        )
    )

    df["close_date"] = (
        pd.to_datetime(
            df["close_date"],
            errors="coerce",
        )
    )

    df["amount"] = (
        pd.to_numeric(
            df["amount"],
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

    Records without an opportunity identifier are removed.
    """

    df = remove_invalid_keys(
        df,
        ["opportunity_id"],
    )

    df = deduplicate(
        df,
        ["opportunity_id"],
    )

    return df


# ----------------------------------------------------------------------
# FOREIGN KEY VALIDATION
# ----------------------------------------------------------------------

def validate_foreign_keys(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Validate that required foreign key fields are populated.

    Referential integrity against the dimension datasets will
    be evaluated in a later pipeline stage.
    """

    foreign_key_columns = [
        "customer_id",
        "user_id",
        "record_type_id",
        "stage_id",
    ]

    for column in foreign_key_columns:

        invalid_count = (
            df[column].isna()
            | (df[column] == "")
        ).sum()

        if invalid_count > 0:

            raise ValueError(
                f"Foreign key column "
                f"'{column}' contains "
                f"{invalid_count} invalid records."
            )

    return df


# ----------------------------------------------------------------------
# PIPELINE
# ----------------------------------------------------------------------

def process_opportunities() -> pd.DataFrame:
    """
    Execute the complete Silver transformation
    for the opportunity dataset.
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
            "Bronze opportunity dataset is empty."
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

    df = standardize_opportunities(df)

    # --------------------------------------------------------------
    # 3. Validate primary key
    # --------------------------------------------------------------

    df = apply_quality_rules(df)

    # --------------------------------------------------------------
    # 4. Validate foreign key fields
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

    print("Silver Layer - Opportunities")
    print("============================")

    process_opportunities()

    print(
        "\nOpportunity Silver transformation "
        "completed successfully."
    )

"""
Gold Layer - Dimension Opportunity
==================================

Builds the Opportunity dimension by consolidating the Silver
opportunity and customer datasets.

Responsibilities:

- Read standardized Silver datasets
- Validate source structures
- Join opportunities with customers
- Standardize analytical attributes
- Validate relationships
- Remove invalid opportunity identifiers
- Deduplicate opportunities
- Generate a deterministic surrogate key
- Add a standard N/A member
- Persist the Gold dimension

Contracts and quotes are intentionally not joined into this
dimension because they represent transactional information that
will be used later during Fact Revenue processing.

Business rules related to revenue classification are intentionally
excluded from this dimension.
"""

from hashlib import sha256
from pathlib import Path

import pandas as pd


# ----------------------------------------------------------------------
# CONFIGURATION
# ----------------------------------------------------------------------

OPPORTUNITIES_PATH = Path(
    "data/silver/opportunities.parquet"
)

CUSTOMERS_PATH = Path(
    "data/silver/customers.parquet"
)

GOLD_PATH = Path(
    "data/gold/dim_opportunity.parquet"
)

OPPORTUNITIES_SOURCE_TABLE = (
    "opportunities"
)

CUSTOMERS_SOURCE_TABLE = (
    "customers"
)


OPPORTUNITY_COLUMNS = [
    "opportunity_id",
    "customer_id",
    "opportunity_type",
    "brand",
    "origin",
    "opportunity_date",
    "close_date",
]


CUSTOMER_COLUMNS = [
    "customer_id",
    "customer_name",
    "city",
    "state",
    "segment",
]


# ----------------------------------------------------------------------
# VALIDATION
# ----------------------------------------------------------------------

def validate_columns(
    df: pd.DataFrame,
    expected_columns: list[str],
    dataset_name: str,
) -> None:
    """
    Validate whether a source contains all required columns.
    """

    missing_columns = [
        column
        for column in expected_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing expected columns in "
            f"{dataset_name}: "
            f"{missing_columns}"
        )


# ----------------------------------------------------------------------
# STANDARDIZATION
# ----------------------------------------------------------------------

def standardize_opportunities(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Standardize opportunity attributes for analytical use.
    """

    df = df.copy()

    text_columns = [
        "opportunity_id",
        "customer_id",
        "opportunity_type",
        "brand",
        "origin",
    ]

    for column in text_columns:

        df[column] = (
            df[column]
            .astype("string")
            .str.strip()
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

    return df


def standardize_customers(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Standardize customer attributes for analytical use.
    """

    df = df.copy()

    text_columns = [
        "customer_id",
        "customer_name",
        "city",
        "state",
        "segment",
    ]

    for column in text_columns:

        df[column] = (
            df[column]
            .astype("string")
            .str.strip()
        )

    df["customer_name"] = (
        df["customer_name"]
        .str.title()
    )

    df["city"] = (
        df["city"]
        .str.title()
    )

    df["state"] = (
        df["state"]
        .str.upper()
    )

    df["segment"] = (
        df["segment"]
        .str.title()
    )

    return df


# ----------------------------------------------------------------------
# QUALITY RULES
# ----------------------------------------------------------------------

def remove_invalid_opportunities(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Remove opportunities without a valid opportunity identifier.
    """

    return df[
        df["opportunity_id"].notna()
        & (df["opportunity_id"] != "")
    ].copy()


def remove_duplicate_opportunities(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Keep one analytical record per opportunity.
    """

    return (
        df
        .drop_duplicates(
            subset=["opportunity_id"],
            keep="last",
        )
        .reset_index(drop=True)
    )


def validate_customer_relationship(
    opportunities: pd.DataFrame,
    customers: pd.DataFrame,
) -> None:
    """
    Validate that opportunity customer identifiers
    are present in the customer dataset.

    The validation is performed before the analytical join
    so referential integrity problems are explicit.
    """

    customer_ids = set(
        customers["customer_id"]
        .dropna()
        .astype(str)
    )

    opportunity_customer_ids = (
        opportunities["customer_id"]
        .dropna()
        .astype(str)
    )

    invalid_ids = sorted(
        set(opportunity_customer_ids)
        - customer_ids
    )

    if invalid_ids:

        raise ValueError(
            "Opportunities contain customer IDs "
            "that do not exist in the customer "
            f"dataset. Invalid IDs: {invalid_ids[:10]}"
        )


# ----------------------------------------------------------------------
# ANALYTICAL JOIN
# ----------------------------------------------------------------------

def build_opportunity_dimension(
    opportunities: pd.DataFrame,
    customers: pd.DataFrame,
) -> pd.DataFrame:
    """
    Join opportunities with customer descriptive attributes.
    """

    customer_attributes = customers[
        CUSTOMER_COLUMNS
    ].copy()

    customer_attributes = (
        customer_attributes
        .drop_duplicates(
            subset=["customer_id"],
            keep="last",
        )
    )

    dimension = opportunities[
        OPPORTUNITY_COLUMNS
    ].merge(
        customer_attributes,
        on="customer_id",
        how="left",
        validate="many_to_one",
    )

    return dimension


# ----------------------------------------------------------------------
# SURROGATE KEY
# ----------------------------------------------------------------------

def generate_surrogate_key(
    opportunity_id: str,
) -> str:
    """
    Generate a deterministic surrogate key based on
    the source opportunity identifier.
    """

    normalized_value = (
        str(opportunity_id)
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
    Add the opportunity surrogate key.
    """

    df = df.copy()

    df["opportunity_sk"] = (
        df["opportunity_id"]
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
    cannot be resolved during analytical processing.
    """

    unknown_record = pd.DataFrame(
        [
            {
                "opportunity_sk": (
                    generate_surrogate_key(
                        "N/A"
                    )
                ),
                "opportunity_id": "N/A",
                "customer_id": "N/A",
                "customer_name": "N/A",
                "city": "N/A",
                "state": "N/A",
                "segment": "N/A",
                "opportunity_type": "N/A",
                "brand": "N/A",
                "origin": "N/A",
                "opportunity_date": pd.NaT,
                "close_date": pd.NaT,
            }
        ]
    )

    return pd.concat(
        [
            unknown_record,
            df[
                [
                    "opportunity_sk",
                    "opportunity_id",
                    "customer_id",
                    "customer_name",
                    "city",
                    "state",
                    "segment",
                    "opportunity_type",
                    "brand",
                    "origin",
                    "opportunity_date",
                    "close_date",
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

def process_dim_opportunity() -> pd.DataFrame:
    """
    Execute the complete Gold transformation
    for the Opportunity dimension.
    """

    if not OPPORTUNITIES_PATH.exists():
        raise FileNotFoundError(
            "Silver opportunity dataset not found: "
            f"{OPPORTUNITIES_PATH}"
        )

    if not CUSTOMERS_PATH.exists():
        raise FileNotFoundError(
            "Silver customer dataset not found: "
            f"{CUSTOMERS_PATH}"
        )

    opportunities = pd.read_parquet(
        OPPORTUNITIES_PATH
    )

    customers = pd.read_parquet(
        CUSTOMERS_PATH
    )

    if opportunities.empty:
        raise ValueError(
            "Silver opportunity dataset is empty."
        )

    if customers.empty:
        raise ValueError(
            "Silver customer dataset is empty."
        )

    print(
        f"Silver opportunity records: "
        f"{len(opportunities)}"
    )

    print(
        f"Silver customer records: "
        f"{len(customers)}"
    )

    # --------------------------------------------------------------
    # Validate source structures
    # --------------------------------------------------------------

    validate_columns(
        opportunities,
        OPPORTUNITY_COLUMNS,
        OPPORTUNITIES_SOURCE_TABLE,
    )

    validate_columns(
        customers,
        CUSTOMER_COLUMNS,
        CUSTOMERS_SOURCE_TABLE,
    )

    # --------------------------------------------------------------
    # Standardize source datasets
    # --------------------------------------------------------------

    opportunities = (
        standardize_opportunities(
            opportunities
        )
    )

    customers = (
        standardize_customers(
            customers
        )
    )

    # --------------------------------------------------------------
    # Apply technical quality rules
    # --------------------------------------------------------------

    opportunities = (
        remove_invalid_opportunities(
            opportunities
        )
    )

    customers = (
        customers[
            customers["customer_id"].notna()
            & (customers["customer_id"] != "")
        ]
        .copy()
    )

    customers = (
        customers
        .drop_duplicates(
            subset=["customer_id"],
            keep="last",
        )
        .reset_index(drop=True)
    )

    validate_customer_relationship(
        opportunities,
        customers,
    )

    opportunities = (
        remove_duplicate_opportunities(
            opportunities
        )
    )

    # --------------------------------------------------------------
    # Build analytical dimension
    # --------------------------------------------------------------

    dimension = (
        build_opportunity_dimension(
            opportunities,
            customers,
        )
    )

    # --------------------------------------------------------------
    # Generate surrogate key
    # --------------------------------------------------------------

    dimension = add_surrogate_key(
        dimension
    )

    # --------------------------------------------------------------
    # Add standard N/A member
    # --------------------------------------------------------------

    dimension = add_unknown_member(
        dimension
    )

    # --------------------------------------------------------------
    # Final column order
    # --------------------------------------------------------------

    dimension = dimension[
        [
            "opportunity_sk",
            "opportunity_id",
            "customer_id",
            "customer_name",
            "city",
            "state",
            "segment",
            "opportunity_type",
            "brand",
            "origin",
            "opportunity_date",
            "close_date",
        ]
    ]

    # --------------------------------------------------------------
    # Persist Gold
    # --------------------------------------------------------------

    save_gold(
        dimension
    )

    print(
        f"Gold records: {len(dimension)}"
    )

    return dimension


# ----------------------------------------------------------------------
# MAIN
# ----------------------------------------------------------------------

if __name__ == "__main__":

    print(
        "Gold Layer - Dimension Opportunity"
    )

    print(
        "=================================="
    )

    process_dim_opportunity()

    print(
        "\nOpportunity dimension "
        "created successfully."
    )

"""
Gold Layer - Revenue Fact
=========================

Builds the Revenue fact table from standardized Silver datasets
and Gold analytical dimensions.

The public implementation uses synthetic data and business rules.

Revenue is generated only for opportunities that reached a
won stage.

Revenue classification:

- Prospecting -> Prospecting
- Retention -> Renewal
- Expansion -> Cross-Sell or Up-Sell

Synthetic Expansion rule:

- Alpha -> Cross-Sell
- Beta -> Up-Sell
- Gamma -> Up-Sell

Revenue value rules:

- Prospecting:
    Uses the opportunity amount.

- Retention:
    Uses the active contract value when available.
    Otherwise, uses the opportunity amount.

- Expansion:
    Uses the maximum accepted quote amount when available.
    Otherwise, uses the opportunity amount.

Responsibilities:

- Read Silver operational datasets
- Read Gold analytical dimensions
- Apply revenue business rules
- Generate analytical foreign keys
- Generate a deterministic fact key
- Validate the final fact
- Persist the Gold fact

The implementation is intentionally synthetic and does not expose
proprietary production logic or identifiers.
"""

from hashlib import sha256
from pathlib import Path

import pandas as pd


# ----------------------------------------------------------------------
# SOURCE PATHS
# ----------------------------------------------------------------------

OPPORTUNITIES_PATH = Path(
    "data/silver/opportunities.parquet"
)

USERS_PATH = Path(
    "data/silver/users.parquet"
)

QUOTES_PATH = Path(
    "data/silver/quotes.parquet"
)

CONTRACTS_PATH = Path(
    "data/silver/contracts.parquet"
)


# ----------------------------------------------------------------------
# GOLD DIMENSION PATHS
# ----------------------------------------------------------------------

DIM_OPPORTUNITY_PATH = Path(
    "data/gold/dim_opportunity.parquet"
)

DIM_USER_PATH = Path(
    "data/gold/dim_user.parquet"
)

DIM_BRAND_PATH = Path(
    "data/gold/dim_brand.parquet"
)

DIM_CALENDAR_PATH = Path(
    "data/gold/dim_calendar.parquet"
)

DIM_STAGE_PATH = Path(
    "data/gold/dim_opportunity_stage.parquet"
)

DIM_NEGOTIATION_TYPE_PATH = Path(
    "data/gold/dim_negotiation_type.parquet"
)

DIM_REVENUE_HIERARCHY_PATH = Path(
    "data/gold/dim_revenue_hierarchy.parquet"
)


# ----------------------------------------------------------------------
# OUTPUT
# ----------------------------------------------------------------------

GOLD_PATH = Path(
    "data/gold/fact_revenue.parquet"
)


# ----------------------------------------------------------------------
# BUSINESS MAPPINGS
# ----------------------------------------------------------------------

NEGOTIATION_TYPE_MAPPING = {
    "Prospecting": "Prospecting",
    "Retention": "Renewal",
    "Expansion": "Expansion",
}


EXPANSION_BRAND_MAPPING = {
    "Alpha": "Cross-Sell",
    "Beta": "Up-Sell",
    "Gamma": "Up-Sell",
}


# ----------------------------------------------------------------------
# VALIDATION HELPERS
# ----------------------------------------------------------------------

def validate_columns(
    df,
    expected_columns,
    source_name,
):
    """
    Validate that the source contains all required columns.
    """

    missing_columns = [
        column
        for column in expected_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing expected columns in "
            f"{source_name}: {missing_columns}"
        )


def validate_file(path, source_name):
    """
    Validate that a required dataset exists.
    """

    if not path.exists():
        raise FileNotFoundError(
            f"{source_name} not found: {path}"
        )


# ----------------------------------------------------------------------
# KEY HELPERS
# ----------------------------------------------------------------------

def generate_surrogate_key(value):
    """
    Generate a deterministic SHA-256 key.
    """

    normalized_value = (
        str(value)
        .strip()
        .upper()
    )

    return sha256(
        normalized_value.encode("utf-8")
    ).hexdigest()


def get_unknown_key():
    """
    Return the deterministic unknown member key.
    """

    return generate_surrogate_key(
        "N/A"
    )


# ----------------------------------------------------------------------
# SOURCE PREPARATION
# ----------------------------------------------------------------------

def prepare_opportunities(df):
    """
    Standardize opportunity values and data types.
    """

    df = df.copy()

    text_columns = [
        "opportunity_id",
        "customer_id",
        "user_id",
        "record_type_id",
        "stage_id",
        "opportunity_type",
        "brand",
        "origin",
    ]

    for column in text_columns:
        df[column] = (
            df[column]
            .astype("string")
            .str.strip()
            .str.title()
        )

    df["opportunity_date"] = pd.to_datetime(
        df["opportunity_date"],
        errors="coerce",
    )

    df["close_date"] = pd.to_datetime(
        df["close_date"],
        errors="coerce",
    )

    df["amount"] = pd.to_numeric(
        df["amount"],
        errors="coerce",
    )

    return df


def prepare_quotes(df):
    """
    Standardize quote values and data types.
    """

    df = df.copy()

    text_columns = [
        "quote_id",
        "opportunity_id",
        "quote_status",
    ]

    for column in text_columns:
        df[column] = (
            df[column]
            .astype("string")
            .str.strip()
            .str.title()
        )

    df["quote_date"] = pd.to_datetime(
        df["quote_date"],
        errors="coerce",
    )

    df["quoted_amount"] = pd.to_numeric(
        df["quoted_amount"],
        errors="coerce",
    )

    return df


def prepare_contracts(df):
    """
    Standardize contract values and data types.
    """

    df = df.copy()

    text_columns = [
        "contract_id",
        "opportunity_id",
        "contract_status",
    ]

    for column in text_columns:
        df[column] = (
            df[column]
            .astype("string")
            .str.strip()
            .str.title()
        )

    df["contract_start_date"] = pd.to_datetime(
        df["contract_start_date"],
        errors="coerce",
    )

    df["contract_end_date"] = pd.to_datetime(
        df["contract_end_date"],
        errors="coerce",
    )

    df["contract_value"] = pd.to_numeric(
        df["contract_value"],
        errors="coerce",
    )

    return df


# ----------------------------------------------------------------------
# REVENUE CLASSIFICATION
# ----------------------------------------------------------------------

def classify_revenue(opportunity):
    """
    Determine the analytical revenue classification.
    """

    opportunity_type = opportunity[
        "opportunity_type"
    ]

    brand = opportunity[
        "brand"
    ]

    negotiation_type = NEGOTIATION_TYPE_MAPPING.get(
        opportunity_type
    )

    if negotiation_type is None:
        raise ValueError(
            "Unmapped opportunity type: "
            f"{opportunity_type}"
        )

    if negotiation_type == "Expansion":
        revenue_level_3 = EXPANSION_BRAND_MAPPING.get(
            brand
        )

        if revenue_level_3 is None:
            raise ValueError(
                "No synthetic Expansion mapping "
                f"found for brand: {brand}"
            )
    else:
        revenue_level_3 = negotiation_type

    return (
        negotiation_type,
        revenue_level_3,
    )


# ----------------------------------------------------------------------
# REVENUE VALUE
# ----------------------------------------------------------------------

def get_active_contract_value(
    opportunity_id,
    contracts,
):
    """
    Return the active contract value for an opportunity.

    If multiple active contracts exist, the highest value is used.
    """

    matching_contracts = contracts[
        contracts["opportunity_id"]
        == opportunity_id
    ]

    active_contracts = matching_contracts[
        matching_contracts["contract_status"]
        == "Active"
    ]

    active_contracts = active_contracts[
        active_contracts["contract_value"].notna()
        & (active_contracts["contract_value"] > 0)
    ]

    if active_contracts.empty:
        return None

    return active_contracts[
        "contract_value"
    ].max()


def get_accepted_quote_value(
    opportunity_id,
    quotes,
):
    """
    Return the highest accepted quote value
    for an opportunity.
    """

    matching_quotes = quotes[
        quotes["opportunity_id"]
        == opportunity_id
    ]

    accepted_quotes = matching_quotes[
        matching_quotes["quote_status"]
        == "Accepted"
    ]

    accepted_quotes = accepted_quotes[
        accepted_quotes["quoted_amount"].notna()
        & (accepted_quotes["quoted_amount"] > 0)
    ]

    if accepted_quotes.empty:
        return None

    return accepted_quotes[
        "quoted_amount"
    ].max()


def calculate_revenue_value(
    opportunity,
    contracts,
    quotes,
):
    """
    Calculate the analytical revenue value.
    """

    opportunity_type = opportunity[
        "opportunity_type"
    ]

    opportunity_amount = opportunity[
        "amount"
    ]

    if pd.isna(opportunity_amount):
        return None

    if opportunity_amount <= 0:
        return None

    if opportunity_type == "Prospecting":
        return opportunity_amount

    if opportunity_type == "Retention":
        contract_value = get_active_contract_value(
            opportunity["opportunity_id"],
            contracts,
        )

        if contract_value is not None:
            return contract_value

        return opportunity_amount

    if opportunity_type == "Expansion":
        quote_value = get_accepted_quote_value(
            opportunity["opportunity_id"],
            quotes,
        )

        if quote_value is not None:
            return quote_value

        return opportunity_amount

    raise ValueError(
        "Unsupported opportunity type: "
        f"{opportunity_type}"
    )


# ----------------------------------------------------------------------
# DIMENSION LOOKUPS
# ----------------------------------------------------------------------

def build_lookup(
    df,
    key_column,
    value_column,
):
    """
    Build a dictionary lookup between a business key
    and a Gold surrogate key.
    """

    return dict(
        zip(
            df[key_column],
            df[value_column],
        )
    )


def build_stage_lookup(stage_df):
    """
    Build a lookup containing the stage analytical key
    and the won indicator.
    """

    return (
        stage_df[
            [
                "stage_id",
                "opportunity_stage_sk",
                "is_won",
            ]
        ]
        .drop_duplicates(
            subset=["stage_id"]
        )
        .set_index("stage_id")
        .to_dict("index")
    )


def get_lookup_key(
    lookup,
    business_key,
):
    """
    Return a dimension key or the standard unknown key.
    """

    if pd.isna(business_key):
        return get_unknown_key()

    return lookup.get(
        business_key,
        get_unknown_key(),
    )


# ----------------------------------------------------------------------
# FACT BUILDING
# ----------------------------------------------------------------------

def build_revenue_fact(
    opportunities,
    quotes,
    contracts,
    dim_opportunity,
    dim_user,
    dim_brand,
    dim_calendar,
    dim_stage,
    dim_negotiation_type,
    dim_revenue_hierarchy,
):
    """
    Build the Revenue fact.

    Only opportunities associated with a won stage generate
    analytical revenue.
    """

    opportunity_lookup = build_lookup(
        dim_opportunity,
        "opportunity_id",
        "opportunity_sk",
    )

    user_lookup = build_lookup(
        dim_user,
        "user_id",
        "user_sk",
    )

    brand_lookup = build_lookup(
        dim_brand,
        "brand",
        "brand_sk",
    )

    calendar_lookup = build_lookup(
        dim_calendar[
            dim_calendar["date"].notna()
        ],
        "date",
        "calendar_sk",
    )

    stage_lookup = build_stage_lookup(
        dim_stage
    )

    negotiation_lookup = build_lookup(
        dim_negotiation_type,
        "negotiation_type",
        "negotiation_type_sk",
    )

    hierarchy_lookup = (
        dim_revenue_hierarchy[
            [
                "revenue_level_2",
                "revenue_level_3",
                "revenue_hierarchy_sk",
            ]
        ]
        .drop_duplicates(
            subset=[
                "revenue_level_2",
                "revenue_level_3",
            ]
        )
        .set_index(
            [
                "revenue_level_2",
                "revenue_level_3",
            ]
        )["revenue_hierarchy_sk"]
        .to_dict()
    )

    records = []

    for _, opportunity in opportunities.iterrows():

        stage_id = opportunity[
            "stage_id"
        ]

        stage_information = stage_lookup.get(
            stage_id
        )

        if stage_information is None:
            raise ValueError(
                "Opportunity references an unknown "
                f"stage_id: {stage_id}"
            )

        # --------------------------------------------------------------
        # Revenue eligibility
        # --------------------------------------------------------------

        if not bool(
            stage_information["is_won"]
        ):
            continue

        negotiation_type, revenue_level_3 = (
            classify_revenue(
                opportunity
            )
        )

        revenue_value = calculate_revenue_value(
            opportunity,
            contracts,
            quotes,
        )

        if revenue_value is None:
            continue

        if revenue_value <= 0:
            continue

        revenue_level_2 = negotiation_type

        hierarchy_key = hierarchy_lookup.get(
            (
                revenue_level_2,
                revenue_level_3,
            )
        )

        if hierarchy_key is None:
            raise ValueError(
                "Revenue hierarchy member not found "
                f"for ({revenue_level_2}, "
                f"{revenue_level_3})."
            )

        close_date = opportunity[
            "close_date"
        ]

        calendar_key = get_lookup_key(
            calendar_lookup,
            close_date,
        )

        opportunity_key = get_lookup_key(
            opportunity_lookup,
            opportunity["opportunity_id"],
        )

        user_key = get_lookup_key(
            user_lookup,
            opportunity["user_id"],
        )

        brand_key = get_lookup_key(
            brand_lookup,
            opportunity["brand"],
        )

        negotiation_key = get_lookup_key(
            negotiation_lookup,
            negotiation_type,
        )

        revenue_sk_seed = "|".join(
            [
                str(
                    opportunity["opportunity_id"]
                ),
                str(
                    negotiation_type
                ),
                str(
                    revenue_level_3
                ),
            ]
        )

        revenue_sk = generate_surrogate_key(
            revenue_sk_seed
        )

        records.append(
            {
                "revenue_sk": revenue_sk,
                "opportunity_sk": opportunity_key,
                "user_sk": user_key,
                "brand_sk": brand_key,
                "calendar_sk": calendar_key,
                "opportunity_stage_sk": stage_information[
                    "opportunity_stage_sk"
                ],
                "negotiation_type_sk": negotiation_key,
                "revenue_hierarchy_sk": hierarchy_key,
                "revenue_value": revenue_value,
            }
        )

    fact = pd.DataFrame(
        records
    )

    if fact.empty:
        raise ValueError(
            "No revenue records were generated. "
            "Check opportunity stages and revenue rules."
        )

    return fact


# ----------------------------------------------------------------------
# FACT VALIDATION
# ----------------------------------------------------------------------

def validate_fact(df):
    """
    Validate the final Revenue fact.
    """

    expected_columns = [
        "revenue_sk",
        "opportunity_sk",
        "user_sk",
        "brand_sk",
        "calendar_sk",
        "opportunity_stage_sk",
        "negotiation_type_sk",
        "revenue_hierarchy_sk",
        "revenue_value",
    ]

    validate_columns(
        df,
        expected_columns,
        "fact_revenue",
    )

    duplicate_keys = (
        df["revenue_sk"]
        .duplicated()
        .sum()
    )

    if duplicate_keys > 0:
        raise ValueError(
            "Revenue fact contains duplicate "
            f"revenue_sk values: {duplicate_keys}"
        )

    invalid_revenue = (
        df["revenue_value"].isna()
        | (df["revenue_value"] <= 0)
    ).sum()

    if invalid_revenue > 0:
        raise ValueError(
            "Revenue fact contains "
            f"{invalid_revenue} invalid revenue values."
        )

    foreign_key_columns = [
        "opportunity_sk",
        "user_sk",
        "brand_sk",
        "calendar_sk",
        "opportunity_stage_sk",
        "negotiation_type_sk",
        "revenue_hierarchy_sk",
    ]

    for column in foreign_key_columns:

        invalid_keys = (
            df[column].isna()
            | (df[column] == "")
        ).sum()

        if invalid_keys > 0:
            raise ValueError(
                f"Foreign key column '{column}' "
                f"contains {invalid_keys} invalid records."
            )


# ----------------------------------------------------------------------
# PERSISTENCE
# ----------------------------------------------------------------------

def save_gold(df):
    """
    Persist the Revenue fact.
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
# MAIN PROCESS
# ----------------------------------------------------------------------

def process_fact_revenue():
    """
    Build and persist the Revenue fact.
    """

    required_files = {
        "Silver opportunities": OPPORTUNITIES_PATH,
        "Silver users": USERS_PATH,
        "Silver quotes": QUOTES_PATH,
        "Silver contracts": CONTRACTS_PATH,
        "Gold opportunity dimension": DIM_OPPORTUNITY_PATH,
        "Gold user dimension": DIM_USER_PATH,
        "Gold brand dimension": DIM_BRAND_PATH,
        "Gold calendar dimension": DIM_CALENDAR_PATH,
        "Gold opportunity stage dimension": DIM_STAGE_PATH,
        "Gold negotiation type dimension": DIM_NEGOTIATION_TYPE_PATH,
        "Gold revenue hierarchy dimension": DIM_REVENUE_HIERARCHY_PATH,
    }

    for source_name, path in required_files.items():
        validate_file(
            path,
            source_name,
        )

    opportunities = pd.read_parquet(
        OPPORTUNITIES_PATH
    )

    users = pd.read_parquet(
        USERS_PATH
    )

    quotes = pd.read_parquet(
        QUOTES_PATH
    )

    contracts = pd.read_parquet(
        CONTRACTS_PATH
    )

    dim_opportunity = pd.read_parquet(
        DIM_OPPORTUNITY_PATH
    )

    dim_user = pd.read_parquet(
        DIM_USER_PATH
    )

    dim_brand = pd.read_parquet(
        DIM_BRAND_PATH
    )

    dim_calendar = pd.read_parquet(
        DIM_CALENDAR_PATH
    )

    dim_stage = pd.read_parquet(
        DIM_STAGE_PATH
    )

    dim_negotiation_type = pd.read_parquet(
        DIM_NEGOTIATION_TYPE_PATH
    )

    dim_revenue_hierarchy = pd.read_parquet(
        DIM_REVENUE_HIERARCHY_PATH
    )

    # ------------------------------------------------------------------
    # Validate source structures
    # ------------------------------------------------------------------

    validate_columns(
        opportunities,
        [
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
        ],
        "opportunities",
    )

    validate_columns(
        users,
        [
            "user_id",
        ],
        "users",
    )

    validate_columns(
        quotes,
        [
            "quote_id",
            "opportunity_id",
            "quote_status",
            "quote_date",
            "quoted_amount",
        ],
        "quotes",
    )

    validate_columns(
        contracts,
        [
            "contract_id",
            "opportunity_id",
            "contract_status",
            "contract_start_date",
            "contract_end_date",
            "contract_value",
        ],
        "contracts",
    )

    validate_columns(
        dim_opportunity,
        [
            "opportunity_sk",
            "opportunity_id",
        ],
        "dim_opportunity",
    )

    validate_columns(
        dim_user,
        [
            "user_sk",
            "user_id",
        ],
        "dim_user",
    )

    validate_columns(
        dim_brand,
        [
            "brand_sk",
            "brand",
        ],
        "dim_brand",
    )

    validate_columns(
        dim_calendar,
        [
            "calendar_sk",
            "date",
        ],
        "dim_calendar",
    )

    validate_columns(
        dim_stage,
        [
            "opportunity_stage_sk",
            "stage_id",
            "is_won",
        ],
        "dim_opportunity_stage",
    )

    validate_columns(
        dim_negotiation_type,
        [
            "negotiation_type_sk",
            "negotiation_type",
        ],
        "dim_negotiation_type",
    )

    validate_columns(
        dim_revenue_hierarchy,
        [
            "revenue_hierarchy_sk",
            "revenue_level_2",
            "revenue_level_3",
        ],
        "dim_revenue_hierarchy",
    )

    # ------------------------------------------------------------------
    # Prepare Silver sources
    # ------------------------------------------------------------------

    opportunities = prepare_opportunities(
        opportunities
    )

    quotes = prepare_quotes(
        quotes
    )

    contracts = prepare_contracts(
        contracts
    )

    print(
        f"Silver opportunities: "
        f"{len(opportunities)}"
    )

    print(
        f"Silver quotes: "
        f"{len(quotes)}"
    )

    print(
        f"Silver contracts: "
        f"{len(contracts)}"
    )

    # ------------------------------------------------------------------
    # Build fact
    # ------------------------------------------------------------------

    fact = build_revenue_fact(
        opportunities=opportunities,
        quotes=quotes,
        contracts=contracts,
        dim_opportunity=dim_opportunity,
        dim_user=dim_user,
        dim_brand=dim_brand,
        dim_calendar=dim_calendar,
        dim_stage=dim_stage,
        dim_negotiation_type=dim_negotiation_type,
        dim_revenue_hierarchy=dim_revenue_hierarchy,
    )

    # ------------------------------------------------------------------
    # Validate and persist
    # ------------------------------------------------------------------

    validate_fact(
        fact
    )

    save_gold(
        fact
    )

    print(
        f"Gold records: "
        f"{len(fact)}"
    )

    print(
        f"Total revenue: "
        f"{fact['revenue_value'].sum():,.2f}"
    )

    print(
        "\nRevenue fact created successfully."
    )

    return fact


if __name__ == "__main__":
    print(
        "Gold Layer - Revenue Fact"
    )

    print(
        "========================="
    )

    process_fact_revenue()

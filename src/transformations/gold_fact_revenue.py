"""
Gold Layer - Fact Revenue
=========================

Builds the Revenue fact from Silver operational datasets and
Gold analytical dimensions.

The fact represents one analytical revenue occurrence.

Synthetic business rules:

- Prospecting opportunities generate Prospecting revenue.
- Retention opportunities are classified as Renewal.
- Expansion opportunities are classified as Cross-Sell or
  Up-Sell according to the synthetic Revenue Hierarchy rules.

The revenue hierarchy determines the analytical classification,
while this fact stores the measurable revenue value.

Responsibilities:

- Read standardized Silver datasets
- Read Gold dimensions
- Validate source structures
- Apply synthetic revenue business rules
- Resolve analytical surrogate keys
- Generate a deterministic fact key
- Validate referential integrity
- Persist the Revenue fact

No proprietary production identifiers or business rules
are used in this implementation.
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

USERS_PATH = Path(
    "data/silver/users.parquet"
)

QUOTES_PATH = Path(
    "data/silver/quotes.parquet"
)

CONTRACTS_PATH = Path(
    "data/silver/contracts.parquet"
)

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

DIM_NEGOTIATION_PATH = Path(
    "data/gold/dim_negotiation_type.parquet"
)

DIM_HIERARCHY_PATH = Path(
    "data/gold/dim_revenue_hierarchy.parquet"
)

GOLD_PATH = Path(
    "data/gold/fact_revenue.parquet"
)


# ----------------------------------------------------------------------
# SOURCE COLUMNS
# ----------------------------------------------------------------------

OPPORTUNITY_COLUMNS = [
    "opportunity_id",
    "customer_id",
    "user_id",
    "stage_id",
    "opportunity_type",
    "brand",
    "opportunity_date",
    "close_date",
    "amount",
]


USER_COLUMNS = [
    "user_id",
    "department",
]


QUOTE_COLUMNS = [
    "quote_id",
    "opportunity_id",
    "quote_status",
    "quote_date",
    "quoted_amount",
]


CONTRACT_COLUMNS = [
    "contract_id",
    "opportunity_id",
    "contract_status",
    "contract_value",
]


DIM_OPPORTUNITY_COLUMNS = [
    "opportunity_sk",
    "opportunity_id",
]


DIM_USER_COLUMNS = [
    "user_sk",
    "user_id",
]


DIM_BRAND_COLUMNS = [
    "brand_sk",
    "brand",
]


DIM_CALENDAR_COLUMNS = [
    "calendar_sk",
    "date",
]


DIM_STAGE_COLUMNS = [
    "opportunity_stage_sk",
    "stage_id",
]


DIM_NEGOTIATION_COLUMNS = [
    "negotiation_type_sk",
    "negotiation_type",
]


DIM_HIERARCHY_COLUMNS = [
    "revenue_hierarchy_sk",
    "revenue_level_1",
    "revenue_level_2",
    "revenue_level_3",
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
    Validate whether a dataset contains all required columns.
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


def validate_source_paths() -> None:
    """
    Validate that all required Silver and Gold datasets exist.
    """

    required_paths = [
        OPPORTUNITIES_PATH,
        USERS_PATH,
        QUOTES_PATH,
        CONTRACTS_PATH,
        DIM_OPPORTUNITY_PATH,
        DIM_USER_PATH,
        DIM_BRAND_PATH,
        DIM_CALENDAR_PATH,
        DIM_STAGE_PATH,
        DIM_NEGOTIATION_PATH,
        DIM_HIERARCHY_PATH,
    ]

    missing_paths = [
        path
        for path in required_paths
        if not path.exists()
    ]

    if missing_paths:
        raise FileNotFoundError(
            "Required datasets not found: "
            f"{missing_paths}"
        )


# ----------------------------------------------------------------------
# STANDARDIZATION
# ----------------------------------------------------------------------

def standardize_opportunities(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Standardize opportunity attributes required by the fact.
    """

    df = df.copy()

    text_columns = [
        "opportunity_id",
        "customer_id",
        "user_id",
        "stage_id",
        "opportunity_type",
        "brand",
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


def standardize_users(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Standardize user attributes required by the fact.
    """

    df = df.copy()

    df["user_id"] = (
        df["user_id"]
        .astype("string")
        .str.strip()
    )

    df["department"] = (
        df["department"]
        .astype("string")
        .str.strip()
        .str.title()
    )

    return df


def standardize_quotes(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Standardize quote attributes required by the fact.
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
        )

    df["quote_status"] = (
        df["quote_status"]
        .str.title()
    )

    df["quote_date"] = (
        pd.to_datetime(
            df["quote_date"],
            errors="coerce",
        )
    )

    df["quoted_amount"] = (
        pd.to_numeric(
            df["quoted_amount"],
            errors="coerce",
        )
    )

    return df


def standardize_contracts(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Standardize contract attributes required by the fact.
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
        )

    df["contract_status"] = (
        df["contract_status"]
        .str.title()
    )

    df["contract_value"] = (
        pd.to_numeric(
            df["contract_value"],
            errors="coerce",
        )
    )

    return df


# ----------------------------------------------------------------------
# BUSINESS RULES
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


def classify_revenue(
    opportunity_type: str,
    brand: str,
) -> tuple[str, str]:
    """
    Classify an opportunity into its analytical negotiation
    type and revenue hierarchy level.

    Returns:

    negotiation_type
    revenue_level_3
    """

    negotiation_type = (
        NEGOTIATION_TYPE_MAPPING.get(
            opportunity_type
        )
    )

    if negotiation_type is None:
        raise ValueError(
            "Unsupported opportunity type: "
            f"{opportunity_type}"
        )

    if negotiation_type == "Expansion":

        revenue_level_3 = (
            EXPANSION_BRAND_MAPPING.get(
                brand
            )
        )

        if revenue_level_3 is None:
            raise ValueError(
                "Expansion brand has no "
                "revenue classification: "
                f"{brand}"
            )

    else:

        revenue_level_3 = (
            negotiation_type
        )

    return (
        negotiation_type,
        revenue_level_3,
    )


# ----------------------------------------------------------------------
# TRANSACTIONAL VALUE
# ----------------------------------------------------------------------

def select_revenue_value(
    opportunity: pd.Series,
    quotes: pd.DataFrame,
    contracts: pd.DataFrame,
) -> float:
    """
    Determine the analytical revenue value.

    Synthetic rule:

    - Prospecting uses the opportunity amount.
    - Renewal prefers the active contract value when available;
      otherwise it uses the opportunity amount.
    - Expansion prefers the accepted quote amount when available;
      otherwise it uses the opportunity amount.

    This is a synthetic public rule designed for the portfolio.
    """

    opportunity_id = (
        opportunity["opportunity_id"]
    )

    opportunity_amount = (
        opportunity["amount"]
    )

    if pd.isna(opportunity_amount):
        opportunity_amount = 0.0

    opportunity_type = (
        opportunity["opportunity_type"]
    )

    if opportunity_type == "Retention":

        active_contracts = contracts[
            (
                contracts["opportunity_id"]
                == opportunity_id
            )
            & (
                contracts["contract_status"]
                == "Active"
            )
        ]

        if not active_contracts.empty:

            contract_value = (
                active_contracts[
                    "contract_value"
                ]
                .dropna()
                .sum()
            )

            if contract_value > 0:
                return float(
                    contract_value
                )

        return float(
            opportunity_amount
        )

    if opportunity_type == "Expansion":

        accepted_quotes = quotes[
            (
                quotes["opportunity_id"]
                == opportunity_id
            )
            & (
                quotes["quote_status"]
                == "Accepted"
            )
        ]

        if not accepted_quotes.empty:

            quote_value = (
                accepted_quotes[
                    "quoted_amount"
                ]
                .dropna()
                .max()
            )

            if pd.notna(quote_value):
                return float(
                    quote_value
                )

        return float(
            opportunity_amount
        )

    return float(
        opportunity_amount
    )


# ----------------------------------------------------------------------
# SURROGATE KEYS
# ----------------------------------------------------------------------

def generate_surrogate_key(
    value: str,
) -> str:
    """
    Generate a deterministic SHA-256 surrogate key.
    """

    normalized_value = (
        str(value)
        .strip()
        .upper()
    )

    return sha256(
        normalized_value.encode("utf-8")
    ).hexdigest()


# ----------------------------------------------------------------------
# DIMENSION LOOKUPS
# ----------------------------------------------------------------------

def prepare_dimension_lookup(
    df: pd.DataFrame,
    key_column: str,
    value_column: str,
) -> dict:
    """
    Create a simple source-value to surrogate-key lookup.
    """

    lookup = (
        df[
            [
                key_column,
                value_column,
            ]
        ]
        .drop_duplicates(
            subset=[value_column]
        )
    )

    return dict(
        zip(
            lookup[value_column].astype(str),
            lookup[key_column].astype(str),
        )
    )


def prepare_date_lookup(
    df: pd.DataFrame,
) -> dict:
    """
    Create a date to calendar surrogate-key lookup.
    """

    lookup = df[
        [
            "calendar_sk",
            "date",
        ]
    ].copy()

    lookup["date"] = pd.to_datetime(
        lookup["date"],
        errors="coerce",
    ).dt.normalize()

    lookup = lookup.dropna(
        subset=["date"]
    )

    return dict(
        zip(
            lookup["date"],
            lookup["calendar_sk"],
        )
    )


# ----------------------------------------------------------------------
# REFERENTIAL INTEGRITY
# ----------------------------------------------------------------------

def resolve_key(
    lookup: dict,
    value,
    dimension_name: str,
) -> str:
    """
    Resolve a dimension surrogate key.

    If a value cannot be resolved, use the standard N/A key.
    """

    if pd.isna(value):
        return generate_surrogate_key(
            "N/A"
        )

    resolved = lookup.get(
        str(value)
    )

    if resolved is None:

        return generate_surrogate_key(
            "N/A"
        )

    return resolved


# ----------------------------------------------------------------------
# FACT CONSTRUCTION
# ----------------------------------------------------------------------

def build_fact_revenue(
    opportunities: pd.DataFrame,
    quotes: pd.DataFrame,
    contracts: pd.DataFrame,
    dim_opportunity: pd.DataFrame,
    dim_user: pd.DataFrame,
    dim_brand: pd.DataFrame,
    dim_calendar: pd.DataFrame,
    dim_stage: pd.DataFrame,
    dim_negotiation: pd.DataFrame,
    dim_hierarchy: pd.DataFrame,
) -> pd.DataFrame:
    """
    Build the Revenue fact using Silver transactional data
    and Gold dimension lookups.
    """

    opportunity_lookup = prepare_dimension_lookup(
        dim_opportunity,
        "opportunity_sk",
        "opportunity_id",
    )

    user_lookup = prepare_dimension_lookup(
        dim_user,
        "user_sk",
        "user_id",
    )

    brand_lookup = prepare_dimension_lookup(
        dim_brand,
        "brand_sk",
        "brand",
    )

    stage_lookup = prepare_dimension_lookup(
        dim_stage,
        "opportunity_stage_sk",
        "stage_id",
    )

    negotiation_lookup = prepare_dimension_lookup(
        dim_negotiation,
        "negotiation_type_sk",
        "negotiation_type",
    )

    hierarchy_lookup = {}

    for _, row in dim_hierarchy.iterrows():

        hierarchy_key = (
            (
                str(
                    row["revenue_level_2"]
                ).strip(),
                str(
                    row["revenue_level_3"]
                ).strip(),
            )
        )

        hierarchy_lookup[
            hierarchy_key
        ] = row[
            "revenue_hierarchy_sk"
        ]

    calendar_lookup = prepare_date_lookup(
        dim_calendar
    )

    records = []

    for _, opportunity in opportunities.iterrows():

        negotiation_type, revenue_level_3 = (
            classify_revenue(
                opportunity[
                    "opportunity_type"
                ],
                opportunity[
                    "brand"
                ],
            )
        )

        revenue_value = (
            select_revenue_value(
                opportunity,
                quotes,
                contracts,
            )
        )

        if revenue_value <= 0:
            continue

        hierarchy_key = (
            negotiation_type,
            revenue_level_3,
        )

        hierarchy_sk = hierarchy_lookup.get(
            hierarchy_key
        )

        if hierarchy_sk is None:

            raise ValueError(
                "Revenue hierarchy not found "
                f"for {hierarchy_key}"
            )

        close_date = pd.to_datetime(
            opportunity["close_date"],
            errors="coerce",
        )

        close_date = (
            close_date.normalize()
            if pd.notna(close_date)
            else pd.NaT
        )

        revenue_sk_seed = "|".join(
            [
                str(
                    opportunity[
                        "opportunity_id"
                    ]
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
                "opportunity_sk": resolve_key(
                    opportunity_lookup,
                    opportunity[
                        "opportunity_id"
                    ],
                    "opportunity",
                ),
                "user_sk": resolve_key(
                    user_lookup,
                    opportunity[
                        "user_id"
                    ],
                    "user",
                ),
                "brand_sk": resolve_key(
                    brand_lookup,
                    opportunity[
                        "brand"
                    ],
                    "brand",
                ),
                "calendar_sk": (
                    resolve_key(
                        calendar_lookup,
                        close_date,
                        "calendar",
                    )
                ),
                "opportunity_stage_sk": (
                    resolve_key(
                        stage_lookup,
                        opportunity[
                            "stage_id"
                        ],
                        "opportunity_stage",
                    )
                ),
                "negotiation_type_sk": (
                    resolve_key(
                        negotiation_lookup,
                        negotiation_type,
                        "negotiation_type",
                    )
                ),
                "revenue_hierarchy_sk": (
                    hierarchy_sk
                ),
                "revenue_value": round(
                    revenue_value,
                    2,
                ),
            }
        )

    return pd.DataFrame(records)


# ----------------------------------------------------------------------
# FACT VALIDATION
# ----------------------------------------------------------------------

def validate_fact(
    df: pd.DataFrame,
) -> None:
    """
    Validate the resulting Revenue fact.
    """

    required_columns = [
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
        required_columns,
        "fact_revenue",
    )

    if df.empty:
        raise ValueError(
            "Revenue fact is empty."
        )

    if (
        df["revenue_sk"]
        .duplicated()
        .any()
    ):
        raise ValueError(
            "Revenue fact contains "
            "duplicate revenue_sk values."
        )

    if (
        df["revenue_value"]
        .isna()
        .any()
    ):
        raise ValueError(
            "Revenue fact contains "
            "null revenue values."
        )

    if (
        df["revenue_value"]
        <= 0
    ).any():
        raise ValueError(
            "Revenue fact contains "
            "non-positive revenue values."
        )


# ----------------------------------------------------------------------
# PERSISTENCE
# ----------------------------------------------------------------------

def save_gold(
    df: pd.DataFrame,
) -> None:
    """
    Persist the Revenue fact as Parquet.
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

def process_fact_revenue() -> pd.DataFrame:
    """
    Execute the complete Gold transformation
    for the Revenue fact.
    """

    validate_source_paths()

    # --------------------------------------------------------------
    # Read Silver sources
    # --------------------------------------------------------------

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

    # --------------------------------------------------------------
    # Read Gold dimensions
    # --------------------------------------------------------------

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

    dim_negotiation = pd.read_parquet(
        DIM_NEGOTIATION_PATH
    )

    dim_hierarchy = pd.read_parquet(
        DIM_HIERARCHY_PATH
    )

    # --------------------------------------------------------------
    # Validate Silver sources
    # --------------------------------------------------------------

    validate_columns(
        opportunities,
        OPPORTUNITY_COLUMNS,
        "opportunities",
    )

    validate_columns(
        users,
        USER_COLUMNS,
        "users",
    )

    validate_columns(
        quotes,
        QUOTE_COLUMNS,
        "quotes",
    )

    validate_columns(
        contracts,
        CONTRACT_COLUMNS,
        "contracts",
    )

    # --------------------------------------------------------------
    # Validate Gold dimensions
    # --------------------------------------------------------------

    validate_columns(
        dim_opportunity,
        DIM_OPPORTUNITY_COLUMNS,
        "dim_opportunity",
    )

    validate_columns(
        dim_user,
        DIM_USER_COLUMNS,
        "dim_user",
    )

    validate_columns(
        dim_brand,
        DIM_BRAND_COLUMNS,
        "dim_brand",
    )

    validate_columns(
        dim_calendar,
        DIM_CALENDAR_COLUMNS,
        "dim_calendar",
    )

    validate_columns(
        dim_stage,
        DIM_STAGE_COLUMNS,
        "dim_opportunity_stage",
    )

    validate_columns(
        dim_negotiation,
        DIM_NEGOTIATION_COLUMNS,
        "dim_negotiation_type",
    )

    validate_columns(
        dim_hierarchy,
        DIM_HIERARCHY_COLUMNS,
        "dim_revenue_hierarchy",
    )

    # --------------------------------------------------------------
    # Standardize Silver sources
    # --------------------------------------------------------------

    opportunities = (
        standardize_opportunities(
            opportunities
        )
    )

    users = (
        standardize_users(
            users
        )
    )

    quotes = (
        standardize_quotes(
            quotes
        )
    )

    contracts = (
        standardize_contracts(
            contracts
        )
    )

    # --------------------------------------------------------------
    # Remove invalid opportunity keys
    # --------------------------------------------------------------

    opportunities = opportunities[
        opportunities["opportunity_id"].notna()
        & (
            opportunities["opportunity_id"]
            != ""
        )
    ].copy()

    # --------------------------------------------------------------
    # Build Revenue fact
    # --------------------------------------------------------------

    fact = build_fact_revenue(
        opportunities,
        quotes,
        contracts,
        dim_opportunity,
        dim_user,
        dim_brand,
        dim_calendar,
        dim_stage,
        dim_negotiation,
        dim_hierarchy,
    )

    # --------------------------------------------------------------
    # Validate final fact
    # --------------------------------------------------------------

    validate_fact(
        fact
    )

    # --------------------------------------------------------------
    # Final column order
    # --------------------------------------------------------------

    fact = fact[
        [
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
    ]

    # --------------------------------------------------------------
    # Persist Gold
    # --------------------------------------------------------------

    save_gold(
        fact
    )

    print(
        f"Revenue fact records: {len(fact)}"
    )

    print(
        f"Total revenue: "
        f"{fact['revenue_value'].sum():,.2f}"
    )

    return fact


# ----------------------------------------------------------------------
# MAIN
# ----------------------------------------------------------------------

if __name__ == "__main__":

    print(
        "Gold Layer - Fact Revenue"
    )

    print(
        "========================="
    )

    process_fact_revenue()

    print(
        "\nRevenue fact created successfully."
    )"""
Gold Layer - Fact Revenue
=========================

Builds the Revenue fact from Silver operational datasets and
Gold analytical dimensions.

The fact represents one analytical revenue occurrence.

Synthetic business rules:

- Prospecting opportunities generate Prospecting revenue.
- Retention opportunities are classified as Renewal.
- Expansion opportunities are classified as Cross-Sell or
  Up-Sell according to the synthetic Revenue Hierarchy rules.

The revenue hierarchy determines the analytical classification,
while this fact stores the measurable revenue value.

Responsibilities:

- Read standardized Silver datasets
- Read Gold dimensions
- Validate source structures
- Apply synthetic revenue business rules
- Resolve analytical surrogate keys
- Generate a deterministic fact key
- Validate referential integrity
- Persist the Revenue fact

No proprietary production identifiers or business rules
are used in this implementation.
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

USERS_PATH = Path(
    "data/silver/users.parquet"
)

QUOTES_PATH = Path(
    "data/silver/quotes.parquet"
)

CONTRACTS_PATH = Path(
    "data/silver/contracts.parquet"
)

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

DIM_NEGOTIATION_PATH = Path(
    "data/gold/dim_negotiation_type.parquet"
)

DIM_HIERARCHY_PATH = Path(
    "data/gold/dim_revenue_hierarchy.parquet"
)

GOLD_PATH = Path(
    "data/gold/fact_revenue.parquet"
)


# ----------------------------------------------------------------------
# SOURCE COLUMNS
# ----------------------------------------------------------------------

OPPORTUNITY_COLUMNS = [
    "opportunity_id",
    "customer_id",
    "user_id",
    "stage_id",
    "opportunity_type",
    "brand",
    "opportunity_date",
    "close_date",
    "amount",
]


USER_COLUMNS = [
    "user_id",
    "department",
]


QUOTE_COLUMNS = [
    "quote_id",
    "opportunity_id",
    "quote_status",
    "quote_date",
    "quoted_amount",
]


CONTRACT_COLUMNS = [
    "contract_id",
    "opportunity_id",
    "contract_status",
    "contract_value",
]


DIM_OPPORTUNITY_COLUMNS = [
    "opportunity_sk",
    "opportunity_id",
]


DIM_USER_COLUMNS = [
    "user_sk",
    "user_id",
]


DIM_BRAND_COLUMNS = [
    "brand_sk",
    "brand",
]


DIM_CALENDAR_COLUMNS = [
    "calendar_sk",
    "date",
]


DIM_STAGE_COLUMNS = [
    "opportunity_stage_sk",
    "stage_id",
]


DIM_NEGOTIATION_COLUMNS = [
    "negotiation_type_sk",
    "negotiation_type",
]


DIM_HIERARCHY_COLUMNS = [
    "revenue_hierarchy_sk",
    "revenue_level_1",
    "revenue_level_2",
    "revenue_level_3",
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
    Validate whether a dataset contains all required columns.
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


def validate_source_paths() -> None:
    """
    Validate that all required Silver and Gold datasets exist.
    """

    required_paths = [
        OPPORTUNITIES_PATH,
        USERS_PATH,
        QUOTES_PATH,
        CONTRACTS_PATH,
        DIM_OPPORTUNITY_PATH,
        DIM_USER_PATH,
        DIM_BRAND_PATH,
        DIM_CALENDAR_PATH,
        DIM_STAGE_PATH,
        DIM_NEGOTIATION_PATH,
        DIM_HIERARCHY_PATH,
    ]

    missing_paths = [
        path
        for path in required_paths
        if not path.exists()
    ]

    if missing_paths:
        raise FileNotFoundError(
            "Required datasets not found: "
            f"{missing_paths}"
        )


# ----------------------------------------------------------------------
# STANDARDIZATION
# ----------------------------------------------------------------------

def standardize_opportunities(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Standardize opportunity attributes required by the fact.
    """

    df = df.copy()

    text_columns = [
        "opportunity_id",
        "customer_id",
        "user_id",
        "stage_id",
        "opportunity_type",
        "brand",
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


def standardize_users(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Standardize user attributes required by the fact.
    """

    df = df.copy()

    df["user_id"] = (
        df["user_id"]
        .astype("string")
        .str.strip()
    )

    df["department"] = (
        df["department"]
        .astype("string")
        .str.strip()
        .str.title()
    )

    return df


def standardize_quotes(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Standardize quote attributes required by the fact.
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
        )

    df["quote_status"] = (
        df["quote_status"]
        .str.title()
    )

    df["quote_date"] = (
        pd.to_datetime(
            df["quote_date"],
            errors="coerce",
        )
    )

    df["quoted_amount"] = (
        pd.to_numeric(
            df["quoted_amount"],
            errors="coerce",
        )
    )

    return df


def standardize_contracts(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Standardize contract attributes required by the fact.
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
        )

    df["contract_status"] = (
        df["contract_status"]
        .str.title()
    )

    df["contract_value"] = (
        pd.to_numeric(
            df["contract_value"],
            errors="coerce",
        )
    )

    return df


# ----------------------------------------------------------------------
# BUSINESS RULES
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


def classify_revenue(
    opportunity_type: str,
    brand: str,
) -> tuple[str, str]:
    """
    Classify an opportunity into its analytical negotiation
    type and revenue hierarchy level.

    Returns:

    negotiation_type
    revenue_level_3
    """

    negotiation_type = (
        NEGOTIATION_TYPE_MAPPING.get(
            opportunity_type
        )
    )

    if negotiation_type is None:
        raise ValueError(
            "Unsupported opportunity type: "
            f"{opportunity_type}"
        )

    if negotiation_type == "Expansion":

        revenue_level_3 = (
            EXPANSION_BRAND_MAPPING.get(
                brand
            )
        )

        if revenue_level_3 is None:
            raise ValueError(
                "Expansion brand has no "
                "revenue classification: "
                f"{brand}"
            )

    else:

        revenue_level_3 = (
            negotiation_type
        )

    return (
        negotiation_type,
        revenue_level_3,
    )


# ----------------------------------------------------------------------
# TRANSACTIONAL VALUE
# ----------------------------------------------------------------------

def select_revenue_value(
    opportunity: pd.Series,
    quotes: pd.DataFrame,
    contracts: pd.DataFrame,
) -> float:
    """
    Determine the analytical revenue value.

    Synthetic rule:

    - Prospecting uses the opportunity amount.
    - Renewal prefers the active contract value when available;
      otherwise it uses the opportunity amount.
    - Expansion prefers the accepted quote amount when available;
      otherwise it uses the opportunity amount.

    This is a synthetic public rule designed for the portfolio.
    """

    opportunity_id = (
        opportunity["opportunity_id"]
    )

    opportunity_amount = (
        opportunity["amount"]
    )

    if pd.isna(opportunity_amount):
        opportunity_amount = 0.0

    opportunity_type = (
        opportunity["opportunity_type"]
    )

    if opportunity_type == "Retention":

        active_contracts = contracts[
            (
                contracts["opportunity_id"]
                == opportunity_id
            )
            & (
                contracts["contract_status"]
                == "Active"
            )
        ]

        if not active_contracts.empty:

            contract_value = (
                active_contracts[
                    "contract_value"
                ]
                .dropna()
                .sum()
            )

            if contract_value > 0:
                return float(
                    contract_value
                )

        return float(
            opportunity_amount
        )

    if opportunity_type == "Expansion":

        accepted_quotes = quotes[
            (
                quotes["opportunity_id"]
                == opportunity_id
            )
            & (
                quotes["quote_status"]
                == "Accepted"
            )
        ]

        if not accepted_quotes.empty:

            quote_value = (
                accepted_quotes[
                    "quoted_amount"
                ]
                .dropna()
                .max()
            )

            if pd.notna(quote_value):
                return float(
                    quote_value
                )

        return float(
            opportunity_amount
        )

    return float(
        opportunity_amount
    )


# ----------------------------------------------------------------------
# SURROGATE KEYS
# ----------------------------------------------------------------------

def generate_surrogate_key(
    value: str,
) -> str:
    """
    Generate a deterministic SHA-256 surrogate key.
    """

    normalized_value = (
        str(value)
        .strip()
        .upper()
    )

    return sha256(
        normalized_value.encode("utf-8")
    ).hexdigest()


# ----------------------------------------------------------------------
# DIMENSION LOOKUPS
# ----------------------------------------------------------------------

def prepare_dimension_lookup(
    df: pd.DataFrame,
    key_column: str,
    value_column: str,
) -> dict:
    """
    Create a simple source-value to surrogate-key lookup.
    """

    lookup = (
        df[
            [
                key_column,
                value_column,
            ]
        ]
        .drop_duplicates(
            subset=[value_column]
        )
    )

    return dict(
        zip(
            lookup[value_column].astype(str),
            lookup[key_column].astype(str),
        )
    )


def prepare_date_lookup(
    df: pd.DataFrame,
) -> dict:
    """
    Create a date to calendar surrogate-key lookup.
    """

    lookup = df[
        [
            "calendar_sk",
            "date",
        ]
    ].copy()

    lookup["date"] = pd.to_datetime(
        lookup["date"],
        errors="coerce",
    ).dt.normalize()

    lookup = lookup.dropna(
        subset=["date"]
    )

    return dict(
        zip(
            lookup["date"],
            lookup["calendar_sk"],
        )
    )


# ----------------------------------------------------------------------
# REFERENTIAL INTEGRITY
# ----------------------------------------------------------------------

def resolve_key(
    lookup: dict,
    value,
    dimension_name: str,
) -> str:
    """
    Resolve a dimension surrogate key.

    If a value cannot be resolved, use the standard N/A key.
    """

    if pd.isna(value):
        return generate_surrogate_key(
            "N/A"
        )

    resolved = lookup.get(
        str(value)
    )

    if resolved is None:

        return generate_surrogate_key(
            "N/A"
        )

    return resolved


# ----------------------------------------------------------------------
# FACT CONSTRUCTION
# ----------------------------------------------------------------------

def build_fact_revenue(
    opportunities: pd.DataFrame,
    quotes: pd.DataFrame,
    contracts: pd.DataFrame,
    dim_opportunity: pd.DataFrame,
    dim_user: pd.DataFrame,
    dim_brand: pd.DataFrame,
    dim_calendar: pd.DataFrame,
    dim_stage: pd.DataFrame,
    dim_negotiation: pd.DataFrame,
    dim_hierarchy: pd.DataFrame,
) -> pd.DataFrame:
    """
    Build the Revenue fact using Silver transactional data
    and Gold dimension lookups.
    """

    opportunity_lookup = prepare_dimension_lookup(
        dim_opportunity,
        "opportunity_sk",
        "opportunity_id",
    )

    user_lookup = prepare_dimension_lookup(
        dim_user,
        "user_sk",
        "user_id",
    )

    brand_lookup = prepare_dimension_lookup(
        dim_brand,
        "brand_sk",
        "brand",
    )

    stage_lookup = prepare_dimension_lookup(
        dim_stage,
        "opportunity_stage_sk",
        "stage_id",
    )

    negotiation_lookup = prepare_dimension_lookup(
        dim_negotiation,
        "negotiation_type_sk",
        "negotiation_type",
    )

    hierarchy_lookup = {}

    for _, row in dim_hierarchy.iterrows():

        hierarchy_key = (
            (
                str(
                    row["revenue_level_2"]
                ).strip(),
                str(
                    row["revenue_level_3"]
                ).strip(),
            )
        )

        hierarchy_lookup[
            hierarchy_key
        ] = row[
            "revenue_hierarchy_sk"
        ]

    calendar_lookup = prepare_date_lookup(
        dim_calendar
    )

    records = []

    for _, opportunity in opportunities.iterrows():

        negotiation_type, revenue_level_3 = (
            classify_revenue(
                opportunity[
                    "opportunity_type"
                ],
                opportunity[
                    "brand"
                ],
            )
        )

        revenue_value = (
            select_revenue_value(
                opportunity,
                quotes,
                contracts,
            )
        )

        if revenue_value <= 0:
            continue

        hierarchy_key = (
            negotiation_type,
            revenue_level_3,
        )

        hierarchy_sk = hierarchy_lookup.get(
            hierarchy_key
        )

        if hierarchy_sk is None:

            raise ValueError(
                "Revenue hierarchy not found "
                f"for {hierarchy_key}"
            )

        close_date = pd.to_datetime(
            opportunity["close_date"],
            errors="coerce",
        )

        close_date = (
            close_date.normalize()
            if pd.notna(close_date)
            else pd.NaT
        )

        revenue_sk_seed = "|".join(
            [
                str(
                    opportunity[
                        "opportunity_id"
                    ]
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
                "opportunity_sk": resolve_key(
                    opportunity_lookup,
                    opportunity[
                        "opportunity_id"
                    ],
                    "opportunity",
                ),
                "user_sk": resolve_key(
                    user_lookup,
                    opportunity[
                        "user_id"
                    ],
                    "user",
                ),
                "brand_sk": resolve_key(
                    brand_lookup,
                    opportunity[
                        "brand"
                    ],
                    "brand",
                ),
                "calendar_sk": (
                    resolve_key(
                        calendar_lookup,
                        close_date,
                        "calendar",
                    )
                ),
                "opportunity_stage_sk": (
                    resolve_key(
                        stage_lookup,
                        opportunity[
                            "stage_id"
                        ],
                        "opportunity_stage",
                    )
                ),
                "negotiation_type_sk": (
                    resolve_key(
                        negotiation_lookup,
                        negotiation_type,
                        "negotiation_type",
                    )
                ),
                "revenue_hierarchy_sk": (
                    hierarchy_sk
                ),
                "revenue_value": round(
                    revenue_value,
                    2,
                ),
            }
        )

    return pd.DataFrame(records)


# ----------------------------------------------------------------------
# FACT VALIDATION
# ----------------------------------------------------------------------

def validate_fact(
    df: pd.DataFrame,
) -> None:
    """
    Validate the resulting Revenue fact.
    """

    required_columns = [
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
        required_columns,
        "fact_revenue",
    )

    if df.empty:
        raise ValueError(
            "Revenue fact is empty."
        )

    if (
        df["revenue_sk"]
        .duplicated()
        .any()
    ):
        raise ValueError(
            "Revenue fact contains "
            "duplicate revenue_sk values."
        )

    if (
        df["revenue_value"]
        .isna()
        .any()
    ):
        raise ValueError(
            "Revenue fact contains "
            "null revenue values."
        )

    if (
        df["revenue_value"]
        <= 0
    ).any():
        raise ValueError(
            "Revenue fact contains "
            "non-positive revenue values."
        )


# ----------------------------------------------------------------------
# PERSISTENCE
# ----------------------------------------------------------------------

def save_gold(
    df: pd.DataFrame,
) -> None:
    """
    Persist the Revenue fact as Parquet.
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

def process_fact_revenue() -> pd.DataFrame:
    """
    Execute the complete Gold transformation
    for the Revenue fact.
    """

    validate_source_paths()

    # --------------------------------------------------------------
    # Read Silver sources
    # --------------------------------------------------------------

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

    # --------------------------------------------------------------
    # Read Gold dimensions
    # --------------------------------------------------------------

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

    dim_negotiation = pd.read_parquet(
        DIM_NEGOTIATION_PATH
    )

    dim_hierarchy = pd.read_parquet(
        DIM_HIERARCHY_PATH
    )

    # --------------------------------------------------------------
    # Validate Silver sources
    # --------------------------------------------------------------

    validate_columns(
        opportunities,
        OPPORTUNITY_COLUMNS,
        "opportunities",
    )

    validate_columns(
        users,
        USER_COLUMNS,
        "users",
    )

    validate_columns(
        quotes,
        QUOTE_COLUMNS,
        "quotes",
    )

    validate_columns(
        contracts,
        CONTRACT_COLUMNS,
        "contracts",
    )

    # --------------------------------------------------------------
    # Validate Gold dimensions
    # --------------------------------------------------------------

    validate_columns(
        dim_opportunity,
        DIM_OPPORTUNITY_COLUMNS,
        "dim_opportunity",
    )

    validate_columns(
        dim_user,
        DIM_USER_COLUMNS,
        "dim_user",
    )

    validate_columns(
        dim_brand,
        DIM_BRAND_COLUMNS,
        "dim_brand",
    )

    validate_columns(
        dim_calendar,
        DIM_CALENDAR_COLUMNS,
        "dim_calendar",
    )

    validate_columns(
        dim_stage,
        DIM_STAGE_COLUMNS,
        "dim_opportunity_stage",
    )

    validate_columns(
        dim_negotiation,
        DIM_NEGOTIATION_COLUMNS,
        "dim_negotiation_type",
    )

    validate_columns(
        dim_hierarchy,
        DIM_HIERARCHY_COLUMNS,
        "dim_revenue_hierarchy",
    )

    # --------------------------------------------------------------
    # Standardize Silver sources
    # --------------------------------------------------------------

    opportunities = (
        standardize_opportunities(
            opportunities
        )
    )

    users = (
        standardize_users(
            users
        )
    )

    quotes = (
        standardize_quotes(
            quotes
        )
    )

    contracts = (
        standardize_contracts(
            contracts
        )
    )

    # --------------------------------------------------------------
    # Remove invalid opportunity keys
    # --------------------------------------------------------------

    opportunities = opportunities[
        opportunities["opportunity_id"].notna()
        & (
            opportunities["opportunity_id"]
            != ""
        )
    ].copy()

    # --------------------------------------------------------------
    # Build Revenue fact
    # --------------------------------------------------------------

    fact = build_fact_revenue(
        opportunities,
        quotes,
        contracts,
        dim_opportunity,
        dim_user,
        dim_brand,
        dim_calendar,
        dim_stage,
        dim_negotiation,
        dim_hierarchy,
    )

    # --------------------------------------------------------------
    # Validate final fact
    # --------------------------------------------------------------

    validate_fact(
        fact
    )

    # --------------------------------------------------------------
    # Final column order
    # --------------------------------------------------------------

    fact = fact[
        [
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
    ]

    # --------------------------------------------------------------
    # Persist Gold
    # --------------------------------------------------------------

    save_gold(
        fact
    )

    print(
        f"Revenue fact records: {len(fact)}"
    )

    print(
        f"Total revenue: "
        f"{fact['revenue_value'].sum():,.2f}"
    )

    return fact


# ----------------------------------------------------------------------
# MAIN
# ----------------------------------------------------------------------

if __name__ == "__main__":

    print(
        "Gold Layer - Fact Revenue"
    )

    print(
        "========================="
    )

    process_fact_revenue()

    print(
        "\nRevenue fact created successfully."
    )

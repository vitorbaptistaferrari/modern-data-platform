"""
Synthetic Data Generator
========================

Generates synthetic datasets representing an operational
revenue environment for the Modern Data Platform project.

The generated data is intentionally synthetic and contains
no proprietary or production information.

The generator is designed to be:

- Data-volume agnostic
- Time-period agnostic
- Reproducible through a configurable random seed
- Suitable for testing the Bronze, Silver and Gold layers
"""

from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path

import random
import string

import pandas as pd


# ----------------------------------------------------------------------
# CONFIGURATION
# ----------------------------------------------------------------------

@dataclass
class GeneratorConfig:
    """
    Configuration for synthetic data generation.
    """

    start_date: date
    end_date: date

    n_customers: int
    n_users: int
    n_opportunities: int

    seed: int = 42


DEFAULT_CONFIG = GeneratorConfig(
    start_date=date(2025, 1, 1),
    end_date=date(2027, 12, 31),
    n_customers=1000,
    n_users=50,
    n_opportunities=5000,
    seed=42,
)


OUTPUT_DIR = Path("data/synthetic")


# ----------------------------------------------------------------------
# CUSTOMERS
# ----------------------------------------------------------------------

def generate_customers(
    config: GeneratorConfig,
) -> pd.DataFrame:
    """
    Generate synthetic customer records.
    """

    random.seed(config.seed)

    states = [
        "SP",
        "RJ",
        "MG",
        "PR",
        "SC",
        "RS",
        "BA",
        "PE",
        "GO",
        "ES",
    ]

    cities_by_state = {
        "SP": [
            "São Paulo",
            "Campinas",
            "Santos",
            "Sorocaba",
        ],
        "RJ": [
            "Rio de Janeiro",
            "Niterói",
            "Petrópolis",
        ],
        "MG": [
            "Belo Horizonte",
            "Uberlândia",
            "Juiz de Fora",
        ],
        "PR": [
            "Curitiba",
            "Londrina",
            "Maringá",
        ],
        "SC": [
            "Florianópolis",
            "Joinville",
            "Blumenau",
        ],
        "RS": [
            "Porto Alegre",
            "Caxias do Sul",
            "Pelotas",
        ],
        "BA": [
            "Salvador",
            "Feira de Santana",
            "Vitória da Conquista",
        ],
        "PE": [
            "Recife",
            "Olinda",
            "Caruaru",
        ],
        "GO": [
            "Goiânia",
            "Anápolis",
            "Aparecida de Goiânia",
        ],
        "ES": [
            "Vitória",
            "Vila Velha",
            "Serra",
        ],
    }

    customer_segments = [
        "Small",
        "Medium",
        "Large",
    ]

    customer_status = [
        "Active",
        "Inactive",
    ]

    records = []

    for i in range(
        1,
        config.n_customers + 1,
    ):
        state = random.choice(states)

        city = random.choice(
            cities_by_state[state]
        )

        records.append(
            {
                "customer_id": (
                    f"CUST-{i:06d}"
                ),
                "customer_name": (
                    f"Customer {i:06d}"
                ),
                "tax_id": "".join(
                    random.choices(
                        string.digits,
                        k=14,
                    )
                ),
                "city": city,
                "state": state,
                "segment": random.choice(
                    customer_segments
                ),
                "status": random.choice(
                    customer_status
                ),
            }
        )

    return pd.DataFrame(records)


# ----------------------------------------------------------------------
# USERS
# ----------------------------------------------------------------------

def generate_users(
    config: GeneratorConfig,
) -> pd.DataFrame:
    """
    Generate synthetic users representing commercial
    and operational responsibilities.
    """

    random.seed(config.seed + 1)

    departments = [
        "Commercial",
        "Customer Success",
        "Operations",
        "Management",
    ]

    roles_by_department = {
        "Commercial": [
            "Sales Representative",
            "Account Executive",
            "Sales Manager",
        ],
        "Customer Success": [
            "Customer Success Analyst",
            "Customer Success Manager",
        ],
        "Operations": [
            "Operations Analyst",
            "Operations Manager",
        ],
        "Management": [
            "Manager",
            "Director",
        ],
    }

    records = []

    for i in range(
        1,
        config.n_users + 1,
    ):
        department = random.choice(
            departments
        )

        records.append(
            {
                "user_id": (
                    f"USER-{i:05d}"
                ),
                "user_name": (
                    f"User {i:05d}"
                ),
                "department": department,
                "role": random.choice(
                    roles_by_department[
                        department
                    ]
                ),
                "active": random.choice(
                    [True, True, True, False]
                ),
            }
        )

    return pd.DataFrame(records)


# ----------------------------------------------------------------------
# RECORD TYPES
# ----------------------------------------------------------------------

def generate_record_types() -> pd.DataFrame:
    """
    Generate synthetic opportunity record types.
    """

    records = [
        {
            "record_type_id": "RT-001",
            "record_type_name": (
                "New Business"
            ),
        },
        {
            "record_type_id": "RT-002",
            "record_type_name": (
                "Existing Business"
            ),
        },
        {
            "record_type_id": "RT-003",
            "record_type_name": (
                "Strategic Account"
            ),
        },
    ]

    return pd.DataFrame(records)


# ----------------------------------------------------------------------
# OPPORTUNITY STAGES
# ----------------------------------------------------------------------

def generate_opportunity_stages() -> pd.DataFrame:
    """
    Generate synthetic opportunity stages.
    """

    records = [
        {
            "stage_id": "STG-001",
            "stage_name": "Qualification",
            "stage_order": 1,
            "is_closed": False,
            "is_won": False,
        },
        {
            "stage_id": "STG-002",
            "stage_name": "Proposal",
            "stage_order": 2,
            "is_closed": False,
            "is_won": False,
        },
        {
            "stage_id": "STG-003",
            "stage_name": "Negotiation",
            "stage_order": 3,
            "is_closed": False,
            "is_won": False,
        },
        {
            "stage_id": "STG-004",
            "stage_name": "Closed Won",
            "stage_order": 4,
            "is_closed": True,
            "is_won": True,
        },
        {
            "stage_id": "STG-005",
            "stage_name": "Closed Lost",
            "stage_order": 5,
            "is_closed": True,
            "is_won": False,
        },
    ]

    return pd.DataFrame(records)


# ----------------------------------------------------------------------
# OPPORTUNITIES
# ----------------------------------------------------------------------

def generate_opportunities(
    config: GeneratorConfig,
    customers: pd.DataFrame,
    users: pd.DataFrame,
    record_types: pd.DataFrame,
    stages: pd.DataFrame,
) -> pd.DataFrame:
    """
    Generate synthetic opportunity records.
    """

    random.seed(config.seed + 2)

    brands = [
        "Alpha",
        "Beta",
        "Gamma",
    ]

    opportunity_types = [
        "Prospecting",
        "Retention",
        "Expansion",
    ]

    opportunity_origins = [
        "Inbound",
        "Outbound",
        "Referral",
        "Partner",
        "Existing Customer",
    ]

    customer_ids = (
        customers["customer_id"].tolist()
    )

    user_ids = (
        users["user_id"].tolist()
    )

    record_type_ids = (
        record_types[
            "record_type_id"
        ].tolist()
    )

    stage_ids = (
        stages["stage_id"].tolist()
    )

    date_range_days = (
        config.end_date - config.start_date
    ).days

    records = []

    for i in range(
        1,
        config.n_opportunities + 1,
    ):
        customer_id = random.choice(
            customer_ids
        )

        user_id = random.choice(
            user_ids
        )

        record_type_id = random.choice(
            record_type_ids
        )

        stage_id = random.choice(
            stage_ids
        )

        opportunity_type = random.choice(
            opportunity_types
        )

        opportunity_date = (
            config.start_date
            + timedelta(
                days=random.randint(
                    0,
                    date_range_days,
                )
            )
        )

        close_date = (
            opportunity_date
            + timedelta(
                days=random.randint(
                    7,
                    120,
                )
            )
        )

        if close_date > config.end_date:
            close_date = config.end_date

        amount = round(
            random.uniform(
                10000,
                2000000,
            ),
            2,
        )

        records.append(
            {
                "opportunity_id": (
                    f"OPP-{i:07d}"
                ),
                "customer_id": (
                    customer_id
                ),
                "user_id": user_id,
                "record_type_id": (
                    record_type_id
                ),
                "stage_id": stage_id,
                "opportunity_type": (
                    opportunity_type
                ),
                "brand": random.choice(
                    brands
                ),
                "origin": random.choice(
                    opportunity_origins
                ),
                "opportunity_date": (
                    opportunity_date
                ),
                "close_date": close_date,
                "amount": amount,
            }
        )

    return pd.DataFrame(records)


# ----------------------------------------------------------------------
# CONTRACTS
# ----------------------------------------------------------------------

def generate_contracts(
    config: GeneratorConfig,
    opportunities: pd.DataFrame,
) -> pd.DataFrame:
    """
    Generate synthetic contract records.
    """

    random.seed(config.seed + 3)

    contract_statuses = [
        "Draft",
        "Active",
        "Expired",
        "Cancelled",
    ]

    records = []

    for i, opportunity in opportunities.iterrows():

        if random.random() > 0.65:
            continue

        start_date = opportunity[
            "close_date"
        ]

        duration_days = random.choice(
            [
                180,
                365,
                730,
            ]
        )

        end_date = (
            start_date
            + timedelta(
                days=duration_days
            )
        )

        if end_date > config.end_date:
            end_date = config.end_date

        records.append(
            {
                "contract_id": (
                    f"CON-{i + 1:07d}"
                ),
                "opportunity_id": (
                    opportunity[
                        "opportunity_id"
                    ]
                ),
                "contract_status": (
                    random.choice(
                        contract_statuses
                    )
                ),
                "contract_start_date": (
                    start_date
                ),
                "contract_end_date": (
                    end_date
                ),
                "contract_value": round(
                    opportunity["amount"]
                    * random.uniform(
                        0.90,
                        1.10,
                    ),
                    2,
                ),
            }
        )

    return pd.DataFrame(records)


# ----------------------------------------------------------------------
# QUOTES
# ----------------------------------------------------------------------

def generate_quotes(
    config: GeneratorConfig,
    opportunities: pd.DataFrame,
) -> pd.DataFrame:
    """
    Generate synthetic quote records.
    """

    random.seed(config.seed + 4)

    quote_statuses = [
        "Draft",
        "Presented",
        "Accepted",
        "Rejected",
        "Expired",
    ]

    records = []

    for i, opportunity in opportunities.iterrows():

        n_quotes = random.choices(
            [0, 1, 2],
            weights=[
                0.20,
                0.65,
                0.15,
            ],
            k=1,
        )[0]

        for quote_number in range(
            1,
            n_quotes + 1,
        ):
            quote_date = (
                opportunity[
                    "opportunity_date"
                ]
                + timedelta(
                    days=random.randint(
                        1,
                        60,
                    )
                )
            )

            if quote_date > opportunity[
                "close_date"
            ]:
                quote_date = opportunity[
                    "close_date"
                ]

            quoted_amount = round(
                opportunity["amount"]
                * random.uniform(
                    0.90,
                    1.15,
                ),
                2,
            )

            records.append(
                {
                    "quote_id": (
                        f"QUO-"
                        f"{i + 1:07d}-"
                        f"{quote_number}"
                    ),
                    "opportunity_id": (
                        opportunity[
                            "opportunity_id"
                        ]
                    ),
                    "quote_status": (
                        random.choice(
                            quote_statuses
                        )
                    ),
                    "quote_date": (
                        quote_date
                    ),
                    "quoted_amount": (
                        quoted_amount
                    ),
                }
            )

    return pd.DataFrame(records)


# ----------------------------------------------------------------------
# TARGETS
# ----------------------------------------------------------------------

def generate_targets(
    config: GeneratorConfig,
) -> pd.DataFrame:
    """
    Generate synthetic business targets.

    Targets are generated by reporting period,
    brand, target type and record nature.
    """

    random.seed(config.seed + 5)

    brands = [
        "Alpha",
        "Beta",
        "Gamma",
    ]

    target_types = [
        "Prospecting",
        "Retention",
        "Expansion",
    ]

    periods = pd.date_range(
        start=config.start_date,
        end=config.end_date,
        freq="MS",
    )

    records = []

    target_id = 1

    for period in periods:

        for brand in brands:

            for target_type in target_types:

                target_value = round(
                    random.uniform(
                        50000,
                        500000,
                    ),
                    2,
                )

                records.append(
                    {
                        "target_id": (
                            f"TGT-{target_id:07d}"
                        ),
                        "period": (
                            period.date()
                        ),
                        "brand": brand,
                        "target_type": (
                            target_type
                        ),
                        "nature": (
                            "Monthly Target"
                        ),
                        "target_value": (
                            target_value
                        ),
                    }
                )

                target_id += 1

    return pd.DataFrame(records)


# ----------------------------------------------------------------------
# PERSISTENCE
# ----------------------------------------------------------------------

def save_dataset(
    df: pd.DataFrame,
    dataset_name: str,
) -> Path:
    """
    Save a generated dataset as Parquet.
    """

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = (
        OUTPUT_DIR
        / f"{dataset_name}.parquet"
    )

    df.to_parquet(
        output_path,
        index=False,
    )

    print(
        f"Saved {dataset_name}: "
        f"{len(df)} records"
    )

    print(
        f"Path: {output_path}"
    )

    return output_path


# ----------------------------------------------------------------------
# MAIN
# ----------------------------------------------------------------------

if __name__ == "__main__":

    config = DEFAULT_CONFIG

    print("Synthetic Data Generator")
    print("------------------------")

    print(
        f"Period: "
        f"{config.start_date} → "
        f"{config.end_date}"
    )

    print(
        f"Customers: "
        f"{config.n_customers}"
    )

    print(
        f"Users: "
        f"{config.n_users}"
    )

    print(
        f"Opportunities: "
        f"{config.n_opportunities}"
    )

    print(
        f"Seed: "
        f"{config.seed}"
    )

    # --------------------------------------------------------------
    # Generate source datasets
    # --------------------------------------------------------------

    record_types = (
        generate_record_types()
    )

    stages = (
        generate_opportunity_stages()
    )

    customers = generate_customers(
        config
    )

    users = generate_users(
        config
    )

    opportunities = generate_opportunities(
        config,
        customers,
        users,
        record_types,
        stages,
    )

    contracts = generate_contracts(
        config,
        opportunities,
    )

    quotes = generate_quotes(
        config,
        opportunities,
    )

    targets = generate_targets(
        config
    )

    # --------------------------------------------------------------
    # Persist source datasets
    # --------------------------------------------------------------

    save_dataset(
        customers,
        "customers",
    )

    save_dataset(
        users,
        "users",
    )

    save_dataset(
        record_types,
        "record_types",
    )

    save_dataset(
        stages,
        "opportunity_stages",
    )

    save_dataset(
        opportunities,
        "opportunities",
    )

    save_dataset(
        contracts,
        "contracts",
    )

    save_dataset(
        quotes,
        "quotes",
    )

    save_dataset(
        targets,
        "targets",
    )

    print(
        "\nSynthetic data generation completed."
    )

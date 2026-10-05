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

import random
import string

import pandas as pd


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


def generate_customers(
    config: GeneratorConfig,
) -> pd.DataFrame:
    """
    Generate synthetic customer records.

    The generated customers represent organizations that may
    participate in the revenue lifecycle.
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
                "customer_id": f"CUST-{i:06d}",
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


def generate_users(
    config: GeneratorConfig,
) -> pd.DataFrame:
    """
    Generate synthetic users representing commercial and
    operational responsibilities.
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
                "user_id": f"USER-{i:05d}",
                "user_name": f"User {i:05d}",
                "department": department,
                "role": random.choice(
                    roles_by_department[department]
                ),
                "active": random.choice(
                    [True, True, True, False]
                ),
            }
        )

    return pd.DataFrame(records)


def generate_record_types() -> pd.DataFrame:
    """
    Generate synthetic opportunity record types.
    """

    records = [
        {
            "record_type_id": "RT-001",
            "record_type_name": "New Business",
        },
        {
            "record_type_id": "RT-002",
            "record_type_name": "Existing Business",
        },
        {
            "record_type_id": "RT-003",
            "record_type_name": "Strategic Account",
        },
    ]

    return pd.DataFrame(records)


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


def generate_opportunities(
    config: GeneratorConfig,
    customers: pd.DataFrame,
    users: pd.DataFrame,
    record_types: pd.DataFrame,
    stages: pd.DataFrame,
) -> pd.DataFrame:
    """
    Generate synthetic opportunity records.

    Opportunities are linked to previously generated
    customers, users, record types and stages.
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
        record_types["record_type_id"].tolist()
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
                "customer_id": customer_id,
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

    record_types = (
        generate_record_types()
    )

    print("\nGenerated record types:")
    print(record_types)

    stages = (
        generate_opportunity_stages()
    )

    print("\nGenerated opportunity stages:")
    print(stages)

    customers = generate_customers(
        config
    )

    print("\nGenerated customers:")
    print(customers.head())

    print(
        f"\nTotal customers: "
        f"{len(customers)}"
    )

    users = generate_users(
        config
    )

    print("\nGenerated users:")
    print(users.head())

    print(
        f"\nTotal users: "
        f"{len(users)}"
    )

    opportunities = generate_opportunities(
        config,
        customers,
        users,
        record_types,
        stages,
    )

    print("\nGenerated opportunities:")
    print(opportunities.head())

    print(
        f"\nTotal opportunities: "
        f"{len(opportunities)}"
    )

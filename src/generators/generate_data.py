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
from datetime import date

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


def generate_customers(config: GeneratorConfig) -> pd.DataFrame:
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

    for i in range(1, config.n_customers + 1):
        state = random.choice(states)
        city = random.choice(cities_by_state[state])

        records.append(
            {
                "customer_id": f"CUST-{i:06d}",
                "customer_name": f"Customer {i:06d}",
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


def generate_users(config: GeneratorConfig) -> pd.DataFrame:
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

    for i in range(1, config.n_users + 1):
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

    customers = generate_customers(config)

    print("\nGenerated customers:")
    print(customers.head())

    print(
        f"\nTotal customers: "
        f"{len(customers)}"
    )

    users = generate_users(config)

    print("\nGenerated users:")
    print(users.head())

    print(
        f"\nTotal users: "
        f"{len(users)}"
    )

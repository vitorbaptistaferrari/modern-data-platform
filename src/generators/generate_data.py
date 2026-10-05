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

if __name__ == "__main__":
    config = DEFAULT_CONFIG

    print("Synthetic Data Generator")
    print("------------------------")
    print(f"Period: {config.start_date} → {config.end_date}")
    print(f"Customers: {config.n_customers}")
    print(f"Users: {config.n_users}")
    print(f"Opportunities: {config.n_opportunities}")
    print(f"Seed: {config.seed}")

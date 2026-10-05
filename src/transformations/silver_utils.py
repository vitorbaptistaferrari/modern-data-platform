"""
Silver Layer Utilities
======================

Reusable utilities for Silver layer transformations.

The goal is to centralize common technical processing
patterns such as:

- Source validation
- Text standardization
- Primary key validation
- Deduplication
- Silver metadata
- Persistence

Business rules remain outside these utilities.
"""

from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

import pandas as pd


def validate_columns(
    df: pd.DataFrame,
    expected_columns: Iterable[str],
) -> None:
    """
    Validate whether the source contains all expected columns.
    """

    missing_columns = [
        column
        for column in expected_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            "Missing expected columns: "
            f"{missing_columns}"
        )


def standardize_text_columns(
    df: pd.DataFrame,
    columns: Iterable[str],
) -> pd.DataFrame:
    """
    Standardize text columns by converting values to strings
    and removing leading/trailing whitespace.
    """

    df = df.copy()

    for column in columns:

        if column not in df.columns:
            continue

        df[column] = (
            df[column]
            .astype("string")
            .str.strip()
        )

    return df


def remove_invalid_keys(
    df: pd.DataFrame,
    key_columns: Iterable[str],
) -> pd.DataFrame:
    """
    Remove records where any primary key component
    is null or empty.
    """

    df = df.copy()

    for column in key_columns:

        df = df[
            df[column].notna()
            & (df[column] != "")
        ]

    return df


def deduplicate(
    df: pd.DataFrame,
    key_columns: Iterable[str],
    order_column: str = "dt_ingestao",
) -> pd.DataFrame:
    """
    Deduplicate records using the provided key columns.

    When an ordering column is available, the most recent
    record is retained.
    """

    df = df.copy()

    if order_column in df.columns:

        df = df.sort_values(
            by=order_column
        )

    df = df.drop_duplicates(
        subset=list(key_columns),
        keep="last",
    )

    return df


def add_silver_metadata(
    df: pd.DataFrame,
    source_table: str,
) -> pd.DataFrame:
    """
    Add technical metadata related to Silver processing.
    """

    df = df.copy()

    df["dt_processamento_silver"] = (
        datetime.now(timezone.utc)
    )

    df["nm_camada_origem"] = (
        "bronze"
    )

    df["nm_tabela_origem"] = (
        source_table
    )

    return df


def save_silver(
    df: pd.DataFrame,
    output_path: Path,
) -> None:
    """
    Persist a Silver dataset as Parquet.
    """

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    df.to_parquet(
        output_path,
        index=False,
    )

    print(
        f"Silver output: {output_path}"
    )

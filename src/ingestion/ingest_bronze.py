"""
Bronze Layer Ingestion
======================

Implements a simple ingestion pattern representing
a Copy Job from operational sources into the Bronze layer.

The ingestion process intentionally performs only
technical operations:

- Read source data
- Validate the expected structure
- Add ingestion metadata
- Persist the data
- Avoid business transformations

Business rules and analytical transformations belong
to the Silver and Gold layers.
"""

from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


# ----------------------------------------------------------------------
# CONFIGURATION
# ----------------------------------------------------------------------

SOURCE_DIR = Path("data/synthetic")

BRONZE_DIR = Path("data/bronze")


# ----------------------------------------------------------------------
# INGESTION FUNCTION
# ----------------------------------------------------------------------

def ingest_to_bronze(
    source_path: Path,
    bronze_path: Path,
) -> pd.DataFrame:
    """
    Ingest a synthetic source dataset into the Bronze layer.

    The function simulates a Copy Job pattern by reading
    the selected source dataset and persisting it into
    the Bronze layer.

    The process uses Full Load with Overwrite.
    """

    if not source_path.exists():
        raise FileNotFoundError(
            f"Source file not found: {source_path}"
        )

    df = pd.read_parquet(source_path)

    if df.empty:
        raise ValueError(
            f"Source dataset is empty: {source_path}"
        )

    ingestion_timestamp = datetime.now(
        timezone.utc
    )

    df = df.copy()

    df["dt_ingestao"] = ingestion_timestamp

    bronze_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    df.to_parquet(
        bronze_path,
        index=False,
    )

    print(
        f"Ingested: {source_path.name}"
    )

    print(
        f"Records: {len(df)}"
    )

    print(
        f"Bronze output: {bronze_path}"
    )

    return df


# ----------------------------------------------------------------------
# MAIN
# ----------------------------------------------------------------------

if __name__ == "__main__":

    print("Bronze Layer Ingestion")
    print("----------------------")

    source_file = (
        SOURCE_DIR / "opportunities.parquet"
    )

    bronze_file = (
        BRONZE_DIR / "opportunities.parquet"
    )

    ingest_to_bronze(
        source_file,
        bronze_file,
    )

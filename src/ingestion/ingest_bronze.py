"""
Bronze Layer Ingestion
======================

Implements a reusable ingestion pattern representing
a Copy Job from operational sources into the Bronze layer.

The ingestion process performs technical operations only:

- Read source data
- Validate the source
- Add ingestion metadata
- Persist the data
- Use Full Load with Overwrite

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


DATASETS = [
    "customers",
    "users",
    "record_types",
    "opportunity_stages",
    "opportunities",
    "contracts",
    "quotes",
    "targets",
]


# ----------------------------------------------------------------------
# INGESTION
# ----------------------------------------------------------------------

def ingest_to_bronze(
    source_path: Path,
    bronze_path: Path,
) -> pd.DataFrame:
    """
    Ingest a single dataset into the Bronze layer.

    The process represents a Copy Job pattern using
    Full Load with Overwrite.
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

    df["dt_ingestao"] = (
        ingestion_timestamp
    )

    bronze_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    df.to_parquet(
        bronze_path,
        index=False,
    )

    print(
        f"[SUCCESS] {source_path.name}"
    )

    print(
        f"Records: {len(df)}"
    )

    print(
        f"Bronze: {bronze_path}"
    )

    return df


# ----------------------------------------------------------------------
# PIPELINE
# ----------------------------------------------------------------------

def run_bronze_ingestion() -> None:
    """
    Execute Bronze ingestion for all configured datasets.
    """

    print("Bronze Layer Ingestion")
    print("======================")

    successful_datasets = []
    failed_datasets = []

    for dataset_name in DATASETS:

        source_path = (
            SOURCE_DIR
            / f"{dataset_name}.parquet"
        )

        bronze_path = (
            BRONZE_DIR
            / f"{dataset_name}.parquet"
        )

        try:

            ingest_to_bronze(
                source_path,
                bronze_path,
            )

            successful_datasets.append(
                dataset_name
            )

        except Exception as error:

            failed_datasets.append(
                {
                    "dataset": dataset_name,
                    "error": str(error),
                }
            )

            print(
                f"[ERROR] "
                f"{dataset_name}: "
                f"{error}"
            )

    # --------------------------------------------------------------
    # Execution summary
    # --------------------------------------------------------------

    print("\nIngestion Summary")
    print("-----------------")

    print(
        f"Successful: "
        f"{len(successful_datasets)}"
    )

    print(
        f"Failed: "
        f"{len(failed_datasets)}"
    )

    if failed_datasets:

        print("\nFailed datasets:")

        for failure in failed_datasets:

            print(
                f"- {failure['dataset']}: "
                f"{failure['error']}"
            )

        raise RuntimeError(
            "Bronze ingestion completed "
            "with failures."
        )

    print(
        "\nBronze ingestion completed successfully."
    )


# ----------------------------------------------------------------------
# MAIN
# ----------------------------------------------------------------------

if __name__ == "__main__":

    run_bronze_ingestion()

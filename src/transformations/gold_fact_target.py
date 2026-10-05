"""
Gold Layer - Fact Target
========================

Builds the Target fact from the Silver target dataset and
Gold analytical dimensions.

Fact grain:

- Reporting period
- Brand
- Target type
- Nature

The fact represents business target values provided by the
synthetic source environment.

Responsibilities:

- Read standardized Silver target data
- Read Gold analytical dimensions
- Validate source structures
- Apply analytical target classification
- Resolve analytical surrogate keys
- Validate referential integrity
- Generate a deterministic fact key
- Persist the Target fact

The fact does not calculate or redistribute target values.
It represents the target values supplied by the source.
"""

from hashlib import sha256
from pathlib import Path

import pandas as pd


# ----------------------------------------------------------------------
# CONFIGURATION
# ----------------------------------------------------------------------

SILVER_PATH = Path(
    "data/silver/targets.parquet"
)

DIM_BRAND_PATH = Path(
    "data/gold/dim_brand.parquet"
)

DIM_CALENDAR_PATH = Path(
    "data/gold/dim_calendar.parquet"
)

DIM_TARGET_TYPE_PATH = Path(
    "data/gold/dim_target_type.parquet"
)

DIM_HIERARCHY_PATH = Path(
    "data/gold/dim_revenue_hierarchy.parquet"
)

GOLD_PATH = Path(
    "data/gold/fact_target.parquet"
)


# ----------------------------------------------------------------------
# SOURCE COLUMNS
# ----------------------------------------------------------------------

TARGET_COLUMNS = [
    "target_id",
    "period",
    "brand",
    "target_type",
    "nature",
    "target_value",
]


DIM_BRAND_COLUMNS = [
    "brand_sk",
    "brand",
]


DIM_CALENDAR_COLUMNS = [
    "calendar_sk",
    "date",
]


DIM_TARGET_TYPE_COLUMNS = [
    "target_type_sk",
    "target_type",
]


DIM_HIERARCHY_COLUMNS = [
    "revenue_hierarchy_sk",
    "revenue_level_1",
    "revenue_level_2",
    "revenue_level_3",
]


# ----------------------------------------------------------------------
# BUSINESS RULES
# ----------------------------------------------------------------------

TARGET_TYPE_MAPPING = {
    "Prospecting": "Prospecting",
    "Retention": "Renewal",
    "Expansion": "Expansion",
}


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
        SILVER_PATH,
        DIM_BRAND_PATH,
        DIM_CALENDAR_PATH,
        DIM_TARGET_TYPE_PATH,
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

def standardize_targets(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Standardize target attributes required by the fact.
    """

    df = df.copy()

    text_columns = [
        "target_id",
        "brand",
        "target_type",
        "nature",
    ]

    for column in text_columns:

        df[column] = (
            df[column]
            .astype("string")
            .str.strip()
        )

    df["brand"] = (
        df["brand"]
        .str.title()
    )

    df["target_type"] = (
        df["target_type"]
        .str.title()
    )

    df["nature"] = (
        df["nature"]
        .str.title()
    )

    df["period"] = (
        pd.to_datetime(
            df["period"],
            errors="coerce",
        )
        .dt.normalize()
    )

    df["target_value"] = (
        pd.to_numeric(
            df["target_value"],
            errors="coerce",
        )
    )

    return df


# ----------------------------------------------------------------------
# BUSINESS TRANSFORMATION
# ----------------------------------------------------------------------

def apply_target_type_rules(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Translate operational target types into analytical
    target types.
    """

    df = df.copy()

    df["analytical_target_type"] = (
        df["target_type"]
        .map(
            TARGET_TYPE_MAPPING
        )
    )

    return df


def validate_target_type_mapping(
    df: pd.DataFrame,
) -> None:
    """
    Validate that every source target type can be
    mapped to an analytical target type.
    """

    unmapped_values = (
        df.loc[
            df[
                "analytical_target_type"
            ].isna(),
            "target_type",
        ]
        .drop_duplicates()
        .tolist()
    )

    if unmapped_values:
        raise ValueError(
            "Unmapped target types found: "
            f"{unmapped_values}"
        )


# ----------------------------------------------------------------------
# QUALITY RULES
# ----------------------------------------------------------------------

def remove_invalid_targets(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Remove records without a valid target identifier.
    """

    return df[
        df["target_id"].notna()
        & (df["target_id"] != "")
    ].copy()


def validate_target_values(
    df: pd.DataFrame,
) -> None:
    """
    Validate target values and required analytical fields.
    """

    invalid_periods = (
        df["period"].isna()
    ).sum()

    if invalid_periods > 0:
        raise ValueError(
            "Target dataset contains "
            f"{invalid_periods} invalid periods."
        )

    invalid_values = (
        df["target_value"].isna()
    ).sum()

    if invalid_values > 0:
        raise ValueError(
            "Target dataset contains "
            f"{invalid_values} invalid target values."
        )

    non_positive_values = (
        df["target_value"]
        <= 0
    ).sum()

    if non_positive_values > 0:
        raise ValueError(
            "Target dataset contains "
            f"{non_positive_values} non-positive "
            "target values."
        )


def validate_target_grain(
    df: pd.DataFrame,
) -> None:
    """
    Validate the expected analytical grain:

    period + brand + analytical target type + nature
    """

    grain_columns = [
        "period",
        "brand",
        "analytical_target_type",
        "nature",
    ]

    duplicated_grain = (
        df.duplicated(
            subset=grain_columns,
            keep=False,
        )
    )

    if duplicated_grain.any():

        duplicated_records = (
            df.loc[
                duplicated_grain,
                grain_columns,
            ]
            .drop_duplicates()
            .to_dict(
                orient="records"
            )
        )

        raise ValueError(
            "Target fact grain contains "
            "duplicate analytical combinations: "
            f"{duplicated_records[:10]}"
        )


# ----------------------------------------------------------------------
# SURROGATE KEY
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


def generate_fact_key(
    period,
    brand: str,
    target_type: str,
    nature: str,
) -> str:
    """
    Generate a deterministic fact key based on the
    analytical grain of the Target fact.
    """

    fact_seed = "|".join(
        [
            str(period),
            str(brand),
            str(target_type),
            str(nature),
        ]
    )

    return generate_surrogate_key(
        fact_seed
    )


# ----------------------------------------------------------------------
# DIMENSION LOOKUPS
# ----------------------------------------------------------------------

def prepare_lookup(
    df: pd.DataFrame,
    key_column: str,
    value_column: str,
) -> dict:
    """
    Create a value-to-surrogate-key lookup.
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
    Create a date-to-calendar-key lookup.
    """

    lookup = df[
        [
            "calendar_sk",
            "date",
        ]
    ].copy()

    lookup["date"] = (
        pd.to_datetime(
            lookup["date"],
            errors="coerce",
        )
        .dt.normalize()
    )

    lookup = lookup.dropna(
        subset=["date"]
    )

    return dict(
        zip(
            lookup["date"],
            lookup["calendar_sk"],
        )
    )


def prepare_hierarchy_lookup(
    df: pd.DataFrame,
) -> dict:
    """
    Create a lookup based on the analytical
    negotiation type and hierarchy level.
    """

    lookup = {}

    for _, row in df.iterrows():

        key = (
            str(
                row["revenue_level_2"]
            ).strip(),
            str(
                row["revenue_level_3"]
            ).strip(),
        )

        lookup[key] = (
            row["revenue_hierarchy_sk"]
        )

    return lookup


# ----------------------------------------------------------------------
# KEY RESOLUTION
# ----------------------------------------------------------------------

def resolve_key(
    lookup: dict,
    value,
) -> str:
    """
    Resolve a dimension surrogate key.

    If the value is not found, use the standard N/A key.
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

def build_fact_target(
    targets: pd.DataFrame,
    dim_brand: pd.DataFrame,
    dim_calendar: pd.DataFrame,
    dim_target_type: pd.DataFrame,
    dim_hierarchy: pd.DataFrame,
) -> pd.DataFrame:
    """
    Build the Target fact from the standardized target dataset
    and Gold dimension lookups.
    """

    brand_lookup = prepare_lookup(
        dim_brand,
        "brand_sk",
        "brand",
    )

    calendar_lookup = prepare_date_lookup(
        dim_calendar
    )

    target_type_lookup = prepare_lookup(
        dim_target_type,
        "target_type_sk",
        "target_type",
    )

    hierarchy_lookup = (
        prepare_hierarchy_lookup(
            dim_hierarchy
        )
    )

    records = []

    for _, target in targets.iterrows():

        analytical_target_type = (
            target[
                "analytical_target_type"
            ]
        )

        hierarchy_key = (
            (
                analytical_target_type,
                analytical_target_type,
            )
        )

        hierarchy_sk = (
            hierarchy_lookup.get(
                hierarchy_key
            )
        )

        if hierarchy_sk is None:

            raise ValueError(
                "Revenue hierarchy not found "
                f"for target type: "
                f"{analytical_target_type}"
            )

        period = pd.to_datetime(
            target["period"],
            errors="coerce",
        )

        period = (
            period.normalize()
            if pd.notna(period)
            else pd.NaT
        )

        records.append(
            {
                "target_fact_sk": (
                    generate_fact_key(
                        period,
                        target["brand"],
                        analytical_target_type,
                        target["nature"],
                    )
                ),
                "calendar_sk": resolve_key(
                    calendar_lookup,
                    period,
                ),
                "brand_sk": resolve_key(
                    brand_lookup,
                    target["brand"],
                ),
                "target_type_sk": resolve_key(
                    target_type_lookup,
                    analytical_target_type,
                ),
                "revenue_hierarchy_sk": (
                    hierarchy_sk
                ),
                "nature": target[
                    "nature"
                ],
                "target_value": round(
                    float(
                        target[
                            "target_value"
                        ]
                    ),
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
    Validate the resulting Target fact.
    """

    required_columns = [
        "target_fact_sk",
        "calendar_sk",
        "brand_sk",
        "target_type_sk",
        "revenue_hierarchy_sk",
        "nature",
        "target_value",
    ]

    validate_columns(
        df,
        required_columns,
        "fact_target",
    )

    if df.empty:
        raise ValueError(
            "Target fact is empty."
        )

    if (
        df["target_fact_sk"]
        .duplicated()
        .any()
    ):
        raise ValueError(
            "Target fact contains "
            "duplicate target_fact_sk values."
        )

    if (
        df["target_value"]
        .isna()
        .any()
    ):
        raise ValueError(
            "Target fact contains "
            "null target values."
        )

    if (
        df["target_value"]
        <= 0
    ).any():
        raise ValueError(
            "Target fact contains "
            "non-positive target values."
        )


# ----------------------------------------------------------------------
# PERSISTENCE
# ----------------------------------------------------------------------

def save_gold(
    df: pd.DataFrame,
) -> None:
    """
    Persist the Target fact as Parquet.
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

def process_fact_target() -> pd.DataFrame:
    """
    Execute the complete Gold transformation
    for the Target fact.
    """

    validate_source_paths()

    # --------------------------------------------------------------
    # Read Silver source
    # --------------------------------------------------------------

    targets = pd.read_parquet(
        SILVER_PATH
    )

    # --------------------------------------------------------------
    # Read Gold dimensions
    # --------------------------------------------------------------

    dim_brand = pd.read_parquet(
        DIM_BRAND_PATH
    )

    dim_calendar = pd.read_parquet(
        DIM_CALENDAR_PATH
    )

    dim_target_type = pd.read_parquet(
        DIM_TARGET_TYPE_PATH
    )

    dim_hierarchy = pd.read_parquet(
        DIM_HIERARCHY_PATH
    )

    # --------------------------------------------------------------
    # Validate source
    # --------------------------------------------------------------

    validate_columns(
        targets,
        TARGET_COLUMNS,
        "targets",
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
        dim_target_type,
        DIM_TARGET_TYPE_COLUMNS,
        "dim_target_type",
    )

    validate_columns(
        dim_hierarchy,
        DIM_HIERARCHY_COLUMNS,
        "dim_revenue_hierarchy",
    )

    # --------------------------------------------------------------
    # Standardize source
    # --------------------------------------------------------------

    targets = standardize_targets(
        targets
    )

    # --------------------------------------------------------------
    # Apply technical quality rules
    # --------------------------------------------------------------

    targets = remove_invalid_targets(
        targets
    )

    # --------------------------------------------------------------
    # Apply analytical business rules
    # --------------------------------------------------------------

    targets = apply_target_type_rules(
        targets
    )

    validate_target_type_mapping(
        targets
    )

    validate_target_values(
        targets
    )

    validate_target_grain(
        targets
    )

    # --------------------------------------------------------------
    # Build Target fact
    # --------------------------------------------------------------

    fact = build_fact_target(
        targets,
        dim_brand,
        dim_calendar,
        dim_target_type,
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
            "target_fact_sk",
            "calendar_sk",
            "brand_sk",
            "target_type_sk",
            "revenue_hierarchy_sk",
            "nature",
            "target_value",
        ]
    ]

    # --------------------------------------------------------------
    # Persist Gold
    # --------------------------------------------------------------

    save_gold(
        fact
    )

    print(
        f"Target fact records: {len(fact)}"
    )

    print(
        f"Total target value: "
        f"{fact['target_value'].sum():,.2f}"
    )

    return fact


# ----------------------------------------------------------------------
# MAIN
# ----------------------------------------------------------------------

if __name__ == "__main__":

    print(
        "Gold Layer - Fact Target"
    )

    print(
        "========================"
    )

    process_fact_target()

    print(
        "\nTarget fact created successfully."
    )

"""
Gold Layer - Dimension Calendar
===============================

Builds the Calendar dimension from the Silver opportunity and target
datasets.

The calendar is generated dynamically from the minimum and maximum
dates available across the analytical source datasets.

This implementation is intentionally time-period agnostic and does
not depend on hardcoded reporting years.

Responsibilities:

- Read standardized Silver data
- Validate source structures
- Identify the required analytical date range
- Generate one row per calendar date
- Create calendar attributes
- Generate a deterministic surrogate key
- Add a standard N/A member
- Persist the Gold dimension

The calendar is shared by Revenue and Target facts.
"""


from hashlib import sha256
from pathlib import Path

import pandas as pd


OPPORTUNITIES_PATH = Path(
    "data/silver/opportunities.parquet"
)

TARGETS_PATH = Path(
    "data/silver/targets.parquet"
)

GOLD_PATH = Path(
    "data/gold/dim_calendar.parquet"
)


OPPORTUNITY_DATE_COLUMNS = [
    "opportunity_date",
    "close_date",
]

TARGET_DATE_COLUMNS = [
    "period",
]


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


def prepare_opportunity_dates(df):
    """
    Convert opportunity date columns to datetime.
    """

    df = df.copy()

    for column in OPPORTUNITY_DATE_COLUMNS:
        df[column] = pd.to_datetime(
            df[column],
            errors="coerce",
        )

    return df


def prepare_target_dates(df):
    """
    Convert target period to datetime.
    """

    df = df.copy()

    df["period"] = pd.to_datetime(
        df["period"],
        errors="coerce",
    )

    return df


def get_source_date_range(
    df,
    date_columns,
    source_name,
):
    """
    Return the minimum and maximum valid dates from a source.
    """

    valid_dates = []

    for column in date_columns:
        if column in df.columns:
            valid_dates.append(
                df[column].dropna()
            )

    if not valid_dates:
        raise ValueError(
            f"No valid date columns found in "
            f"{source_name}."
        )

    combined_dates = pd.concat(
        valid_dates,
        ignore_index=True,
    )

    if combined_dates.empty:
        raise ValueError(
            f"No valid dates were found in "
            f"{source_name}."
        )

    minimum_date = combined_dates.min()
    maximum_date = combined_dates.max()

    if pd.isna(minimum_date):
        raise ValueError(
            f"No valid minimum date was found in "
            f"{source_name}."
        )

    if pd.isna(maximum_date):
        raise ValueError(
            f"No valid maximum date was found in "
            f"{source_name}."
        )

    return (
        minimum_date.date(),
        maximum_date.date(),
    )


def get_combined_date_range(
    opportunity_df,
    target_df,
):
    """
    Combine the date ranges from Revenue and Target sources.
    """

    opportunity_start, opportunity_end = (
        get_source_date_range(
            opportunity_df,
            OPPORTUNITY_DATE_COLUMNS,
            "opportunities",
        )
    )

    target_start, target_end = (
        get_source_date_range(
            target_df,
            TARGET_DATE_COLUMNS,
            "targets",
        )
    )

    start_date = min(
        opportunity_start,
        target_start,
    )

    end_date = max(
        opportunity_end,
        target_end,
    )

    return start_date, end_date


def generate_calendar(
    start_date,
    end_date,
):
    """
    Generate one row per calendar date.
    """

    dates = pd.date_range(
        start=start_date,
        end=end_date,
        freq="D",
    )

    calendar = pd.DataFrame(
        {
            "date": dates,
        }
    )

    calendar["year"] = (
        calendar["date"].dt.year
    )

    calendar["month"] = (
        calendar["date"].dt.month
    )

    calendar["month_name"] = (
        calendar["date"].dt.strftime("%B")
    )

    calendar["month_year"] = (
        calendar["date"].dt.strftime("%Y-%m")
    )

    calendar["quarter"] = (
        "Q"
        + calendar["date"]
        .dt.quarter
        .astype(str)
    )

    calendar["year_quarter"] = (
        calendar["year"].astype(str)
        + "-"
        + calendar["quarter"]
    )

    calendar["day_of_month"] = (
        calendar["date"].dt.day
    )

    calendar["day_of_week"] = (
        calendar["date"].dt.dayofweek + 1
    )

    calendar["day_name"] = (
        calendar["date"].dt.strftime("%A")
    )

    return calendar


def generate_surrogate_key(value):
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


def add_surrogate_key(df):
    """
    Add the calendar surrogate key.
    """

    df = df.copy()

    df["calendar_sk"] = (
        df["date"]
        .dt.strftime("%Y-%m-%d")
        .apply(generate_surrogate_key)
    )

    return df


def add_unknown_member(df):
    """
    Add the standard unknown calendar member.
    """

    unknown_record = pd.DataFrame(
        [
            {
                "calendar_sk": generate_surrogate_key(
                    "N/A"
                ),
                "date": pd.NaT,
                "year": pd.NA,
                "month": pd.NA,
                "month_name": "N/A",
                "month_year": "N/A",
                "quarter": "N/A",
                "year_quarter": "N/A",
                "day_of_month": pd.NA,
                "day_of_week": pd.NA,
                "day_name": "N/A",
            }
        ]
    )

    return pd.concat(
        [
            unknown_record,
            df,
        ],
        ignore_index=True,
    )


def validate_calendar(df):
    """
    Validate the final calendar structure.
    """

    required_columns = [
        "calendar_sk",
        "date",
        "year",
        "month",
        "month_name",
        "month_year",
        "quarter",
        "year_quarter",
        "day_of_month",
        "day_of_week",
        "day_name",
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            "Calendar is missing expected "
            f"columns: {missing_columns}"
        )

    duplicate_keys = (
        df["calendar_sk"]
        .duplicated()
        .sum()
    )

    if duplicate_keys > 0:
        raise ValueError(
            "Calendar contains duplicate "
            f"surrogate keys: {duplicate_keys}"
        )


def save_gold(df):
    """
    Persist the Gold calendar dimension.
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


def process_dim_calendar():
    """
    Build the Calendar Gold dimension.
    """

    if not OPPORTUNITIES_PATH.exists():
        raise FileNotFoundError(
            "Silver opportunity dataset not found: "
            f"{OPPORTUNITIES_PATH}"
        )

    if not TARGETS_PATH.exists():
        raise FileNotFoundError(
            "Silver target dataset not found: "
            f"{TARGETS_PATH}"
        )

    opportunities = pd.read_parquet(
        OPPORTUNITIES_PATH
    )

    targets = pd.read_parquet(
        TARGETS_PATH
    )

    if opportunities.empty:
        raise ValueError(
            "Silver opportunity dataset is empty."
        )

    if targets.empty:
        raise ValueError(
            "Silver target dataset is empty."
        )

    print(
        f"Opportunity records: "
        f"{len(opportunities)}"
    )

    print(
        f"Target records: "
        f"{len(targets)}"
    )

    validate_columns(
        opportunities,
        OPPORTUNITY_DATE_COLUMNS,
        "opportunities",
    )

    validate_columns(
        targets,
        TARGET_DATE_COLUMNS,
        "targets",
    )

    opportunities = prepare_opportunity_dates(
        opportunities
    )

    targets = prepare_target_dates(
        targets
    )

    start_date, end_date = (
        get_combined_date_range(
            opportunities,
            targets,
        )
    )

    print(
        f"Calendar period: "
        f"{start_date} → {end_date}"
    )

    calendar = generate_calendar(
        start_date,
        end_date,
    )

    calendar = add_surrogate_key(
        calendar
    )

    calendar = add_unknown_member(
        calendar
    )

    calendar = calendar[
        [
            "calendar_sk",
            "date",
            "year",
            "month",
            "month_name",
            "month_year",
            "quarter",
            "year_quarter",
            "day_of_month",
            "day_of_week",
            "day_name",
        ]
    ]

    validate_calendar(
        calendar
    )

    save_gold(
        calendar
    )

    print(
        f"Gold records: "
        f"{len(calendar)}"
    )

    return calendar


if __name__ == "__main__":
    print(
        "Gold Layer - Dimension Calendar"
    )

    print(
        "==============================="
    )

    process_dim_calendar()

    print(
        "\nCalendar dimension "
        "created successfully."
    )

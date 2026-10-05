"""
Gold Layer - Dimension Calendar
===============================

Builds the Calendar dimension from the Silver opportunity dataset.

The calendar is generated dynamically from the minimum and maximum
dates available in the source data.

This implementation is intentionally time-period agnostic and does
not depend on hardcoded reporting years.

Responsibilities:

- Read standardized Silver data
- Validate the source structure
- Identify the required date range
- Generate one row per calendar date
- Create calendar attributes
- Generate a deterministic surrogate key
- Add a standard N/A member
- Persist the Gold dimension

Business rules are intentionally excluded from this dimension.
"""

from datetime import date
from hashlib import sha256
from pathlib import Path

import pandas as pd


# ----------------------------------------------------------------------
# CONFIGURATION
# ----------------------------------------------------------------------

SILVER_PATH = Path(
    "data/silver/opportunities.parquet"
)

GOLD_PATH = Path(
    "data/gold/dim_calendar.parquet"
)

SOURCE_TABLE = "opportunities"


EXPECTED_COLUMNS = [
    "opportunity_date",
    "close_date",
]


# ----------------------------------------------------------------------
# VALIDATION
# ----------------------------------------------------------------------

def validate_columns(
    df: pd.DataFrame,
) -> None:
    """
    Validate whether the source contains all required columns.
    """

    missing_columns = [
        column
        for column in EXPECTED_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            "Missing expected columns: "
            f"{missing_columns}"
        )


# ----------------------------------------------------------------------
# DATE PREPARATION
# ----------------------------------------------------------------------

def prepare_dates(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Convert source date columns to pandas datetime values.
    """

    df = df.copy()

    for column in EXPECTED_COLUMNS:

        df[column] = pd.to_datetime(
            df[column],
            errors="coerce",
        )

    return df


def get_date_range(
    df: pd.DataFrame,
) -> tuple[date, date]:
    """
    Identify the minimum and maximum dates required
    to build the calendar dimension.
    """

    minimum_date = (
        df[EXPECTED_COLUMNS]
        .min()
        .min()
    )

    maximum_date = (
        df[EXPECTED_COLUMNS]
        .max()
        .max()
    )

    if pd.isna(minimum_date):
        raise ValueError(
            "No valid dates were found in the source data."
        )

    if pd.isna(maximum_date):
        raise ValueError(
            "No valid maximum date was found in the source data."
        )

    return (
        minimum_date.date(),
        maximum_date.date(),
    )


# ----------------------------------------------------------------------
# CALENDAR GENERATION
# ----------------------------------------------------------------------

def generate_calendar(
    start_date: date,
    end_date: date,
) -> pd.DataFrame:
    """
    Generate one row for each calendar date in the required period.
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
        calendar["date"]
        .dt.year
    )

    calendar["month"] = (
        calendar["date"]
        .dt.month
    )

    calendar["month_name"] = (
        calendar["date"]
        .dt.strftime("%B")
    )

    calendar["month_year"] = (
        calendar["date"]
        .dt.strftime("%Y-%m")
    )

    calendar["quarter"] = (
        "Q"
        + calendar["date"]
        .dt.quarter
        .astype(str)
    )

    calendar["year_quarter"] = (
        calendar["year"]
        .astype(str)
        + "-"
        + calendar["quarter"]
    )

    calendar["day_of_month"] = (
        calendar["date"]
        .dt.day
    )

    calendar["day_of_week"] = (
        calendar["date"]
        .dt.dayofweek
        + 1
    )

    calendar["day_name"] = (
        calendar["date"]
        .dt.strftime("%A")
    )

    return calendar


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


def add_surrogate_key(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Add the calendar surrogate key based on the date.
    """

    df = df.copy()

    df["calendar_sk"] = (
        df["date"]
        .dt.strftime("%Y-%m-%d")
        .apply(generate_surrogate_key)
    )

    return df


# ----------------------------------------------------------------------
# STANDARD N/A MEMBER
# ----------------------------------------------------------------------

def add_unknown_member(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Add a standard N/A member for unresolved dates.
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


# ----------------------------------------------------------------------
# PERSISTENCE
# ----------------------------------------------------------------------

def save_gold(
    df: pd.DataFrame,
) -> None:
    """
    Persist the Gold dimension as Parquet.
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

def process_dim_calendar() -> pd.DataFrame:
    """
    Execute the complete Gold transformation
    for the Calendar dimension.
    """

    if not SILVER_PATH.exists():
        raise FileNotFoundError(
            f"Silver dataset not found: "
            f"{SILVER_PATH}"
        )

    df = pd.read_parquet(
        SILVER_PATH
    )

    if df.empty:
        raise ValueError(
            "Silver opportunity dataset is empty."
        )

    print(
        f"Silver records: {len(df)}"
    )

    validate_columns(
        df
    )

    df = prepare_dates(
        df
    )

    start_date, end_date = (
        get_date_range(df)
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

    save_gold(
        calendar
    )

    print(
        f"Gold records: {len(calendar)}"
    )

    return calendar


# ----------------------------------------------------------------------
# MAIN
# ----------------------------------------------------------------------

if __name__ == "__main__":

    print("Gold Layer - Dimension Calendar")
    print("===============================")

    process_dim_calendar()

    print(
        "\nCalendar dimension created successfully."
    )

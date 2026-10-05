# DAX Measures - Year-over-Year

## Previous Year Measures

The Previous Year measures extend the Revenue and Revenue YTD calculations using the shared Calendar dimension.

These measures provide the foundation for Year-over-Year analysis.

---

## Revenue LY

### Purpose

Returns the Revenue value for the equivalent period in the previous year.

### DAX

    Revenue LY =
    CALCULATE (
        [Revenue],
        SAMEPERIODLASTYEAR ( 'Dim Calendar'[date] )
    )

### Analytical Behavior

The measure shifts the current Calendar filter context one year backward.

For example, if the current context is:

    March 2026

Revenue LY returns:

    Revenue for March 2025

If the current context is:

    Q2 2026

Revenue LY returns:

    Revenue for Q2 2025

The calculation is driven by the Calendar dimension rather than by a hardcoded year.

---

## Revenue LY YTD

### Purpose

Returns the cumulative Revenue for the equivalent Year-to-Date period in the previous year.

### DAX

    Revenue LY YTD =
    CALCULATE (
        [Revenue YTD],
        SAMEPERIODLASTYEAR ( 'Dim Calendar'[date] )
    )

### Analytical Behavior

The measure combines the existing Revenue YTD calculation with a one-year shift in the Calendar context.

For example, if the current context is:

    March 2026

Revenue LY YTD represents:

    January 2025
    +
    February 2025
    +
    March 2025

If the current context is:

    September 2026

Revenue LY YTD represents:

    January 2025
    through
    September 2025

This preserves the same accumulated period across years.

---

# Year-over-Year

## Revenue YoY

### Purpose

Measures the percentage variation between current Revenue and Revenue from the equivalent period in the previous year.

### DAX

    Revenue YoY =
    DIVIDE (
        [Revenue] - [Revenue LY],
        [Revenue LY],
        0
    )

### Analytical Behavior

The measure compares the current period against the equivalent previous-year period.

The calculation is:

    Current Revenue
        -
    Previous Year Revenue
        ÷
    Previous Year Revenue

Conceptually:

    Revenue YoY =
        (Revenue - Revenue LY)
        /
        Revenue LY

Examples:

- `0.10` represents 10% growth.
- `0.25` represents 25% growth.
- `-0.10` represents a 10% decrease.

The measure should be formatted as a percentage in the Semantic Model.

---

# Why the Measures Are Separated

Revenue LY and Revenue LY YTD represent different analytical concepts.

### Revenue LY

Compares the current period with the equivalent period from the previous year.

Example:

    March 2026
        vs
    March 2025

### Revenue LY YTD

Compares the accumulated current-year period with the equivalent accumulated period from the previous year.

Example:

    January–March 2026
        vs
    January–March 2025

Keeping these calculations separate prevents monthly and accumulated comparisons from being mixed.

---

# Calendar Dependency

The calculations depend on the shared Calendar dimension:

    'Dim Calendar'[date]

The Calendar dimension provides:

- Date
- Year
- Month
- Month-Year
- Quarter
- Year-Quarter

The measures do not use hardcoded years.

---

# Filter Context

The measures are designed to respect the existing analytical filter context.

For example, when filtering by:

- Brand
- Revenue Hierarchy
- User
- Opportunity Stage
- Negotiation Type

the Year-over-Year calculation compares the selected context with the corresponding previous-year context.

This allows the same measures to be reused across different analytical views.

---

# Validation Example

For a simplified monthly example:

| Month | Revenue | Revenue LY | Revenue YoY |
|---|---:|---:|---:|
| January | 100 | 80 | 25.0% |
| February | 150 | 120 | 25.0% |
| March | 200 | 250 | -20.0% |

For March:

    Revenue = 200
    Revenue LY = 250

Therefore:

    Revenue YoY =
    (200 - 250) / 250

    Revenue YoY = -20%

---

# YTD Validation Example

For a March YTD comparison:

| Period | Revenue YTD | Revenue LY YTD |
|---|---:|---:|
| March | 450 | 420 |

The corresponding YTD variation is:

    (450 - 420) / 420

    = 7.14%

The YTD variation can be added as a separate measure once the base LY measures have been validated.

---

# Design Principles

## Calendar-Driven Time Intelligence

All time intelligence calculations use the shared Calendar dimension.

## No Hardcoded Periods

The measures do not depend on a specific year.

## Reusable Measures

Revenue LY YTD reuses Revenue YTD rather than duplicating its aggregation logic.

## Separation of Monthly and YTD Analysis

Monthly comparisons and accumulated comparisons remain separate measures.

## Safe Division

DIVIDE is used to prevent errors when the previous-year value is zero or unavailable.

---

# Next Measures

The next analytical layer will introduce:

- Revenue YoY YTD
- Revenue Variance
- Target Variance
- Achievement YTD
- Achievement YTD vs Previous Year

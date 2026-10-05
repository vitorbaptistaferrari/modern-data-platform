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

# Year-over-Year Measures

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

    Revenue YoY
        =
    (Revenue - Revenue LY)
        /
    Revenue LY

Examples:

- `0.10` represents 10% growth.
- `0.25` represents 25% growth.
- `-0.10` represents a 10% decrease.

The measure should be formatted as a percentage in the Semantic Model.

### Zero or Unavailable Previous-Year Revenue

The current implementation uses `0` as the alternate result of `DIVIDE`.

Therefore, when Revenue LY is zero or unavailable, the measure returns `0`.

This behavior reflects the current DAX implementation.

---

## Revenue YoY YTD

### Purpose

Measures the percentage variation between accumulated Revenue in the current year and the equivalent accumulated period in the previous year.

### DAX

    Revenue YoY YTD =
    DIVIDE (
        [Revenue YTD] - [Revenue LY YTD],
        [Revenue LY YTD],
        0
    )

### Analytical Behavior

The measure compares:

    Revenue YTD
        vs
    Revenue LY YTD

For example, when the current context is March 2026:

    Revenue YTD
        =
    January 2026
    +
    February 2026
    +
    March 2026

while:

    Revenue LY YTD
        =
    January 2025
    +
    February 2025
    +
    March 2025

The result represents the accumulated Year-over-Year variation.

The calculation is:

    Revenue YoY YTD
        =
    (Revenue YTD - Revenue LY YTD)
        /
    Revenue LY YTD

### Zero or Unavailable Previous-Year Revenue

The current implementation uses `0` as the alternate result of `DIVIDE`.

Therefore, when Revenue LY YTD is zero or unavailable, the measure returns `0`.

This behavior reflects the current DAX implementation.

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

Similarly, Revenue YoY and Revenue YoY YTD represent different comparison contexts.

### Revenue YoY

Measures the variation for the current filter period.

### Revenue YoY YTD

Measures the variation for the accumulated year-to-date period.

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

| Period | Revenue YTD | Revenue LY YTD | Revenue YoY YTD |
|---|---:|---:|---:|
| March | 450 | 420 | 7.14% |

The corresponding YTD variation is:

    (450 - 420) / 420

    = 7.14%

This calculation is implemented by the `Revenue YoY YTD` measure.

---

# Design Principles

## Calendar-Driven Time Intelligence

All time intelligence calculations use the shared Calendar dimension.

## No Hardcoded Periods

The measures do not depend on a specific year.

## Reusable Measures

Revenue LY YTD reuses Revenue YTD rather than duplicating its aggregation logic.

Revenue YoY YTD reuses Revenue YTD and Revenue LY YTD.

## Separation of Monthly and YTD Analysis

Monthly comparisons and accumulated comparisons remain separate measures.

## Safe Division

`DIVIDE` is used to prevent calculation errors when the previous-year value is zero or unavailable.

The current implementation explicitly uses `0` as the alternate result for the Year-over-Year measures.

---

# Current Year-over-Year Measure Set

The Semantic Model currently implements:

- Revenue LY
- Revenue LY YTD
- Revenue YoY
- Revenue YoY YTD

These measures provide the previous-year and Year-over-Year comparison layer of the analytical model.

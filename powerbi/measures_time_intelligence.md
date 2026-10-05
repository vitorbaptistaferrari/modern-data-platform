# DAX Measures - Time Intelligence

## Year-to-Date Measures

The Year-to-Date measures extend the base Revenue and Target measures using the shared Calendar dimension.

The Calendar dimension is the central time dimension for both analytical facts.

This allows Revenue and Target to use the same time context when calculating accumulated values.

---

## Revenue YTD

### Purpose

Returns cumulative realized revenue from the beginning of the current year through the current date in the filter context.

### DAX

    Revenue YTD =
    CALCULATE (
        [Revenue],
        DATESYTD ( 'Dim Calendar'[date] )
    )

### Analytical Behavior

The measure accumulates Revenue according to the date context provided by the Calendar dimension.

For example, if the current context is:

    January

Revenue YTD represents:

    January Revenue

If the current context is:

    February

Revenue YTD represents:

    January Revenue
    +
    February Revenue

If the current context is:

    March

Revenue YTD represents:

    January Revenue
    +
    February Revenue
    +
    March Revenue

The accumulation restarts when the calendar year changes.

---

## Target YTD

### Purpose

Returns cumulative target from the beginning of the current year through the current date in the filter context.

### DAX

    Target YTD =
    CALCULATE (
        [Target],
        DATESYTD ( 'Dim Calendar'[date] )
    )

### Analytical Behavior

The measure accumulates Target using the same Calendar dimension used by Revenue YTD.

For example:

    January Target

returns:

    January Target

While:

    February Target

returns:

    January Target
    +
    February Target

And:

    March Target

returns:

    January Target
    +
    February Target
    +
    March Target

The accumulation restarts when the calendar year changes.

---

# YTD Design Principles

## Shared Calendar

Both YTD measures use:

    'Dim Calendar'[date]

This ensures that Revenue and Target use the same analytical time context.

## Measure Reuse

Revenue YTD is built from:

    [Revenue]

Target YTD is built from:

    [Target]

This keeps the calculation modular and avoids duplicating the underlying aggregation logic.

## No Hardcoded Year

The measures do not contain a specific reporting year.

The current year is determined by the Calendar filter context.

This preserves the time-period-agnostic design of the platform.

## Accumulation Behavior

YTD represents an accumulated value rather than the value of the individual month.

Conceptually:

    Monthly Revenue
        ↓
    Revenue YTD
        ↓
    Cumulative Revenue

And:

    Monthly Target
        ↓
    Target YTD
        ↓
    Cumulative Target

---

# Validation Example

For a simplified example:

| Month | Revenue | Revenue YTD | Target | Target YTD |
|---|---:|---:|---:|---:|
| January | 100 | 100 | 120 | 120 |
| February | 150 | 250 | 130 | 250 |
| March | 200 | 450 | 160 | 410 |

The monthly values remain monthly values.

The YTD measures accumulate those monthly values.

This distinction is important when building Revenue vs Target analytical visuals.

---

# Relationship with Other Time-Intelligence Measures

Revenue YTD and Target YTD are foundational measures for the other time-intelligence calculations in the Semantic Model.

They are reused by:

- Revenue LY YTD
- Revenue YoY YTD
- Revenue Target Variance YTD
- Achievement YTD

The measures therefore form a reusable calculation chain rather than duplicating aggregation logic.

---

# Current Time-Intelligence Measure Set

The current Semantic Model implements the following time-related measures:

## YTD

- Revenue YTD
- Target YTD
- Achievement YTD

## Previous Year

- Revenue LY
- Revenue LY YTD

## Year-over-Year

- Revenue YoY
- Revenue YoY YTD

All calculations use the shared `Dim Calendar` dimension.

---

# Design Principles

## Centralized Calendar

Time-intelligence calculations use the dedicated `Dim Calendar` dimension.

## Reusable Measures

More advanced calculations reuse the existing base and YTD measures.

## No Hardcoded Periods

The calculations do not depend on a specific reporting year.

## Monthly vs YTD Separation

Monthly values and accumulated values are kept as separate measures.

This prevents cumulative calculations from being mixed with individual-period values.

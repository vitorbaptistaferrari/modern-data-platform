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

# Next Measures

The next time-intelligence layer will introduce:

- Revenue LY
- Revenue LY YTD
- Revenue YoY
- Revenue Variance
- Target Variance
- Achievement YTD

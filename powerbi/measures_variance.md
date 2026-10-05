# DAX Measures - Variance and Achievement

## Variance and YTD Achievement Measures

This layer extends the base Revenue, Target and Year-over-Year measures into accumulated performance and variance analysis.

The measures support the main analytical questions of the Revenue Data Platform:

- How much revenue was realized?
- How much was targeted?
- How much of the target was achieved?
- How does the current period compare with the previous year?
- How does accumulated performance compare with the accumulated target?
- What is the variance between actual revenue and target?

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

The current implementation uses `0` as the alternate result when Revenue LY YTD is zero or unavailable.

---

## Revenue Variance

### Purpose

Measures the absolute difference between realized Revenue and Target.

### DAX

    Revenue Variance =
    [Revenue] - [Target]

### Analytical Behavior

A positive value means Revenue is above Target.

A negative value means Revenue is below Target.

Conceptually:

    Revenue Variance
        =
    Actual Revenue
        -
    Target

Example:

    Revenue = 500,000
    Target = 450,000

    Revenue Variance = 50,000

---

## Revenue Target Variance YTD

### Purpose

Provides the accumulated difference between Revenue YTD and Target YTD.

### DAX

    Revenue Target Variance YTD =
    [Revenue YTD] - [Target YTD]

### Analytical Behavior

The measure is intended for accumulated performance analysis.

For example:

    Revenue YTD = 1,200,000
    Target YTD = 1,000,000

    Revenue Target Variance YTD = 200,000

A positive result indicates that accumulated Revenue is above the accumulated Target.

A negative result indicates that accumulated Revenue is below the accumulated Target.

---

## Achievement YTD

### Purpose

Measures the percentage of accumulated Target achieved by accumulated Revenue.

### DAX

    Achievement YTD =
    DIVIDE (
        [Revenue YTD],
        [Target YTD],
        0
    )

### Analytical Behavior

The measure compares accumulated Revenue against accumulated Target.

Conceptually:

    Revenue YTD
        ÷
    Target YTD
        =
    Achievement YTD

Example:

    Revenue YTD = 900,000
    Target YTD = 1,000,000

    Achievement YTD = 90%

The current implementation uses `0` as the alternate result when Target YTD is zero or unavailable.

---

# Monthly vs YTD Measures

The Semantic Model intentionally keeps monthly and accumulated measures separate.

### Monthly

    Revenue
    Target
    Achievement %
    Revenue Variance

### Year-to-Date

    Revenue YTD
    Target YTD
    Achievement YTD
    Revenue Target Variance YTD

### Previous Year

    Revenue LY
    Revenue LY YTD

### Year-over-Year

    Revenue YoY
    Revenue YoY YTD

This separation prevents accumulated calculations from being mixed with monthly values.

---

# Analytical Relationships

The measures can be organized conceptually as:

    Revenue
        |
        +-- Revenue YTD
        |       |
        |       +-- Revenue YoY YTD
        |
        +-- Revenue LY
        |       |
        |       +-- Revenue LY YTD
        |
        +-- Revenue YoY

    Target
        |
        +-- Target YTD

    Revenue + Target
        |
        +-- Achievement %
        +-- Achievement YTD
        +-- Revenue Variance
        +-- Revenue Target Variance YTD

This structure emphasizes measure reuse and avoids duplicating aggregation logic.

---

# Filter Context

All measures continue to respect the Semantic Model filter context.

For example, the same measures can be evaluated by:

- Brand
- Revenue Hierarchy
- User
- Opportunity Stage
- Negotiation Type
- Year
- Quarter
- Month

No measure introduces a hardcoded brand, year or reporting period.

---

# Safe Division

Percentage measures use `DIVIDE` rather than direct division.

The current implementation uses an explicit alternate result of `0` for:

- Achievement YTD
- Revenue YoY
- Revenue YoY YTD

The base `Achievement %` measure does not specify an alternate result and therefore returns BLANK when the denominator is zero or unavailable.

This difference reflects the current implementation of the Semantic Model.

---

# Formatting Recommendations

The Semantic Model should use the following display formats:

| Measure | Format |
|---|---|
| Revenue | Currency |
| Target | Currency |
| Revenue YTD | Currency |
| Target YTD | Currency |
| Revenue LY | Currency |
| Revenue LY YTD | Currency |
| Revenue Variance | Currency |
| Revenue Target Variance YTD | Currency |
| Achievement % | Percentage |
| Achievement YTD | Percentage |
| Revenue YoY | Percentage |
| Revenue YoY YTD | Percentage |

The currency format should follow the Brazilian analytical context:

    R$ #,##0.00

Percentage measures should use:

    0.00%

---

# Current Measure Set

The Semantic Model currently implements the following analytical measures.

## Base

- Revenue
- Target
- Achievement %

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

## Variance

- Revenue Variance
- Revenue Target Variance YTD

All measures are implemented in the current public Power BI Semantic Model.

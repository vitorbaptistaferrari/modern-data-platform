# DAX Measures

## Base Measures

The semantic measure layer is built on top of the analytical fact tables available in the Power BI Semantic Model.

For the public repository, these analytical tables are populated with controlled synthetic data embedded in the Power BI project.

The measures provide the foundation for more advanced calculations such as YTD, Year-over-Year and target achievement.

---

## Revenue

### Purpose

Returns the total realized revenue in the current filter context.

### DAX

    Revenue =
    SUM ( 'Fact Revenue'[revenue_value] )

### Analytical Behavior

The measure respects the filter context provided by the Semantic Model.

Revenue can be analyzed by:

- Year
- Month
- Brand
- User
- Opportunity
- Opportunity Stage
- Negotiation Type
- Revenue Hierarchy

The measure contains no hardcoded reporting period or business classification.

---

## Target

### Purpose

Returns the total target value in the current filter context.

### DAX

    Target =
    SUM ( 'Fact Target'[target_value] )

### Analytical Behavior

The measure respects the shared dimensions available to Fact Target.

Target can be analyzed by:

- Year
- Month
- Brand
- Target Type
- Revenue Hierarchy

Target is stored independently from Revenue because actual revenue and business targets originate from different analytical facts.

---

## Achievement %

### Purpose

Measures the percentage of target achieved by comparing realized Revenue against the corresponding Target.

### DAX

    Achievement % =
    DIVIDE (
        [Revenue],
        [Target]
    )

### Analytical Behavior

The measure is intentionally built from the base measures rather than directly referencing fact columns.

This allows the same calculation to work across different filter contexts.

The analytical relationship is:

    Revenue
        ÷
    Target
        =
    Achievement %

A result of:

- 1.00 represents 100% achievement.
- 0.80 represents 80% achievement.
- 1.20 represents 120% achievement.

The measure should be formatted as a percentage in the Semantic Model.

### Missing Target Behavior

The measure uses DIVIDE without a fallback value.

When Target is zero or unavailable, the result is BLANK rather than 0%.

This distinction is intentional.

A zero percentage means that Revenue exists but represents zero achievement.

A blank result indicates that there is no valid Target available for the current analytical context.

---

# Base Measure Design Principles

## Reusable Base Measures

Base measures should be simple and reusable.

Complex calculations should build on top of these measures rather than duplicating the underlying aggregation logic.

## Filter Context

Measures must respect the filter context provided by the Semantic Model.

No reporting period should be hardcoded into the base measures.

## Separation of Facts

Revenue is calculated from:

Fact Revenue

Target is calculated from:

Fact Target

The two facts are not directly related.

Shared dimensions provide the analytical context used to compare them.

## Safe Division

Percentage calculations use DIVIDE rather than direct division.

When the denominator is zero or unavailable, the result is BLANK rather than an artificial 0%.

---

# Time Intelligence Measures

The following measures extend the base calculations:

- Revenue YTD
- Target YTD
- Revenue LY
- Revenue LY YTD
- Revenue YoY
- Revenue YoY YTD

These calculations use the shared Dim Calendar dimension.

---

# Variance Measures

The analytical model uses explicit variance names to make the business meaning clear.

## Revenue Variance

Represents the difference between current Revenue and current Target.

    Revenue Variance =
    [Revenue] - [Target]

## Revenue Target Variance YTD

Represents the accumulated difference between Revenue YTD and Target YTD.

    Revenue Target Variance YTD =
    [Revenue YTD] - [Target YTD]

The explicit naming prevents ambiguity between monthly variance, YTD variance and Year-over-Year variation.

---

# Measure Naming Principles

Measure names should clearly communicate the analytical context.

Avoid ambiguous names such as:

- Variance
- Growth
- Previous
- Target Difference

Prefer explicit names such as:

- Revenue Variance
- Revenue Target Variance YTD
- Revenue YoY
- Revenue YoY YTD
- Revenue LY
- Revenue LY YTD

This makes the Semantic Model easier to understand and consume.

---

# Formatting Recommendations

| Measure | Format |
|---|---|
| Revenue | Currency |
| Target | Currency |
| Achievement % | Percentage |
| Revenue Variance | Currency |
| Revenue Target Variance YTD | Currency |

The currency format should follow the Brazilian analytical context:

    R$ #,##0.00

Percentage measures should use:

    0.00%

---

# Analytical Measure Set

The complete analytical measure set currently implemented in the Semantic Model is:

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

The complete measure set is implemented in the current public Power BI Semantic Model.

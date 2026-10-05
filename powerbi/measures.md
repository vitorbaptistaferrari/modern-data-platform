# DAX Measures

## Base Measures

The first semantic measures are built directly on top of the Gold fact tables.

These measures provide the foundation for the analytical layer and are reused by more advanced calculations such as YTD, Year-over-Year and target achievement.

---

## Revenue

### Purpose

Returns the total realized revenue in the current filter context.

### DAX

    Revenue =
    SUM ( 'Fact Revenue'[revenue_value] )

### Analytical Behavior

The measure respects the filter context provided by the Semantic Model.

For example, Revenue can be analyzed by:

- Year
- Month
- Brand
- User
- Opportunity
- Opportunity Stage
- Negotiation Type
- Revenue Hierarchy

The measure intentionally contains no hardcoded period or business classification.

---

## Target

### Purpose

Returns the total target value in the current filter context.

### DAX

    Target =
    SUM ( 'Fact Target'[target_value] )

### Analytical Behavior

The measure respects the shared dimensions available to Fact Target.

It can therefore be analyzed by:

- Year
- Month
- Brand
- Target Type
- Revenue Hierarchy

Target is stored independently from Revenue because actual revenue and business targets originate from different analytical facts.

---

## Achievement %

### Purpose

Measures the percentage of target achieved by comparing realized revenue against the corresponding target.

### DAX

    Achievement % =
    DIVIDE (
        [Revenue],
        [Target],
        0
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

---

# Measure Design Principles

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

Achievement calculations use DIVIDE rather than direct division to avoid errors when the target is zero or unavailable.

---

# Next Measures

The next layer of measures will extend these base calculations into time intelligence and variance analysis.

Planned measures include:

- Revenue YTD
- Target YTD
- Revenue LY
- Revenue LY YTD
- Revenue YoY
- Revenue Variance
- Target Variance

# Semantic Model

## Purpose

The semantic model represents the analytical layer of the Modern Data Platform project.

It transforms the outputs of the Gold analytical layer into a business-oriented dimensional model designed for reporting, analytics and reusable business measures.

The public implementation uses synthetic data exclusively for demonstration purposes.

No proprietary or production data is included in the repository.

## Architecture

The semantic model follows a star-schema-oriented architecture.

    Dimensional Model
            │
            ├── Fact Revenue
            │
            └── Fact Target

Shared dimensions are reused across the analytical facts where appropriate.

## Fact Tables

### Fact Revenue

The grain of Fact Revenue is one analytical revenue occurrence per opportunity in the current public implementation.

The table contains foreign keys to the relevant dimensions and the analytical revenue value.

Main attributes:

- `revenue_sk`
- `opportunity_sk`
- `user_sk`
- `brand_sk`
- `calendar_sk`
- `opportunity_stage_sk`
- `negotiation_type_sk`
- `revenue_hierarchy_sk`
- `revenue_value`

Revenue is generated only for opportunities classified as won in the public analytical representation.

### Fact Target

The grain of Fact Target is:

    Period + Brand + Analytical Target Type + Nature

Main attributes:

- `target_fact_sk`
- `calendar_sk`
- `brand_sk`
- `target_type_sk`
- `revenue_hierarchy_sk`
- `nature`
- `target_value`

The fact represents analytical targets independently from realized revenue.

## Dimension Tables

### Dim Calendar

Provides the shared time dimension used by both fact tables.

It supports:

- Date analysis
- Year
- Month
- Month name
- Month-year
- Quarter
- Time intelligence

The calendar is used as the central time dimension for DAX calculations.

### Dim Brand

Represents the analytical brand dimension.

Main attributes:

- `brand_sk`
- `brand_name`
- `is_active`

### Dim User

Represents users associated with revenue opportunities.

Main attributes include:

- `user_sk`
- `user_id`
- `user_name`
- `department`
- `role`
- `active`

### Dim Opportunity

Represents the analytical opportunity entity and provides descriptive context for revenue analysis.

Main attributes include:

- `opportunity_sk`
- `opportunity_id`
- `customer_id`
- `customer_name`
- `city`
- `state`
- `segment`
- `opportunity_type`
- `brand`
- `origin`
- `opportunity_date`
- `close_date`

### Dim Opportunity Stage

Represents the opportunity lifecycle stage.

Main attributes include:

- `opportunity_stage_sk`
- `stage_id`
- `stage_name`
- `stage_order`
- `is_closed`
- `is_won`

The `is_won` attribute is used to distinguish opportunities that contribute to recognized revenue from opportunities that do not.

### Dim Negotiation Type

Represents the analytical negotiation classification:

- Prospecting
- Renewal
- Expansion

### Dim Target Type

Represents the analytical classification used by target data:

- Prospecting
- Renewal
- Expansion

### Dim Revenue Hierarchy

Represents the analytical revenue hierarchy.

    Revenue
    ├── Prospecting
    │   └── Prospecting
    ├── Renewal
    │   └── Renewal
    └── Expansion
        ├── Expansion
        ├── Cross-Sell
        └── Up-Sell

The hierarchy allows business analysis at different levels of granularity.

## Relationships

The semantic model uses one-to-many relationships from dimensions to facts.

### Fact Revenue

Fact Revenue is related to:

- Dim Calendar
- Dim Brand
- Dim User
- Dim Opportunity
- Dim Opportunity Stage
- Dim Negotiation Type
- Dim Revenue Hierarchy

### Fact Target

Fact Target is related to:

- Dim Calendar
- Dim Brand
- Dim Target Type
- Dim Revenue Hierarchy

The model does not use direct fact-to-fact relationships.

Dimensions are not unnecessarily chained together.

## Shared Dimensions

The following dimensions are shared across analytical processes:

- Dim Calendar
- Dim Brand
- Dim Revenue Hierarchy

This allows revenue and target analysis to be performed using common analytical contexts.

## Measures

The semantic model contains reusable DAX measures.

### Base Measures

- Revenue
- Target
- Achievement %

### Time Intelligence

- Revenue YTD
- Target YTD
- Revenue LY
- Revenue LY YTD

### Variance and Comparison

- Revenue YoY
- Revenue YoY YTD
- Revenue Variance
- Revenue Target Variance YTD
- Achievement YTD

Measures are designed to operate independently from individual report visuals.

## Business Logic

The semantic model preserves the analytical concepts defined in the Gold layer.

Revenue classification includes:

- Prospecting
- Renewal
- Expansion

Expansion can be further classified into:

- Expansion
- Cross-Sell
- Up-Sell

Revenue is associated with won opportunities in the public analytical representation.

Targets are modeled independently from realized revenue to allow direct comparison between planned and realized performance.

## Synthetic Data Strategy

Production data is intentionally excluded from the public implementation.

Synthetic data is used to demonstrate:

- Fact and dimension relationships
- Revenue analysis
- Target analysis
- Revenue hierarchy
- Time intelligence
- Achievement calculations
- Variance calculations

The synthetic data does not represent actual customers, transactions, commercial values or production identifiers.

## Power BI Implementation

The semantic model is implemented as a Power BI Project using the `.pbip` format.

The Power BI project is stored under:

    powerbi/

The implementation includes:

- Semantic model metadata
- Report metadata
- Relationships
- DAX measures
- Analytical tables

The Power BI artifact is versioned together with the engineering code and technical documentation in GitHub.

## Design Principles

The semantic model follows these principles:

1. Dimensional modeling.
2. Separation of facts and dimensions.
3. Reusable shared dimensions.
4. Centralized time intelligence.
5. Reusable business measures.
6. No direct fact-to-fact relationships.
7. Business-rule isolation.
8. Synthetic data for public demonstration.
9. Separation between production implementation and public portfolio representation.
10. Alignment between Gold analytical structures and the Power BI semantic layer.

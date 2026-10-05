# Semantic Model

## Overview

The Semantic Model is the analytical consumption layer built on top of the Gold layer.

Its purpose is to expose a consistent analytical structure for reporting and business intelligence workloads.

The model follows a star schema pattern, with fact tables at the center and descriptive dimensions surrounding them.

The Semantic Model does not apply source ingestion or technical transformation logic.

Its responsibilities are:

- Define analytical relationships
- Expose business-friendly dimensions
- Provide reusable measures
- Support time intelligence
- Enable consistent Power BI analysis

---

## Model Structure

The Semantic Model is composed of two fact tables and a set of shared and fact-specific dimensions.

### Fact Tables

- Fact Revenue
- Fact Target

### Dimensions

- Dim Brand
- Dim Calendar
- Dim User
- Dim Opportunity
- Dim Opportunity Stage
- Dim Negotiation Type
- Dim Target Type
- Dim Revenue Hierarchy

---

## Star Schema

Conceptually, the model follows this structure:

    Dim Calendar
          │
          ├──────────────► Fact Revenue
          │
          └──────────────► Fact Target

    Dim Brand
          │
          ├──────────────► Fact Revenue
          │
          └──────────────► Fact Target

    Dim Revenue Hierarchy
          │
          ├──────────────► Fact Revenue
          │
          └──────────────► Fact Target

    Dim User
          │
          └──────────────► Fact Revenue

    Dim Opportunity
          │
          └──────────────► Fact Revenue

    Dim Opportunity Stage
          │
          └──────────────► Fact Revenue

    Dim Negotiation Type
          │
          └──────────────► Fact Revenue

    Dim Target Type
          │
          └──────────────► Fact Target

---

## Fact Revenue

### Purpose

Fact Revenue represents analytical revenue generated from opportunity-related business rules.

### Grain

The current public implementation represents one analytical revenue occurrence per opportunity.

The fact structure is designed so that the grain can evolve if future business rules require multiple revenue components per opportunity.

### Key

Primary analytical key:

`revenue_sk`

### Foreign Keys

- `calendar_sk`
- `brand_sk`
- `user_sk`
- `opportunity_sk`
- `opportunity_stage_sk`
- `negotiation_type_sk`
- `revenue_hierarchy_sk`

### Measure Columns

- `revenue_value`

---

## Fact Target

### Purpose

Fact Target represents business targets by reporting period, brand and analytical target classification.

### Grain

The target grain is:

`period + brand + target_type + nature`

### Key

Primary analytical key:

`target_fact_sk`

### Foreign Keys

- `calendar_sk`
- `brand_sk`
- `target_type_sk`
- `revenue_hierarchy_sk`

### Measure Columns

- `target_value`

### Descriptive Columns

- `nature`

---

## Dimensions

### Dim Calendar

### Purpose

Provides the shared time dimension for Revenue and Target analysis.

### Key

`calendar_sk`

### Relationship Targets

- Fact Revenue
- Fact Target

### Main Attributes

- Date
- Year
- Month
- Month Name
- Month-Year
- Quarter
- Year-Quarter
- Day of Month
- Day of Week
- Day Name

---

### Dim Brand

### Purpose

Provides the analytical brand context.

### Key

`brand_sk`

### Relationship Targets

- Fact Revenue
- Fact Target

### Main Attribute

- Brand

---

### Dim User

### Purpose

Provides the user or responsible-person context for revenue analysis.

### Key

`user_sk`

### Relationship Target

- Fact Revenue

### Main Attributes

- User
- Department
- Role
- Active Status

---

### Dim Opportunity

### Purpose

Provides descriptive context for revenue generated from opportunities.

### Key

`opportunity_sk`

### Relationship Target

- Fact Revenue

### Main Attributes

- Opportunity
- Customer
- City
- State
- Segment
- Opportunity Type
- Brand
- Origin
- Opportunity Date
- Close Date

---

### Dim Opportunity Stage

### Purpose

Provides the analytical sales-stage context.

### Key

`opportunity_stage_sk`

### Relationship Target

- Fact Revenue

### Main Attributes

- Stage
- Stage Order
- Closed Indicator
- Won Indicator

---

### Dim Negotiation Type

### Purpose

Provides the analytical classification of the commercial negotiation.

### Key

`negotiation_type_sk`

### Relationship Target

- Fact Revenue

### Main Attributes

- Negotiation Type

Current analytical classifications include:

- Prospecting
- Renewal
- Expansion

---

### Dim Target Type

### Purpose

Provides the analytical classification of target records.

### Key

`target_type_sk`

### Relationship Target

- Fact Target

### Main Attributes

- Target Type

Current analytical classifications include:

- Prospecting
- Renewal
- Expansion

---

### Dim Revenue Hierarchy

### Purpose

Provides the shared revenue classification hierarchy used by both facts.

### Key

`revenue_hierarchy_sk`

### Relationship Targets

- Fact Revenue
- Fact Target

### Hierarchy

    Revenue
    ├── Prospecting
    │   └── Prospecting
    │
    ├── Renewal
    │   └── Renewal
    │
    └── Expansion
        ├── Expansion
        ├── Cross-Sell
        └── Up-Sell

The aggregated Expansion member allows target values to be analyzed at the Expansion level.

The Cross-Sell and Up-Sell members allow revenue to be analyzed at a more detailed level.

---

# Relationships

All relationships follow a dimensional modeling pattern:

**Dimension → Fact**

The expected cardinality is:

**1 : Many**

The expected filter direction is:

**Single**

The facts do not have direct relationships with each other.

---

## Fact Revenue Relationships

| Dimension | Dimension Key | Fact Foreign Key | Cardinality | Cross-filter |
|---|---|---|---|---|
| Dim Calendar | `calendar_sk` | `calendar_sk` | 1 : * | Single |
| Dim Brand | `brand_sk` | `brand_sk` | 1 : * | Single |
| Dim User | `user_sk` | `user_sk` | 1 : * | Single |
| Dim Opportunity | `opportunity_sk` | `opportunity_sk` | 1 : * | Single |
| Dim Opportunity Stage | `opportunity_stage_sk` | `opportunity_stage_sk` | 1 : * | Single |
| Dim Negotiation Type | `negotiation_type_sk` | `negotiation_type_sk` | 1 : * | Single |
| Dim Revenue Hierarchy | `revenue_hierarchy_sk` | `revenue_hierarchy_sk` | 1 : * | Single |

---

## Fact Target Relationships

| Dimension | Dimension Key | Fact Foreign Key | Cardinality | Cross-filter |
|---|---|---|---|---|
| Dim Calendar | `calendar_sk` | `calendar_sk` | 1 : * | Single |
| Dim Brand | `brand_sk` | `brand_sk` | 1 : * | Single |
| Dim Target Type | `target_type_sk` | `target_type_sk` | 1 : * | Single |
| Dim Revenue Hierarchy | `revenue_hierarchy_sk` | `revenue_hierarchy_sk` | 1 : * | Single |

---

# Relationship Principles

## No Fact-to-Fact Relationships

Fact Revenue and Fact Target are intentionally independent.

The two facts are analyzed through shared dimensions such as:

- Calendar
- Brand
- Revenue Hierarchy

This prevents direct fact-to-fact filtering and avoids ambiguous analytical paths.

---

## No Dimension-to-Dimension Relationships

Dimensions are not directly related to one another in the Semantic Model.

Each dimension connects directly to the fact table that requires its analytical context.

This preserves the star schema structure.

---

## Surrogate Keys

Relationships use deterministic surrogate keys generated in the Gold layer.

For example:

`Dim Brand[brand_sk]`

relates to:

`Fact Revenue[brand_sk]`

rather than using the descriptive brand value.

This keeps analytical relationships based on stable Gold-layer identifiers.

---

# Shared Dimensions

Some dimensions are shared across both fact tables.

### Dim Calendar

    Dim Calendar
         │
         ├──► Fact Revenue
         │
         └──► Fact Target

### Dim Brand

    Dim Brand
         │
         ├──► Fact Revenue
         │
         └──► Fact Target

### Dim Revenue Hierarchy

    Dim Revenue Hierarchy
         │
         ├──► Fact Revenue
         │
         └──► Fact Target

Shared dimensions allow Revenue and Target to be analyzed using common business contexts.

---

# Analytical Measures

The Semantic Model will expose reusable analytical measures rather than requiring report authors to recreate calculations.

Planned measures include:

- Revenue
- Target
- Achievement %
- Revenue YTD
- Target YTD
- Revenue LY
- Revenue LY YTD
- Revenue YoY
- Revenue Variance
- Target Variance

The exact DAX implementation will be defined after the relationship model is established.

---

# Time Intelligence

The Calendar dimension is shared between Revenue and Target.

This allows common time filters to be applied to both facts.

Examples include:

- Year
- Quarter
- Month
- Month-Year
- YTD
- Previous Year
- Year-over-Year

The calendar is generated dynamically from the relevant Silver source periods and is not tied to a fixed reporting year.

---

# Semantic Layer Responsibilities

The Semantic Model is responsible for analytical interpretation, not source processing.

### Data Engineering

Bronze and Silver handle:

- Ingestion
- Standardization
- Technical quality
- Deduplication

### Analytical Modeling

Gold handles:

- Business rules
- Facts
- Dimensions
- Surrogate keys
- Revenue classification

### Semantic Modeling

The Semantic Model handles:

- Relationships
- Measures
- Time intelligence
- Analytical hierarchies
- Business-friendly consumption

### Visualization

Power BI handles:

- Reports
- Dashboards
- Charts
- User interaction

---

# Design Principles

## Star Schema

The model follows a star schema to simplify analytical querying and reduce relationship ambiguity.

## Shared Dimensions

Common business dimensions are reused across facts whenever they represent the same analytical concept.

## Single-Direction Filtering

Relationships use single-direction filtering from dimensions toward facts unless a future analytical requirement explicitly justifies another pattern.

## Reusable Measures

Business calculations are implemented as reusable semantic measures rather than duplicated in individual reports.

## Separation of Concerns

The Semantic Model does not contain source ingestion or technical transformation logic.

## Analytical Stability

The Semantic Model is designed to remain stable as source volumes and reporting periods evolve.

> **The data changes. The architecture remains.**

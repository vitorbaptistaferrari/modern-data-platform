# Power BI Semantic Model

## Overview

This directory contains the analytical layer of the Modern Data Platform project.

The Semantic Model is built on top of the Gold layer and is designed to provide a reusable analytical interface for Power BI reporting.

The model follows a star schema and separates:

- Analytical facts
- Descriptive dimensions
- Relationships
- Business measures
- Time intelligence
- Performance indicators

The public implementation is based on synthetic data and does not contain proprietary production information.

---

# Semantic Model Architecture

The analytical model follows this structure:

    Gold Layer
        │
        ▼
    Semantic Model
        │
        ├── Dimensions
        │
        ├── Fact Tables
        │
        ├── Relationships
        │
        └── Measures
                │
                ▼
             Power BI

---

# Fact Tables

## Fact Revenue

Source:

`data/gold/fact_revenue.parquet`

Purpose:

Represents realized analytical revenue generated from won opportunities.

### Grain

One analytical revenue occurrence per opportunity in the current public implementation.

### Key

`revenue_sk`

### Foreign Keys

- `calendar_sk`
- `brand_sk`
- `user_sk`
- `opportunity_sk`
- `opportunity_stage_sk`
- `negotiation_type_sk`
- `revenue_hierarchy_sk`

### Measures

- `revenue_value`

---

## Fact Target

Source:

`data/gold/fact_target.parquet`

Purpose:

Represents business targets by reporting period, brand, target type and record nature.

### Grain

One record per:

`period + brand + target_type + nature`

### Key

`target_fact_sk`

### Foreign Keys

- `calendar_sk`
- `brand_sk`
- `target_type_sk`
- `revenue_hierarchy_sk`

### Measures

- `target_value`

### Descriptive Attributes

- `nature`

---

# Dimensions

## Dim Calendar

Source:

`data/gold/dim_calendar.parquet`

Key:

`calendar_sk`

Main attributes:

- `date`
- `year`
- `month`
- `month_name`
- `month_year`
- `quarter`
- `year_quarter`
- `day_of_month`
- `day_of_week`
- `day_name`

Used by:

- Fact Revenue
- Fact Target

---

## Dim Brand

Source:

`data/gold/dim_brand.parquet`

Key:

`brand_sk`

Main attribute:

- `brand`

Used by:

- Fact Revenue
- Fact Target

---

## Dim User

Source:

`data/gold/dim_user.parquet`

Key:

`user_sk`

Main attributes:

- `user_id`
- `user_name`
- `department`
- `role`
- `active`

Used by:

- Fact Revenue

---

## Dim Opportunity

Source:

`data/gold/dim_opportunity.parquet`

Key:

`opportunity_sk`

Main attributes:

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

Used by:

- Fact Revenue

---

## Dim Opportunity Stage

Source:

`data/gold/dim_opportunity_stage.parquet`

Key:

`opportunity_stage_sk`

Main attributes:

- `stage_id`
- `stage_name`
- `stage_order`
- `is_closed`
- `is_won`

Used by:

- Fact Revenue

---

## Dim Negotiation Type

Source:

`data/gold/dim_negotiation_type.parquet`

Key:

`negotiation_type_sk`

Main attribute:

- `negotiation_type`

Used by:

- Fact Revenue

---

## Dim Target Type

Source:

`data/gold/dim_target_type.parquet`

Key:

`target_type_sk`

Main attribute:

- `target_type`

Used by:

- Fact Target

---

## Dim Revenue Hierarchy

Source:

`data/gold/dim_revenue_hierarchy.parquet`

Key:

`revenue_hierarchy_sk`

Hierarchy attributes:

- `revenue_level_1`
- `revenue_level_2`
- `revenue_level_3`

Used by:

- Fact Revenue
- Fact Target

### Hierarchy Structure

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

---

# Relationships

All relationships follow the dimensional modeling pattern:

`Dimension → Fact`

Expected cardinality:

`1 : Many`

Expected cross-filter direction:

`Single`

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

# Fact-to-Fact Relationships

No direct relationship should exist between:

`Fact Revenue`

and:

`Fact Target`

The two facts are analyzed through shared dimensions.

Shared analytical dimensions include:

- Dim Calendar
- Dim Brand
- Dim Revenue Hierarchy

This prevents ambiguous filtering paths and preserves the star schema.

---

# Dimension-to-Dimension Relationships

Dimensions should not be directly related to one another in the Semantic Model.

Each dimension connects directly to the fact table that requires its analytical context.

---

# Measures

The Semantic Model exposes reusable business measures.

## Base Measures

- Revenue
- Target
- Achievement %

## Year-to-Date

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

The DAX definitions are documented separately in:

- `measures.md`
- `measures_time_intelligence.md`
- `measures_year_over_year.md`
- `measures_variance.md`

---

# Time Intelligence

The Semantic Model uses `Dim Calendar` as the shared time dimension.

Time intelligence calculations are based on:

`Dim Calendar[date]`

The model supports:

- Year
- Quarter
- Month
- Month-Year
- YTD
- Previous Year
- Year-over-Year

No measure contains a hardcoded reporting year.

---

# Formatting

Recommended formats:

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

Currency should follow the Brazilian analytical context:

`R$ #,##0.00`

Percentage measures should use:

`0.00%`

---

# Gold-to-Semantic Mapping

The Semantic Model does not recreate Gold transformations.

It consumes the analytical structures already created in the Gold layer.

The responsibility boundaries are:

    Bronze
        ↓
    Ingestion

    Silver
        ↓
    Standardization
    Technical Quality

    Gold
        ↓
    Business Rules
    Facts
    Dimensions
    Surrogate Keys

    Semantic Model
        ↓
    Relationships
    Measures
    Time Intelligence
    Analytical Hierarchies

    Power BI
        ↓
    Visualization
    Reporting
    Analysis

---

# Implementation Status

## Completed

- Gold dimensions
- Gold facts
- Surrogate keys
- Revenue hierarchy
- Calendar dimension
- Semantic Model design
- Relationship specification
- Base DAX measures
- YTD measures
- Previous Year measures
- Year-over-Year measures
- Variance measures

## Next Implementation Step

Create the Power BI Semantic Model artifact and connect the Gold analytical tables.

The implementation should reproduce the relationship contract documented in this directory without introducing direct fact-to-fact or dimension-to-dimension relationships.

---

# Design Principles

## Star Schema

The model follows a star schema to simplify analytical querying and reduce relationship ambiguity.

## Shared Dimensions

Common analytical dimensions are reused across facts whenever they represent the same business concept.

## Single-Direction Filtering

Relationships use single-direction filtering from dimensions toward facts.

## Reusable Measures

Business calculations are implemented as reusable semantic measures.

## Separation of Concerns

The Semantic Model does not perform source ingestion or technical transformations.

## Analytical Stability

The Semantic Model is designed to remain stable as source volumes and reporting periods evolve.

> The data changes. The architecture remains.

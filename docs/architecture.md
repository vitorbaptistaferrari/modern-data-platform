# Architecture

## Overview

This project implements an end-to-end modern data platform using a Medallion Architecture.

The platform transforms operational revenue data into a trusted analytical model for reporting and decision-making.

The architecture separates technical ingestion, data standardization, business transformation and analytical consumption into clearly defined layers.

The implementation is based on synthetic data and is intentionally independent from any proprietary production environment.

---

## Architecture Layers

The platform is organized into the following layers:

Sources
   │
   ▼
Ingestion
   │
   ▼
Bronze
   │
   ▼
Silver
   │
   ▼
Gold
   │
   ▼
Semantic Model
   │
   ▼
Power BI

Each layer has a specific responsibility.

---

## Sources

The synthetic platform represents three main source domains:

- CRM / Revenue Source
- Target Data
- Geographic Reference

The CRM domain represents operational commercial entities such as customers, opportunities, contracts and quotes.

Target data represents business targets by reporting period, brand and target classification.

Geographic reference data is used to enrich analytical entities with location attributes.

All source data used in this repository is synthetic.

---

## Ingestion Layer

The ingestion layer represents a Copy Job pattern that extracts the required fields from operational sources and moves them into the Bronze layer.

The ingestion strategy used in the initial implementation is:

**Full Load with Overwrite**

This approach was selected as a pragmatic starting point because the synthetic source environment contains historical data and the expected data volume is manageable.

The architecture is not dependent on this strategy permanently.

Future implementations may introduce incremental or hybrid ingestion using mechanisms such as:

- Watermarks
- Change tracking
- Source timestamps
- Incremental extraction criteria

The ingestion layer focuses on moving data reliably into the platform.

It does not apply analytical business rules.

---

# Bronze Layer

The Bronze layer represents the raw ingestion zone.

Its primary responsibilities are:

- Read source datasets
- Validate source availability
- Preserve source information
- Add technical ingestion metadata
- Persist the ingested data
- Provide ingestion execution status

The current implementation uses:

**Full Load with Overwrite**

Each dataset is processed independently so that failures can be identified at dataset level.

Technical metadata includes the ingestion timestamp:

dt_ingestao

The Bronze layer intentionally avoids business transformations.

Examples of logic that do not belong in Bronze:

- Revenue classification
- Business segmentation
- Revenue hierarchy
- KPI calculations
- Analytical aggregations

---

# Silver Layer

The Silver layer transforms Bronze data into standardized and quality-controlled datasets.

Its responsibilities include:

- Structural validation
- Column validation
- Data type standardization
- Text normalization
- Primary key validation
- Foreign key validation
- Deduplication
- Technical processing metadata
- Persistence of standardized datasets

The current Silver implementation contains reusable utilities to reduce duplicated transformation logic across entities.

Common utilities include:

- validate_columns()
- standardize_text_columns()
- remove_invalid_keys()
- deduplicate()
- add_silver_metadata()
- save_silver()

This promotes consistency across Silver transformations.

---

## Silver Entities

The current Silver layer contains the following datasets:

- Customers
- Users
- Record Types
- Opportunity Stages
- Opportunities
- Contracts
- Quotes
- Targets

Each transformation follows the same general pattern:

Read Bronze
    ↓
Validate Structure
    ↓
Standardize
    ↓
Apply Technical Quality Rules
    ↓
Add Silver Metadata
    ↓
Persist Silver

---

## Silver Data Quality

The Silver layer performs technical data quality checks such as:

- Required column validation
- Primary key validation
- Foreign key validation
- Null and empty key detection
- Duplicate detection
- Data type conversion

These checks ensure that the datasets entering the Gold layer have a predictable and consistent structure.

---

## Business Rules Boundary

Business semantics are intentionally kept outside the Silver layer.

For example, the source classification:

Retention

may later become:

Renewal

in the Gold layer.

Likewise, the classification of Expansion opportunities into:

- Cross-Sell
- Up-Sell

belongs to the analytical business rules implemented in Gold.

This separation prevents business logic from being mixed with technical data preparation.

---

# Gold Layer

The Gold layer is the analytical business layer of the platform.

Its responsibilities include:

- Apply business rules
- Create analytical dimensions
- Create analytical fact tables
- Generate surrogate keys
- Establish analytical relationships
- Consolidate business concepts
- Prepare data for semantic modeling

The Gold layer transforms standardized operational entities into an analytical model.

Conceptually:

Silver Entities
      │
      ▼
Business Rules
      │
      ├── Dimensions
      │
      └── Facts
             │
             ▼
       Analytical Model

---

## Analytical Dimensions

The planned Gold model includes dimensions such as:

- Brand
- Calendar
- User
- Negotiation Type
- Opportunity Stage
- Opportunity
- Target Type
- Revenue Hierarchy

Dimensions provide descriptive context for analytical facts.

---

## Analytical Facts

The planned Gold model includes:

- Revenue Fact
- Target Fact

The Revenue Fact represents analytical revenue generated from opportunity-related business rules.

The Target Fact represents business targets by reporting period, brand and target classification.

---

## Revenue Classification

Revenue is classified using business rules rather than hardcoded record identifiers.

The analytical model supports:

- Prospecting
- Renewal
- Expansion
  - Cross-Sell
  - Up-Sell

The exact classification is determined during Gold processing based on opportunity attributes and related business entities.

---

## Surrogate Keys

The Gold layer uses surrogate keys to provide stable analytical identifiers for dimensions and facts.

The public implementation uses deterministic hashing for selected business keys.

This approach allows analytical relationships to remain independent from source-system identifiers.

---

# Semantic Model

The Semantic Model is not considered another Medallion layer.

It is the analytical consumption layer built on top of the Gold model.

Its responsibilities include:

- Define analytical relationships
- Expose business measures
- Provide reusable calculations
- Support time intelligence
- Simplify Power BI consumption

Examples of analytical measures include:

- Revenue
- Target
- Achievement %
- Revenue YTD
- Target YTD
- Revenue LY
- Revenue YoY
- Revenue Variance

---

# Power BI

Power BI is the final visualization and consumption layer.

The reporting layer consumes the Semantic Model rather than directly accessing raw operational sources.

This provides a clear separation between:

Data Engineering
        ↓
Analytical Modeling
        ↓
Semantic Modeling
        ↓
Visualization

The platform is therefore not designed around individual dashboards.

The dashboard is the final consumer of a reusable analytical data product.

---

# Design Principles

## Separation of Responsibilities

Each layer has a clearly defined responsibility.

Bronze → Ingestion
Silver → Standardization & Technical Quality
Gold → Business Rules & Analytical Modeling
Semantic Model → Analytical Consumption
Power BI → Visualization

---

## Data-Volume Agnostic

The architecture does not depend on a fixed number of customers, opportunities or transactions.

New entities and increasing data volumes can be introduced without redesigning the core architecture.

---

## Time-Period Agnostic

The platform is not tied to a specific reporting year.

New reporting periods can be introduced without redesigning the architecture.

---

## Synthetic by Design

All data in this public repository is synthetic.

No proprietary data, credentials, production identifiers or internal company information are included.

The project demonstrates architecture and engineering patterns rather than exposing a production implementation.

---

## Business Rule Isolation

Business rules are implemented in the Gold layer rather than embedded in ingestion or technical standardization processes.

This makes the platform easier to maintain, test and evolve.

---

## Reusability

Common technical transformations are centralized into reusable utilities whenever possible.

This reduces duplicated code and creates consistent processing patterns across datasets.

---

## Data-Driven Architecture

The platform is designed so that the data changes while the underlying architecture remains stable.

> **The data changes. The architecture remains.**

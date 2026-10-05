# Architecture

## Overview

The `modern-data-platform` project demonstrates an end-to-end data engineering and analytics architecture based on the Medallion Architecture.

The platform is organized into two complementary areas:

### Data Engineering

    Synthetic Sources
            |
            v
        Ingestion
            |
            v
         Bronze
            |
            v
         Silver
            |
            v
          Gold

### Analytics

    Gold analytical structures
            |
            v
    Synthetic Analytical Dataset
            |
            v
    Power BI Semantic Model
            |
            v
       Power BI Report

The two areas are conceptually aligned, but the public Power BI implementation does not require a physical runtime connection to the Gold layer.

This design allows the repository to remain functional and reproducible without exposing production data or depending on proprietary infrastructure.

## Architectural Layers

### Source Layer

The public project uses synthetic source data representing common business domains found in a revenue-oriented data platform.

The main source domains include:

- CRM data
- Target data
- Customer and opportunity data
- Supporting reference data

The source data is generated specifically for the public repository.

No production data is used.

## Ingestion Layer

The ingestion layer is responsible for bringing source data into the platform with minimal transformation.

The public implementation uses local synthetic files to reproduce the ingestion pattern.

The conceptual production-oriented pattern represented by the project is compatible with a Copy Job style ingestion process.

The ingestion strategy is currently based on:

- Full Load
- Overwrite processing
- Metadata-driven execution
- Structural validation

The current approach is intentionally simple and reproducible.

Future implementations could introduce incremental or hybrid ingestion strategies using mechanisms such as:

- Watermarks
- Change tracking
- Source modification timestamps
- Incremental processing

## Bronze Layer

The Bronze layer represents the first persisted layer of the Medallion Architecture.

Its primary responsibility is controlled ingestion and preservation of source information.

The Bronze layer performs limited technical processing such as:

- Schema normalization
- Column normalization
- Empty-row handling
- Structural validation
- Ingestion metadata
- Persistence of source datasets

The ingestion timestamp is recorded as technical metadata.

Business rules are intentionally not applied at this stage.

The Bronze layer therefore maintains a close representation of the ingested source structure while providing enough technical standardization for downstream processing.

## Silver Layer

The Silver layer transforms ingested data into standardized and reusable datasets.

Its responsibilities include:

- Data type standardization
- Column standardization
- Data validation
- Duplicate handling
- Key generation
- Metadata enrichment
- Reusable transformation logic
- Consolidation of related source entities

The Silver layer provides cleaner and more consistent datasets for analytical processing.

Business rules that define analytical concepts are kept primarily outside the Silver layer whenever they belong to the business or analytical domain.

## Gold Layer

The Gold layer contains business-oriented analytical structures.

Its responsibilities include:

- Business rule application
- Dimensional modeling
- Analytical dimensions
- Analytical fact tables
- Surrogate keys
- Revenue classification
- Target modeling
- Analytical hierarchies

The public model contains dimensions such as:

- Dim Calendar
- Dim Brand
- Dim User
- Dim Opportunity
- Dim Opportunity Stage
- Dim Negotiation Type
- Dim Target Type
- Dim Revenue Hierarchy

The main analytical facts are:

- Fact Revenue
- Fact Target

The Gold layer is therefore the main analytical output of the Data Engineering pipeline.

## Semantic Model

The Power BI Semantic Model is not considered a fourth Medallion layer.

It is the analytical modeling layer used to organize business concepts for reporting and business intelligence.

The semantic model follows the structures and concepts defined in the Gold layer, including:

- Fact and dimension structures
- Analytical hierarchies
- Shared dimensions
- Surrogate-key-based relationships
- Revenue and target concepts
- Time intelligence

### Public Implementation

For public reproducibility, the Power BI project uses a controlled synthetic analytical dataset embedded directly in the semantic model.

This is an intentional design decision.

The public project does not establish a direct runtime connection between Power BI and the Gold layer.

Instead, the synthetic Power BI dataset reproduces the relevant analytical structures defined by Gold.

This provides a practical balance between:

- Architectural fidelity
- Public reproducibility
- Data privacy
- Functional Power BI analysis
- Independence from production infrastructure

The conceptual relationship can therefore be represented as:

    Gold
      |
      | analytical design
      v
    Synthetic Analytical Dataset
      |
      v
    Power BI Semantic Model
      |
      v
    Power BI Report

The arrows above represent architectural alignment rather than a required physical data connection in the public implementation.

## Power BI Layer

The Power BI layer provides reporting and business intelligence capabilities over the semantic model.

The semantic model includes reusable DAX measures for:

- Revenue
- Target
- Achievement
- Year-to-date analysis
- Previous-year analysis
- Year-over-year variation
- Revenue variance
- Target variance

The Power BI project is maintained in `.pbip` format to support version control and transparent project structure.

## Data Flow

The complete conceptual flow is:

    Synthetic Sources
            |
            v
       Ingestion
            |
            v
         Bronze
            |
            v
         Silver
            |
            v
          Gold
            |
            | analytical structures
            v
    Synthetic Analytical Dataset
            |
            v
    Power BI Semantic Model
            |
            v
       Power BI Report

The first part represents the Data Engineering pipeline.

The second part represents the public analytical implementation.

## Data Engineering Principles

The architecture follows several core principles.

### Separation of Responsibilities

Each layer has a defined responsibility.

- Bronze focuses on ingestion.
- Silver focuses on standardization and reusable transformation.
- Gold focuses on business-oriented analytical structures.
- Semantic Model focuses on analytical consumption.
- Power BI focuses on visualization and reporting.

### Reusability

Transformation and analytical logic should be implemented through reusable components whenever possible.

### Data-Volume Agnostic Design

The public implementation is designed so that the architecture does not depend on a specific production data volume.

The synthetic dataset is intentionally smaller than a production environment while preserving the relevant structural patterns.

### Business Rule Isolation

Business rules should be kept explicit and separated from low-level ingestion logic.

This makes the platform easier to maintain and adapt when business definitions change.

### Data-Driven Architecture

The platform should rely on metadata, configuration and reusable processing patterns instead of excessive hardcoding.

### Reproducibility

The public repository must remain executable and understandable without access to proprietary infrastructure.

Synthetic data is therefore used wherever production data would otherwise be required.

## Production vs Public Implementation

The architecture intentionally distinguishes between the conceptual production pattern and the public portfolio implementation.

### Conceptual Architecture

A production implementation could follow:

    Source Systems
          |
          v
    Fabric Ingestion
          |
          v
        Bronze
          |
          v
        Silver
          |
          v
         Gold
          |
          v
    Semantic Model
          |
          v
       Power BI

### Public Repository

The public implementation uses:

    Synthetic Source Files
          |
          v
       Bronze
          |
          v
       Silver
          |
          v
        Gold

and separately:

    Synthetic Analytical Dataset
          |
          v
    Power BI Semantic Model
          |
          v
       Power BI Report

The public implementation intentionally avoids requiring external production infrastructure while preserving the same analytical concepts.

## Design Principle

A central principle of the project is:

> The data changes. The architecture remains.

Production data may change in structure, volume or business context.

The objective of the architecture is to provide reusable patterns that remain applicable as the underlying data evolves.

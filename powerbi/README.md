# Power BI Semantic Model

This directory contains the Power BI implementation of the analytical semantic model for the Modern Data Platform project.

The semantic model represents the analytical layer of an end-to-end data engineering solution based on Medallion Architecture.

## Purpose

The Power BI implementation demonstrates how the analytical outputs of the data platform are structured for business intelligence and analytics.

The model follows a dimensional architecture with separate fact and dimension tables, shared dimensions, explicit relationships and reusable DAX measures.

The public implementation is designed for portfolio and technical demonstration purposes.

## Data Privacy

No proprietary, production or confidential data is included in this repository.

The Power BI model uses synthetic data created exclusively to demonstrate the analytical structure, dimensional relationships and business calculations of the project.

The public implementation therefore represents the analytical architecture and business concepts of the solution without exposing production information.

## Power BI Project

The Power BI project is stored using the Power BI Project (`.pbip`) format.

Main project:

- `ModernDataPlatform.pbip`

Associated project directories:

- `ModernDataPlatform.Report/`
- `ModernDataPlatform.SemanticModel/`

Using the Power BI Project format allows the report and semantic model artifacts to be versioned together with the rest of the repository.

## Semantic Model

The model follows a star-schema-oriented structure.

### Fact tables

- `Fact Revenue`
- `Fact Target`

### Dimension tables

- `Dim Calendar`
- `Dim Brand`
- `Dim User`
- `Dim Opportunity`
- `Dim Opportunity Stage`
- `Dim Negotiation Type`
- `Dim Target Type`
- `Dim Revenue Hierarchy`

### Measures

The model contains reusable analytical measures for revenue, targets, achievement, time intelligence and variance analysis.

Core measures include:

- `Revenue`
- `Target`
- `Achievement %`
- `Revenue YTD`
- `Target YTD`
- `Revenue LY`
- `Revenue LY YTD`
- `Revenue YoY`
- `Revenue YoY YTD`
- `Revenue Variance`
- `Revenue Target Variance YTD`
- `Achievement YTD`

## Relationships

The semantic model uses one-to-many relationships from dimensions to fact tables.

Fact Revenue is related to:

- Dim Calendar
- Dim Brand
- Dim User
- Dim Opportunity
- Dim Opportunity Stage
- Dim Negotiation Type
- Dim Revenue Hierarchy

Fact Target is related to:

- Dim Calendar
- Dim Brand
- Dim Target Type
- Dim Revenue Hierarchy

The model avoids direct fact-to-fact relationships and unnecessary dimension-to-dimension relationships.

## Revenue Hierarchy

The revenue hierarchy is represented as:

    Revenue
    ├── Prospecting
    │   └── Prospecting
    ├── Renewal
    │   └── Renewal
    └── Expansion
        ├── Expansion
        ├── Cross-Sell
        └── Up-Sell

This hierarchy allows revenue analysis at different business levels while maintaining a consistent analytical structure.

## Time Intelligence

Time intelligence is based on `Dim Calendar`.

The model includes:

- Year-to-date revenue
- Year-to-date target
- Previous-year revenue
- Previous-year year-to-date revenue
- Year-over-year variation
- Year-to-date year-over-year variation

The calendar is treated as a shared analytical dimension rather than being duplicated across fact tables.

## Design Principles

The semantic model follows these principles:

1. Separate facts and dimensions.
2. Reuse shared dimensions across analytical processes.
3. Keep business measures reusable and independent from individual report visuals.
4. Avoid direct relationships between fact tables.
5. Centralize time intelligence in a shared calendar dimension.
6. Keep production and proprietary data outside the public repository.
7. Use synthetic data exclusively for public demonstration.
8. Keep the semantic model aligned with the Gold analytical layer.

## Public Portfolio Scope

This repository is a public technical representation of the solution architecture.

It focuses on demonstrating:

- Data Engineering architecture
- Medallion Architecture
- Dimensional modeling
- Analytical data structures
- Microsoft Fabric-oriented design
- Power BI Semantic Modeling
- DAX measures
- Data quality concepts
- Business-rule isolation
- Data and analytics integration

Production-specific implementation details, proprietary identifiers, confidential data and internal infrastructure are intentionally excluded.

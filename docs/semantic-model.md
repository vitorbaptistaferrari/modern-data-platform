# Power BI Semantic Model

## Purpose

The Power BI Semantic Model represents the analytical layer of the `modern-data-platform` project.

It provides a dimensional structure for revenue and target analysis, including shared dimensions, analytical fact tables, business hierarchies and reusable DAX measures.

The model is designed according to the analytical structures defined in the Gold layer.

The semantic model is not considered a fourth Medallion layer. It is the analytical modeling layer used to organize data for reporting and business intelligence.

## Public Reproducibility

The public repository does not connect the Power BI project directly to production systems, proprietary databases or internal data platforms.

Instead, the Power BI project uses a controlled synthetic dataset embedded directly in the semantic model.

The synthetic dataset reproduces the analytical structures and business concepts defined by the Gold layer.

This approach provides:

- Reproducibility
- Functional Power BI analysis
- No dependency on external infrastructure
- No exposure of proprietary data
- Clear separation between production architecture and public demonstration

The relationship between the Data Engineering and Analytics components can therefore be understood as:

    Synthetic Sources
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

The Gold layer and the Power BI Semantic Model are architecturally aligned, but the public Power BI project does not require a physical runtime connection to the Gold layer.

## Model Architecture

The semantic model follows a star-schema design.

The model contains two analytical fact tables supported by shared and role-specific dimensions.

### Fact Tables

#### Fact Revenue

`Fact Revenue` represents analytical revenue occurrences.

The current public implementation uses one analytical revenue occurrence per opportunity that meets the revenue criteria.

Main analytical attributes include:

- Revenue
- Opportunity
- User
- Brand
- Calendar
- Opportunity Stage
- Negotiation Type
- Revenue Hierarchy

The fact table contains foreign keys to the corresponding dimensions and the analytical revenue value.

#### Fact Target

`Fact Target` represents analytical target values.

The grain of the table is defined by:

- Period
- Brand
- Analytical Target Type
- Target Nature

The table contains the target value associated with the corresponding analytical context.

## Dimensions

The semantic model contains the following dimensions:

### Dim Calendar

Provides the time dimension used by the analytical model.

Main attributes include:

- Date
- Year
- Month
- Month Name
- Month-Year
- Quarter

The calendar dimension is used as the primary time context for time-intelligence calculations.

### Dim Brand

Represents the brands used in revenue and target analysis.

### Dim User

Represents the users associated with analytical revenue occurrences.

### Dim Opportunity

Represents the opportunity-level business entity associated with revenue.

### Dim Opportunity Stage

Represents the lifecycle stage of an opportunity.

### Dim Negotiation Type

Represents the broader analytical negotiation categories:

- Prospecting
- Renewal
- Expansion

### Dim Target Type

Represents the analytical categories used for target allocation.

### Dim Revenue Hierarchy

Provides a more detailed analytical hierarchy for revenue.

The public model includes:

- Prospecting
- Renewal
- Expansion
- Cross-Sell
- Up-Sell

This allows analysis at both the broader negotiation level and the more detailed revenue hierarchy level.

## Relationships

The semantic model follows a dimensional relationship pattern.

Dimensions provide filtering context for the fact tables.

The intended relationship structure is:

    Dim Calendar --------\
    Dim Brand ------------\
    Dim User --------------\
    Dim Opportunity --------> Fact Revenue
    Dim Opportunity Stage --/
    Dim Negotiation Type --/
    Dim Revenue Hierarchy -/

    Dim Calendar --------\
    Dim Brand ------------\
    Dim Target Type --------> Fact Target
    Dim Revenue Hierarchy -/

The model does not use direct fact-to-fact relationships.

Shared dimensions allow revenue and target analysis to be performed within a consistent analytical context.

## Revenue Business Logic

The analytical revenue structure is based on three primary negotiation categories:

- Prospecting
- Renewal
- Expansion

Expansion can be further classified into:

- Expansion
- Cross-Sell
- Up-Sell

Revenue is associated with opportunities that meet the public implementation's revenue criteria.

The public implementation intentionally uses synthetic business rules and values to demonstrate the analytical model without reproducing proprietary production logic.

## Target Modeling

Targets are modeled independently from revenue.

This separation allows target values to be analyzed by:

- Period
- Brand
- Target Type
- Revenue Hierarchy
- Target Nature

The independent target fact table avoids direct fact-to-fact relationships and preserves the dimensional modeling approach.

## DAX Measures

The semantic model contains reusable measures for the main analytical calculations.

Current measures include:

- Revenue
- Target
- Achievement %
- Revenue YTD
- Target YTD
- Revenue LY
- Revenue LY YTD
- Revenue YoY
- Revenue YoY YTD
- Revenue Variance
- Revenue Target Variance YTD
- Achievement YTD

### Revenue

Calculates the total analytical revenue within the current filter context.

### Target

Calculates the total target value within the current filter context.

### Achievement %

Calculates revenue achievement relative to the target.

### Revenue YTD

Calculates cumulative revenue from the beginning of the year through the current date context.

### Target YTD

Calculates cumulative target from the beginning of the year through the current date context.

### Revenue LY

Calculates revenue for the corresponding period in the previous year.

### Revenue LY YTD

Calculates year-to-date revenue for the corresponding period in the previous year.

### Revenue YoY

Calculates the year-over-year variation between current revenue and previous-year revenue.

### Revenue YoY YTD

Calculates the year-over-year variation between current YTD revenue and previous-year YTD revenue.

### Revenue Variance

Calculates the difference between revenue and target.

### Revenue Target Variance YTD

Calculates the difference between cumulative revenue and cumulative target.

### Achievement YTD

Calculates cumulative revenue achievement against cumulative target.

## Time Intelligence

Time intelligence calculations are based on `Dim Calendar`.

The model uses the calendar dimension as the primary date context for:

- YTD calculations
- Previous-year calculations
- Year-over-year analysis

The semantic model therefore separates time-intelligence logic from transactional date attributes and centralizes analytical time context in the calendar dimension.

## Gold Layer Alignment

The semantic model follows the analytical concepts established in the Gold layer.

This includes:

- Dimensional modeling
- Revenue and target facts
- Shared analytical dimensions
- Surrogate-key-based relationships
- Revenue hierarchy
- Business-oriented analytical structures
- Time-based analysis

The purpose of this alignment is to ensure that the analytical model represents the same conceptual structures as the engineered data platform.

The public Power BI implementation does not claim to reproduce a production connection between Gold and Power BI.

Instead, it demonstrates how the analytical structures produced by the data engineering layer can be represented and consumed by a BI semantic model.

## Design Principles

The semantic model follows these principles:

- Star-schema dimensional modeling
- Shared dimensions
- Explicit business concepts
- Reusable DAX measures
- Centralized calendar dimension
- Separation of facts and dimensions
- No fact-to-fact relationships
- Separation between data engineering and presentation
- Reproducibility
- Synthetic data for public demonstration
- No dependency on proprietary infrastructure

## Public Scope

This semantic model is part of a public portfolio project.

Production data, proprietary business information, internal identifiers, credentials and company-specific infrastructure are intentionally excluded.

The objective is to demonstrate the technical reasoning behind a modern analytical architecture while keeping the project functional, reproducible and safe to publish.

The model therefore prioritizes:

- Architectural clarity
- Analytical consistency
- Reproducibility
- Technical transparency
- Public usability

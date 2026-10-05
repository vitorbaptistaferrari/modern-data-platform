# Data Model

## Overview

The data model represents a synthetic revenue analytics platform designed to demonstrate data engineering and analytical modeling concepts using a Medallion Architecture.

The model is organized into two main source domains:

- CRM Data
- Target Data

The source entities are transformed through the Bronze, Silver and Gold layers before being consumed by the analytical model.

The public implementation uses synthetic data and does not expose production structures, identifiers or proprietary business information.

---

## Source Domains

### CRM Data

The CRM domain represents commercial and operational entities required to support revenue analysis.

The main entities are:

- Customer
- Opportunity
- Contract
- Quote
- User
- Record Type
- Opportunity Stage

These entities represent a simplified CRM environment and are used as the conceptual foundation for the revenue analytical model.

### Target Data

The Target domain represents commercial targets used for performance analysis.

Target data contains information related to:

- Period
- Brand
- Target type
- Target nature
- Target value

Target data is transformed independently and later integrated into the Gold analytical layer.

---

# CRM Entities

## Customer

Represents customers associated with commercial opportunities.

Representative attributes include:

- Customer identifier
- Customer name
- City
- State

The geographic attributes are maintained directly within the synthetic CRM dataset and do not depend on an external geographic reference table.

---

## Opportunity

Represents commercial opportunities associated with customers and users.

Representative attributes include:

- Opportunity identifier
- Customer identifier
- Opportunity type
- Brand
- Opportunity stage
- Opportunity amount
- Opportunity date
- Close date

Opportunities represent the main business entity used to derive analytical revenue.

The Gold layer applies business rules based on opportunity type, stage and related commercial information to determine analytical revenue.

---

## Contract

Represents contractual information associated with commercial opportunities.

Representative attributes include:

- Contract identifier
- Opportunity identifier
- Contract status
- Contract value

Contract information supports revenue calculations for retention scenarios.

---

## Quote

Represents commercial quotations associated with opportunities.

Representative attributes include:

- Quote identifier
- Opportunity identifier
- Quote status
- Quote value

Quote information supports revenue calculations for expansion scenarios.

---

## User

Represents commercial users responsible for opportunities.

Representative attributes include:

- User identifier
- User name

Users are represented as a Gold dimension and are associated with analytical revenue through the opportunity structure.

---

## Opportunity Stage

Represents the lifecycle stage of an opportunity.

Representative attributes include:

- Stage identifier
- Stage name
- Stage order

The opportunity stage is used to determine whether an opportunity qualifies for analytical revenue.

---

## Record Type

Represents the classification of CRM opportunities.

Representative attributes include:

- Record type identifier
- Record type name

Record types provide structural classification information used during the transformation process.

---

# Target Data

## Target

Target data represents commercial performance goals.

Representative attributes include:

- Target period
- Brand
- Target type
- Target nature
- Target value

The Gold layer transforms these attributes into the analytical target structure.

---

# Gold Analytical Model

The Gold layer reorganizes the standardized source data into a dimensional analytical model.

The main analytical structures are:

### Dimensions

- Dim Calendar
- Dim Brand
- Dim User
- Dim Opportunity
- Dim Opportunity Stage
- Dim Negotiation Type
- Dim Target Type
- Dim Revenue Hierarchy

### Facts

- Fact Revenue
- Fact Target

---

## Fact Revenue

The `Fact Revenue` table represents analytical revenue events.

Its grain is defined as:

> One analytical revenue occurrence per qualifying opportunity.

Revenue values are derived according to the applicable business rules.

The revenue logic considers different commercial scenarios, including:

- Prospecting
- Renewal
- Expansion

Expansion can additionally be classified into:

- Cross-Sell
- Up-Sell

The fact table contains foreign keys to the relevant analytical dimensions.

---

## Fact Target

The `Fact Target` table represents analytical commercial targets.

Its grain is defined as:

> One target record per period, brand, analytical target type and target nature.

The table contains foreign keys to the relevant analytical dimensions and stores the target value used for performance analysis.

---

# Revenue Hierarchy

The analytical model represents revenue using a hierarchical commercial structure.

The main categories are:

- Prospecting
- Renewal
- Expansion
- Cross-Sell
- Up-Sell

Cross-Sell and Up-Sell are represented as analytical classifications within the Expansion context.

This hierarchy allows revenue to be analyzed at different commercial levels without exposing proprietary production classifications.

---

# Relationships

The analytical model follows a dimensional modeling approach.

Fact tables contain foreign keys to shared dimensions.

The main relationships include:

- Fact Revenue → Dim Calendar
- Fact Revenue → Dim Brand
- Fact Revenue → Dim User
- Fact Revenue → Dim Opportunity
- Fact Revenue → Dim Opportunity Stage
- Fact Revenue → Dim Negotiation Type
- Fact Revenue → Dim Revenue Hierarchy
- Fact Target → Dim Calendar
- Fact Target → Dim Brand
- Fact Target → Dim Target Type
- Fact Target → Dim Revenue Hierarchy

The model does not establish direct fact-to-fact relationships.

Shared dimensions are used to provide consistent analytical filtering across revenue and target information.

---

# Surrogate Keys

The Gold layer uses surrogate keys to identify analytical entities.

Keys are generated independently from the source identifiers and provide stable analytical references within the public model.

This approach separates source-system identifiers from the analytical model and supports dimensional modeling practices.

---

# Business Rules

Business rules are implemented in the Gold layer rather than in the Bronze or Silver layers.

Examples include:

- Determining which opportunities qualify for revenue
- Classifying revenue according to negotiation type
- Applying revenue hierarchy classifications
- Selecting the appropriate commercial value for each revenue scenario
- Structuring target information for analytical consumption

The Silver layer remains focused on standardization, validation and technical data quality.

---

# Analytical Model

The Gold structures are consumed by the Power BI Semantic Model.

The semantic model provides:

- Revenue analysis
- Target analysis
- Achievement analysis
- Variance analysis
- Time intelligence
- Year-over-year analysis
- Commercial hierarchy analysis

The analytical model is implemented using synthetic data to preserve public reproducibility.

---

# Public Scope

The model is intentionally simplified and synthetic.

It is designed to demonstrate:

- Medallion Architecture
- Data transformation
- Dimensional modeling
- Surrogate keys
- Business-rule implementation
- Revenue and target modeling
- Semantic modeling
- Analytical consumption

Production data, proprietary identifiers, internal system structures and confidential business rules are intentionally excluded from the repository.

The implementation demonstrates the architecture and engineering approach rather than reproducing a production environment.

---

# Design Principle

> The data changes. The architecture remains.

The public model is therefore designed around reusable engineering and analytical patterns rather than dependencies on a specific production dataset.

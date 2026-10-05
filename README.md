# Modern Data Platform

End-to-end data engineering project designed to demonstrate a modern revenue analytics platform using Medallion Architecture, synthetic data and a Power BI Semantic Model.

The project brings together data ingestion, transformation, dimensional modeling, analytical business rules and BI consumption in a single end-to-end architecture.

> **The data changes. The architecture remains.**

---

## Project Overview

The Modern Data Platform is a public portfolio project that simulates the architecture of a revenue analytics platform.

The project was designed around a common data engineering challenge:

> Transform operational commercial data into reliable, standardized and analytics-ready structures that can support revenue, target, performance and time-based analysis.

The implementation uses synthetic data and public-facing business rules while preserving the architectural concepts found in real-world data platforms.

The project demonstrates the complete analytical path:

    Synthetic Sources
          ↓
      Ingestion
          ↓
       Bronze
          ↓
       Silver
          ↓
        Gold
          ↓
    Analytical Model
          ↓
    Power BI Semantic Model
          ↓
        Analytics

---

## Architecture

The data engineering architecture follows the Medallion Architecture pattern.

    ┌───────────────────────────────┐
    │       Synthetic Sources       │
    │                               │
    │  CRM Data      Target Data    │
    └───────────────┬───────────────┘
                    │
                    ▼
    ┌───────────────────────────────┐
    │           Bronze              │
    │                               │
    │  Raw ingestion                │
    │  Technical metadata           │
    │  Structural validation        │
    └───────────────┬───────────────┘
                    │
                    ▼
    ┌───────────────────────────────┐
    │            Silver             │
    │                               │
    │  Standardization              │
    │  Data validation              │
    │  Deduplication                │
    │  Technical metadata           │
    └───────────────┬───────────────┘
                    │
                    ▼
    ┌───────────────────────────────┐
    │             Gold              │
    │                               │
    │  Business rules               │
    │  Dimensional modeling         │
    │  Surrogate keys               │
    │  Revenue and target facts     │
    └───────────────┬───────────────┘
                    │
                    │
                    ▼
    ┌───────────────────────────────┐
    │      Analytical Dataset       │
    │                               │
    │  Controlled synthetic data    │
    └───────────────┬───────────────┘
                    │
                    ▼
    ┌───────────────────────────────┐
    │    Power BI Semantic Model    │
    │                               │
    │  Star schema                  │
    │  DAX measures                 │
    │  Time intelligence            │
    │  Variance analysis             │
    └───────────────┬───────────────┘
                    │
                    ▼
    ┌───────────────────────────────┐
    │           Analytics           │
    │                               │
    │  Revenue                      │
    │  Targets                      │
    │  Achievement                  │
    │  YoY analysis                 │
    └───────────────────────────────┘

The connection between the Gold layer and the analytical dataset represents architectural alignment. The public Power BI implementation uses a controlled synthetic dataset embedded in the semantic model rather than connecting directly to production infrastructure.

---

## Data Engineering Layers

### Bronze

The Bronze layer is responsible for ingestion and technical preservation of source data.

Main responsibilities include:

- Source ingestion
- Structural validation
- Technical metadata
- Raw data preservation
- Full-load processing

Business rules are intentionally not applied at this stage.

---

### Silver

The Silver layer transforms Bronze datasets into standardized and validated structures.

Main responsibilities include:

- Data type standardization
- Text normalization
- Primary key validation
- Foreign key field validation
- Deduplication
- Technical data quality rules
- Silver metadata

Reusable transformation utilities are used where appropriate to keep the transformation logic consistent across datasets.

---

### Gold

The Gold layer converts standardized data into analytics-ready structures.

Main responsibilities include:

- Business rules
- Dimensional modeling
- Surrogate key generation
- Revenue classification
- Target modeling
- Analytical hierarchies
- Fact and dimension construction

The main analytical structures are:

**Dimensions**

- Dim Calendar
- Dim Brand
- Dim User
- Dim Opportunity
- Dim Opportunity Stage
- Dim Negotiation Type
- Dim Target Type
- Dim Revenue Hierarchy

**Facts**

- Fact Revenue
- Fact Target

---

## Revenue Analytics

The analytical model represents commercial revenue through different business scenarios.

The revenue hierarchy includes:

- Prospecting
- Renewal
- Expansion
- Cross-Sell
- Up-Sell

Cross-Sell and Up-Sell are represented as analytical classifications within the Expansion context.

The revenue fact is designed around the following grain:

> One analytical revenue occurrence per qualifying opportunity.

The Gold layer applies the business rules required to determine the analytical revenue value and classification.

---

## Target Analytics

The target model represents commercial performance goals.

The `Fact Target` table uses the following analytical grain:

> One target record per period, brand, analytical target type and target nature.

This structure allows revenue and target information to be analyzed through shared dimensions.

---

# Power BI Semantic Model

The project includes a Power BI Semantic Model based on a dimensional architecture.

The semantic model contains:

- Revenue fact
- Target fact
- Shared dimensions
- Revenue hierarchy
- Time dimension
- Analytical DAX measures

The model follows a star-schema approach, with fact tables connected to shared analytical dimensions.

The semantic model is not considered an additional Medallion layer. It represents the analytical consumption layer built on top of the Gold structures.

---

## Analytical Measures

The semantic model includes measures for:

### Core Metrics

- Revenue
- Target
- Achievement %

### Year-to-Date

- Revenue YTD
- Target YTD
- Achievement YTD

### Previous Year

- Revenue LY
- Revenue LY YTD

### Year-over-Year

- Revenue YoY
- Revenue YoY YTD

### Variance

- Revenue Variance
- Revenue Target Variance YTD

These measures support revenue performance, target achievement, variance and time-based analysis.

---

## Time Intelligence

The analytical model includes reusable time-intelligence calculations for:

- Year-to-date analysis
- Previous-year comparison
- Year-over-year variation

The calendar dimension provides the date structure required by the analytical model.

---

## Data Model

The Gold layer and Power BI Semantic Model share the same analytical concepts.

The main dimensional relationships include:

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

Direct fact-to-fact relationships are intentionally avoided.

Shared dimensions provide consistent analytical filtering across revenue and target data.

---

## Technology Stack

### Data Engineering

- Python
- Pandas
- PyArrow
- Parquet
- Medallion Architecture
- Dimensional Modeling

### Analytics

- Power BI
- DAX
- Power BI Semantic Model
- PBIP

### Data Modeling

- Fact tables
- Dimension tables
- Surrogate keys
- Star schema
- Business-rule transformations

---

## Repository Structure

    modern-data-platform/
    │
    ├── README.md
    │
    ├── docs/
    │   ├── architecture.md
    │   ├── data-model.md
    │   └── semantic-model.md
    │
    ├── powerbi/
    │   ├── ModernDataPlatform.pbip
    │   ├── ModernDataPlatform.Report/
    │   ├── ModernDataPlatform.SemanticModel/
    │   ├── README.md
    │   ├── measures.md
    │   ├── measures_time_intelligence.md
    │   ├── measures_variance.md
    │   └── measures_year_over_year.md
    │
    └── src/
        ├── generators/
        │   └── generate_data.py
        │
        ├── ingestion/
        │   └── ingest_bronze.py
        │
        └── transformations/
            ├── gold_dim_brand.py
            ├── gold_dim_calendar.py
            ├── gold_dim_negotiation_type.py
            ├── gold_dim_opportunity.py
            ├── gold_dim_opportunity_stage.py
            ├── gold_dim_revenue_hierarchy.py
            ├── gold_dim_target_type.py
            ├── gold_dim_user.py
            ├── gold_fact_revenue.py
            ├── gold_fact_target.py
            ├── silver_contracts.py
            ├── silver_customers.py
            ├── silver_opportunities.py
            ├── silver_opportunity_stages.py
            ├── silver_quotes.py
            ├── silver_record_types.py
            ├── silver_targets.py
            ├── silver_users.py
            └── silver_utils.py

---

## Engineering Decisions

The project intentionally separates technical transformation from business logic.

### Bronze

Focused on ingestion and technical preservation.

### Silver

Focused on standardization, validation and reusable transformation logic.

### Gold

Focused on business rules and analytical modeling.

### Semantic Model

Focused on analytical consumption and reusable measures.

This separation improves maintainability and makes the architecture easier to evolve as source structures or analytical requirements change.

---

## Data Quality

Data quality is addressed throughout the transformation pipeline.

Examples include:

- Required column validation
- Primary key validation
- Foreign key field validation
- Duplicate detection
- Data type validation
- Empty dataset validation
- Analytical grain validation
- Positive-value validation where required

The objective is to prevent invalid structures from propagating into analytical layers.

---

## Public and Synthetic Scope

This repository is intentionally designed for public demonstration.

All datasets used for the public implementation are synthetic.

The project does not expose:

- Production data
- Production identifiers
- Credentials
- Internal URLs
- Proprietary source structures
- Confidential business information

The objective is to demonstrate engineering architecture, transformation patterns, analytical modeling and BI implementation without reproducing a production environment.

---

## Documentation

Additional technical documentation is available in the repository:

- [Architecture](docs/architecture.md)
- [Data Model](docs/data-model.md)
- [Semantic Model](docs/semantic-model.md)
- [Power BI Documentation](powerbi/README.md)
- [DAX Measures](powerbi/measures.md)
- [Time Intelligence Measures](powerbi/measures_time_intelligence.md)
- [Variance Measures](powerbi/measures_variance.md)
- [Year-over-Year Measures](powerbi/measures_year_over_year.md)

---

## Engineering Principles

This project follows a few core principles:

- Separate technical transformation from business logic
- Keep analytical structures independent from source-system identifiers
- Use dimensional modeling for analytical consumption
- Validate data before it reaches the analytical layer
- Prefer reusable transformation patterns
- Keep public implementations reproducible
- Protect proprietary information
- Design the architecture to evolve independently from the source data

> **The data changes. The architecture remains.**

---

## Project Status

The current implementation includes:

- Synthetic data generation
- Bronze ingestion
- Silver transformations
- Gold dimensions
- Gold fact tables
- Revenue business rules
- Target modeling
- Power BI Semantic Model
- DAX analytical measures
- Time intelligence
- Variance analysis
- Year-over-year analysis
- Technical documentation

The project is continuously evolving as new engineering and analytical capabilities are added.

---

## Author

**Vitor Baptista Ferrari**

Data Engineer | Data & Analytics | Microsoft Fabric | Power BI | Python | SQL

São Paulo, Brazil

[LinkedIn](https://www.linkedin.com/in/vitor-baptista-ferrari-3310534a/)

# Power BI Semantic Model

This directory contains the Power BI Semantic Model for the `modern-data-platform` project.

The semantic model represents the analytical layer of the project and is designed according to the dimensional structures and business concepts defined in the Gold layer.

## Purpose

The model provides a structured analytical foundation for revenue and target analysis, including:

- Revenue analysis
- Target analysis
- Achievement analysis
- Year-to-date calculations
- Year-over-year comparisons
- Revenue variance analysis
- Revenue hierarchy analysis

The model is implemented using a dimensional architecture with shared dimensions and analytical fact tables.

## Public Reproducibility

The Power BI project uses a controlled synthetic dataset embedded directly in the semantic model.

This approach is intentional.

The public repository does not connect to production systems, proprietary databases or internal company infrastructure. Instead, the Power BI model uses synthetic analytical data designed to reproduce the relevant business structures and demonstrate the analytical capabilities of the project.

The synthetic dataset is aligned with the concepts and structures defined in the Gold layer, allowing the semantic model to remain functionally representative without exposing production data.

This makes the project reproducible and self-contained for portfolio demonstration purposes.

## Model Architecture

The semantic model follows a star-schema design.

### Fact Tables

#### Fact Revenue

Contains analytical revenue occurrences.

The table is designed around the following concepts:

- Revenue occurrence
- Opportunity
- User
- Brand
- Calendar
- Opportunity stage
- Negotiation type
- Revenue hierarchy

#### Fact Target

Contains analytical target values.

The table is designed around:

- Period
- Brand
- Target type
- Revenue hierarchy
- Target nature
- Target value

## Dimensions

The model contains the following dimensions:

- Dim Calendar
- Dim Brand
- Dim User
- Dim Opportunity
- Dim Opportunity Stage
- Dim Negotiation Type
- Dim Target Type
- Dim Revenue Hierarchy

Shared dimensions such as Calendar, Brand and Revenue Hierarchy support analysis across the fact tables.

## Relationships

The model follows a dimensional relationship pattern:

- Dimensions → Fact Revenue
- Dimensions → Fact Target

There are no direct fact-to-fact relationships.

The model is designed to keep analytical filtering primarily driven by dimensions.

## Revenue Hierarchy

Revenue is organized into analytical categories representing the business concepts defined in the Gold layer.

The hierarchy includes:

- Prospecting
- Renewal
- Expansion
- Cross-Sell
- Up-Sell

This structure allows revenue to be analyzed both at the broader negotiation level and at more specific revenue categories.

## DAX Measures

The semantic model includes reusable DAX measures for analytical calculations.

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

The measures are documented separately in the `powerbi/` directory.

## Time Intelligence

Time intelligence is based on the dedicated `Dim Calendar` table.

The model includes calculations for:

- Year-to-date revenue
- Year-to-date targets
- Previous-year revenue
- Previous-year year-to-date revenue
- Year-over-year variation

The calendar dimension provides the primary time context for analytical calculations.

## Project Structure

The Power BI project is stored using the Power BI Project (`.pbip`) format.

The directory contains:

- Power BI report definition
- Semantic model definition
- Model tables
- Relationships
- Measures
- Model metadata

The project files are versioned together with the data engineering code and documentation.

## Design Principles

The semantic model follows these principles:

- Dimensional modeling
- Reusable measures
- Shared dimensions
- Explicit business concepts
- Separation between analytical modeling and presentation
- Reproducibility
- Synthetic data for public demonstration
- No dependency on production data

## Public Scope

This repository is a public portfolio project.

Production data, proprietary business information, credentials, internal identifiers and company-specific infrastructure are intentionally excluded.

The objective is to demonstrate the engineering and analytical architecture, implementation patterns and technical reasoning involved in building a modern data platform.

The project therefore prioritizes reproducibility and architectural transparency over reproducing any specific production environment.

# Data Model

## Overview

The project uses synthetic data to simulate an operational revenue environment.

The data model is designed to represent the main entities required to support revenue analytics while remaining independent from any proprietary or production dataset.

The model is intentionally data-volume and time-period agnostic.

New customers, opportunities, transactions and reporting periods can be introduced without changing the underlying architecture.

---

## Source Domains

The synthetic environment is composed of two main source domains:

### CRM

The CRM source represents operational commercial data.

Main entities:

- Customer
- Opportunity
- Contract
- Quote
- User
- Record Type
- Opportunity Stage

Customer records contain location attributes such as city and state as part of the synthetic CRM dataset.

### Target Data

Target data represents business targets by period, brand and revenue classification.

---

## Entity Relationships

The main conceptual relationships are:

    Customer
       |
       +--< Opportunity
                 |
                 +--< Contract
                 |
                 +--< Quote

    User
       |
       +--< Opportunity

    Opportunity Stage
       |
       +--< Opportunity

    Record Type
       |
       +--< Opportunity

The relationships above represent the conceptual structure of the synthetic operational data.

---

## Customer

The Customer entity represents organizations participating in the commercial process.

Representative attributes include:

- Customer identifier
- Customer name
- City
- State
- Customer segment

The geographic attributes are generated as part of the synthetic customer dataset.

No external geographic reference dataset is required by the current public implementation.

---

## Opportunity

The Opportunity entity represents commercial opportunities associated with customers.

Representative attributes include:

- Opportunity identifier
- Customer identifier
- Opportunity name
- Opportunity type
- Brand
- Opportunity stage
- Opportunity amount
- Opportunity date
- Close date

Opportunities provide the central business entity from which revenue-oriented analytical structures are derived.

---

## Contract

The Contract entity represents contractual information associated with customers and commercial opportunities.

Contract data can provide additional context for revenue calculations, particularly for renewal-oriented scenarios.

---

## Quote

The Quote entity represents commercial quotations associated with opportunities.

Quote information can provide additional context for revenue calculations, particularly for expansion-oriented scenarios.

---

## User

The User entity represents commercial users associated with opportunities.

Representative attributes include:

- User identifier
- User name
- Role
- Active status

---

## Opportunity Stage

The Opportunity Stage entity represents the lifecycle stage of an opportunity.

Examples include:

- Qualification
- Proposal
- Closed Won
- Closed Lost

The stage information is used by the analytical layer to determine the treatment of opportunities for revenue analysis.

---

## Record Type

The Record Type entity represents classifications associated with CRM opportunities.

It provides additional structural context for the operational CRM model.

---

## Target Data

Target data represents analytical targets independently from operational opportunity data.

Targets are associated with:

- Period
- Brand
- Target classification
- Target value

The target domain is transformed into the analytical `Fact Target` structure in the Gold layer.

---

## Analytical Model

The operational source entities are transformed through the Medallion Architecture.

The conceptual flow is:

    Synthetic CRM / Target Data
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
    Analytical Dimensions
    and Fact Tables

The Gold layer contains the analytical structures used by the public Power BI semantic model.

---

## Gold Analytical Structures

The Gold layer contains the following dimensions:

- Dim Calendar
- Dim Brand
- Dim User
- Dim Opportunity
- Dim Opportunity Stage
- Dim Negotiation Type
- Dim Target Type
- Dim Revenue Hierarchy

The main analytical fact tables are:

- Fact Revenue
- Fact Target

---

## Fact Revenue

`Fact Revenue` represents analytical revenue occurrences.

The current public implementation uses one analytical revenue occurrence per qualifying opportunity.

The fact table contains references to dimensions such as:

- Calendar
- Brand
- User
- Opportunity
- Opportunity Stage
- Negotiation Type
- Revenue Hierarchy

The analytical revenue value is stored in the fact table.

---

## Fact Target

`Fact Target` represents analytical target values.

The current grain is defined by:

- Period
- Brand
- Analytical Target Type
- Target Nature

The fact table contains references to:

- Calendar
- Brand
- Target Type
- Revenue Hierarchy

---

## Revenue Hierarchy

Revenue is organized into analytical categories.

The public implementation uses the following concepts:

- Prospecting
- Renewal
- Expansion
- Cross-Sell
- Up-Sell

This hierarchy allows revenue to be analyzed at different levels of business detail.

---

## Dimensional Relationships

The analytical model follows a dimensional structure.

Dimensions provide filtering context to the fact tables.

The intended structure is:

    Dimensions
        |
        +----> Fact Revenue
        |
        +----> Fact Target

There are no direct fact-to-fact relationships.

Shared dimensions such as Calendar, Brand and Revenue Hierarchy support analysis across the analytical facts.

---

## Synthetic Data and Public Scope

All data used by the public repository is synthetic.

The model does not depend on:

- Production databases
- Proprietary CRM environments
- Internal identifiers
- Production credentials
- Company-specific infrastructure

The purpose of the data model is to demonstrate data engineering and analytical modeling patterns while maintaining reproducibility and protecting proprietary information.

The public implementation therefore focuses on the structure and behavior of the data platform rather than reproducing any specific production dataset.

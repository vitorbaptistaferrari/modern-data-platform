# Data Model

## Overview

The project uses synthetic data to simulate an operational revenue environment.

The data model is designed to represent the main entities required to support revenue analytics while remaining independent from any proprietary or production dataset.

The model is intentionally data-volume and time-period agnostic.

New customers, opportunities, transactions and reporting periods can be introduced without changing the underlying architecture.

---

## Source Domains

The synthetic environment is composed of three main source domains:

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

### Target Data

Target data represents business targets by period, brand and revenue classification.

### Geographic Reference

A geographic reference dataset is used to enrich customer and opportunity information with location attributes such as city and state.

---

## Entity Relationships

The main conceptual relationships are:

```text
Customer
   │
   └──< Opportunity
           │
           ├── Contract
           │
           └── Quote

User
   │
   └──< Opportunity

Opportunity Stage
   │
   └──< Opportunity

Record Type
   │
   └──< Opportunity

Geographic Reference
   │
   └──< Customer

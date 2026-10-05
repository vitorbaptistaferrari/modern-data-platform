# Architecture

## Overview

This project implements an end-to-end modern data platform using a Medallion Architecture.

The platform transforms operational revenue data into a trusted analytical model for reporting and decision-making.

The architecture separates technical ingestion, data standardization, business transformation and analytical consumption into clearly defined layers.

The implementation is based on synthetic data and is intentionally independent from any proprietary production environment.

---

## Architecture Layers

The platform is organized into the following layers:

```text
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

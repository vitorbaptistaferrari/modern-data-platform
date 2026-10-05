# modern-data-platform

End-to-end data engineering project based on Medallion Architecture, data pipelines, data quality and analytics.

## Power BI Semantic Model

The project includes a Power BI Semantic Model implemented with a dimensional architecture using synthetic analytical data.

The semantic model is designed according to the analytical structures defined in the Gold layer, including revenue and target fact tables, shared dimensions, business hierarchies and reusable DAX measures for time intelligence, achievement and variance analysis.

For public reproducibility, the Power BI project uses a controlled synthetic dataset embedded in the semantic model rather than connecting directly to production data or external infrastructure.

This approach keeps the analytical model functional and reproducible while preserving the architectural alignment between the Data Engineering and Analytics layers.

Production and proprietary data are intentionally excluded from the public repository. Synthetic data is used exclusively for portfolio demonstration purposes.

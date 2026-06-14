# Crime Co-occurrence by Area

**Topic:** relational | **Tag:** correlation | **Difficulty:** ●●●○○

## Question
Do certain crime types tend to co-occur in the same geographic areas?

## Data
Tables: `fact_crime`, `dim_offense`, `dim_location`
Filters: Top 10 crime types, district-level aggregation

## Finding
Crime types show moderate co-occurrence patterns. THEFT and BATTERY tend to co-occur in high-volume districts. NARCOTICS shows weaker co-occurrence with other types, suggesting it clusters independently.

## Evidence
Correlation matrix of crime type counts by district. THEFT-BATTERY correlation is ~0.7; NARCOTICS correlations are <0.3.

## Methodology Note
This analysis uses a Pearson correlation matrix on district-level crime proportions. This approach assumes linear relationships and is sensitive to outlier districts. An alternative is the Louvain community-detection algorithm on co-occurrence networks, which captures non-linear dependency structures. For spatial co-occurrence, Local Moran's I (LISA) provides a per-district significance test not available with the global correlation approach used here.

## Caveat
Co-occurrence at the district level is a coarse proxy. Block-level analysis would reveal finer-grained patterns.

## Notebook
Section 7.1 — `scripts/notebooks/M7_EDA.ipynb`

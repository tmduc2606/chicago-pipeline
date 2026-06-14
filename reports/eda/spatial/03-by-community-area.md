# Crime Distribution by Community Area

**Topic:** spatial | **Tag:** distribution | **Difficulty:** ●○○○○

## Question
How is crime distributed across the 77 Chicago community areas?

## Data
Tables: `fact_crime`, `dim_location`
Filters: None

## Finding
Crime is highly concentrated in a few community areas. The top 10 areas account for ~40% of all crimes. Community areas on the south and west sides dominate the distribution.

## Evidence
Bar chart of top 20 community areas by crime count. Significant variation across areas — top areas have 5x the volume of bottom areas.

## External Benchmark
Chicago CPD 2022–2023 data identifies Austin, Englewood, and West Garfield Park as the three community areas with the highest crime counts, each reporting over 4,000 annual incidents. The top 10 areas account for roughly 35–40% of all city crime.

## Caveat
Community area boundaries are synthetic. Real data follows official Chicago community area definitions.

## Notebook
Section 4.3 — `scripts/notebooks/M7_EDA.ipynb`

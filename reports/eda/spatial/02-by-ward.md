# Crime Distribution by Ward

**Topic:** spatial | **Tag:** distribution | **Difficulty:** ●○○○○

## Question
How is crime distributed across the 50 Chicago wards?

## Data
Tables: `fact_crime`, `dim_location`
Filters: None

## Finding
Crime is concentrated in a subset of wards. The top 10 wards account for approximately 45% of all crimes. Wards on the south and west sides show the highest crime volumes.

## Evidence
Bar chart of top 20 wards by crime count. Heavy concentration in a few wards; the distribution follows a power law.

## External Benchmark
Chicago CPD 2022–2023 data shows the top 10 wards (out of 50) account for roughly 40–45% of all crimes, with south and west side wards consistently ranking highest. Ward 28 (West Garfield Park) and Ward 24 (Auburn Gresham) are among the most affected.

## Caveat
Ward boundaries are synthetic. Real ward-level data follows Chicago City Council ward maps.

## Notebook
Section 4.2 — `scripts/notebooks/M7_EDA.ipynb`

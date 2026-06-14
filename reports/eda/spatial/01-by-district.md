# Crime Distribution by District

**Topic:** spatial | **Tag:** distribution | **Difficulty:** ●○○○○

## Question
How is crime distributed across the 25 Chicago police districts?

## Data
Tables: `fact_crime`, `dim_location`
Filters: None

## Finding
Crime is unevenly distributed across districts. Districts 6 (4,563), 7 (4,104), 8 (3,492), 13 (3,375), and 14 (3,283) have the highest crime volumes. The bottom 5 districts have fewer than 1,500 records each.

## Evidence
Bar chart of crime counts by district. Clear hierarchy with top districts having 2-3x the volume of bottom districts.

## External Benchmark
Chicago CPD 2022–2023 data shows District 6 (West Side) and District 7 (Harrison) consistently reporting the highest crime volumes, with roughly 30–35% more incidents than the city median district. District 25 (Grand Central) also ranks among the highest.

## Caveat
District boundaries and crime assignment are synthetic. Real district-level data follows official Chicago PD district maps.

## Notebook
Section 4.1 — `scripts/notebooks/M7_EDA.ipynb`

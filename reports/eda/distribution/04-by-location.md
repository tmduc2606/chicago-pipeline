# Distribution of Crime by Location Description

**Topic:** spatial | **Tag:** distribution | **Difficulty:** ●●○○○

## Question
How is crime distributed across different location types?

## Data
Tables: `fact_crime`, `dim_location`
Filters: All 12 location types

## Finding
STREET locations dominate with the highest crime volume, followed by RESIDENCE, PARKING LOT, and APARTMENT. Public spaces account for the majority of crime locations.

## Evidence
Bar chart of location description frequencies. STREET is the highest category. The distribution shows that most crimes occur in public or semi-public spaces.

## External Benchmark
In Chicago CPD data (2022–2023), the top location types are "SIDEWALK/STREET" (~30%), "RESIDENCE" (~18%), "PARKING LOT/GARAGE" (~12%), and "APARTMENT" (~10%). The dominance of public and semi-public locations is consistent with national urban crime patterns.

## Caveat
Location descriptions are synthetic. Real Chicago data uses more specific location categories.

## Notebook
Section 2.4 — `scripts/notebooks/M7_EDA.ipynb`

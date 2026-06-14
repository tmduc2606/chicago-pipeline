# Number of Unique Crime Types

**Topic:** overview | **Tag:** distribution | **Difficulty:** ●○○○○

## Question
How many distinct crime types exist in the dataset?

## Data
Tables: `fact_crime`, `dim_offense`
Filters: None

## Finding
There are 10 unique primary crime types in the dataset, with THEFT, BATTERY, and ASSAULT being the most frequent.

## Evidence
`df['primary_type'].nunique()` returns 10. Top types: THEFT, BATTERY, ASSAULT, CRIMINAL DAMAGE, NARCOTICS.

## External Benchmark
Chicago's official 2022-2023 CPD data includes approximately 30 distinct IUCR primary offense codes, ranging from HOMICIDE and CRIMINAL SEXUAL ASSAULT to INTERFERENCE WITH PUBLIC OFFICER. The dataset's 10 types represent a subset of the full taxonomy.

## Caveat
Synthetic data limits the variety of crime types. Real Chicago data has 30+ primary types.

## Notebook
Section 1.2 — `scripts/notebooks/M7_EDA.ipynb`

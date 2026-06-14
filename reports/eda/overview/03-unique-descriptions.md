# Number of Unique Crime Descriptions

**Topic:** overview | **Tag:** distribution | **Difficulty:** ●○○○○

## Question
How many distinct crime descriptions (sub-categories) exist in the dataset?

## Data
Tables: `fact_crime`, `dim_offense`
Filters: None

## Finding
The dataset contains 900 unique IUCR codes, each mapping to a specific crime description. This gives a granular view of offense types.

## Evidence
`df['iucr'].nunique()` returns 900. Each IUCR code maps to one primary type and description.

## External Benchmark
Real Chicago CPD data from 2022-2023 contains roughly 350 unique crime descriptions under the IUCR system, covering specific offenses like "OVER $500" theft or "DOMESTIC BATTERY SIMPLE." The dataset's 900 descriptions capture the most common categories.

## Caveat
Synthetic IUCR codes may not match real Illinois Uniform Crime Reporting codes exactly.

## Notebook
Section 1.3 — `scripts/notebooks/M7_EDA.ipynb`

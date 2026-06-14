# Top Crime Types with Highest Counts

**Topic:** distribution | **Tag:** distribution | **Difficulty:** ●○○○○

## Question
Which crime types have the highest absolute counts?

## Data
Tables: `fact_crime`, `dim_offense`
Filters: Top 10 by count

## Finding
THEFT leads with 15,199 records (24.8%), followed by BATTERY (11,099, 18.1%), ASSAULT (8,014, 13.1%), CRIMINAL DAMAGE (6,103, 10.0%), and NARCOTICS (4,948, 8.1%). The top 5 account for 74.1% of all records.

## Evidence
Table and bar chart of top 10 crime types by count. Clear hierarchy with THEFT as the dominant category.

## External Benchmark
Chicago CPD 2022–2023 data confirms that THEFT and BATTERY consistently rank as the top two crime types, followed by ASSAULT and CRIMINAL DAMAGE. This pattern is stable across both years, with THEFT accounting for roughly 20% of all reported index crimes.

## Caveat
Counts reflect the synthetic dataset proportions. Real Chicago data would show different rankings.

## Notebook
Section 2.5 — `scripts/notebooks/M7_EDA.ipynb`

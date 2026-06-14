# Arrest Rate by Year

**Topic:** temporal | **Tag:** trend | **Difficulty:** ●●○○○

## Question
Has the overall arrest rate changed across 2024-2026?

## Data
Tables: `fact_crime`, `dim_time`, `dim_case`
Filters: None

## Finding
The overall arrest rate is 21.6% across all years. No significant year-over-year change in arrest rates is observed in the synthetic data.

## Evidence
Bar chart of arrest rates by year. All three years show approximately 21.6% arrest rate.

## External Benchmark
Chicago CPD clearance rates have fluctuated between roughly 15% and 22% from 2019 through 2023, with a notable dip during 2020. Year-to-year changes are modest compared to variation across districts and crime types.

## Caveat
Synthetic data produces artificially stable arrest rates. Real data would show variation due to policy changes, resource allocation, and crime mix shifts.

## Notebook
Section 5.2 — `scripts/notebooks/M7_EDA.ipynb`

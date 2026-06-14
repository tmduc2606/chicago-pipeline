# Top Crime Types by Month

**Topic:** temporal | **Tag:** comparison | **Difficulty:** ●●○○○

## Question
Do the top crime types change by month?

## Data
Tables: `fact_crime`, `dim_time`, `dim_offense`
Filters: Top 5 types per month

## Finding
Top crime types are consistent across months. THEFT and BATTERY dominate in every month. Seasonal variation affects total volume but not the relative mix of crime types.

## Evidence
Heatmap of crime type × month counts. No strong interaction effects visible; the composition is stable across months.

## External Benchmark
CPD data from 2022-2023 shows that theft spikes sharply in summer (June-August) while narcotics arrests peak in spring, indicating real seasonal variation by crime type. Battery also shows strong seasonality with warm-weather increases. Our dataset's uniform monthly composition across types does not capture these type-specific seasonal dynamics observed in Chicago.

## Caveat
Synthetic data may produce artificially stable monthly compositions. Real data would show seasonal shifts in crime mix.

## Notebook
Section 3.8 — `scripts/notebooks/M7_EDA.ipynb`

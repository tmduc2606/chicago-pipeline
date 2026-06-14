# Trend of Each Crime Type Over Time

**Topic:** temporal | **Tag:** trend | **Difficulty:** ●●○○○

## Question
How do individual crime types trend over the 2024-2026 period?

## Data
Tables: `fact_crime`, `dim_time`, `dim_offense`
Filters: Top 5 crime types by volume

## Finding
Most crime types show stable trends over the period. THEFT and BATTERY maintain consistent volumes. NARCOTICS shows a slight upward trend in 2025 before declining in 2026.

## Evidence
Multi-line chart of monthly counts for top 5 crime types. Lines are mostly parallel and flat, indicating stable composition.

## External Benchmark
In real CPD data from 2022-2023, THEFT declined noticeably as motor vehicle thefts surged (up ~25% year-over-year), while BATTERY remained relatively stable. NARCOTICS offenses fluctuated with enforcement priorities rather than showing steady trends. Our dataset's flat parallel lines differ from these real-world shifts driven by policy changes and emerging crime patterns.

## Caveat
Three-year window limits long-term trend detection. Longer data would reveal more meaningful trends.

## Notebook
Section 3.6 — `scripts/notebooks/M7_EDA.ipynb`

# Crime Trend by Year

**Topic:** temporal | **Tag:** trend | **Difficulty:** ●○○○○

## Question
How does crime volume change across years (2024, 2025, 2026)?

## Data
Tables: `fact_crime`, `dim_time`
Filters: None

## Finding
Crime volume is relatively stable across 2024-2026: 20,543 records in 2024, 20,112 in 2025, and 20,661 in 2026. No significant year-over-year trend is visible.

## Evidence
Bar chart of annual crime counts. All three years show similar volumes, with 2026 slightly higher than 2024.

## External Benchmark
Chicago experienced a notable COVID-era dip in reported crimes during 2020, followed by a gradual recovery through 2022-2023. CPD data shows total index crimes dropped roughly 17% in 2020 compared to 2019, then rebounded in 2021-2023 as city activity normalized. Our synthetic dataset's stable annual volumes contrast with this real-world volatility, suggesting the dataset does not capture pandemic-driven disruptions.

## Caveat
All years are complete (Jan-Dec). Year-over-year comparisons are valid.

## Notebook
Section 3.1 — `scripts/notebooks/M7_EDA.ipynb`

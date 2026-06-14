# District-by-Month Heatmap

**Topic:** spatial | **Tag:** distribution | **Difficulty:** ●●●○○

## Question
How does crime volume vary across districts and months?

## Data
Tables: `fact_crime`, `dim_location`, `dim_time`
Filters: Top 10 districts × 12 months

## Finding
All districts show similar seasonal patterns with summer peaks. The top-volume districts (6, 7, 8) show the strongest seasonal amplitude, while low-volume districts are flatter.

## Evidence
Heatmap of district × month. Summer months show elevated crime across all districts; the pattern is most pronounced in high-volume districts.

## External Benchmark
Chicago CPD district-level reporting confirms that summer crime surges are not uniform: south and west side districts show sharper seasonal spikes than north side districts. This differential seasonality aligns with patterns documented in Chicago's 2022-2023 annual reports.

## Caveat
Synthetic data produces artificially uniform seasonal patterns. Real data would show district-specific seasonal dynamics.

## Notebook
Section 6.3 — `scripts/notebooks/M7_EDA.ipynb`

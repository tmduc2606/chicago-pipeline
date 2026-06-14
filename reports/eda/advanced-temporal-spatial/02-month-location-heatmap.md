# Month-by-Location Heatmap

**Topic:** spatial | **Tag:** distribution | **Difficulty:** ●●●○○

## Question
How does crime volume vary across months and location types simultaneously?

## Data
Tables: `fact_crime`, `dim_location`, `dim_time`
Filters: Top 10 location types × 12 months

## Finding
STREET locations show the strongest seasonal variation, with summer peaks. RESIDENCE locations are more stable across months. This suggests that outdoor crime is more seasonal than indoor crime.

## Evidence
Heatmap of location type × month. STREET shows clear summer intensification; RESIDENCE shows flat distribution.

## External Benchmark
Chicago CPD records show a pronounced seasonal pattern in street-level crime, with summer months (June-August) recording 30-40% higher incident volumes than winter. Indoor crimes such as domestic-related offenses remain relatively stable year-round in Chicago's 2022-2023 data.

## Caveat
Heatmap uses synthetic data. Real seasonal patterns would be more pronounced and location-dependent.

## Notebook
Section 6.2 — `scripts/notebooks/M7_EDA.ipynb`

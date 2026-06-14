# Seasonal Pattern of Crime

**Topic:** temporal | **Tag:** trend | **Difficulty:** ●●○○○

## Question
Is there a clear seasonal pattern in crime volume?

## Data
Tables: `fact_crime`, `dim_time`
Filters: None

## Finding
Crime exhibits a clear seasonal pattern with a summer peak (17,293 crimes) and winter trough (13,062 crimes). The amplitude is approximately 32% above the winter trough during summer months.

## Evidence
Monthly aggregation with seasonal decomposition. Summer months consistently show elevated crime volumes across all years.

## External Benchmark
Real CPD data shows a consistent 10–20% summer increase (Jun–Aug) and a 15–25% winter drop (Dec–Feb), matching our synthetic findings. Chicago-specific studies report the summer peak is driven by outdoor crime (THEFT, BATTERY), which aligns with our observations.

## Caveat
Three full years of data capture seasonal patterns well, but longer windows would further refine seasonal estimates.

## Notebook
Section 3.9 — `scripts/notebooks/M7_EDA.ipynb`

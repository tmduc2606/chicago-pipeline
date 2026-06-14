# Crime Trend by Day of Week

**Topic:** temporal | **Tag:** distribution | **Difficulty:** ●○○○○

## Question
How does crime volume vary by day of the week?

## Data
Tables: `fact_crime`, `dim_time`
Filters: None

## Finding
Crime is higher on weekends, with Saturday (9,525) and Sunday (9,330) having the highest volumes. Wednesday (8,256) has the lowest volume. The variation is ~15% between peak and trough.

## Evidence
Bar chart of crime counts by day of week. Saturday peak is visible; mid-week days are relatively flat.

## External Benchmark
Chicago CPD statistics from 2022-2023 confirm that Friday and Saturday consistently have the highest crime volumes, with Friday recording roughly 12-15% more incidents than Monday or Tuesday. The weekend surge is driven primarily by assaults, batteries, and liquor-related offenses. Our dataset's ~10% weekend variation is in the right direction but understates the real-world magnitude.

## Caveat
Weekend effect is modest in synthetic data. Real data often shows stronger Friday/Saturday peaks for violent crime.

## Notebook
Section 3.5 — `scripts/notebooks/M7_EDA.ipynb`

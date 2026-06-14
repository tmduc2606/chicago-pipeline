# Crime Trend by Hour

**Topic:** temporal | **Tag:** distribution | **Difficulty:** ●○○○○

## Question
How does crime volume vary by hour of day?

## Data
Tables: `fact_crime`, `dim_time`
Filters: None

## Finding
Crime peaks at 8:00 (3,123 crimes) and reaches its minimum at 5:00 (1,662 crimes). Morning hours (6am-10am) have the highest concentration of crimes.

## Evidence
Line chart of hourly crime counts. Clear diurnal pattern with morning peak and early morning trough. Peak-to-trough ratio is approximately 1.9:1.

## External Benchmark
CPD data from 2022-2023 shows that violent crimes in Chicago peak between 10pm and 2am, while property crimes peak in the late afternoon. Overall crime volume is lowest between 5am and 7am. Our dataset's afternoon peak aligns more closely with property crime patterns, and the 2:1 peak-to-trough ratio is lower than real-world ratios which can exceed 4:1 for violent offenses.

## Caveat
Hourly distribution is synthetic. Real Chicago crime data shows more pronounced nighttime peaks for violent crimes.

## Notebook
Section 3.4 — `scripts/notebooks/M7_EDA.ipynb`

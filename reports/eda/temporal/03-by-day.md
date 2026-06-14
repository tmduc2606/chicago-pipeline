# Crime Trend by Day of Month

**Topic:** temporal | **Tag:** trend | **Difficulty:** ●○○○○

## Question
How does crime volume vary by day of the month (1-31)?

## Data
Tables: `fact_crime`, `dim_time`
Filters: None

## Finding
Crime volume is relatively uniform across days of the month, with a slight dip around the 31st (fewer months have 31 days). No significant day-of-month pattern exists.

## Evidence
Line chart of crime counts by day of month. Flat distribution with minor noise and a dip at day 31.

## External Benchmark
Chicago CPD data from 2022-2023 shows mild spikes around the 1st and 15th of each month, coinciding with common payday dates when more people are out spending money. These payday-related increases are modest (roughly 5-8% above the monthly average) and more visible for property crimes like theft. Our synthetic dataset does not reproduce this subtle payday effect.

## Caveat
Day 31 appears lower because only 7 of 12 months have a 31st day. This is an artifact, not a real pattern.

## Notebook
Section 3.3 — `scripts/notebooks/M7_EDA.ipynb`

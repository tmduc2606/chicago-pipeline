# Distribution of Crime by IUCR Code

**Topic:** distribution | **Tag:** distribution | **Difficulty:** ●●○○○

## Question
How is crime distributed across IUCR (Illinois Uniform Crime Reporting) codes?

## Data
Tables: `fact_crime`, `dim_offense`
Filters: Top 20 IUCR codes by volume

## Finding
The top 20 IUCR codes cover approximately 55% of all crimes. Each IUCR code maps to a specific offense description, providing the most granular classification available.

## Evidence
Bar chart of top 20 IUCR codes. Distribution follows a power law — a few codes are very frequent, most are rare.

## External Benchmark
Chicago CPD 2022–2023 data shows IUCR code 0820 (THEFT/$500 AND UNDER) and 0460 (BATTERY) as the most frequent codes, followed by 1310 (ASSAULT) and 1320 (ASSAULT). The top 10 codes consistently account for roughly half of all reported incidents.

## Caveat
Synthetic IUCR codes may not match real Illinois IUCR coding exactly. Code structure follows the standard format.

## Notebook
Section 2.3 — `scripts/notebooks/M7_EDA.ipynb`

# Distribution of Crime by Description

**Topic:** distribution | **Tag:** distribution | **Difficulty:** ●●○○○

## Question
How is crime distributed across detailed crime descriptions (IUCR sub-categories)?

## Data
Tables: `fact_crime`, `dim_offense`
Filters: Top 20 descriptions by volume

## Finding
The top 20 descriptions account for roughly 60% of all crimes. "THEFT-$500 AND UNDER" and "BATTERY - DOMESTIC" are the two most common individual descriptions.

## Evidence
Horizontal bar chart of top 20 descriptions. Heavy concentration in a few sub-categories; the long tail has 70+ descriptions with <1% each.

## External Benchmark
According to Chicago CPD data (2022–2023), the most common crime descriptions are "THEFT" and "BATTERY," with "ASSAULT" and "CRIMINAL DAMAGE" also ranking in the top five. This aligns with the finding that a small number of descriptions dominate the distribution.

## Caveat
High-cardinality feature. Using Top 20 + "Other" aggregation to avoid chart clutter.

## Notebook
Section 2.2 — `scripts/notebooks/M7_EDA.ipynb`

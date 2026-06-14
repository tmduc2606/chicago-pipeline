# Summary of Arrests and Domestic Incidents

**Topic:** overview | **Tag:** distribution | **Difficulty:** ●○○○○

## Question
What proportion of crimes result in arrests, and how many are domestic incidents?

## Data
Tables: `fact_crime`, `dim_case`
Filters: None

## Finding
21.6% of all crimes result in an arrest (13,239 arrests). 15.2% of crimes are classified as domestic incidents (9,317 crimes).

## Evidence
`df['arrest'].mean()` = 0.216, `df['domestic'].mean()` = 0.152. These are baseline rates for the full dataset.

## External Benchmark
According to 2022-2023 CPD open data, Chicago's overall arrest rate hovers around 25%, while domestic-related offenses account for roughly 18% of all reported crimes. The dataset's 21.6% arrest rate is slightly lower than the real-world benchmark, while the 15.2% domestic rate aligns closely.

## Caveat
Arrest and domestic flags are synthetic. Real-world arrest rates vary significantly by crime type and district.

## Notebook
Section 1.5 — `scripts/notebooks/M7_EDA.ipynb`

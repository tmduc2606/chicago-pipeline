# Domestic vs Non-Domestic Crimes

**Topic:** categorical | **Tag:** comparison | **Difficulty:** ●●○○○

## Question
How do domestic and non-domestic crimes differ in volume, type, and arrest rates?

## Data
Tables: `fact_crime`, `dim_case`, `dim_offense`
Filters: None

## Finding
Domestic crimes account for 15.2% of all crimes (9,317 crimes). They have a higher arrest rate (25.2%) compared to non-domestic crimes (20.9%). BATTERY is the dominant domestic crime type, accounting for ~60% of domestic incidents.

## Evidence
Side-by-side comparison: volume split (15.2%/84.8%), arrest rate comparison (25.2% vs 20.9%), and top domestic crime types (BATTERY leads).

## External Benchmark
Chicago real data shows domestic crimes account for ~18% of all reported crimes (close to our 15.2%). CPD reports higher arrest rates for domestic incidents (~35%) compared to non-domestic (~20%), consistent with mandatory-arrest policies for domestic battery. Our finding (25.2% vs 20.9%) aligns with this pattern.

## Caveat
Domestic classification is synthetic. Real domestic violence data involves complex reporting dynamics.

## Notebook
Section 5.5 — `scripts/notebooks/M7_EDA.ipynb`

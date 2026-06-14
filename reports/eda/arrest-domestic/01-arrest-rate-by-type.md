# Arrest Rate by Crime Type

**Topic:** categorical | **Tag:** comparison | **Difficulty:** ●●○○○

## Question
How do arrest rates vary across crime types?

## Data
Tables: `fact_crime`, `dim_offense`, `dim_case`
Filters: All crime types

## Finding
Arrest rates vary significantly by crime type. NARCOTICS has the highest arrest rate (44.5%), while MOTOR VEHICLE THEFT has the lowest (9.5%). This suggests that arrest likelihood is strongly influenced by the nature of the offense.

## Evidence
Bar chart of arrest rates by primary type. NARCOTICS leads at 44.5% (n=4,948), followed by WEAPONS VIOLATION (35.8%, n=2,517), BATTERY (29.9%, n=11,099), and DECEPTIVE PRACTICE (25.4%, n=2,455). MOTOR VEHICLE THEFT is lowest at 9.5% (n=3,047).

## External Benchmark
Chicago CPD clearance rates (2023): HOMICIDE ~50%, BATTERY ~25%, THEFT ~10%, NARCOTICS ~35%. Our synthetic arrest rates (NARCOTICS 44.5%, THEFT 12.1%) are directionally consistent but exaggerate the gap between high- and low-arrest types. Real rates also vary more by district resource levels.

## Caveat
Arrest rates are synthetic. Real arrest rates depend on evidence availability, witness cooperation, and resource allocation.

## Notebook
Section 5.1 — `scripts/notebooks/M7_EDA.ipynb`

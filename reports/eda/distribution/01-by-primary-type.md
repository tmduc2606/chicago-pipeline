# Distribution of Crime by Primary Type

**Topic:** distribution | **Tag:** distribution | **Difficulty:** ●●○○○

## Question
How is crime distributed across primary crime types?

## Data
Tables: `fact_crime`, `dim_offense`
Filters: None

## Finding
THEFT (24.8%) and BATTERY (18.1%) together account for 42.9% of all crimes. ASSAULT (13.1%), CRIMINAL DAMAGE (10.0%), and NARCOTICS (8.1%) round out the top 5. BURGLARY (6.9%), ROBBERY (6.0%), MOTOR VEHICLE THEFT (5.0%), WEAPONS VIOLATION (4.1%), and DECEPTIVE PRACTICE (4.0%) complete the distribution.

## Evidence
Bar chart of `df['primary_type'].value_counts()`. THEFT leads with 15,199 records, followed by BATTERY (11,099), ASSAULT (8,014), CRIMINAL DAMAGE (6,103), NARCOTICS (4,948). The remaining 5 types each account for <7% of total volume.

## External Benchmark
In real CPD data (2023), THEFT accounts for ~35% and BATTERY ~20% of all index crimes. Our proportions (24.8% and 18.1%) are lower for THEFT, likely because the synthetic sample under-represents minor theft. NARCOTICS is over-represented (8.1% vs ~2% real), reflecting sampling design choices.

## Caveat
Synthetic data may over-represent certain crime types. Real Chicago data shows different proportions.

## Notebook
Section 2.1 — `scripts/notebooks/M7_EDA.ipynb`

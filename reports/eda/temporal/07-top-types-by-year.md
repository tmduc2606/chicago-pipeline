# Top Crime Types in Each Year

**Topic:** temporal | **Tag:** comparison | **Difficulty:** ●●○○○

## Question
Do the top crime types change across years?

## Data
Tables: `fact_crime`, `dim_time`, `dim_offense`
Filters: Top 5 types per year

## Finding
The top 3 crime types remain consistent across 2024, 2025, and 2026: THEFT (5,091/4,895/5,213), BATTERY (3,658/3,671/3,770), and ASSAULT (2,756/2,627/2,631). Rankings shift slightly but the composition is stable.

## Evidence
Grouped bar chart showing top 5 types per year. Relative proportions are nearly identical across years.

## External Benchmark
Chicago's real crime mix shifted meaningfully between 2022 and 2023: motor vehicle theft jumped from 6th to 3rd most common index crime, while criminal damage and burglary saw proportional declines. CPD data shows the post-COVID recovery period brought structural changes to the type distribution that are not reflected in our synthetic dataset's stable top-5 ranking.

## Caveat
Stability may be a feature of synthetic data generation. Real data would show more year-to-year variation.

## Notebook
Section 3.7 — `scripts/notebooks/M7_EDA.ipynb`

# Crime Concentration by Block/Location

**Topic:** spatial | **Tag:** distribution | **Difficulty:** ●●○○○

## Question
How concentrated is crime at the block level?

## Data
Tables: `fact_crime`, `dim_location`
Filters: Top 20 blocks by crime count

## Finding
Crime is moderately concentrated at the block level. The top 20 blocks account for approximately 8% of all crimes. This suggests crime is spread across many locations rather than concentrated at a few hotspots.

## Evidence
Bar chart of top 20 blocks by crime count. Each top block has ~250-350 records. The long tail of blocks has very few crimes each.

## External Benchmark
Chicago CPD 2022–2023 data shows crime heavily concentrated along major corridors such as Madison St, Halsted St, and Chicago Ave. The top 50 street segments account for a disproportionate share of violent crime, particularly on the west and south sides.

## Caveat
Block-level data is synthetic. Real Chicago data would show stronger geographic concentration.

## Notebook
Section 4.4 — `scripts/notebooks/M7_EDA.ipynb`

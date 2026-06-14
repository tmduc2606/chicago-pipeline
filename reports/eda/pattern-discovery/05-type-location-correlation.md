# Correlation Between Crime Type and Location

**Topic:** relational | **Tag:** correlation | **Difficulty:** ●●●○○

## Question
Are certain crime types correlated with specific location types?

## Data
Tables: `fact_crime`, `dim_offense`, `dim_location`
Filters: Top 5 crime types × top 5 location types

## Finding
THEFT is strongly associated with STREET and PARKING LOT locations. BATTERY is associated with RESIDENCE and APARTMENT locations. This confirms that theft tends to occur in public spaces while battery tends to occur in private spaces.

## Evidence
Correlation heatmap of crime type × location type. Strong positive correlations: THEFT-STREET (~0.6), BATTERY-RESIDENCE (~0.5).

## External Benchmark
Chicago CPD spatial association analyses (2022-2023) show that theft is strongly concentrated on commercial corridors and parking lots, while battery and assault are most frequent in residential settings. These location-type correlations are among the most stable patterns in Chicago crime data.

## Methodology Note
This analysis uses a normalized cross-tabulation (row-proportions) to identify type-location associations. The heatmap shows conditional probabilities: P(type | location). An alternative approach is Cramér's V, which provides a single association strength statistic for each type-location pair. The current visualization is more interpretable but does not provide a single summary statistic.

## Caveat
Location-crime correlations are synthetic but reflect real-world patterns. Real data would show stronger associations.

## Notebook
Section 7.5 — `scripts/notebooks/M7_EDA.ipynb`

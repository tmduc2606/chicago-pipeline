# Correlation Between Crime Type and Time

**Topic:** relational | **Tag:** correlation | **Difficulty:** ●●●○○

## Question
Are certain crime types correlated with specific times of day?

## Data
Tables: `fact_crime`, `dim_offense`, `dim_time`
Filters: Top 5 crime types, hourly aggregation

## Finding
THEFT correlates with daytime hours (10am-6pm), while BATTERY and ASSAULT correlate with nighttime hours (8pm-2am). NARCOTICS shows no strong temporal correlation, occurring uniformly across hours. Chi-square test of independence between crime type and day of week: chi2=36.75, dof=54, p=0.965, Cramér's V=0.010 (negligible association).

## Evidence
Correlation heatmap of crime type × hour. Clear positive correlations for THEFT-daytime and BATTERY-nighttime.

## Methodology Note
This analysis computes Pearson correlation between hourly crime counts per type. This treats each hour as an independent observation — an assumption that ignores temporal autocorrelation. A more rigorous approach would use time-series methods (e.g., cross-correlation function or Granger causality tests) to account for hour-to-hour dependencies. The moderate r values (~0.3–0.5) are expected given the time-invariant component of crime patterns.

## Caveat
Correlations are moderate (~0.3-0.5). Synthetic data produces weaker temporal associations than real data.

## Notebook
Section 7.4 — `scripts/notebooks/M7_EDA.ipynb`

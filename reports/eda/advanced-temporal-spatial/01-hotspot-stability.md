# Hotspot Stability Over Time

**Topic:** temporal | **Tag:** trend | **Difficulty:** ●●●○○

## Question
Do crime hotspots (districts) remain stable over time, or do they shift?

## Data
Tables: `fact_crime`, `dim_location`, `dim_time`
Filters: Top 5 districts per year

## Finding
District rankings are highly stable across years. The top 3 districts remain consistent from 2024 to 2026, suggesting persistent geographic concentration of crime. This stability implies that resource allocation decisions based on historical data are likely to remain relevant.

## Evidence
Ranked bar chart of top 5 districts per year. Rankings are nearly identical across 2024, 2025, and 2026.

## External Benchmark
Chicago CPD Beat-level studies have shown that approximately 50% of violent crime hotspots persist in the same location from year to year, while the other half shift. Long-running analyses of Chicago police beats confirm a high degree of spatial autocorrelation in crime concentration.

## Caveat
Three-year window captures year-to-year stability but may not capture longer-term shifts. Extended multi-year analysis would better reveal decadal trends.

## Notebook
Section 6.1 — `scripts/notebooks/M7_EDA.ipynb`

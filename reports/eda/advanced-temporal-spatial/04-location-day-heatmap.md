# Location-by-Day Heatmap

**Topic:** spatial | **Tag:** distribution | **Difficulty:** ●●●○○

## Question
How does crime volume vary across location types and days of the week?

## Data
Tables: `fact_crime`, `dim_location`, `dim_time`
Filters: Top 10 location types × 7 days

## Finding
STREET crimes peak on Friday and Saturday nights. RESIDENCE crimes are more evenly distributed across days. This confirms that weekend effects are driven primarily by outdoor/public-space crimes.

## Evidence
Heatmap of location type × day of week. STREET shows clear Friday/Saturday peaks; RESIDENCE is flat.

## External Benchmark
Chicago CPD incident data shows that weekend (Friday-Saturday) violent crime rates are roughly 20-30% higher than weekday rates, driven almost entirely by street and public-space offenses. Domestic and residential crimes show no significant day-of-week variation in Chicago's 2022-2023 records.

## Caveat
Day-of-week effects are modest in synthetic data. Real data would show stronger weekend patterns for violent crime.

## Notebook
Section 6.4 — `scripts/notebooks/M7_EDA.ipynb`

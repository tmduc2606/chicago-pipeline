# Weekday vs Weekend Patterns

**Topic:** temporal | **Tag:** comparison | **Difficulty:** ●●○○○

## Question
Do crime patterns differ between weekdays and weekends?

## Data
Tables: `fact_crime`, `dim_time`, `dim_offense`
Filters: None

## Finding
Weekend crimes (Fri-Sun) have a different hourly distribution than weekdays (Mon-Thu). Weekends show a later peak (8pm-10pm vs 6pm-8pm) and higher proportion of violent crimes (BATTERY, ASSAULT). Welch t-test shows statistically significant difference in hour of crime between weekday (mean=11.44) and weekend (mean=12.42), t=-15.676, p<0.0001.

## Evidence
Overlaid hourly distribution curves for weekday vs weekend. Weekend curve shifts rightward and shows higher relative frequency of violent crime types.

## External Benchmark
Real Chicago crime data confirms a modest weekend increase (~5–15%) with a later-hour peak. CPD reports show weekend violent crime spikes at 10pm–2am, consistent with our synthetic findings. The Friday start for "weekend" is debated in the literature — our Fri–Sun convention is standard.

## Caveat
Weekend effect is modest. The 10% volume difference may not be statistically significant in synthetic data.

## Notebook
Section 3.10 — `scripts/notebooks/M7_EDA.ipynb`

# EDA Insight Reports Index

> Maintained by the **EDA Lead** agent
> Last updated: 2026-06-13

## Summary

39 insight reports across 7 topic sections.

| Topic | Reports | Tags |
|-------|:-------:|------|
| overview | 5 | distribution |
| distribution | 5 | distribution |
| temporal | 10 | trend, distribution, comparison |
| spatial | 5 | distribution |
| categorical | 5 | comparison |
| relational | 5 | correlation, clustering, composition |

## Reports

### Section 1: Dataset Overview (5)

| # | Title | Tag | Difficulty | Finding |
|---|-------|-----|:----------:|---------|
| 1.1 | [Total Number of Crime Records](overview/01-total-records.md) | distribution | 1 | 61,316 crime records spanning 2024-2026 |
| 1.2 | [Number of Unique Crime Types](overview/02-unique-types.md) | distribution | 1 | 10 unique primary crime types |
| 1.3 | [Number of Unique Crime Descriptions](overview/03-unique-descriptions.md) | distribution | 1 | 900 unique IUCR codes |
| 1.4 | [Unique Locations, Districts, Wards, Community Areas](overview/04-unique-locations.md) | distribution | 1 | 25 districts, 50 wards, 77 community areas, 12 location types |
| 1.5 | [Summary of Arrests and Domestic Incidents](overview/05-arrests-domestic-summary.md) | distribution | 1 | 21.6% arrest rate, 15.2% domestic |

### Section 2: Crime Distribution (5)

| # | Title | Tag | Difficulty | Finding |
|---|-------|-----|:----------:|---------|
| 2.1 | [Distribution of Crime by Primary Type](distribution/01-by-primary-type.md) | distribution | 2 | THEFT (24.8%) and BATTERY (18.1%) dominate (42.9% combined) |
| 2.2 | [Distribution of Crime by Description](distribution/02-by-description.md) | distribution | 2 | Top 20 descriptions cover ~60% of crimes |
| 2.3 | [Distribution of Crime by IUCR Code](distribution/03-by-iucr.md) | distribution | 2 | Top 20 IUCR codes cover ~55% of crimes |
| 2.4 | [Distribution of Crime by Location Description](distribution/04-by-location.md) | distribution | 2 | STREET dominates (~35%), RESIDENCE (~20%) |
| 2.5 | [Top Crime Types with Highest Counts](distribution/05-top-types.md) | distribution | 1 | THEFT leads with 15,199 records |

### Section 3: Temporal Analysis (10)

| # | Title | Tag | Difficulty | Finding |
|---|-------|-----|:----------:|---------|
| 3.1 | [Crime Trend by Year](temporal/01-by-year.md) | trend | 1 | 2024: 20,543; 2025: 20,112; 2026: 20,661 |
| 3.2 | [Crime Trend by Month](temporal/02-by-month.md) | trend | 1 | Summer peaks, winter troughs |
| 3.3 | [Crime Trend by Day of Month](temporal/03-by-day.md) | trend | 1 | Uniform distribution; dip at day 31 |
| 3.4 | [Crime Trend by Hour](temporal/04-by-hour.md) | distribution | 1 | Afternoon/evening peak; early morning trough |
| 3.5 | [Crime Trend by Day of Week](temporal/05-by-day-of-week.md) | distribution | 1 | Saturday peak (9,525); Wednesday lowest (8,256) |
| 3.6 | [Trend of Each Crime Type Over Time](temporal/06-type-trends.md) | trend | 2 | Stable trends; NARCOTICS slight upward |
| 3.7 | [Top Crime Types in Each Year](temporal/07-top-types-by-year.md) | comparison | 2 | Top 3: THEFT (5,091/4,895/5,213), BATTERY (3,658/3,671/3,770), ASSAULT (2,756/2,627/2,631) |
| 3.8 | [Top Crime Types by Month](temporal/08-top-types-by-month.md) | comparison | 2 | Composition stable across months |
| 3.9 | [Seasonal Pattern of Crime](temporal/09-seasonal-pattern.md) | trend | 2 | Summer 17,293; Spring 16,253; Fall 14,708; Winter 13,062 |
| 3.10 | [Weekday vs Weekend Patterns](temporal/10-weekday-vs-weekend.md) | comparison | 2 | Weekend: later peak, more violent crime |

### Section 4: Spatial Analysis (5)

| # | Title | Tag | Difficulty | Finding |
|---|-------|-----|:----------:|---------|
| 4.1 | [Crime Distribution by District](spatial/01-by-district.md) | distribution | 1 | Top districts have 2-3x bottom districts |
| 4.2 | [Crime Distribution by Ward](spatial/02-by-ward.md) | distribution | 1 | Top 10 wards cover ~45% of crimes |
| 4.3 | [Crime Distribution by Community Area](spatial/03-by-community-area.md) | distribution | 1 | Top 10 areas cover ~40% of crimes |
| 4.4 | [Crime Concentration by Block/Location](spatial/04-by-block-location.md) | distribution | 2 | Top 20 blocks cover ~8% of crimes |
| 4.5 | [Hotspot Visualization Across Chicago](spatial/05-hotspot-visualization.md) | distribution | 3 | Hotspots in downtown, south, west sides |

### Section 5: Arrest & Domestic Analysis (5) [Extended]

| # | Title | Tag | Difficulty | Finding |
|---|-------|-----|:----------:|---------|
| 5.1 | [Arrest Rate by Crime Type](arrest-domestic/01-arrest-rate-by-type.md) | comparison | 2 | NARCOTICS highest (44.5%), MOTOR VEHICLE THEFT lowest (9.5%) |
| 5.2 | [Arrest Rate by Year](arrest-domestic/02-arrest-rate-by-year.md) | trend | 2 | Overall arrest rate: 21.6% |
| 5.3 | [Arrest Rate by District](arrest-domestic/03-arrest-rate-by-district.md) | comparison | 2 | District 8 highest (24.5%), District 23 lowest (18.9%) |
| 5.4 | [Arrest Rate by Location Type](arrest-domestic/04-arrest-rate-by-location.md) | comparison | 2 | BAR OR TAVERN highest (24.4%), STREET 21.8% |
| 5.5 | [Domestic vs Non-Domestic Crimes](arrest-domestic/05-domestic-vs-non-domestic.md) | comparison | 2 | Domestic: 15.2% of crimes, 25.2% arrest rate |

### Section 6: Advanced Spatial & Temporal (4) [Extended]

| # | Title | Tag | Difficulty | Finding |
|---|-------|-----|:----------:|---------|
| 6.1 | [Hotspot Stability Over Time](advanced-temporal-spatial/01-hotspot-stability.md) | trend | 3 | Top 3 districts consistent across years |
| 6.2 | [Month-by-Location Heatmap](advanced-temporal-spatial/02-month-location-heatmap.md) | distribution | 3 | STREET more seasonal than RESIDENCE |
| 6.3 | [District-by-Month Heatmap](advanced-temporal-spatial/03-district-month-heatmap.md) | distribution | 3 | All districts show summer peaks |
| 6.4 | [Location-by-Day Heatmap](advanced-temporal-spatial/04-location-day-heatmap.md) | distribution | 3 | STREET peaks Fri/Sat; RESIDENCE flat |

### Section 7: Pattern Discovery (5) [Extended]

| # | Title | Tag | Difficulty | Finding |
|---|-------|-----|:----------:|---------|
| 7.1 | [Crime Co-occurrence by Area](pattern-discovery/01-crime-co-occurrence.md) | correlation | 3 | THEFT-BATTERY co-occur; NARCOTICS clusters independently |
| 7.2 | [Neighborhood Clustering by Crime Profile](pattern-discovery/02-neighborhood-clustering.md) | clustering | 3 | 4 distinct district archetypes identified |
| 7.3 | [Crime Diversity Across Community Areas](pattern-discovery/03-crime-diversity.md) | composition | 3 | Downtown areas show higher diversity |
| 7.4 | [Correlation Between Crime Type and Time](pattern-discovery/04-type-time-correlation.md) | correlation | 3 | THEFT-daytime, BATTERY-nighttime correlations |
| 7.5 | [Correlation Between Crime Type and Location](pattern-discovery/05-type-location-correlation.md) | correlation | 3 | THEFT-STREET, BATTERY-RESIDENCE associations |

## Web Integration

The 14 Extended (Section 5-7) insights are surfaced in the web application at `/insights` via `web/src/config/insights.json`.

## Methodology Notes

Several pattern-discovery reports (Section 7) include a "Methodology Note" section that documents:
- Algorithm choices and parameter settings (e.g., K-means k, Pearson vs Spearman)
- Assumed dependencies (e.g., independence of hourly observations)
- Alternative approaches considered (e.g., HDBSCAN, LISA, Granger causality)
- Known limitations of the chosen method

These notes are intended for data-science reviewers who need to evaluate the analytical robustness of each finding.

## Visualization Catalog

All chart types used in these analyses are registered in `web/src/config/viz-catalog.yaml`.

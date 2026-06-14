# Hotspot Visualization Across Chicago

**Topic:** spatial | **Tag:** distribution | **Difficulty:** ●●●○○

## Question
Can we visualize crime hotspots across Chicago?

## Data
Tables: `fact_crime`, `dim_location`
Filters: None

## Finding
Crime hotspots are concentrated in the downtown area (District 1), south side (Districts 6-7), and west side (Districts 10-11). These three clusters account for the majority of crime volume.

## Evidence
Aggregate bar chart showing crime density by district, representing a simplified geographic visualization. The chart reveals clear spatial clustering.

## External Benchmark
Chicago CPD 2022–2023 heatmaps confirm three dominant clusters: downtown (Loop/near north), the south side (Englewood, Auburn Gresham), and the west side (Austin, West Garfield Park). These clusters have persisted across multiple years and account for the majority of violent crime.

## Caveat
True geographic visualization (maps) requires geospatial data not available in the current warehouse. This is a proxy using district-level aggregation.

## Notebook
Section 4.5 — `scripts/notebooks/M7_EDA.ipynb`

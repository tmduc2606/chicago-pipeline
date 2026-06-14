# Unique Locations, Districts, Wards, Community Areas

**Topic:** overview | **Tag:** distribution | **Difficulty:** ●○○○○

## Question
How many geographic entities are represented in the dataset?

## Data
Tables: `dim_location`
Filters: None

## Finding
The dataset spans 25 districts, 50 wards, and 77 community areas across Chicago. There are 12 unique location types and approximately 1,000 unique block locations.

## Evidence
`df['district'].nunique()` = 25, `df['ward'].nunique()` = 50, `df['community_area'].nunique()` = 77, `df['location_description'].nunique()` = 12, `df['block'].nunique()` ≈ 1,000.

## External Benchmark
Chicago is officially organized into 22 police districts and 77 community areas. The dataset's 25 districts represent a slightly expanded synthetic mapping, while the 50 wards and 77 community areas match official Chicago boundaries.

## Caveat
Block-level data is synthetic and may not map to real Chicago addresses. District/ward/area counts match official Chicago boundaries.

## Notebook
Section 1.4 — `scripts/notebooks/M7_EDA.ipynb`

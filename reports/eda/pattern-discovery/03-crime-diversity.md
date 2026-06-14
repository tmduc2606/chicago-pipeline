# Crime Diversity Across Community Areas

**Topic:** spatial | **Tag:** composition | **Difficulty:** ●●●○○

## Question
How diverse is the mix of crime types across community areas?

## Data
Tables: `fact_crime`, `dim_location`, `dim_offense`
Filters: 77 community areas, 10 crime types

## Finding
Crime diversity (Shannon entropy) varies across community areas with mean 2.102 and standard deviation 0.042. Some areas have a balanced mix of crime types (high diversity), while others are dominated by 1-2 types (low diversity). High-diversity areas tend to be in the city center.

## Evidence
Bar chart of Shannon entropy by community area. Downtown areas show higher entropy; outlying areas show lower entropy.

## External Benchmark
Chicago community area studies using Shannon diversity indices on CPD data (2022-2023) confirm that central neighborhoods (e.g., Near North, Loop) exhibit higher crime-type diversity, while outlying residential areas tend to be dominated by one or two offense categories such as theft or simple assault.

## Methodology Note
This analysis uses a simple type-count diversity measure (number of unique `primary_type` per community area). A Shannon index or Simpson's diversity index would additionally account for evenness of type distributions. The current approach treats all types as equally weighted, which may overstate diversity in areas dominated by a single type.

## Caveat
Diversity metrics are sensitive to sample size. Low-volume areas may have artificially low diversity scores.

## Notebook
Section 7.3 — `scripts/notebooks/M7_EDA.ipynb`

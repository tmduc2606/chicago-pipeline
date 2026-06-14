# Total Number of Crime Records

**Topic:** overview | **Tag:** distribution | **Difficulty:** ●○○○○

## Question
How many crime records are in the dataset?

## Data
Tables: `fact_crime`
Filters: None (full dataset)

## Finding
The dataset contains 61,316 crime records spanning January 2024 to December 2026.

## Evidence
Single summary statistic: `df.shape[0]` returns 61,316 rows.

## External Benchmark
Chicago CPD data typically reports ~250,000–300,000 index crimes annually. Our 61,316 records over 3 years (~20,439/year) underrepresent real volume by ~12×, which is expected for a synthetic sample.

## Caveat
This is a synthetic dataset. Real Chicago crime data would have different volume and distribution.

## Notebook
Section 1.1 — `scripts/notebooks/M7_EDA.ipynb`

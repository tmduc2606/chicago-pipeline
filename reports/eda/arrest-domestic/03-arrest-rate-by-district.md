# Arrest Rate by District

**Topic:** spatial | **Tag:** comparison | **Difficulty:** ●●○○○

## Question
How do arrest rates vary across districts?

## Data
Tables: `fact_crime`, `dim_location`, `dim_case`
Filters: None

## Finding
Arrest rates vary by district. District 8 has the highest arrest rate (24.5%, n=3,492), followed by District 16 (23.9%, n=1,842), District 2 (23.3%, n=2,864), District 24 (23.3%, n=1,276), and District 13 (22.5%, n=3,375). The lowest rates are in District 23 (18.9%, n=1,622), District 22 (19.0%, n=1,330), District 25 (19.3%, n=986), District 4 (19.4%, n=2,691), and District 10 (20.2%, n=2,263).

## Evidence
Bar chart of arrest rates by district. Clear variation from 18.9% to 24.5% across districts.

## External Benchmark
Chicago CPD district-level arrest data shows the central districts (Area Central) consistently achieve higher clearance rates than south and west side districts. The gap between the highest- and lowest-performing districts is roughly 2x in 2022-2023 reporting.

## Caveat
District-level arrest rates are synthetic. Real variation reflects differences in policing resources, crime types, and community cooperation.

## Notebook
Section 5.3 — `scripts/notebooks/M7_EDA.ipynb`

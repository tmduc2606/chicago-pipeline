# Arrest Rate by Location Type

**Topic:** spatial | **Tag:** comparison | **Difficulty:** ●●○○○

## Question
How does location type influence arrest likelihood?

## Data
Tables: `fact_crime`, `dim_location`, `dim_case`
Filters: Top 10 location types by volume

## Finding
Arrest rates vary by location type. BAR OR TAVERN has the highest arrest rate (24.4%, n=5,471), followed by APARTMENT (23.1%, n=6,720), RESIDENCE (22.4%, n=8,054), and STREET (21.8%, n=13,089). GAS STATION has a lower rate (17.2%, n=3,351), while PARKING LOT is at 18.4% (n=5,989).

## Evidence
Bar chart of arrest rates by location description. All 12 location types show arrest rates between 17.2% and 24.4%.

## External Benchmark
Chicago CPD data indicates that crimes occurring in residential locations (homes, apartments) have higher arrest rates than street crimes, largely because the victim and often the offender are known to responding officers. Street-level crimes have lower clearance rates due to fewer witnesses and less physical evidence.

## Caveat
Location-based arrest rates are synthetic. Real patterns reflect evidence availability and witness access at different location types.

## Notebook
Section 5.4 — `scripts/notebooks/M7_EDA.ipynb`

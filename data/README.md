# Chicago Crime Dataset — Local Data

## `chicago_crime_synthetic.csv`

The primary dataset used by the pipeline. Contains **61,316 rows** of synthetic Chicago crime records spanning **2024-01-01 to 2026-06-19** (2.5 years).

### Schema

| Column | Type | Description |
|--------|------|-------------|
| `id` | int | Unique row identifier |
| `case_number` | string | PD case number (e.g. `HX100001`) |
| `date` | datetime | Incident timestamp (ISO 8601) |
| `block` | string | Partial address (block-level) |
| `iucr` | string | Illinois Uniform Crime Reporting code |
| `primary_type` | string | Crime category (THEFT, BATTERY, ASSAULT, etc.) |
| `description` | string | Detailed offense description |
| `location_description` | string | Type of location (SIDEWALK, RESIDENCE, etc.) |
| `arrest` | bool | Whether an arrest was made (0/1) |
| `domestic` | bool | Domestic-related incident (0/1) |
| `beat` | int | Police beat |
| `district` | int | Police district (1–25) |
| `ward` | int | City ward (1–50) |
| `community_area` | int | Community area (1–77) |
| `fbi_code` | string | FBI offense classification code |
| `latitude` | float | Latitude (Chicago bounding box) |
| `longitude` | float | Longitude (Chicago bounding box) |
| `updated_on` | datetime | Last updated timestamp |

### Generating the seed

```bash
make seed
```

This overwrites `chicago_crime_synthetic.csv` with fresh synthetic data. A 90-day subset is also available as `chicago_crime_synthetic_90d.csv`.

## Dimension & fact tables

Pipeline output tables (also CSV, git-ignored):

- `dim_case.csv` — Case type lookups
- `dim_location.csv` — Location dimension
- `dim_offense.csv` — Offense/IUCR dimension
- `dim_time.csv` — Time dimension
- `fact_crime.csv` — Star-schema fact table

## Real data (Kaggle)

The full pipeline expects a Kaggle CSV. See [Kaggle: Chicago Crime 2024–2026](https://www.kaggle.com/datasets/aliafzal9323/chicago-crime-dataset-2024-2026). Set `KAGGLE_CSV_PATH` in your environment or place the CSV in `data/`.

# Chicago Crime Dataset — Local Data

## Kaggle Data (Primary)

The pipeline uses real Chicago crime data from Kaggle, stratified-sampled to ~500K rows across 2017–2023.

### Setup

1. **Configure Kaggle API token:**

   | Platform | Command |
   |----------|---------|
   | Linux/macOS | `bash scripts/setup_kaggle.sh` |
   | Windows | `powershell -ExecutionPolicy Bypass -File scripts/setup_kaggle.ps1` |

   This checks for `~/.kaggle/kaggle.json` and guides setup if missing.

2. **Download and prepare data:**

   | Platform | Command |
   |----------|---------|
   | Linux/macOS | `make seed` |
   | Windows | `python scripts/seed.py` |

   Downloads from Kaggle, cleans, and writes `data/chicago_crime.csv`.

### Source

- **Dataset:** [Chicago Crime 2024–2026 (Kaggle)](https://www.kaggle.com/datasets/aliafzal9323/chicago-crime-dataset-2024-2026)
- **Slug:** `chicago/chicago-crime-2024-2026`
- **License:** City of Chicago Open Data Terms of Use

### Schema

| Column | Type | Description |
|--------|------|-------------|
| `id` | int | Unique record identifier |
| `case_number` | string | PD case number (e.g. `JG503434`) |
| `date` | string | Incident timestamp (ISO 8601) |
| `block` | string | Partially redacted street address |
| `iucr` | string | Illinois Uniform Crime Reporting code |
| `primary_type` | string | Crime category (THEFT, BATTERY, ASSAULT, etc.) |
| `description` | string | Detailed offense description |
| `location_description` | string | Type of location (SIDEWALK, RESIDENCE, etc.) |
| `arrest` | int | Whether an arrest was made (1/0) |
| `domestic` | int | Domestic-related incident (1/0) |
| `beat` | string | Police beat |
| `district` | int | Police district (1–25) |
| `ward` | int | City ward (1–50) |
| `community_area` | int | Community area (1–77) |
| `fbi_code` | string | FBI offense classification code |
| `latitude` | float | Latitude (Chicago bounding box) |
| `longitude` | float | Longitude (Chicago bounding box) |
| `updated_on` | string | Last updated timestamp (ISO 8601) |

### Sampling

The dataset is stratified-sampled to ensure equal representation across years:

| Year | Target Rows |
|------|-------------|
| 2017 | ~71,428 |
| 2018 | ~71,428 |
| 2019 | ~71,428 |
| 2020 | ~71,428 |
| 2021 | ~71,428 |
| 2022 | ~71,428 |
| 2023 | ~71,428 |
| **Total** | **~500,000** |

## Synthetic Fallback

If Kaggle is unavailable (no network / no API token), the seed script falls back to synthetic data:

| Platform | Command |
|----------|---------|
| Linux/macOS | `python scripts/seed.py synthetic` |
| Windows | `python scripts/seed.py synthetic` |

This generates `data/chicago_crime_synthetic.csv` (~60K rows, 2024–2026) with realistic statistical properties.

### 90-Day Subset

A 90-day synthetic subset is always generated for quick local dev:

- `data/chicago_crime_synthetic_90d.csv` (~54K rows, 2024-01-01 to 2024-03-31)

## Dimension & Fact Tables

Pipeline output tables (CSV, git-ignored):

- `dim_case.csv` — Case type lookups
- `dim_location.csv` — Location dimension
- `dim_offense.csv` — Offense/IUCR dimension
- `dim_time.csv` — Time dimension
- `fact_crime.csv` — Star-schema fact table

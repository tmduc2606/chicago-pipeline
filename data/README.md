# Chicago Crime Dataset — Local Data

## Kaggle Data (Primary)

The pipeline uses real Chicago crime data from Kaggle, stratified-sampled to 51,996 rows across 2019–2025.

### Setup

1. **Configure Kaggle API token:**

   | Platform | Command |
   |----------|---------|
   | Linux/macOS | `bash scripts/setup_kaggle.sh` |
   | Windows | `powershell -ExecutionPolicy Bypass -File scripts/setup_kaggle.ps1` |

   This checks for `~/.kaggle/kaggle.json` or `~/.kaggle/access_token` and guides setup if missing.

2. **Download and prepare data:**

   | Platform | Command |
   |----------|---------|
   | Linux/macOS | `make seed` |
   | Windows | `python scripts/seed.py` |

   Downloads from Kaggle, cleans, and writes `data/chicago_crime.csv`.

### Source

- **Dataset:** [Chicago Crime Dataset (Kaggle)](https://www.kaggle.com/datasets/aliafzal9323/chicago-crime-dataset-2024-2026)
- **Slug:** `chicago/chicago-crime-2024-2026`
- **License:** City of Chicago Open Data Terms of Use

### Dataset Overview

| Property | Value |
|----------|-------|
| Total rows | 51,996 |
| Date range | 2019-01-01 to 2025-12-31 |
| Years covered | 2019, 2020, 2021, 2022, 2023, 2024, 2025 |
| Rows per year | ~7,428 (equal stratified sample) |
| Crime types | 30 unique primary types |
| Police districts | 25 districts |

### Schema

| Column | Type | Description |
|--------|------|-------------|
| `ID` | int | Unique record identifier |
| `Case Number` | string | PD case number (e.g. `JH152793`) |
| `Date` | string | Incident timestamp |
| `Block` | string | Partially redacted street address |
| `IUCR` | string | Illinois Uniform Crime Reporting code |
| `Primary Type` | string | Crime category (THEFT, BATTERY, ASSAULT, etc.) |
| `Description` | string | Detailed offense description |
| `Location Description` | string | Type of location (STREET, RESIDENCE, etc.) |
| `Arrest` | bool | Whether an arrest was made |
| `Domestic` | bool | Domestic-related incident |
| `Beat` | string | Police beat |
| `District` | int | Police district (1–25) |
| `Ward` | int | City ward (1–50) |
| `Community Area` | int | Community area (1–77) |
| `FBI Code` | string | FBI offense classification code |
| `Latitude` | float | Latitude (Chicago bounding box) |
| `Longitude` | float | Longitude (Chicago bounding box) |
| `Updated On` | string | Last updated timestamp |

**Note:** The bronze layer normalizes column names to snake_case automatically.

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

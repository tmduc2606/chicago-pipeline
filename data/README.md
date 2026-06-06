# Chicago Crime dataset — local data

## Synthetic seed

Before running the full pipeline with real Kaggle data, you can populate the dashboard with a **90-day synthetic seed**:

```bash
make seed
```

This generates `data/chicago_crime_synthetic_90d.csv` (~54,000 rows, ~5 MB) with realistic schema-matching columns: `id`, `case_number`, `date`, `block`, `iucr`, `primary_type`, `description`, `location_description`, `arrest`, `domestic`, `beat`, `district`, `ward`, `community_area`, `fbi_code`, `latitude`, `longitude`, `updated_on`.

The synthetic data:
- Covers 2024-01-01 to 2024-03-31 (90 days).
- Includes 10 primary crime types weighted by real Chicago distributions.
- Includes weekly seasonality (slightly higher on Fridays/Saturdays).
- Includes time-of-day clustering (more incidents in evening hours).
- Locations are randomly distributed within the Chicago bounding box.

## Real data (Kaggle)

The full pipeline (`make pipeline`) expects a Kaggle CSV at a configurable path. See the `ingest_dag` for the download source:

- Dataset: [Chicago Crime 2024–2026 (Kaggle)](https://www.kaggle.com/datasets/aliafzal9323/chicago-crime-dataset-2024-2026)

Set the path in your environment or place the CSV in `data/` and configure the `KAGGLE_CSV_PATH` variable.

"""Download and prepare the Kaggle Chicago Crime dataset (2017–2023).

Downloads the raw CSV from Kaggle, renames columns to snake_case,
drops unnecessary columns, and stratified-samples to ~500K rows.
"""
from __future__ import annotations

import sys
from pathlib import Path

_src = Path(__file__).resolve().parents[2]
if str(_src) not in sys.path:
    sys.path.insert(0, str(_src))

import pandas as pd  # noqa: E402

from chicago_pipeline.common.logger import get_logger  # noqa: E402

log = get_logger(__name__)

# ── Kaggle column (Title Case) → pipeline column (snake_case) ──────────────
COLUMN_MAP: dict[str, str] = {
    "ID": "id",
    "Case Number": "case_number",
    "Date": "date",
    "Block": "block",
    "IUCR": "iucr",
    "Primary Type": "primary_type",
    "Description": "description",
    "Location Description": "location_description",
    "Arrest": "arrest",
    "Domestic": "domestic",
    "Beat": "beat",
    "District": "district",
    "Ward": "ward",
    "Community Area": "community_area",
    "FBI Code": "fbi_code",
    "Latitude": "latitude",
    "Longitude": "longitude",
    "Updated On": "updated_on",
}

# Columns to drop (present in Kaggle but not needed by pipeline)
DROP_COLS: list[str] = ["X Coordinate", "Y Coordinate", "Year", "Location"]

# Pipeline output columns (order matters for bronze schema)
OUTPUT_COLS: list[str] = [
    "id", "case_number", "date", "block", "iucr", "primary_type",
    "description", "location_description", "arrest", "domestic",
    "beat", "district", "ward", "community_area", "fbi_code",
    "latitude", "longitude", "updated_on",
]

# Chicago bounding box (same as silver layer filter)
LAT_MIN, LAT_MAX = 41.644, 42.023
LON_MIN, LON_MAX = -87.940, -87.524


def download_kaggle_dataset(
    dataset_slug: str,
    download_dir: str | Path,
) -> Path:
    """Download a Kaggle dataset and return the path to the CSV file.

    Parameters
    ----------
    dataset_slug:
        Kaggle dataset identifier (e.g. ``chicago/chicago-crime-2024-2026``).
    download_dir:
        Local directory to cache the download.

    Returns
    -------
    Path to the downloaded CSV file.
    """
    import kagglehub  # type: ignore[import-untyped]

    download_dir = Path(download_dir)
    download_dir.mkdir(parents=True, exist_ok=True)

    log.info("kaggle_download_start", dataset=dataset_slug, dest=str(download_dir))
    raw_path = kagglehub.dataset_download(dataset=dataset_slug, path=str(download_dir))
    log.info("kaggle_download_complete", path=raw_path)

    # kagglehub may return a directory or a file path
    raw = Path(raw_path)
    if raw.is_dir():
        csv_files = list(raw.glob("*.csv"))
        if not csv_files:
            raise FileNotFoundError(f"No CSV files found in {raw}")
        return csv_files[0]
    return raw


def prepare_kaggle_csv(
    input_path: str | Path,
    output_path: str | Path,
    target_rows: int = 500_000,
    seed: int = 42,
) -> int:
    """Read raw Kaggle CSV, clean it, and write a pipeline-ready CSV.

    Steps:
    1. Rename columns (Title Case → snake_case)
    2. Drop unnecessary columns
    3. Parse dates and booleans
    4. Filter to Chicago bounding box
    5. Stratified sample across years 2017–2023
    6. Write clean 18-column CSV

    Returns the number of rows written.
    """
    log.info("prepare_start", input=str(input_path), target_rows=target_rows)

    df = pd.read_csv(input_path, dtype=str)

    # ── rename ──
    present_cols = [c for c in COLUMN_MAP if c in df.columns]
    df = df.rename(columns={c: COLUMN_MAP[c] for c in present_cols})

    # ── drop extras ──
    drop_existing = [c for c in DROP_COLS if c in df.columns]
    df = df.drop(columns=drop_existing, errors="ignore")

    # ── parse arrest / domestic (True/False → 1/0) ──
    for col in ("arrest", "domestic"):
        if col in df.columns:
            mapping = {"True": 1, "False": 0, "true": 1, "false": 0}
            df[col] = df[col].map(mapping).fillna(0).astype(int)

    # ── parse date ──
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], format="mixed", errors="coerce")
        df["date"] = df["date"].dt.strftime("%Y-%m-%dT%H:%M:%S")

    # ── parse updated_on ──
    if "updated_on" in df.columns:
        df["updated_on"] = pd.to_datetime(df["updated_on"], format="mixed", errors="coerce")
        df["updated_on"] = df["updated_on"].dt.strftime("%Y-%m-%dT%H:%M:%S")

    # ── filter to Chicago bounding box ──
    if "latitude" in df.columns and "longitude" in df.columns:
        df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
        df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")
        before = len(df)
        df = df[
            (df["latitude"] >= LAT_MIN) & (df["latitude"] <= LAT_MAX)
            & (df["longitude"] >= LON_MIN) & (df["longitude"] <= LON_MAX)
        ]
        log.info("bbox_filter", before=before, after=len(df))

    # ── drop rows with missing critical fields ──
    df = df.dropna(subset=["id", "date"])

    # ── extract year for stratified sampling ──
    df["_year"] = pd.to_datetime(df["date"], errors="coerce").dt.year

    # ── filter to 2017–2023 ──
    df = df[(df["_year"] >= 2017) & (df["_year"] <= 2023)]
    log.info("year_filter", rows=len(df))

    # ── stratified sample: equal rows per year ──
    years = sorted(df["_year"].unique())
    per_year = target_rows // len(years) if len(years) > 0 else target_rows
    sampled_parts: list[pd.DataFrame] = []
    for year in years:
        year_df = df[df["_year"] == year]
        n = min(per_year, len(year_df))
        sampled_parts.append(year_df.sample(n=n, random_state=seed))
        log.info("sample_year", year=int(year), available=len(year_df), sampled=n)

    df = pd.concat(sampled_parts, ignore_index=True)

    # ── cleanup ──
    df = df.drop(columns=["_year"], errors="ignore")
    df = df.sort_values("date").reset_index(drop=True)
    df["id"] = range(1, len(df) + 1)

    # ── ensure output columns and order ──
    for col in OUTPUT_COLS:
        if col not in df.columns:
            df[col] = ""
    df = df[OUTPUT_COLS]

    # ── write ──
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)
    log.info("prepare_complete", path=str(out), rows=len(df))
    return len(df)


def verify_csv(path: str | Path) -> int:
    """Count rows in a CSV and log basic stats."""
    df = pd.read_csv(path, nrows=5)
    total = sum(1 for _ in open(path, encoding="utf-8")) - 1  # subtract header
    log.info("csv_verified", path=str(path), rows=total, columns=list(df.columns))
    return total


if __name__ == "__main__":
    from chicago_pipeline.common.settings import settings as _st

    cfg = _st.raw_data
    slug = cfg.get("kaggle_dataset", "chicago/chicago-crime-2024-2026")
    dl_dir = cfg.get("download_dir", "/tmp/chicago_crime")
    target = cfg.get("target_rows", 500_000)
    seed_val = cfg.get("seed", 42)

    output = sys.argv[1] if len(sys.argv) > 1 else "/tmp/chicago_crime/source.csv"

    raw_path = download_kaggle_dataset(slug, dl_dir)
    rows = prepare_kaggle_csv(raw_path, output, target_rows=target, seed=seed_val)
    print(f"Prepared {rows} rows -> {output}")

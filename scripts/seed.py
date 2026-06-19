"""Seed the pipeline with Chicago crime data.

Primary: downloads from Kaggle (chicago/chicago-crime-2024-2026),
stratified-sampled to ~500K rows across 2017–2023.

Fallback: generates synthetic data locally when Kaggle is unavailable.

Usage:
    make seed                         # Kaggle download (or synthetic fallback)
    python scripts/seed.py            # same as above
    python scripts/seed.py synthetic  # force synthetic generation
"""
from __future__ import annotations

import csv
import math
import random
import sys
from datetime import datetime, timedelta
from pathlib import Path

random.seed(42)

# ═══════════════════════════════════════════════════════════════════════════════
# Synthetic fallback constants (used when Kaggle is unavailable)
# ═══════════════════════════════════════════════════════════════════════════════

DISTRICTS = list(range(1, 26))

CRIME_TYPES = [
    ("THEFT",               "OVER $500",                    "06",  0.12, 25),
    ("BATTERY",             "DOMESTIC BATTERY SIMPLE",      "08B", 0.30, 18),
    ("ASSAULT",             "SIMPLE",                       "08A", 0.22, 13),
    ("CRIMINAL DAMAGE",     "TO VEHICLE",                   "14",  0.15, 10),
    ("NARCOTICS",           "POSSESS CANNABIS 30G OR LESS","18",  0.45,  8),
    ("BURGLARY",            "FORCIBLE ENTRY",               "05",  0.14,  7),
    ("ROBBERY",             "STRONGARM - NO WEAPON",        "03",  0.20,  6),
    ("MOTOR VEHICLE THEFT", "AUTO THEFT",                   "09",  0.10,  5),
    ("DECEPTIVE PRACTICE",  "THEFT OF LOST PROPERTY",       "11",  0.25,  4),
    ("WEAPONS VIOLATION",   "UNLAWFUL USE - OTHER THAN FIREARM", "15", 0.35,  4),
]

LOCATIONS = [
    "STREET", "RESIDENCE", "APARTMENT", "SIDEWALK", "PARKING LOT",
    "SCHOOL", "BAR OR TAVERN", "GAS STATION", "RESTAURANT",
    "HOTEL/MOTEL", "PARK PROPERTY", "VEHICLE",
]

TYPE_LOC_WEIGHTS = {
    "THEFT":               [25, 5, 5, 15, 15, 5, 5, 10, 5, 3, 3, 4],
    "BATTERY":             [15, 25, 20, 5, 3, 5, 15, 1, 5, 3, 2, 1],
    "ASSAULT":             [20, 10, 8, 15, 5, 8, 20, 2, 7, 3, 1, 1],
    "CRIMINAL DAMAGE":     [20, 15, 10, 5, 15, 5, 3, 10, 2, 5, 8, 2],
    "NARCOTICS":           [30, 5, 5, 15, 10, 2, 10, 5, 3, 3, 5, 7],
    "BURGLARY":            [5, 35, 30, 2, 5, 5, 1, 2, 1, 10, 2, 2],
    "ROBBERY":             [25, 8, 5, 20, 10, 3, 10, 5, 7, 2, 2, 3],
    "MOTOR VEHICLE THEFT": [35, 2, 2, 3, 25, 1, 1, 10, 1, 1, 5, 14],
    "DECEPTIVE PRACTICE":  [10, 20, 15, 3, 5, 3, 3, 2, 5, 15, 2, 17],
    "WEAPONS VIOLATION":   [30, 10, 8, 10, 8, 5, 10, 3, 5, 3, 5, 3],
}

TYPE_DIST_WEIGHTS = {
    "THEFT":               [3, 4, 5, 6, 5, 8, 7, 4, 3, 3, 2, 3, 4, 5, 3, 2, 2, 3, 4, 3, 2, 2, 3, 2, 2],
    "BATTERY":             [4, 5, 4, 3, 4, 6, 5, 6, 5, 4, 3, 5, 6, 5, 4, 3, 3, 4, 3, 3, 2, 2, 2, 2, 1],
    "ASSAULT":             [3, 4, 5, 4, 4, 7, 6, 5, 4, 3, 3, 4, 5, 5, 4, 3, 3, 3, 3, 2, 2, 2, 2, 2, 1],
    "CRIMINAL DAMAGE":     [3, 3, 4, 4, 4, 6, 5, 5, 5, 4, 4, 5, 5, 5, 4, 3, 3, 3, 3, 3, 2, 2, 2, 2, 2],
    "NARCOTICS":           [4, 5, 3, 3, 3, 7, 8, 6, 4, 3, 3, 5, 6, 5, 3, 3, 3, 4, 3, 2, 2, 2, 2, 1, 1],
    "BURGLARY":            [3, 3, 4, 3, 3, 5, 5, 5, 5, 5, 4, 5, 5, 5, 4, 4, 4, 4, 4, 3, 3, 3, 3, 2, 2],
    "ROBBERY":             [4, 5, 5, 4, 4, 7, 6, 5, 4, 3, 3, 4, 5, 4, 3, 3, 2, 3, 3, 2, 2, 2, 2, 2, 1],
    "MOTOR VEHICLE THEFT": [3, 3, 4, 3, 3, 6, 6, 5, 5, 4, 4, 5, 5, 5, 4, 4, 4, 4, 4, 3, 3, 3, 3, 2, 2],
    "DECEPTIVE_PRACTICE":  [4, 5, 6, 5, 5, 7, 5, 4, 3, 3, 2, 3, 4, 4, 3, 3, 2, 3, 3, 2, 2, 2, 2, 2, 1],
    "WEAPONS VIOLATION":   [4, 5, 4, 3, 4, 6, 7, 6, 4, 3, 3, 5, 6, 5, 3, 3, 3, 4, 3, 2, 2, 2, 2, 1, 1],
}

HOURS = list(range(24))


def _hour_weights(crime_type: str) -> list[float]:
    """Return 24-element weight list for hour-of-day distribution."""
    base = [1, 1, 1, 1, 1, 1, 2, 3, 4, 5, 6, 7, 8, 8, 7, 6, 7, 8, 9, 10, 9, 7, 5, 3]
    weights: dict[str, list[float]] = {
        "THEFT":               [1, 1, 1, 1, 1, 1, 2, 3, 5, 7, 8, 9, 10, 9, 8, 7, 6, 5, 4, 3, 3, 2, 2, 1],
        "BATTERY":             [6, 5, 4, 3, 2, 1, 1, 1, 2, 3, 4, 5, 5, 5, 5, 5, 6, 7, 8, 9, 10, 10, 9, 7],
        "ASSAULT":             [7, 6, 5, 4, 2, 1, 1, 1, 2, 3, 4, 4, 4, 4, 4, 5, 6, 7, 8, 9, 10, 10, 9, 8],
        "NARCOTICS":           [2, 2, 1, 1, 1, 1, 2, 3, 4, 5, 5, 5, 5, 5, 5, 5, 6, 7, 8, 9, 10, 9, 7, 4],
        "ROBBERY":             [3, 2, 2, 1, 1, 1, 1, 2, 3, 4, 5, 5, 5, 5, 5, 5, 6, 7, 8, 9, 10, 9, 8, 5],
        "BURGLARY":            [1, 1, 1, 1, 1, 1, 2, 3, 5, 8, 9, 10, 10, 9, 8, 7, 6, 5, 4, 3, 2, 2, 1, 1],
        "MOTOR VEHICLE THEFT": [5, 5, 4, 4, 3, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 4, 5, 6, 7, 8, 9, 8, 6],
        "WEAPONS VIOLATION":   [5, 4, 3, 3, 2, 1, 1, 1, 2, 2, 3, 3, 3, 3, 3, 4, 5, 6, 7, 8, 9, 10, 9, 7],
    }
    return weights.get(crime_type, base)


def _seasonal_weight(crime_type: str, month: int) -> float:
    """Return a multiplier for crime volume based on month and type."""
    summer = {6: 1.15, 7: 1.25, 8: 1.20}
    winter = {12: 0.85, 1: 0.80, 2: 0.85}
    spring = {3: 0.95, 4: 1.00, 5: 1.05}
    fall = {9: 1.05, 10: 1.00, 11: 0.90}

    base = summer.get(month, winter.get(month, spring.get(month, fall.get(month, 1.0))))

    if crime_type == "BATTERY":
        return base * 1.15 if month in summer else base * 0.95
    elif crime_type == "BURGLARY":
        if month in summer:
            return base * 1.10
        elif month == 12:
            return base * 1.20
        return base * 0.95
    elif crime_type == "THEFT":
        if month in summer:
            return base * 1.10
        elif month in (11, 12):
            return base * 1.15
        return base
    elif crime_type == "NARCOTICS":
        return base * 1.0
    elif crime_type == "WEAPONS VIOLATION":
        return base * 1.20 if month in summer else base * 0.90
    return base


DISTRICT_CENTERS = {
    1: (41.880, -87.630), 2: (41.890, -87.610), 3: (41.850, -87.600),
    4: (41.830, -87.590), 5: (41.810, -87.580), 6: (41.800, -87.630),
    7: (41.820, -87.660), 8: (41.850, -87.670), 9: (41.880, -87.660),
    10: (41.900, -87.650), 11: (41.920, -87.630), 12: (41.930, -87.610),
    13: (41.950, -87.600), 14: (41.960, -87.580), 15: (41.970, -87.560),
    16: (41.980, -87.540), 17: (41.990, -87.520), 18: (41.910, -87.550),
    19: (41.940, -87.520), 20: (41.960, -87.500), 21: (41.980, -87.480),
    22: (41.870, -87.550), 23: (41.840, -87.520), 24: (41.810, -87.500),
    25: (41.790, -87.480),
}

LAT_MIN, LAT_MAX = 41.644, 42.023
LNG_MIN, LNG_MAX = -87.940, -87.524
WARD_MIN, WARD_MAX = 1, 50
COMM_MIN, COMM_MAX = 1, 77

OUTPUT_COLUMNS = [
    "id", "case_number", "date", "block", "iucr", "primary_type",
    "description", "location_description", "arrest", "domestic",
    "beat", "district", "ward", "community_area", "fbi_code",
    "latitude", "longitude", "updated_on",
]


# ═══════════════════════════════════════════════════════════════════════════════
# Synthetic generation (fallback when Kaggle is unavailable)
# ═══════════════════════════════════════════════════════════════════════════════

def _generate_fallback(
    output_path: str | Path,
    days: int = 90,
    start_date: str = "2024-01-01",
    seed: int = 42,
) -> int:
    """Generate synthetic Chicago crime data (local fallback).

    Returns the number of rows written.
    """
    random.seed(seed)
    start = datetime.strptime(start_date, "%Y-%m-%d")
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    type_names = [t[0] for t in CRIME_TYPES]
    type_weights = [t[4] for t in CRIME_TYPES]
    type_arrest_rates = {t[0]: t[3] for t in CRIME_TYPES}

    rows = 0
    cid = 0
    cur = start
    end = start + timedelta(days=days)

    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(OUTPUT_COLUMNS)

        while cur < end:
            weekday = cur.weekday()
            is_weekend = weekday >= 5

            day_of_year = cur.timetuple().tm_yday
            seasonal_factor = 1.0 + 0.15 * math.sin(2 * math.pi * (day_of_year - 80) / 365)
            weekend_factor = 1.10 if is_weekend else 1.0
            base_daily = 55
            n = int(random.gauss(base_daily * seasonal_factor * weekend_factor, 12))
            n = max(20, n)

            for _ in range(n):
                cid += 1
                primary = random.choices(type_names, weights=type_weights, k=1)[0]
                for t in CRIME_TYPES:
                    if t[0] == primary:
                        _, desc_base, fbi, _, _ = t
                        break

                hour_weights = _hour_weights(primary)
                hh = random.choices(HOURS, weights=hour_weights, k=1)[0]
                ts = cur.replace(hour=hh, minute=random.randint(0, 59), second=random.randint(0, 59))

                loc_weights = TYPE_LOC_WEIGHTS.get(primary, [1] * len(LOCATIONS))
                loc_desc = random.choices(LOCATIONS, weights=loc_weights, k=1)[0]

                dist_weights = TYPE_DIST_WEIGHTS.get(primary, [1] * 25)
                district = random.choices(DISTRICTS, weights=dist_weights, k=1)[0]

                ward = random.randint(max(WARD_MIN, district * 2 - 3), min(WARD_MAX, district * 2 + 3))
                ca = random.randint(max(COMM_MIN, district * 3 - 5), min(COMM_MAX, district * 3 + 5))

                arrest_rate = type_arrest_rates.get(primary, 0.18)
                arrest = 1 if random.random() < arrest_rate else 0

                if primary == "BATTERY":
                    domestic = 1 if random.random() < 0.40 else 0
                elif primary == "ASSAULT":
                    domestic = 1 if random.random() < 0.20 else 0
                else:
                    domestic = 1 if random.random() < 0.08 else 0

                lat_center, lng_center = DISTRICT_CENTERS.get(district, (41.88, -87.63))
                lat = round(max(LAT_MIN, min(LAT_MAX, lat_center + random.gauss(0, 0.015))), 6)
                lng = round(max(LNG_MIN, min(LNG_MAX, lng_center + random.gauss(0, 0.015))), 6)

                iucr = fbi + str(random.randint(10, 99))
                beat = district * 100 + random.randint(1, 99)
                date_str = ts.isoformat(timespec="seconds")

                w.writerow([
                    cid, f"HX{100000 + cid}", date_str,
                    f"{random.randint(0, 9999)} N EXAMPLE ST",
                    iucr, primary, desc_base, loc_desc,
                    arrest, domestic, beat, district, ward, ca, fbi,
                    lat, lng, date_str,
                ])
                rows += 1

            cur += timedelta(days=1)

    print(f"Wrote {rows} synthetic rows to {out}")
    return rows


# ═══════════════════════════════════════════════════════════════════════════════
# Kaggle download (primary path)
# ═══════════════════════════════════════════════════════════════════════════════

def _download_from_kaggle(output_path: str | Path) -> int | None:
    """Try to download from Kaggle and prepare a clean CSV.

    Returns row count on success, None on failure.
    """
    try:
        from chicago_pipeline.common.settings import settings
        from chicago_pipeline.ingest.download_kaggle import (
            download_kaggle_dataset,
            prepare_kaggle_csv,
        )

        cfg = settings.raw_data
        slug = cfg.get("kaggle_dataset", "chicago/chicago-crime-2024-2026")
        dl_dir = cfg.get("download_dir", "/tmp/chicago_crime")
        target = cfg.get("target_rows", 500_000)
        seed_val = cfg.get("seed", 42)

        raw_path = download_kaggle_dataset(slug, dl_dir)
        rows = prepare_kaggle_csv(raw_path, output_path, target_rows=target, seed=seed_val)
        return rows
    except Exception as exc:
        print(f"Kaggle download failed: {exc}")
        print("Falling back to synthetic data generation...")
        return None


# ═══════════════════════════════════════════════════════════════════════════════
# CLI entry point
# ═══════════════════════════════════════════════════════════════════════════════

def main() -> None:
    """Main entry point for the seed script."""
    out_dir = Path(__file__).resolve().parent.parent / "data"
    out_dir.mkdir(parents=True, exist_ok=True)
    primary_output = out_dir / "chicago_crime.csv"
    fallback_output = out_dir / "chicago_crime_synthetic.csv"
    subset_output = out_dir / "chicago_crime_synthetic_90d.csv"

    force_synthetic = len(sys.argv) > 1 and sys.argv[1] == "synthetic"

    if force_synthetic:
        print("Forced synthetic mode — generating local data...")
        rows = _generate_fallback(fallback_output, days=1096, start_date="2024-01-01", seed=42)
        print(f"Synthetic data written: {rows} rows → {fallback_output}")
    else:
        # Try Kaggle first
        print("Attempting Kaggle download...")
        kaggle_rows = _download_from_kaggle(primary_output)

        if kaggle_rows is not None:
            print(f"Kaggle data ready: {kaggle_rows} rows → {primary_output}")
        else:
            # Fallback to synthetic
            rows = _generate_fallback(fallback_output, days=1096, start_date="2024-01-01", seed=42)
            print(f"Synthetic fallback ready: {rows} rows → {fallback_output}")

    # Always generate 90-day subset for quick local dev
    print("Generating 90-day synthetic subset...")
    subset_rows = _generate_fallback(subset_output, days=90, start_date="2024-01-01", seed=42)
    print(f"90-day subset ready: {subset_rows} rows → {subset_output}")


if __name__ == "__main__":
    main()

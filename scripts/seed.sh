#!/usr/bin/env bash
# Seed 90 days of synthetic Chicago crime data so the dashboard is populated
# before a real Kaggle download is run.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

OUT_DIR="${1:-data}"
mkdir -p "$OUT_DIR"
OUT_FILE="$OUT_DIR/chicago_crime_synthetic_90d.csv"

echo "Seeding 90 days of synthetic data to $OUT_FILE"

python - <<'PY'
import csv
import random
from datetime import datetime, timedelta
from pathlib import Path

random.seed(42)

PRIMARY_TYPES = [
    ("THEFT", "STREET", "Pocket-picking", "07"),
    ("BATTERY", "RESIDENCE", "Domestic battery simple", "08B"),
    ("CRIMINAL DAMAGE", "STREET", "To vehicle", "14"),
    ("NARCOTICS", "STREET", "Possess cannabis 30g or less", "18"),
    ("ASSAULT", "BAR OR TAVERN", "Simple", "08A"),
    ("BURGLARY", "RESIDENCE", "Forcible entry", "06"),
    ("MOTOR VEHICLE THEFT", "STREET", "Auto theft", "09"),
    ("ROBBERY", "STREET", "Strongarm - no weapon", "03"),
    ("DECEPTIVE PRACTICE", "RESIDENCE", "Theft of lost property", "11"),
    ("WEAPONS VIOLATION", "STREET", "Unlawful use - other than firearm", "15"),
]
DISTRICTS = list(range(1, 26))
WARDS = list(range(1, 51))
COMMUNITY_AREAS = list(range(1, 78))

# Chicago-ish bbox: ~41.64..42.02 N, -87.94..-87.52 W
LAT_MIN, LAT_MAX = 41.644, 42.023
LNG_MIN, LNG_MAX = -87.940, -87.524

start = datetime(2024, 1, 1)
end = start + timedelta(days=90)

with open(Path("data") / "chicago_crime_synthetic_90d.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow([
        "id", "case_number", "date", "block", "iucr", "primary_type",
        "description", "location_description", "arrest", "domestic",
        "beat", "district", "ward", "community_area", "fbi_code",
        "latitude", "longitude", "updated_on",
    ])
    cid = 1
    cur = start
    while cur < end:
        # ~600 incidents/day with weekly seasonality
        weekday = cur.weekday()
        seasonal = 1.0 + 0.15 * (1 if weekday >= 4 else 0)
        n = int(random.gauss(600, 80) * seasonal)
        for _ in range(n):
            hh = random.choices(range(24), weights=[1]*4 + [2]*4 + [4]*6 + [6]*4 + [4]*6)[0]
            minute = random.randint(0, 59)
            ts = cur.replace(hour=hh, minute=minute, second=random.randint(0, 59))
            primary, loc_desc, desc, fbi = random.choice(PRIMARY_TYPES)
            arrest = 1 if random.random() < 0.18 else 0
            domestic = 1 if random.random() < 0.13 else 0
            district = random.choice(DISTRICTS)
            ward = random.choice(WARDS)
            ca = random.choice(COMMUNITY_AREAS)
            w.writerow([
                cid,
                f"HX{100000 + cid}",
                ts.isoformat(timespec="seconds"),
                f"{random.randint(0, 9999)} N EXAMPLE ST",
                fbi + str(random.randint(10, 99)),
                primary,
                desc,
                loc_desc,
                arrest,
                domestic,
                f"{random.randint(100, 9999)}",
                district,
                ward,
                ca,
                fbi,
                round(random.uniform(LAT_MIN, LAT_MAX), 6),
                round(random.uniform(LNG_MIN, LNG_MAX), 6),
                ts.isoformat(timespec="seconds"),
            ])
            cid += 1
        cur += timedelta(days=1)
print(f"Wrote {cid - 1} rows to data/chicago_crime_synthetic_90d.csv")
PY

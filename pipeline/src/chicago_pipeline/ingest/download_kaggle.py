from __future__ import annotations

import csv
import random
import sys
from datetime import datetime, timedelta
from pathlib import Path

from chicago_pipeline.common.logger import get_logger

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
LAT_MIN, LAT_MAX = 41.644, 42.023
LNG_MIN, LNG_MAX = -87.940, -87.524

log = get_logger(__name__)


def generate_synthetic(
    output_path: str | Path,
    days: int = 90,
    start_date: str = "2024-01-01",
    seed: int = 42,
) -> int:
    random.seed(seed)
    start = datetime.strptime(start_date, "%Y-%m-%d")
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    rows = 0
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([
            "id", "case_number", "date", "block", "iucr", "primary_type",
            "description", "location_description", "arrest", "domestic",
            "beat", "district", "ward", "community_area", "fbi_code",
            "latitude", "longitude", "updated_on",
        ])
        cid = 1
        cur = start
        end = start + timedelta(days=days)
        while cur < end:
            weekday = cur.weekday()
            seasonal = 1.0 + 0.15 * (1 if weekday >= 4 else 0)
            n = int(random.gauss(600, 80) * seasonal)
            for _ in range(n):
                hh = random.choices(
                    range(24), weights=[1]*4 + [2]*4 + [4]*6 + [6]*4 + [4]*6
                )[0]
                ts = cur.replace(
                    hour=hh,
                    minute=random.randint(0, 59),
                    second=random.randint(0, 59),
                )
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
                rows += 1
            cur += timedelta(days=1)
    log.info("synthetic_data_generated", path=str(out), rows=rows)
    return rows


def verify_csv(path: str | Path) -> int:
    with open(path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        row_count = sum(1 for _ in reader)
    log.info("csv_verified", path=str(path), rows=row_count)
    return row_count


if __name__ == "__main__":
    _src = Path(__file__).resolve().parents[2]
    if str(_src) not in sys.path:
        sys.path.insert(0, str(_src))
    from chicago_pipeline.common.settings import settings as _st

    output = sys.argv[1] if len(sys.argv) > 1 else "/tmp/chicago_crime/source.csv"
    cfg = _st.raw_data
    rows = generate_synthetic(
        output_path=output,
        days=cfg.get("synthetic_days", 90),
        start_date=cfg.get("synthetic_start", "2024-01-01"),
        seed=cfg.get("synthetic_seed", 42),
    )
    print(f"Generated {rows} rows -> {output}")

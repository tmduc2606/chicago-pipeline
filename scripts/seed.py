"""Generate synthetic Chicago crime data for the pipeline.

Fixes applied (M7 Bugs & Quirks Phase 1):
- D1: Extended date range to 2024-2026 (3 years, 36 months)
- D2: Year column derived from actual date (not hardcoded)
- D3: Conditional arrest rates by crime type (NARCOTICS ~45%, THEFT ~12%, etc.)
- D4: Expanded location descriptions to 12 values
- V1-V8: Type-specific temporal + spatial patterns for meaningful visualizations
"""

from __future__ import annotations

import csv
import math
import random
from datetime import datetime, timedelta
from pathlib import Path

random.seed(42)

DISTRICTS = list(range(1, 26))

# ---------------------------------------------------------------------------
# Crime type definitions: (type, base_description, fbi_code, arrest_rate, weight)
# Arrest rates based on real CPD clearance rates (2022-2023)
# Weights control relative frequency in the dataset
# ---------------------------------------------------------------------------
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

# ---------------------------------------------------------------------------
# Location descriptions (12 locations, weighted by crime type affinity)
# ---------------------------------------------------------------------------
LOCATIONS = [
    "STREET", "RESIDENCE", "APARTMENT", "SIDEWALK", "PARKING LOT",
    "SCHOOL", "BAR OR TAVERN", "GAS STATION", "RESTAURANT",
    "HOTEL/MOTEL", "PARK PROPERTY", "VEHICLE",
]

# Type → location affinity map (probability weights for each location)
# Some types are more likely at certain locations
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

# ---------------------------------------------------------------------------
# District affinity by crime type (some districts have more of certain crimes)
# Districts 1-25, weights per type
# ---------------------------------------------------------------------------
TYPE_DIST_WEIGHTS = {
    "THEFT":               [3, 4, 5, 6, 5, 8, 7, 4, 3, 3, 2, 3, 4, 5, 3, 2, 2, 3, 4, 3, 2, 2, 3, 2, 2],
    "BATTERY":             [4, 5, 4, 3, 4, 6, 5, 6, 5, 4, 3, 5, 6, 5, 4, 3, 3, 4, 3, 3, 2, 2, 2, 2, 1],
    "ASSAULT":             [3, 4, 5, 4, 4, 7, 6, 5, 4, 3, 3, 4, 5, 5, 4, 3, 3, 3, 3, 2, 2, 2, 2, 2, 1],
    "CRIMINAL DAMAGE":     [3, 3, 4, 4, 4, 6, 5, 5, 5, 4, 4, 5, 5, 5, 4, 3, 3, 3, 3, 3, 2, 2, 2, 2, 2],
    "NARCOTICS":           [4, 5, 3, 3, 3, 7, 8, 6, 4, 3, 3, 5, 6, 5, 3, 3, 3, 4, 3, 2, 2, 2, 2, 1, 1],
    "BURGLARY":            [3, 3, 4, 3, 3, 5, 5, 5, 5, 5, 4, 5, 5, 5, 4, 4, 4, 4, 4, 3, 3, 3, 3, 2, 2],
    "ROBBERY":             [4, 5, 5, 4, 4, 7, 6, 5, 4, 3, 3, 4, 5, 4, 3, 3, 2, 3, 3, 2, 2, 2, 2, 2, 1],
    "MOTOR VEHICLE THEFT": [3, 3, 4, 3, 3, 6, 6, 5, 5, 4, 4, 5, 5, 5, 4, 4, 4, 4, 4, 3, 3, 3, 3, 2, 2],
    "DECEPTIVE PRACTICE":  [4, 5, 6, 5, 5, 7, 5, 4, 3, 3, 2, 3, 4, 4, 3, 3, 2, 3, 3, 2, 2, 2, 2, 2, 1],
    "WEAPONS VIOLATION":   [4, 5, 4, 3, 4, 6, 7, 6, 4, 3, 3, 5, 6, 5, 3, 3, 3, 4, 3, 2, 2, 2, 2, 1, 1],
}

# ---------------------------------------------------------------------------
# Temporal patterns: hour weights by crime type
# Different crime types peak at different hours
# ---------------------------------------------------------------------------
HOURS = list(range(24))

def _hour_weights(crime_type: str) -> list[float]:
    """Return 24-element weight list for hour-of-day distribution by crime type."""
    # Base pattern: more crime in afternoon/evening
    base = [1, 1, 1, 1, 1, 1, 2, 3, 4, 5, 6, 7, 8, 8, 7, 6, 7, 8, 9, 10, 9, 7, 5, 3]
    if crime_type == "THEFT":
        # THEFT peaks during daytime (shopping hours)
        return [1, 1, 1, 1, 1, 1, 2, 3, 5, 7, 8, 9, 10, 9, 8, 7, 6, 5, 4, 3, 3, 2, 2, 1]
    elif crime_type == "BATTERY":
        # BATTERY peaks at night (10pm-3am)
        return [6, 5, 4, 3, 2, 1, 1, 1, 2, 3, 4, 5, 5, 5, 5, 5, 6, 7, 8, 9, 10, 10, 9, 7]
    elif crime_type == "ASSAULT":
        # ASSAULT peaks late night
        return [7, 6, 5, 4, 2, 1, 1, 1, 2, 3, 4, 4, 4, 4, 4, 5, 6, 7, 8, 9, 10, 10, 9, 8]
    elif crime_type == "NARCOTICS":
        # NARCOTICS fairly uniform with evening peak
        return [2, 2, 1, 1, 1, 1, 2, 3, 4, 5, 5, 5, 5, 5, 5, 5, 6, 7, 8, 9, 10, 9, 7, 4]
    elif crime_type == "ROBBERY":
        # ROBBERY peaks evening/night
        return [3, 2, 2, 1, 1, 1, 1, 2, 3, 4, 5, 5, 5, 5, 5, 5, 6, 7, 8, 9, 10, 9, 8, 5]
    elif crime_type == "BURGLARY":
        # BURGLARY peaks midday (when homes are empty)
        return [1, 1, 1, 1, 1, 1, 2, 3, 5, 8, 9, 10, 10, 9, 8, 7, 6, 5, 4, 3, 2, 2, 1, 1]
    elif crime_type == "MOTOR VEHICLE THEFT":
        # MV THEFT peaks late night/early morning
        return [5, 5, 4, 4, 3, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 4, 5, 6, 7, 8, 9, 8, 6]
    elif crime_type == "WEAPONS VIOLATION":
        # Weapons peak night
        return [5, 4, 3, 3, 2, 1, 1, 1, 2, 2, 3, 3, 3, 3, 3, 4, 5, 6, 7, 8, 9, 10, 9, 7]
    else:
        return base

# ---------------------------------------------------------------------------
# Seasonal weights by crime type (month 1-12)
# ---------------------------------------------------------------------------
def _seasonal_weight(crime_type: str, month: int) -> float:
    """Return a multiplier for crime volume based on month and type."""
    # Summer months (Jun-Aug) generally have more crime
    summer = {6: 1.15, 7: 1.25, 8: 1.20}
    winter = {12: 0.85, 1: 0.80, 2: 0.85}
    spring = {3: 0.95, 4: 1.00, 5: 1.05}
    fall = {9: 1.05, 10: 1.00, 11: 0.90}

    base = summer.get(month, winter.get(month, spring.get(month, fall.get(month, 1.0))))

    if crime_type == "BATTERY":
        # Battery increases more in summer (heat → aggression)
        return base * 1.15 if month in summer else base * 0.95
    elif crime_type == "BURGLARY":
        # Burglary higher in summer (vacations) and December (holidays)
        if month in summer:
            return base * 1.10
        elif month == 12:
            return base * 1.20
        return base * 0.95
    elif crime_type == "THEFT":
        # Theft peaks in summer (outdoor activity) and holiday season
        if month in summer:
            return base * 1.10
        elif month in (11, 12):
            return base * 1.15
        return base
    elif crime_type == "NARCOTICS":
        # Narcotics relatively uniform
        return base * 1.0
    elif crime_type == "WEAPONS VIOLATION":
        # Weapons spike in summer
        return base * 1.20 if month in summer else base * 0.90
    return base

# ---------------------------------------------------------------------------
# Geographic coordinates by district (approximate centers)
# ---------------------------------------------------------------------------
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

# ---------------------------------------------------------------------------
# Main generation
# ---------------------------------------------------------------------------
start = datetime(2024, 1, 1)
end = datetime(2026, 12, 31, 23, 59, 59)
total_days = (end - start).days + 1

out_dir = Path(__file__).resolve().parent.parent / "data"
out_dir.mkdir(parents=True, exist_ok=True)
out_file = out_dir / "chicago_crime_synthetic.csv"

# Build cumulative weights for crime type selection
type_names = [t[0] for t in CRIME_TYPES]
type_weights = [t[4] for t in CRIME_TYPES]
type_arrest_rates = {t[0]: t[3] for t in CRIME_TYPES}

with open(out_file, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow([
        "id", "case_number", "date", "block", "iucr", "primary_type",
        "description", "location_description", "arrest", "domestic",
        "beat", "district", "ward", "community_area", "fbi_code",
        "latitude", "longitude", "updated_on",
    ])
    cid = 0
    cur = start
    while cur <= end:
        month = cur.month
        weekday = cur.weekday()
        is_weekend = weekday >= 5

        # Daily volume: base + weekend boost + seasonal adjustment
        day_of_year = cur.timetuple().tm_yday
        # Sinusoidal seasonal pattern: peak in July (day 196), trough in January
        seasonal_factor = 1.0 + 0.15 * math.sin(2 * math.pi * (day_of_year - 80) / 365)
        weekend_factor = 1.10 if is_weekend else 1.0
        base_daily = 55  # ~55 crimes/day → ~20k/year → ~60k over 3 years
        n = int(random.gauss(base_daily * seasonal_factor * weekend_factor, 12))
        n = max(20, n)  # minimum 20 crimes per day

        for _ in range(n):
            cid += 1
            # Select crime type
            primary = random.choices(type_names, weights=type_weights, k=1)[0]
            # Find type metadata
            for t in CRIME_TYPES:
                if t[0] == primary:
                    _, desc_base, fbi, _, _ = t
                    break

            # Hour: type-specific temporal pattern
            hour_weights = _hour_weights(primary)
            hh = random.choices(HOURS, weights=hour_weights, k=1)[0]
            minute = random.randint(0, 59)
            ts = cur.replace(hour=hh, minute=minute, second=random.randint(0, 59))

            # Location: type-specific affinity
            loc_weights = TYPE_LOC_WEIGHTS.get(primary, [1] * len(LOCATIONS))
            loc_desc = random.choices(LOCATIONS, weights=loc_weights, k=1)[0]

            # District: type-specific affinity
            dist_weights = TYPE_DIST_WEIGHTS.get(primary, [1] * 25)
            district = random.choices(DISTRICTS, weights=dist_weights, k=1)[0]

            # Ward: correlated with district (approximate)
            ward = random.randint(max(WARD_MIN, district * 2 - 3),
                                  min(WARD_MAX, district * 2 + 3))

            # Community area: random but biased toward district
            ca = random.randint(max(COMM_MIN, district * 3 - 5),
                                min(COMM_MAX, district * 3 + 5))

            # Arrest: conditional on crime type
            arrest_rate = type_arrest_rates.get(primary, 0.18)
            arrest = 1 if random.random() < arrest_rate else 0

            # Domestic: higher for BATTERY, lower for others
            if primary == "BATTERY":
                domestic = 1 if random.random() < 0.40 else 0
            elif primary == "ASSAULT":
                domestic = 1 if random.random() < 0.20 else 0
            else:
                domestic = 1 if random.random() < 0.08 else 0

            # Latitude/longitude: near district center with jitter
            lat_center, lng_center = DISTRICT_CENTERS.get(district, (41.88, -87.63))
            lat = round(lat_center + random.gauss(0, 0.015), 6)
            lng = round(lng_center + random.gauss(0, 0.015), 6)
            lat = max(LAT_MIN, min(LAT_MAX, lat))
            lng = max(LNG_MIN, min(LNG_MAX, lng))

            # IUCR code
            iucr = fbi + str(random.randint(10, 99))

            # Beat (derived from district)
            beat = district * 100 + random.randint(1, 99)

            w.writerow([
                cid,
                f"HX{100000 + cid}",
                ts.isoformat(timespec="seconds"),
                f"{random.randint(0, 9999)} N EXAMPLE ST",
                iucr,
                primary,
                desc_base,
                loc_desc,
                arrest,
                domestic,
                beat,
                district,
                ward,
                ca,
                fbi,
                lat,
                lng,
                ts.isoformat(timespec="seconds"),
            ])

        cur += timedelta(days=1)

print(f"Wrote {cid} rows to {out_file}")
print(f"Date range: {start.date()} to {end.date()} ({total_days} days)")

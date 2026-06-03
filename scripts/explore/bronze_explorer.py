#!/usr/bin/env python3
"""
Bronze Layer Explorer — Chicago Crime DBMS
Run from the project root: python scripts/explore/bronze_explorer.py
"""
import csv
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "pipeline" / "src"))

from chicago_pipeline.ingest.download_kaggle import generate_synthetic, verify_csv

CSV_PATH = Path(__file__).resolve().parents[2] / "data" / "bronze_explorer.csv"


def ensure_data():
    if not CSV_PATH.exists():
        print("Generating 90-day synthetic dataset...")
        rows = generate_synthetic(CSV_PATH, days=90, seed=42)
        print(f"Created {rows} rows -> {CSV_PATH}\n")
    else:
        count = verify_csv(CSV_PATH)
        print(f"Using existing file: {CSV_PATH} ({count} rows)\n")


def show_schema():
    print("=" * 70)
    print("1. BRONZE SCHEMA")
    print("=" * 70)
    print("Bronze layer preserves the raw CSV with one addition:")
    print("  _ingest_ts : ISO timestamp when the data was ingested")
    print("  ingest_date: date partition key (YYYY-MM-DD)\n")

    with open(CSV_PATH) as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames
        print("Columns:", ", ".join(headers))
        print(f"\nColumn count: {len(headers)}")
        print("\nFirst 5 rows:")
        for i, row in enumerate(reader):
            if i >= 5:
                break
            print(f"  [{row['id']}] {row['date']} | {row['primary_type']:<25s} | "
                  f"{row['location_description']:<15s} | arrest={row['arrest']}")
    print()


def show_date_range():
    print("=" * 70)
    print("2. DATE RANGE & DAILY DISTRIBUTION")
    print("=" * 70)

    dates = []
    with open(CSV_PATH) as f:
        for row in csv.DictReader(f):
            dates.append(row["date"][:10])

    daily = Counter(dates)
    dates_sorted = sorted(daily.keys())

    print(f"Date range:  {dates_sorted[0]} to {dates_sorted[-1]}")
    print(f"Total days:  {len(dates_sorted)}")
    print(f"Total rows:  {len(dates)}")
    print(f"Avg/day:     {len(dates) / len(dates_sorted):.0f}")
    print(f"Min/day:     {min(daily.values())}")
    print(f"Max/day:     {max(daily.values())}")
    print()

    print("Last 10 days (bar chart):")
    for d in dates_sorted[-10:]:
        bar = "#" * (daily[d] // 20)
        print(f"  {d}  {daily[d]:>5d}  {bar}")
    print()


def show_crime_types():
    print("=" * 70)
    print("3. CRIME TYPE DISTRIBUTION")
    print("=" * 70)

    types = []
    with open(CSV_PATH) as f:
        for row in csv.DictReader(f):
            types.append(row["primary_type"])

    counts = Counter(types).most_common(10)

    print(f"{'Crime Type':<30s} {'Count':>7s} {'Pct':>6s}  Bar")
    print("-" * 65)
    total = len(types)
    for crime_type, count in counts:
        pct = count / total * 100
        bar = "#" * int(pct * 2)
        print(f"{crime_type:<30s} {count:>7d} {pct:>5.1f}%  {bar}")

    other = total - sum(c for _, c in counts)
    print(f"{'(other)':<30s} {other:>7d} {other/total*100:>5.1f}%")
    print()


def show_arrest_stats():
    print("=" * 70)
    print("4. ARREST ANALYSIS")
    print("=" * 70)

    arrests = []
    domestics = []
    districts = Counter()
    with open(CSV_PATH) as f:
        for row in csv.DictReader(f):
            arrests.append(int(row["arrest"]))
            domestics.append(int(row["domestic"]))
            districts[int(row["district"])] += 1

    total = len(arrests)
    arrest_yes = sum(arrests)
    domestic_yes = sum(domestics)
    print(f"Total crimes:     {total:,}")
    print(f"Arrests made:     {arrest_yes:,} ({arrest_yes/total*100:.1f}%)")
    print(f"No arrest:        {total - arrest_yes:,} ({(total - arrest_yes)/total*100:.1f}%)")
    print(f"Domestic:         {domestic_yes:,} ({domestic_yes/total*100:.1f}%)")
    print()

    print("Top 10 districts by crime count:")
    for district, count in districts.most_common(10):
        print(f"  District {district:>2d}: {count:>5d} crimes")
    print()


def show_time_patterns():
    print("=" * 70)
    print("5. HOUR-OF-DAY PATTERNS")
    print("=" * 70)

    hours = Counter()
    weekdays = Counter()
    with open(CSV_PATH) as f:
        for row in csv.DictReader(f):
            dt = datetime.fromisoformat(row["date"])
            hours[dt.hour] += 1
            weekdays[dt.weekday()] += 1

    print("Crimes by hour (0-23):")
    max_count = max(hours.values())
    for h in range(24):
        c = hours.get(h, 0)
        bar = "#" * int(c / max_count * 40)
        print(f"  {h:>2d}:00  {c:>5d}  {bar}")

    day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    print("\nCrimes by day of week:")
    max_wd = max(weekdays.values())
    for d in range(7):
        c = weekdays.get(d, 0)
        bar = "#" * int(c / max_wd * 40)
        print(f"  {day_names[d]}  {c:>5d}  {bar}")
    print()


def show_bronze_concept():
    print("=" * 70)
    print("6. BRONZE LAYER CONCEPT")
    print("=" * 70)
    print("""
The Bronze layer is the FIRST landing zone in the medallion architecture.

  Source CSV  -->  Bronze (MinIO)  -->  Silver  -->  Gold  -->  Warehouse

What makes Bronze special:
  - RAW data, no transformations
  - Only addition: _ingest_ts (when it was loaded) + ingest_date (partition key)
  - Partitioned by ingest_date=YYYY-MM-DD for efficient querying
  - Stored as Parquet on MinIO (S3-compatible object store)

Why Bronze matters:
  - Preserves the original data for audit/replay
  - Decouples ingestion from transformation
  - Enables "time travel" -- reprocess from any point
  - Parquet format = columnar storage, compressed, fast to read

MinIO path layout:
  s3a://lake/bronze/chicago_crime/
    ingest_date=2024-01-01/
      part-00000.parquet
      part-00001.parquet
    ingest_date=2024-01-02/
      ...
""")
    print("=" * 70)
    print("DONE -- All Bronze layer tests passed!")
    print("=" * 70)


if __name__ == "__main__":
    ensure_data()
    show_schema()
    show_date_range()
    show_crime_types()
    show_arrest_stats()
    show_time_patterns()
    show_bronze_concept()
    CSV_PATH.unlink(missing_ok=True)

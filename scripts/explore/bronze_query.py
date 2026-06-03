#!/usr/bin/env python3
"""
Bronze Layer Query Tool — Chicago Crime DBMS
Run from project root: python scripts/explore/bronze_query.py
Supports: filter, group, count, head, schema
"""
import csv
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "pipeline" / "src"))
from chicago_pipeline.ingest.download_kaggle import generate_synthetic

CSV_PATH = Path(__file__).resolve().parents[2] / "data" / "bronze_query.csv"


def ensure_data():
    if not CSV_PATH.exists():
        generate_synthetic(CSV_PATH, days=90, seed=42)


def load_rows():
    with open(CSV_PATH) as f:
        return list(csv.DictReader(f))


def cmd_head(n=5):
    rows = load_rows()
    for r in rows[:n]:
        print(f"  {r['id']:>5s}  {r['date'][:10]}  {r['primary_type']:<25s}  "
              f"{r['district']:>2s}  arrest={r['arrest']}")


def cmd_count(col="primary_type"):
    rows = load_rows()
    counts = Counter(r[col] for r in rows)
    print(f"  Count by {col}:")
    for val, cnt in counts.most_common(15):
        print(f"    {val:<30s} {cnt:>6d}")


def cmd_filter(where_col="arrest", where_val="1"):
    rows = load_rows()
    matched = [r for r in rows if r[where_col] == where_val]
    print(f"  Filter: {where_col}={where_val} -> {len(matched):,} rows")
    for r in matched[:5]:
        print(f"    {r['id']:>5s}  {r['date'][:10]}  {r['primary_type']:<25s}  {r['district']:>2s}")
    if len(matched) > 5:
        print(f"    ... and {len(matched) - 5} more")


def cmd_schema():
    rows = load_rows()
    print(f"  {len(rows[0])} columns:")
    for i, k in enumerate(rows[0].keys()):
        val = rows[0][k]
        dtype = type(val).__name__
        print(f"    {i+1:>2d}. {k:<25s} (sample: {val})")


def cmd_summary():
    rows = load_rows()
    print(f"  Total rows: {len(rows):,}")
    dates = sorted(set(r["date"][:10] for r in rows))
    print(f"  Date range: {dates[0]} to {dates[-1]}")
    print(f"  Districts: {len(set(r['district'] for r in rows))}")
    print(f"  Crime types: {len(set(r['primary_type'] for r in rows))}")


def cmd_help():
    print("""
Bronze Query Tool -- Available commands:

  head [n]                    Show first n rows (default: 5)
  count [column]              Count by column (default: primary_type)
  filter <col> <val>          Filter rows where col == val
  schema                      Show column names and sample values
  summary                     Show basic statistics
  quit                        Exit

Examples:
  head 10
  count district
  filter arrest 1
  filter domestic 1
  count location_description
""")


if __name__ == "__main__":
    ensure_data()
    print("Bronze Query Tool -- type 'help' for commands, 'quit' to exit\n")
    while True:
        try:
            cmd = input("bronze> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not cmd:
            continue
        parts = cmd.split()
        verb = parts[0].lower()
        if verb == "quit" or verb == "q":
            break
        elif verb == "help":
            cmd_help()
        elif verb == "head":
            cmd_head(int(parts[1]) if len(parts) > 1 else 5)
        elif verb == "count":
            cmd_count(parts[1] if len(parts) > 1 else "primary_type")
        elif verb == "filter":
            if len(parts) < 3:
                print("  Usage: filter <column> <value>")
            else:
                cmd_filter(parts[1], parts[2])
        elif verb == "schema":
            cmd_schema()
        elif verb == "summary":
            cmd_summary()
        else:
            print(f"  Unknown command: {verb}. Type 'help' for options.")

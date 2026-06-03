import csv
import os
import tempfile
from pathlib import Path

from chicago_pipeline.ingest.download_kaggle import generate_synthetic, verify_csv


def test_generate_synthetic_creates_file():
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tmp:
        tmp_path = tmp.name
    try:
        row_count = generate_synthetic(tmp_path, days=3, seed=42)
        assert 1300 < row_count < 2500, f"Unexpected row count: {row_count}"
        assert os.path.getsize(tmp_path) > 0
        with open(tmp_path) as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        assert len(rows) == row_count
        expected_fields = {
            "id", "case_number", "date", "block", "iucr", "primary_type",
            "description", "location_description", "arrest", "domestic",
            "beat", "district", "ward", "community_area", "fbi_code",
            "latitude", "longitude", "updated_on",
        }
        assert set(rows[0].keys()) == expected_fields
    finally:
        os.unlink(tmp_path)


def test_generate_synthetic_reproducible():
    with (
        tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tmp1,
        tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tmp2,
    ):
        p1, p2 = tmp1.name, tmp2.name
    try:
        r1 = generate_synthetic(p1, days=1, seed=42)
        r2 = generate_synthetic(p2, days=1, seed=42)
        assert r1 == r2
        with open(p1) as f:
            c1 = f.read()
        with open(p2) as f:
            c2 = f.read()
        assert c1 == c2
    finally:
        os.unlink(p1)
        os.unlink(p2)


def test_verify_csv():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as tmp:
        tmp.write("id,value\n1,10\n2,20\n3,30\n")
        tmp_path = tmp.name
    try:
        count = verify_csv(tmp_path)
        assert count == 3
    finally:
        os.unlink(tmp_path)


def test_verify_csv_empty():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as tmp:
        tmp.write("id,value\n")
        tmp_path = tmp.name
    try:
        count = verify_csv(tmp_path)
        assert count == 0
    finally:
        os.unlink(tmp_path)

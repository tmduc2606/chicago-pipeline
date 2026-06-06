#!/bin/bash
set -euo pipefail

echo "============================================"
echo "  Chicago Pipeline — Full Init"
echo "  $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "============================================"

cd /opt/pipeline
export PYTHONPATH=src

echo ""
echo "[1/7] Copying source CSV..."
mkdir -p /tmp/chicago_crime
cp /data/chicago_crime_synthetic_90d.csv /tmp/chicago_crime/source.csv
echo "  Done: $(wc -l < /tmp/chicago_crime/source.csv) lines"

echo ""
echo "[2/7] Bronze load..."
python3 -m chicago_pipeline.bronze.to_bronze
echo "  Bronze complete"

echo ""
echo "[3/7] Silver transform..."
python3 -m chicago_pipeline.silver.to_silver
echo "  Silver complete"

echo ""
echo "[4/7] Gold transform..."
python3 -m chicago_pipeline.gold.to_gold
echo "  Gold complete"

echo ""
echo "[5/7] Gold → Postgres loader..."
python3 src/chicago_pipeline/warehouse/load_postgres.py
echo "  Postgres load complete"

echo ""
echo "[6/7] dbt run..."
cd /opt/dbt
dbt run --profiles-dir .
echo "  dbt run complete"

echo ""
echo "[7/7] dbt test..."
dbt test --profiles-dir .
echo "  dbt test complete"

echo ""
echo "============================================"
echo "  Pipeline init finished successfully"
echo "  $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "============================================"

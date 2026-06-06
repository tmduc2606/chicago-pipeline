#!/bin/bash
set -e
cd /opt/pipeline
export PYTHONPATH=src

echo "=== M1: Download from Kaggle ==="
python3 -m chicago_pipeline.ingest.download_kaggle

echo "=== M1: Bronze load ==="
python3 -m chicago_pipeline.bronze.to_bronze

echo "=== Pipeline M1 complete ==="

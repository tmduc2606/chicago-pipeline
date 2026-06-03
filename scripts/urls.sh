#!/usr/bin/env bash
# Print all service URLs for chicago-pipeline.
set -euo pipefail

cat <<'EOF'
Service                    URL
-------------------------  --------------------------------
Airflow UI                 http://localhost:8080       (admin / $AIRFLOW_ADMIN_PASSWORD)
MinIO Console              http://localhost:9001       (minio / $MINIO_ROOT_PASSWORD)
MinIO S3 API               http://localhost:9000
Spark Master UI            http://localhost:8081
Postgres                   localhost:5432              (chicago / $POSTGRES_PASSWORD)
Redis                      localhost:6379
FastAPI (Swagger)          http://localhost:8000/docs
FastAPI (ReDoc)            http://localhost:8000/redoc
FastAPI (health)           http://localhost:8000/api/health
React dev server           http://localhost:5173
Prometheus                 http://localhost:9090
Grafana                    http://localhost:3000       (admin / $GRAFANA_ADMIN_PASSWORD)
Marquez (lineage)          http://localhost:3001
EOF

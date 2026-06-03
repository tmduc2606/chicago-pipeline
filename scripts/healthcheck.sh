#!/usr/bin/env bash
# Healthcheck for the chicago-pipeline stack.
# Exits 0 if every service reports healthy; 1 otherwise.
set -uo pipefail

SERVICES=(
  "ccp-minio|http://localhost:9000/minio/health/live"
  "ccp-postgres|nc -z localhost 5432"
  "ccp-redis|redis-cli -h localhost -p 6379 ping"
  "ccp-spark-master|http://localhost:8081"
  "ccp-airflow-webserver|http://localhost:8080/health"
  "ccp-api|http://localhost:8000/api/health/ready"
  "ccp-web|http://localhost:5173"
  "ccp-prometheus|http://localhost:9090/-/healthy"
  "ccp-grafana|http://localhost:3000/api/health"
  "ccp-marquez|http://localhost:3001"
)

fail=0
for entry in "${SERVICES[@]}"; do
  IFS='|' read -r name check <<<"$entry"
  if bash -c "$check" >/dev/null 2>&1; then
    printf "  \033[32mOK\033[0m  %s\n" "$name"
  else
    printf "  \033[31mFAIL\033[0m %s\n" "$name"
    fail=1
  fi
done

if [[ $fail -ne 0 ]]; then
  printf "\nOne or more services are unhealthy. Run: docker compose ps\n"
  exit 1
fi
printf "\nAll services healthy.\n"

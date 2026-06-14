SHELL := /bin/bash
# Chicago Pipeline — root Makefile
# Convention: every agent exposes its primary workflow as `make <verb>`.

# ---- help ----------------------------------------------------------------
.PHONY: help
help: ## Show this help
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-22s\033[0m %s\n", $$1, $$2 }' $(MAKEFILE_LIST) | sort

# ---- environment ---------------------------------------------------------
ENV_FILE ?= .env
include $(ENV_FILE)
export

# ---- stack lifecycle -----------------------------------------------------
.PHONY: up down ps logs health urls reset
up: ## Bring up the docker-compose stack
	docker compose up -d --build
	@$(MAKE) health

down: ## Stop the stack
	docker compose down

ps: ## Show running containers
	docker compose ps

logs: ## Tail logs of all services
	docker compose logs -f --tail=100

health: ## Show health of all services
	@bash scripts/healthcheck.sh

urls: ## Print all service URLs
	@bash scripts/urls.sh

reset: ## Destroy volumes and restart fresh (project-scoped only)
	docker compose down -v
	@echo "Volumes removed. Orphaned volumes pruned safely."

# ---- data engineering ----------------------------------------------------
.PHONY: pipeline spark-bronze spark-silver spark-gold load-postgres quality
pipeline: ## Ingest -> Silver -> Gold -> Postgres -> dbt (one-shot end-to-end)
	@$(MAKE) spark-bronze
	@$(MAKE) spark-silver
	@$(MAKE) spark-gold
	@$(MAKE) load-postgres
	@$(MAKE) dbt-run
	@$(MAKE) dbt-test
	@$(MAKE) quality

seed: ## Generate synthetic data for a fresh pipeline run
	python scripts/seed.py

spark-bronze: seed ## Run Bronze ingestion
	docker compose exec -T spark-master \
	  /opt/spark/bin/spark-submit --master spark://spark-master:7077 \
	    --py-files /opt/pipeline/src \
	  /opt/pipeline/src/chicago_pipeline/bronze/to_bronze.py /data/chicago_crime_synthetic.csv

spark-silver: ## Run Silver transformation
	docker compose exec -T spark-master \
	  /opt/spark/bin/spark-submit --master spark://spark-master:7077 \
	    --py-files /opt/pipeline/src \
	    /opt/pipeline/src/chicago_pipeline/silver/to_silver.py

spark-gold: ## Run Gold aggregation
	docker compose exec -T spark-master \
	  /opt/spark/bin/spark-submit --master spark://spark-master:7077 \
	    --py-files /opt/pipeline/src \
	    /opt/pipeline/src/chicago_pipeline/gold/to_gold.py

quality: ## Run Great Expectations + dbt tests
	@$(MAKE) ge-check
	@$(MAKE) dbt-test

ge-check: ## Run GE validation on Bronze, Silver, and Gold
	docker compose exec -T spark-master \
	  /opt/spark/bin/spark-submit --master spark://spark-master:7077 \
	    --py-files /opt/pipeline/src \
	    /opt/great_expectations/run_validation.py s3a://lake/bronze/chicago_crime chicago_crime_bronze bronze_checkpoint
	docker compose exec -T spark-master \
	  /opt/spark/bin/spark-submit --master spark://spark-master:7077 \
	    --py-files /opt/pipeline/src \
	    /opt/great_expectations/run_validation.py s3a://lake/silver/chicago_crime chicago_crime_silver silver_checkpoint
	docker compose exec -T spark-master \
	  /opt/spark/bin/spark-submit --master spark://spark-master:7077 \
	    --py-files /opt/pipeline/src \
	    /opt/great_expectations/run_validation.py s3a://lake/gold/chicago_crime/fact_crime chicago_crime_gold gold_checkpoint

ge-bronze: ## Run GE validation on Bronze only
	docker compose exec -T spark-master \
	  /opt/spark/bin/spark-submit --master spark://spark-master:7077 \
	    --py-files /opt/pipeline/src \
	    /opt/great_expectations/run_validation.py s3a://lake/bronze/chicago_crime chicago_crime_bronze bronze_checkpoint

ge-silver: ## Run GE validation on Silver only
	docker compose exec -T spark-master \
	  /opt/spark/bin/spark-submit --master spark://spark-master:7077 \
	    --py-files /opt/pipeline/src \
	    /opt/great_expectations/run_validation.py s3a://lake/silver/chicago_crime chicago_crime_silver silver_checkpoint

ge-gold: ## Run GE validation on Gold only
	docker compose exec -T spark-master \
	  /opt/spark/bin/spark-submit --master spark://spark-master:7077 \
	    --py-files /opt/pipeline/src \
	    /opt/great_expectations/run_validation.py s3a://lake/gold/chicago_crime/fact_crime chicago_crime_gold gold_checkpoint

load-postgres: ## Load Gold Parquet -> Postgres (warehouse schema)
	docker compose exec -T spark-master \
	  bash -c "PYTHONPATH=/opt/pipeline/src ENV=local python3 /opt/pipeline/src/chicago_pipeline/warehouse/load_postgres.py"

# ---- dbt -----------------------------------------------------------------
.PHONY: dbt-deps dbt-run dbt-test dbt-docs
dbt-deps: ## Install dbt packages
	docker compose exec -T spark-master bash -c "cd /opt/dbt && dbt deps --profiles-dir ."

dbt-run: dbt-deps ## Run all dbt models
	docker compose exec -T spark-master bash -c "cd /opt/dbt && dbt run --profiles-dir ."

dbt-test: ## Run dbt tests
	docker compose exec -T spark-master bash -c "cd /opt/dbt && dbt test --profiles-dir ."

dbt-docs: ## Generate and serve dbt docs
	docker compose exec -T spark-master bash -c "cd /opt/dbt && dbt docs generate --profiles-dir ."
	@echo "Docs generated at dbt/target/index.html"

# ---- API -----------------------------------------------------------------
.PHONY: api-up api-test api-docs api-lint
api-up: ## Bring up the FastAPI service
	docker compose up -d api

api-test: ## Run the API test suite
	docker compose exec -T api pytest -q --cov=app --cov-report=term-missing

api-docs: ## Open Swagger UI
	@echo "Open http://localhost:8000/docs"

api-lint: ## Lint the API
	docker compose exec -T api ruff check app
	docker compose exec -T api mypy app

# ---- Web -----------------------------------------------------------------
.PHONY: web-up web-build web-lint web-test web-e2e
web-up: ## Bring up the React dev server
	docker compose up -d web

web-build: ## Build the production bundle
	docker compose exec -T web pnpm build

web-lint: ## Lint the SPA
	docker compose exec -T web pnpm lint
	docker compose exec -T web pnpm typecheck

web-test: ## Unit tests
	docker compose exec -T web pnpm test

web-e2e: ## Playwright e2e
	docker compose --profile test run --rm playwright

# ---- contracts & agents --------------------------------------------------
.PHONY: contracts-validate agents-lint
contracts-validate: ## Validate all contract files (CI gate)
	@bash scripts/validate_contracts.sh

agents-lint: ## Validate every agent has the three required files
	@bash scripts/validate_agents.sh

# ---- global quality gates ------------------------------------------------
.PHONY: lint test format
lint: api-lint web-lint ## Lint everything
	@echo "All linters green."

test: api-test web-test ## Run all test suites
	@echo "All tests green."

format: ## Auto-format code
	docker compose exec -T api ruff format app
	docker compose exec -T api ruff check --fix app
	docker compose exec -T web pnpm format

# ---- demo ----------------------------------------------------------------
.PHONY: demo
demo: ## Seed 90 days of synthetic data so the dashboard is populated
	@$(MAKE) seed
	@$(MAKE) pipeline

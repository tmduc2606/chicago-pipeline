#Requires -Version 5.1

<#
.SYNOPSIS
    Chicago Pipeline — Windows PowerShell equivalents of Makefile targets.
.DESCRIPTION
    Run pipeline stages without GNU Make. Mirrors Makefile targets for Windows.
    Usage:
      .\scripts\pipeline.ps1 -Seed
      .\scripts\pipeline.ps1 -SparkBronze
      .\scripts\pipeline.ps1 -SparkSilver
      .\scripts\pipeline.ps1 -SparkGold
      .\scripts\pipeline.ps1 -LoadPostgres
      .\scripts\pipeline.ps1 -DbtRun
      .\scripts\pipeline.ps1 -DbtTest
      .\scripts\pipeline.ps1 -Pipeline        # All stages in sequence
      .\scripts\pipeline.ps1 -GeCheck         # All GE validations
#>

param(
    [switch]$Seed,
    [switch]$SparkBronze,
    [switch]$SparkSilver,
    [switch]$SparkGold,
    [switch]$LoadPostgres,
    [switch]$DbtRun,
    [switch]$DbtTest,
    [switch]$Pipeline,
    [switch]$GeCheck,
    [switch]$GeBronze,
    [switch]$GeSilver,
    [switch]$GeGold
)

$ErrorActionPreference = "Stop"

function Invoke-Seed {
    Write-Host "[pipeline] Generating seed data..." -ForegroundColor Cyan
    python scripts/seed.py
    if ($LASTEXITCODE -ne 0) { throw "seed failed" }
}

function Invoke-SparkBronze {
    Write-Host "[pipeline] Bronze ingestion..." -ForegroundColor Cyan
    docker compose exec -T spark-master `
        /opt/spark/bin/spark-submit --master spark://spark-master:7077 `
        --py-files /opt/pipeline/src `
        /opt/pipeline/src/chicago_pipeline/bronze/to_bronze.py /data/chicago_crime_synthetic_90d.csv
    if ($LASTEXITCODE -ne 0) { throw "spark-bronze failed" }
}

function Invoke-SparkSilver {
    Write-Host "[pipeline] Silver transformation..." -ForegroundColor Cyan
    docker compose exec -T spark-master `
        /opt/spark/bin/spark-submit --master spark://spark-master:7077 `
        --py-files /opt/pipeline/src `
        /opt/pipeline/src/chicago_pipeline/silver/to_silver.py
    if ($LASTEXITCODE -ne 0) { throw "spark-silver failed" }
}

function Invoke-SparkGold {
    Write-Host "[pipeline] Gold aggregation..." -ForegroundColor Cyan
    docker compose exec -T spark-master `
        /opt/spark/bin/spark-submit --master spark://spark-master:7077 `
        --py-files /opt/pipeline/src `
        /opt/pipeline/src/chicago_pipeline/gold/to_gold.py
    if ($LASTEXITCODE -ne 0) { throw "spark-gold failed" }
}

function Invoke-LoadPostgres {
    Write-Host "[pipeline] Loading Gold to Postgres..." -ForegroundColor Cyan
    docker compose exec -T spark-master `
        bash -c "PYTHONPATH=/opt/pipeline/src ENV=local python3 /opt/pipeline/src/chicago_pipeline/warehouse/load_postgres.py"
    if ($LASTEXITCODE -ne 0) { throw "load-postgres failed" }
}

function Invoke-DbtRun {
    Write-Host "[pipeline] dbt run..." -ForegroundColor Cyan
    docker compose exec -T spark-master bash -c "cd /opt/dbt && dbt deps --profiles-dir . && dbt run --profiles-dir ."
    if ($LASTEXITCODE -ne 0) { throw "dbt-run failed" }
}

function Invoke-DbtTest {
    Write-Host "[pipeline] dbt test..." -ForegroundColor Cyan
    docker compose exec -T spark-master bash -c "cd /opt/dbt && dbt test --profiles-dir ."
    if ($LASTEXITCODE -ne 0) { throw "dbt-test failed" }
}

function Invoke-GeBronze {
    Write-Host "[pipeline] GE Bronze..." -ForegroundColor Cyan
    docker compose exec -T spark-master `
        /opt/spark/bin/spark-submit --master spark://spark-master:7077 `
        --py-files /opt/pipeline/src `
        /opt/great_expectations/run_validation.py s3a://lake/bronze/chicago_crime chicago_crime_bronze bronze_checkpoint
    if ($LASTEXITCODE -ne 0) { throw "ge-bronze failed" }
}

function Invoke-GeSilver {
    Write-Host "[pipeline] GE Silver..." -ForegroundColor Cyan
    docker compose exec -T spark-master `
        /opt/spark/bin/spark-submit --master spark://spark-master:7077 `
        --py-files /opt/pipeline/src `
        /opt/great_expectations/run_validation.py s3a://lake/silver/chicago_crime chicago_crime_silver silver_checkpoint
    if ($LASTEXITCODE -ne 0) { throw "ge-silver failed" }
}

function Invoke-GeGold {
    Write-Host "[pipeline] GE Gold (fact_crime)..." -ForegroundColor Cyan
    docker compose exec -T spark-master `
        /opt/spark/bin/spark-submit --master spark://spark-master:7077 `
        --py-files /opt/pipeline/src `
        /opt/great_expectations/run_validation.py s3a://lake/gold/chicago_crime/fact_crime chicago_crime_gold gold_checkpoint
    if ($LASTEXITCODE -ne 0) { throw "ge-gold failed" }
}

function Invoke-Pipeline {
    Invoke-Seed
    Invoke-SparkBronze
    Invoke-SparkSilver
    Invoke-SparkGold
    Invoke-LoadPostgres
    Invoke-DbtRun
    Invoke-DbtTest
    Invoke-GeCheck
    Write-Host "[pipeline] ALL STAGES COMPLETE" -ForegroundColor Green
}

function Invoke-GeCheck {
    Invoke-GeBronze
    Invoke-GeSilver
    Invoke-GeGold
}

# Dispatch
if ($Pipeline) {
    Invoke-Pipeline
} else {
    if ($Seed) { Invoke-Seed }
    if ($SparkBronze) { Invoke-SparkBronze }
    if ($SparkSilver) { Invoke-SparkSilver }
    if ($SparkGold) { Invoke-SparkGold }
    if ($LoadPostgres) { Invoke-LoadPostgres }
    if ($DbtRun) { Invoke-DbtRun }
    if ($DbtTest) { Invoke-DbtTest }
    if ($GeCheck) { Invoke-GeCheck }
    if ($GeBronze) { Invoke-GeBronze }
    if ($GeSilver) { Invoke-GeSilver }
    if ($GeGold) { Invoke-GeGold }
}

if ($MyInvocation.InvocationName -ne "&") {
    Write-Host "No switch provided. Usage: .\scripts\pipeline.ps1 -Pipeline" -ForegroundColor Yellow
}

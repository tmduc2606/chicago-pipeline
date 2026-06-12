#!/usr/bin/env bash
# run_assessment.sh — Chicago Pipeline M0→M6 Comprehensive Assessment Runner
#
# 8-phase assessment pipeline aligned with production-grade standards.
# Phases: Prerequisites → Gates → E2E → Critic → Inspections → Cross-Cutting → Scoring → Report
#
# Usage:
#   bash scripts/run_assessment.sh                  # Full assessment (all 8 phases)
#   bash scripts/run_assessment.sh --gates-only     # Phase 2: Automated gates only
#   bash scripts/run_assessment.sh --e2e-only       # Phase 3: Playwright E2E only
#   bash scripts/run_assessment.sh --critic         # Phase 4: Critic evaluation templates
#   bash scripts/run_assessment.sh --inspections    # Phase 5: Code inspections only
#   bash scripts/run_assessment.sh --cross-cutting  # Phase 6: Cross-cutting analysis only
#   bash scripts/run_assessment.sh --scoring        # Phase 7: Score calculation only
#   bash scripts/run_assessment.sh --report         # Phase 8: Report generation only
#
# Output:
#   docs/assessment/tracking.md                  # Tracking document (living)
#   reports/assessment/evidence/                    # Raw evidence per phase
#   reports/assessment/summary.md                   # Final summary

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

# ── Configuration ──────────────────────────────────────────────────────
OUTPUT_DIR="$REPO_ROOT/reports/assessment"
EVIDENCE_DIR="$OUTPUT_DIR/evidence"
OVERHAUL="$REPO_ROOT/docs/assessment/tracking.md"
SUMMARY="$OUTPUT_DIR/summary.md"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
TIMESTAMP_FILE=$(date -u +"%Y-%m-%dT%H-%M-%SZ")
MODE="${1:-full}"

# Severity thresholds (from docs/assessment/risk_matrix.md)
S1_BLOCK=0           # Hard block: any S1 FAIL = assessment fails
S2_OVERRIDE_THRESHOLD=5  # Architect override needed if >5 S2 open
CRITIC_MIN=7.0       # Minimum critic composite score

# Milestone weights
declare -A MILESTONE_WEIGHTS=(
  ["M0"]=5 ["M1"]=10 ["M2"]=15 ["M3"]=15
  ["M4"]=20 ["M5"]=15 ["M6"]=20
)

# Create directory structure
mkdir -p "$EVIDENCE_DIR/gates"
mkdir -p "$EVIDENCE_DIR/e2e"
mkdir -p "$EVIDENCE_DIR/code-inspections"
mkdir -p "$EVIDENCE_DIR/critic-evaluations"
mkdir -p "$EVIDENCE_DIR/cross-cutting"

# ── Counters ──────────────────────────────────────────────────────────
total=0; passed=0; failed=0; skipped=0
s1_count=0; s2_count=0; s3_count=0; s4_count=0

# Severity-weighted scoring
declare -A MILESTONE_SCORES

# ── Utility Functions ──────────────────────────────────────────────────

gate_result() {
  local name="$1" status="$2" detail="$3" severity="${4:-}"
  total=$((total + 1))
  if [ "$status" = "PASS" ]; then
    passed=$((passed + 1))
    printf "  \033[32mPASS\033[0m  %s %s\n" "$name" "$detail"
  elif [ "$status" = "FAIL" ]; then
    failed=$((failed + 1))
    printf "  \033[31mFAIL\033[0m  %s %s\n" "$name" "$detail"
    # Track severity
    case "$severity" in
      S1) s1_count=$((s1_count + 1)) ;;
      S2) s2_count=$((s2_count + 1)) ;;
      S3) s3_count=$((s3_count + 1)) ;;
      S4) s4_count=$((s4_count + 1)) ;;
    esac
  else
    skipped=$((skipped + 1))
    printf "  \033[33mSKIP\033[0m  %s %s\n" "$name" "$detail"
  fi
  echo "| $name | $status | $detail | $severity |" >> "$EVIDENCE_DIR/gates/results.md"
}

log_finding() {
  local id="$1" severity="$2" title="$3" owner="$4" detail="$5"
  cat >> "$EVIDENCE_DIR/cross-cutting/findings.md" <<EOF
## $id — $title
- **Severity:** $severity
- **Owner:** $owner
- **Detail:** $detail
- **Status:** open

EOF
}

# ── Init evidence files ───────────────────────────────────────────────
cat > "$EVIDENCE_DIR/gates/results.md" <<EOF
# Gate Results — $TIMESTAMP

| Gate | Status | Details | Severity |
|------|--------|---------|----------|
EOF

cat > "$EVIDENCE_DIR/cross-cutting/findings.md" <<EOF
# Cross-Cutting Findings — $TIMESTAMP

EOF

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "  Chicago Pipeline — M0→M6 Assessment (8-Phase)"
echo "  Started: $TIMESTAMP"
echo "  Mode: $MODE"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# ══════════════════════════════════════════════════════════════════════
# Phase 1: Prerequisites
# ══════════════════════════════════════════════════════════════════════
if [ "$MODE" = "full" ]; then
  echo "── Phase 1: Prerequisites ────────────────────────────────────"
  echo ""

  # Check Docker is running
  if docker info > /dev/null 2>&1; then
    gate_result "docker running" "PASS" "Docker daemon accessible"
  else
    gate_result "docker running" "FAIL" "Docker daemon not accessible" "S1"
  fi

  # Check required files exist
  required_files=(
    "Makefile"
    "docker-compose.yaml"
    ".env"
    "contracts/openapi.yaml"
    "contracts/dbt-manifest.json"
    "docs/architecture.md"
    "docs/IMPLEMENTATION_PLAN.md"
    "docs/implementation_mistakes.md"
  )

  for f in "${required_files[@]}"; do
    if [ -f "$f" ]; then
      gate_result "file: $f" "PASS" "exists"
    else
      gate_result "file: $f" "FAIL" "missing" "S2"
    fi
  done

  # Check agent files exist
  agent_dirs=(architect data-engineer backend frontend qa sre docs security)
  for agent in "${agent_dirs[@]}"; do
    if [ -f "agents/$agent/AGENTS.md" ]; then
      gate_result "agent: $agent" "PASS" "AGENTS.md exists"
    else
      gate_result "agent: $agent" "FAIL" "AGENTS.md missing" "S2"
    fi
  done

  echo ""
fi

# ══════════════════════════════════════════════════════════════════════
# Phase 2: Automated Gates
# ══════════════════════════════════════════════════════════════════════
if [ "$MODE" = "full" ] || [ "$MODE" = "--gates-only" ]; then
  echo "── Phase 2: Automated Gates ──────────────────────────────────"
  echo ""

  # api lint — ruff (S2)
  if docker compose exec -T api ruff check app > "$EVIDENCE_DIR/gates/lint-ruff.txt" 2>&1; then
    gate_result "api lint (ruff)" "PASS" "ruff check passed"
  else
    gate_result "api lint (ruff)" "FAIL" "see evidence/gates/lint-ruff.txt" "S2"
  fi

  # api lint — mypy (S3 — strict mode issues, not runtime bugs)
  if docker compose exec -T api mypy app > "$EVIDENCE_DIR/gates/lint-mypy.txt" 2>&1; then
    gate_result "api lint (mypy)" "PASS" "mypy check passed"
  else
    mypy_errors=$(grep -c "^app/" "$EVIDENCE_DIR/gates/lint-mypy.txt" 2>/dev/null || echo 0)
    gate_result "api lint (mypy)" "FAIL" "$mypy_errors type strictness issues (strict=true)" "S3"
  fi

  # api test (S1 — API regression)
  if docker compose exec -T api python -m pytest -q --tb=short > "$EVIDENCE_DIR/gates/api-test.txt" 2>&1; then
    gate_result "api test" "PASS" "pytest"
  else
    gate_result "api test" "FAIL" "see evidence/gates/api-test.txt" "S1"
  fi

  # contracts validate (S1)
  if bash scripts/validate_contracts.sh > "$EVIDENCE_DIR/gates/contracts.txt" 2>&1; then
    gate_result "contracts validate" "PASS" "contracts valid"
  else
    gate_result "contracts validate" "FAIL" "see evidence/gates/contracts.txt" "S1"
  fi

  # agents lint (S2)
  if bash scripts/validate_agents.sh > "$EVIDENCE_DIR/gates/agents.txt" 2>&1; then
    gate_result "agents lint" "PASS" "agent files present"
  else
    gate_result "agents lint" "FAIL" "see evidence/gates/agents.txt" "S2"
  fi

  # dbt test (S1 — data quality)
  if docker compose exec -T spark-master bash -c "cd /opt/dbt && dbt test --profiles-dir ." > "$EVIDENCE_DIR/gates/dbt-test.txt" 2>&1; then
    gate_result "dbt test" "PASS" "dbt tests passed"
  else
    gate_result "dbt test" "FAIL" "see evidence/gates/dbt-test.txt" "S1"
  fi

  # GE validation — bronze (S1)
  if MSYS_NO_PATHCONV=1 docker compose exec -T spark-master /opt/spark/bin/spark-submit --master spark://spark-master:7077 --py-files /opt/pipeline/src /opt/great_expectations/run_validation.py s3a://lake/bronze/chicago_crime chicago_crime_bronze bronze_checkpoint > "$EVIDENCE_DIR/gates/ge-bronze.txt" 2>&1; then
    gate_result "GE bronze" "PASS" "validation passed"
  else
    gate_result "GE bronze" "FAIL" "see evidence/gates/ge-bronze.txt" "S1"
  fi

  # GE validation — silver (S1)
  if MSYS_NO_PATHCONV=1 docker compose exec -T spark-master /opt/spark/bin/spark-submit --master spark://spark-master:7077 --py-files /opt/pipeline/src /opt/great_expectations/run_validation.py s3a://lake/silver/chicago_crime chicago_crime_silver silver_checkpoint > "$EVIDENCE_DIR/gates/ge-silver.txt" 2>&1; then
    gate_result "GE silver" "PASS" "validation passed"
  else
    gate_result "GE silver" "FAIL" "see evidence/gates/ge-silver.txt" "S1"
  fi

  # GE validation — gold (S1)
  if MSYS_NO_PATHCONV=1 docker compose exec -T spark-master /opt/spark/bin/spark-submit --master spark://spark-master:7077 --py-files /opt/pipeline/src /opt/great_expectations/run_validation.py s3a://lake/gold/chicago_crime/fact_crime chicago_crime_gold gold_checkpoint > "$EVIDENCE_DIR/gates/ge-gold.txt" 2>&1; then
    gate_result "GE gold" "PASS" "validation passed"
  else
    gate_result "GE gold" "FAIL" "see evidence/gates/ge-gold.txt" "S1"
  fi

  # gitleaks detect (S1 — no secrets)
  GITLEAKS_BIN=""
  if command -v gitleaks >/dev/null 2>&1; then
    GITLEAKS_BIN="gitleaks"
  elif [ -f "$LOCALAPPDATA/Microsoft/WinGet/Packages/Gitleaks.Gitleaks_Microsoft.Winget.Source_8wekyb3d8bbwe/gitleaks.exe" ]; then
    GITLEAKS_BIN="$LOCALAPPDATA/Microsoft/WinGet/Packages/Gitleaks.Gitleaks_Microsoft.Winget.Source_8wekyb3d8bbwe/gitleaks.exe"
  fi

  if [ -n "$GITLEAKS_BIN" ]; then
    if "$GITLEAKS_BIN" detect --source . --verbose > "$EVIDENCE_DIR/gates/gitleaks.txt" 2>&1; then
      gate_result "gitleaks detect" "PASS" "0 secrets"
    else
      gate_result "gitleaks detect" "FAIL" "see evidence/gates/gitleaks.txt" "S1"
    fi
  else
    gate_result "gitleaks detect" "SKIP" "gitleaks not installed"
  fi

  echo ""
fi

# ══════════════════════════════════════════════════════════════════════
# Phase 3: Playwright E2E
# ══════════════════════════════════════════════════════════════════════
if [ "$MODE" = "full" ] || [ "$MODE" = "--e2e-only" ]; then
  echo "── Phase 3: Playwright E2E ───────────────────────────────────"
  echo ""

  # Clean previous results
  rm -rf test-results playwright-report 2>/dev/null

  if docker compose --profile test run --rm playwright > "$EVIDENCE_DIR/e2e/e2e.txt" 2>&1; then
    gate_result "playwright e2e" "PASS" "Playwright tests passed"
  else
    gate_result "playwright e2e" "FAIL" "see evidence/e2e/e2e.txt" "S1"
  fi

  echo ""
fi

# ══════════════════════════════════════════════════════════════════════
# Phase 4: Critic Evaluations (placeholder — semi-automated)
# ══════════════════════════════════════════════════════════════════════
if [ "$MODE" = "full" ] || [ "$MODE" = "--critic" ]; then
  echo "── Phase 4: Critic Evaluations ───────────────────────────────"
  echo ""

  CRITIC_DIR="$EVIDENCE_DIR/critic-evaluations"
  mkdir -p "$CRITIC_DIR"

  # Generate placeholder templates for each persona
  personas=("data-analyst" "citizen" "executive" "journalist" "first-timer" "policy-maker" "community-organizer" "news-editor")
  for persona in "${personas[@]}"; do
    if [ ! -f "$CRITIC_DIR/$persona.md" ]; then
      cat > "$CRITIC_DIR/$persona.md" <<CRITIC_EOF
# Critic Evaluation: $persona
**Timestamp:** $TIMESTAMP
**Evaluator:** QA Agent (pending manual evaluation)
**Pages evaluated:** TBD

## Rubric Scores
| # | Criterion | Score (0-10) | Evidence | Notes |
|---|-----------|-------------|----------|-------|
| *Pending* | *Manual evaluation required* | — | — | — |

## Composite Score
**Weighted Average:** — / 10
**Verdict:** PENDING

## Notes
This evaluation requires manual execution. The QA agent must:
1. Start the web app: \`docker compose up -d web\`
2. Navigate to each page listed above
3. Score each criterion using the rubric in \`docs/assessment/rubric.md\`
4. Record evidence (screenshots, console output)
5. Update this file with scores and verdict
CRITIC_EOF
      echo "  📝  Created template: critic-evaluations/$persona.md (pending manual evaluation)"
    else
      echo "  ✅  critic-evaluations/$persona.md exists"
    fi
  done

  echo ""
  echo "  Note: Critic evaluations require manual execution by QA agent."
  echo "  Templates created in $CRITIC_DIR/"
  echo ""

  echo ""
fi

# ══════════════════════════════════════════════════════════════════════
# Phase 5: Code Inspections (automated pattern checks)
# ══════════════════════════════════════════════════════════════════════
if [ "$MODE" = "full" ] || [ "$MODE" = "--inspections" ]; then
  echo "── Phase 5: Code Inspections ─────────────────────────────────"
  echo ""

  INSPECTIONS="$EVIDENCE_DIR/code-inspections/all.md"
  cat > "$INSPECTIONS" <<EOF
# Code Inspections — $TIMESTAMP

## Automated Pattern Checks

EOF

  # MISTAKE-001: asyncpg ::date SQL cast
  violations=$(grep -r "::date" api/app/services/ 2>/dev/null | wc -l)
  if [ "$violations" -gt 0 ]; then
    gate_result "MISTAKE-001: ::date cast" "FAIL" "$violations violations in api/app/services/" "S2"
    echo "- **MISTAKE-001:** $violations files use \`::date\` SQL cast (asyncpg rejection risk)" >> "$INSPECTIONS"
  else
    gate_result "MISTAKE-001: ::date cast" "PASS" "0 violations"
    echo "- **MISTAKE-001:** PASS — no \`::date\` casts found" >> "$INSPECTIONS"
  fi

  # MISTAKE-002: Hardcoded coordinates (exclude config/map.ts which is the canonical source)
  violations=$(grep -r "41\.8781" web/src/ --include='*.tsx' --include='*.ts' 2>/dev/null | grep -v "config/map.ts" | wc -l)
  if [ "$violations" -gt 0 ]; then
    gate_result "MISTAKE-002: hardcoded coords" "FAIL" "$violations violations in web/src/" "S2"
    echo "- **MISTAKE-002:** $violations files hardcode Chicago coordinates" >> "$INSPECTIONS"
  else
    gate_result "MISTAKE-002: hardcoded coords" "PASS" "0 violations"
    echo "- **MISTAKE-002:** PASS — no hardcoded coordinates" >> "$INSPECTIONS"
  fi

  # MISTAKE-005: Missing ErrorBoundary isolation
  pages_with_boundary=0
  pages_without_boundary=0
  for page in web/src/pages/*.tsx; do
    if grep -q "ErrorBoundary" "$page" 2>/dev/null; then
      pages_with_boundary=$((pages_with_boundary + 1))
    else
      pages_without_boundary=$((pages_without_boundary + 1))
    fi
  done
  if [ "$pages_without_boundary" -gt 0 ]; then
    gate_result "MISTAKE-005: ErrorBoundary" "FAIL" "$pages_without_boundary pages lack ErrorBoundary" "S2"
    echo "- **MISTAKE-005:** $pages_without_boundary pages without ErrorBoundary wrapper" >> "$INSPECTIONS"
  else
    gate_result "MISTAKE-005: ErrorBoundary" "PASS" "all pages wrapped"
    echo "- **MISTAKE-005:** PASS — all pages have ErrorBoundary" >> "$INSPECTIONS"
  fi

  # MISTAKE-008: Frontend date param mismatch
  # Frontend state uses `from`/`to`, but filtersToParams() converts to `from_date`/`to_date`
  # Backend expects `from_date`/`to_date` — check filters.ts for the conversion
  if grep -q "from_date\|to_date" web/src/stores/filters.ts 2>/dev/null; then
    gate_result "MISTAKE-008: param names" "PASS" "filtersToParams converts from→from_date, to→to_date"
    echo "- **MISTAKE-008:** PASS — param names consistent (converted in filters.ts)" >> "$INSPECTIONS"
  else
    gate_result "MISTAKE-008: param names" "FAIL" "possible param name drift" "S3"
    echo "- **MISTAKE-008:** WARNING — possible param name drift between frontend and backend" >> "$INSPECTIONS"
  fi

  # MISTAKE-010: Pattern repetition check
  echo "" >> "$INSPECTIONS"
  echo "## Pattern Sweep Results" >> "$INSPECTIONS"
  echo "" >> "$INSPECTIONS"

  # Check for consistent error handling patterns
  service_files=$(find api/app/services -name "*.py" 2>/dev/null | wc -l)
  services_with_error=$(grep -rl "try:" api/app/services/ 2>/dev/null | wc -l)
  echo "- Service files with try/except: $services_with_error / $service_files" >> "$INSPECTIONS"

  # Check for consistent async patterns
  services_with_async=$(grep -rl "async def" api/app/services/ 2>/dev/null | wc -l)
  echo "- Service files with async: $services_with_async / $service_files" >> "$INSPECTIONS"

  # File structure checks
  echo "" >> "$INSPECTIONS"
  echo "## Structural Checks" >> "$INSPECTIONS"
  echo "" >> "$INSPECTIONS"

  # Check router files
  router_count=$(find api/app/routers -name "*.py" 2>/dev/null | wc -l)
  echo "- Router files: $router_count" >> "$INSPECTIONS"

  # Check schema files
  schema_count=$(find api/app/schemas -name "*.py" 2>/dev/null | wc -l)
  echo "- Schema files: $schema_count" >> "$INSPECTIONS"

  # Check service files
  echo "- Service files: $service_files" >> "$INSPECTIONS"

  # Check dbt models
  staging_count=$(find dbt/models/staging -name "*.sql" 2>/dev/null | wc -l)
  intermediate_count=$(find dbt/models/intermediate -name "*.sql" 2>/dev/null | wc -l)
  mart_count=$(find dbt/models/marts -name "*.sql" 2>/dev/null | wc -l)
  echo "- dbt staging models: $staging_count" >> "$INSPECTIONS"
  echo "- dbt intermediate models: $intermediate_count" >> "$INSPECTIONS"
  echo "- dbt mart models: $mart_count" >> "$INSPECTIONS"

  # Check web components
  chart_count=$(find web/src/components/charts -name "*.tsx" 2>/dev/null | wc -l)
  map_count=$(find web/src/components/maps -name "*.tsx" 2>/dev/null | wc -l)
  page_count=$(find web/src/pages -name "*.tsx" 2>/dev/null | wc -l)
  echo "- Chart components: $chart_count" >> "$INSPECTIONS"
  echo "- Map components: $map_count" >> "$INSPECTIONS"
  echo "- Page components: $page_count" >> "$INSPECTIONS"

  echo ""
fi

# ══════════════════════════════════════════════════════════════════════
# Phase 6: Cross-Cutting Analysis
# ══════════════════════════════════════════════════════════════════════
if [ "$MODE" = "full" ] || [ "$MODE" = "--cross-cutting" ]; then
  echo "── Phase 6: Cross-Cutting Analysis ──────────────────────────"
  echo ""

  CC="$EVIDENCE_DIR/cross-cutting/analysis.md"
  cat > "$CC" <<EOF
# Cross-Cutting Analysis — $TIMESTAMP

## Pattern Consistency Verification

EOF

  # Check logging consistency
  api_logging=$(grep -r "import logging\|import structlog\|getLogger" api/app/ 2>/dev/null | wc -l)
  echo "- API logging imports: $api_logging" >> "$CC"

  # Check error model consistency
  api_error_model=$(grep -r "request_id\|error_code\|error_message" api/app/schemas/ 2>/dev/null | wc -l)
  echo "- API error model references: $api_error_model" >> "$CC"

  # Check CORS configuration
  cors_config=$(grep -r "CORSMiddleware\|allow_origins\|allow_methods" api/app/main.py 2>/dev/null | wc -l)
  echo "- CORS configuration lines: $cors_config" >> "$CC"

  # Check data flow consistency
  echo "" >> "$CC"
  echo "## Data Flow Verification" >> "$CC"
  echo "" >> "$CC"

  # Verify pipeline stages exist
  for stage in bronze silver gold; do
    if [ -f "pipeline/src/chicago_pipeline/$stage/to_$stage.py" ]; then
      echo "- Pipeline stage \`$stage\`: PASS (to_$stage.py exists)" >> "$CC"
    else
      echo "- Pipeline stage \`$stage\`: FAIL (to_$stage.py missing)" >> "$CC"
      log_finding "CC-001" "S1" "Pipeline stage $stage missing" "Data Engineer" "to_$stage.py not found"
    fi
  done

  # Verify dbt → API → Frontend data flow
  echo "" >> "$CC"
  echo "## Contract Consistency" >> "$CC"
  echo "" >> "$CC"

  # Check OpenAPI endpoints match router count
  openapi_endpoints=$(grep -c "operationId:" contracts/openapi.yaml 2>/dev/null || echo 0)
  echo "- OpenAPI endpoints documented: $openapi_endpoints" >> "$CC"

  # Check frontend API calls match backend routes
  frontend_api_calls=$(grep -c "fetch\|/api/" web/src/lib/api.ts 2>/dev/null || echo 0)
  echo "- Frontend API references: $frontend_api_calls" >> "$CC"

  # Security: gitleaks handles secret detection in Phase 2
  # (grep-based secret checks produce false positives — use gitleaks instead)

  # Check for PII exposure
  pii=$(grep -rn "ssn\|social_security\|credit_card\|bank_account" --include="*.py" --include="*.ts" --include="*.tsx" . 2>/dev/null | grep -v "node_modules\|\.git\|test\|mock" | wc -l)
  echo "- PII pattern references: $pii" >> "$CC"

  echo ""
fi

# ══════════════════════════════════════════════════════════════════════
# Phase 7: Score Calculation
# ══════════════════════════════════════════════════════════════════════
if [ "$MODE" = "full" ] || [ "$MODE" = "--scoring" ]; then
  echo "── Phase 7: Score Calculation ────────────────────────────────"
  echo ""

  # Base score from gates
  base_score=0
  if [ $total -gt 0 ]; then
    base_score=$(( (passed * 100) / total ))
  fi

  # Severity penalty
  severity_penalty=$(( (s1_count * 25) + (s2_count * 10) + (s3_count * 5) + (s4_count * 1) ))

  # Final score (hard block if S1 > 0)
  if [ $s1_count -gt 0 ]; then
    final_score=0
    grade="F"
    block_reason="HARD BLOCK: $s1_count S1 (Critical) findings open"
  else
    final_score=$(( base_score - severity_penalty ))
    if [ $final_score -lt 0 ]; then final_score=0; fi

    # Determine grade
    if [ $final_score -ge 95 ]; then grade="A"
    elif [ $final_score -ge 85 ]; then grade="B"
    elif [ $final_score -ge 70 ]; then grade="C"
    elif [ $final_score -ge 50 ]; then grade="D"
    else grade="F"
    fi
    block_reason=""
  fi

  # Write scoring evidence
  cat > "$EVIDENCE_DIR/scoring.md" <<EOF
# Score Calculation — $TIMESTAMP

## Base Score
- Total checks: $total
- Passed: $passed
- Failed: $failed
- Skipped: $skipped
- Base score: ${base_score}%

## Severity Penalty
- S1 (Critical) findings: $s1_count (× 25 = $((s1_count * 25)))
- S2 (High) findings: $s2_count (× 10 = $((s2_count * 10)))
- S3 (Medium) findings: $s3_count (× 5 = $((s3_count * 5)))
- S4 (Low) findings: $s4_count (× 1 = $((s4_count * 1)))
- Total penalty: ${severity_penalty}%

## Final Score
- Base score: ${base_score}%
- Severity penalty: -${severity_penalty}%
- Final score: ${final_score}%
- Grade: ${grade}
$([ -n "$block_reason" ] && echo "- Block reason: $block_reason")

## Hard-Block Check
- S1 findings: $s1_count (threshold: $S1_BLOCK)
- Assessment passes: $([ $s1_count -eq 0 ] && echo "YES" || echo "NO — S1 HARD BLOCK")
EOF

  echo "  Base score:    ${base_score}%"
  echo "  S1 findings:   $s1_count"
  echo "  S2 findings:   $s2_count"
  echo "  S3 findings:   $s3_count"
  echo "  S4 findings:   $s4_count"
  echo "  Penalty:       -${severity_penalty}%"
  echo "  Final score:   ${final_score}%"
  echo "  Grade:         ${grade}"
  echo ""
  echo "  Note: Flat scoring (all checks weighted equally)."
  echo "  Per-milestone weighted scoring available when milestone tags are added."
  if [ $s1_count -gt 0 ]; then
    echo ""
    echo "  \033[31mHARD BLOCK: $s1_count S1 (Critical) findings must be resolved.\033[0m"
  fi
  echo ""
fi

# ══════════════════════════════════════════════════════════════════════
# Phase 8: Report Generation
# ══════════════════════════════════════════════════════════════════════
if [ "$MODE" = "full" ] || [ "$MODE" = "--report" ]; then
  echo "── Phase 8: Report Generation ───────────────────────────────"
  echo ""

  # Calculate final score if not already done
  if [ $total -gt 0 ]; then
    base_score=$(( (passed * 100) / total ))
  else
    base_score=0
  fi
  severity_penalty=$(( (s1_count * 25) + (s2_count * 10) + (s3_count * 5) + (s4_count * 1) ))
  if [ $s1_count -gt 0 ]; then
    final_score=0
    grade="F"
  else
    final_score=$(( base_score - severity_penalty ))
    if [ $final_score -lt 0 ]; then final_score=0; fi
    if [ $final_score -ge 95 ]; then grade="A"
    elif [ $final_score -ge 85 ]; then grade="B"
    elif [ $final_score -ge 70 ]; then grade="C"
    elif [ $final_score -ge 50 ]; then grade="D"
    else grade="F"
    fi
  fi

  # Generate summary
  cat > "$SUMMARY" <<EOF
# Assessment Summary — $TIMESTAMP

## Overall Result

| Metric | Value |
|--------|-------|
| **Final Score** | ${final_score}% |
| **Grade** | ${grade} |
| **S1 (Critical) Findings** | $s1_count |
| **S2 (High) Findings** | $s2_count |
| **S3 (Medium) Findings** | $s3_count |
| **S4 (Low) Findings** | $s4_count |
| **Total Checks** | $total |
| **Passed** | $passed |
| **Failed** | $failed |
| **Skipped** | $skipped |

## Gate Results

$(cat "$EVIDENCE_DIR/gates/results.md" 2>/dev/null || echo "| — | — | — | — |")

## Severity Distribution

| Severity | Count | Score Impact | Block Status |
|----------|-------|--------------|--------------|
| S1 (Critical) | $s1_count | -25% each | **HARD BLOCK** if > 0 |
| S2 (High) | $s2_count | -10% each | Architect override |
| S3 (Medium) | $s3_count | -5% each | Tracked |
| S4 (Low) | $s4_count | -1% each | Informational |

## Evidence Location

All evidence files: \`reports/assessment/evidence/\`
- Gates: \`evidence/gates/\`
- E2E: \`evidence/e2e/\`
- Code inspections: \`evidence/code-inspections/\`
- Cross-cutting: \`evidence/cross-cutting/\`
- Scoring: \`evidence/scoring.md\`

## Next Steps

$([ $s1_count -gt 0 ] && echo "1. **CRITICAL:** Resolve $s1_count S1 findings before proceeding" || echo "1. No S1 (Critical) findings — good to proceed")
$([ $s2_count -gt 0 ] && echo "2. Review $s2_count S2 findings with Architect for override decisions" || echo "2. No S2 (High) findings")
$([ $s3_count -gt 0 ] && echo "3. Address $s3_count S3 findings or create technical debt tickets" || echo "3. No S3 (Medium) findings")
$([ $s4_count -gt 0 ] && echo "4. Address $s4_count S4 findings opportunistically" || echo "4. No S4 (Low) findings")
5. Update \`docs/assessment/tracking.md\` with findings
6. Complete critic persona evaluations in \`evidence/critic-evaluations/\`
EOF

  # Generate overhaul tracking entry
  cat >> "$OVERHAUL" <<EOF

---

## Assessment Run — $TIMESTAMP

| Metric | Value |
|--------|-------|
| Score | ${final_score}% |
| Grade | ${grade} |
| S1 | $s1_count |
| S2 | $s2_count |
| S3 | $s3_count |
| S4 | $s4_count |

EOF

  echo "  Summary written to: $SUMMARY"
  echo "  Overhaul updated:   docs/assessment/tracking.md"
  echo "  Evidence in:        $EVIDENCE_DIR/"
  echo ""
fi

# ══════════════════════════════════════════════════════════════════════
# Final Summary
# ══════════════════════════════════════════════════════════════════════
echo "═══════════════════════════════════════════════════════════════"
echo "  Assessment Complete"
echo "  Score: ${final_score:-0}% (Grade: ${grade:-F})"
echo "  Passed: $passed / $total  |  Failed: $failed  |  Skipped: $skipped"
echo "  S1: $s1_count  |  S2: $s2_count  |  S3: $s3_count  |  S4: $s4_count"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Exit with failure if S1 findings exist or any gates failed
if [ $s1_count -gt 0 ] || [ $failed -gt 0 ]; then
  exit 1
fi
exit 0

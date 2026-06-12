#!/usr/bin/env bash
# validate_assessment.sh — Assessment Completeness Validator
#
# Validates that an assessment run is complete and well-formed.
# Run after `run_assessment.sh` to ensure all evidence is present.
#
# Usage:
#   bash scripts/validate_assessment.sh
#
# Exit codes:
#   0 = Assessment is complete and valid
#   1 = Assessment has completeness issues

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

EVIDENCE_DIR="reports/assessment/evidence"
OVERHAUL="docs/assessment/tracking.md"
ERRORS=0
WARNINGS=0

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "  Assessment Completeness Validator"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# ── Check 1: Evidence directory structure ──────────────────────────────
echo "── Check 1: Evidence Directory Structure ─────────────────────"
echo ""

required_dirs=(
  "$EVIDENCE_DIR/gates"
  "$EVIDENCE_DIR/e2e"
  "$EVIDENCE_DIR/code-inspections"
  "$EVIDENCE_DIR/critic-evaluations"
  "$EVIDENCE_DIR/cross-cutting"
)

for dir in "${required_dirs[@]}"; do
  if [ -d "$dir" ]; then
    echo "  ✅  $dir exists"
  else
    echo "  ❌  $dir missing"
    ERRORS=$((ERRORS + 1))
  fi
done

# ── Check 2: Gate results exist ───────────────────────────────────────
echo ""
echo "── Check 2: Gate Results ────────────────────────────────────"
echo ""

if [ -f "$EVIDENCE_DIR/gates/results.md" ]; then
  gate_count=$(grep -c "^|" "$EVIDENCE_DIR/gates/results.md" 2>/dev/null || echo 0)
  gate_count=$((gate_count - 2))  # subtract header and separator
  echo "  ✅  Gate results exist ($gate_count gates recorded)"
  
  # Check for FAIL entries
  fails=$(grep -c "| FAIL |" "$EVIDENCE_DIR/gates/results.md" 2>/dev/null || echo 0)
  if [ "$fails" -gt 0 ]; then
    echo "  ⚠️  $fails gate(s) failed — review evidence"
    WARNINGS=$((WARNINGS + 1))
  fi
else
  echo "  ❌  Gate results missing"
  ERRORS=$((ERRORS + 1))
fi

# Check individual gate evidence files
gate_files=(lint-ruff.txt lint-mypy.txt api-test.txt contracts.txt agents.txt dbt-test.txt ge-bronze.txt ge-silver.txt ge-gold.txt gitleaks.txt)
for f in "${gate_files[@]}"; do
  if [ -f "$EVIDENCE_DIR/gates/$f" ]; then
    echo "  ✅  gates/$f exists"
  else
    echo "  ⚠️  gates/$f missing"
    WARNINGS=$((WARNINGS + 1))
  fi
done

# ── Check 3: E2E results exist ────────────────────────────────────────
echo ""
echo "── Check 3: E2E Results ────────────────────────────────────"
echo ""

if [ -f "$EVIDENCE_DIR/e2e/e2e.txt" ]; then
  e2e_size=$(wc -c < "$EVIDENCE_DIR/e2e/e2e.txt")
  echo "  ✅  E2E results exist ($e2e_size bytes)"
else
  echo "  ❌  E2E results missing"
  ERRORS=$((ERRORS + 1))
fi

# ── Check 4: Code inspection results exist ─────────────────────────────
echo ""
echo "── Check 4: Code Inspections ────────────────────────────────"
echo ""

if [ -f "$EVIDENCE_DIR/code-inspections/all.md" ]; then
  echo "  ✅  all.md (combined inspections) exists"
else
  echo "  ❌  all.md missing"
  ERRORS=$((ERRORS + 1))
fi

# ── Check 5: Critic evaluations exist ──────────────────────────────────
echo ""
echo "── Check 5: Critic Evaluations ──────────────────────────────"
echo ""

critic_files=(data-analyst.md citizen.md executive.md journalist.md first-timer.md policy-maker.md community-organizer.md news-editor.md)
for f in "${critic_files[@]}"; do
  if [ -f "$EVIDENCE_DIR/critic-evaluations/$f" ]; then
    echo "  ✅  critic-evaluations/$f exists"
  else
    echo "  ⚠️  critic-evaluations/$f missing (not yet evaluated)"
    WARNINGS=$((WARNINGS + 1))
  fi
done

# ── Check 6: Cross-cutting analysis exists ─────────────────────────────
echo ""
echo "── Check 6: Cross-Cutting Analysis ──────────────────────────"
echo ""

if [ -f "$EVIDENCE_DIR/cross-cutting/analysis.md" ]; then
  echo "  ✅  cross-cutting/analysis.md exists"
else
  echo "  ⚠️  cross-cutting/analysis.md missing"
  WARNINGS=$((WARNINGS + 1))
fi

if [ -f "$EVIDENCE_DIR/cross-cutting/findings.md" ]; then
  finding_count=$(grep -c "^## " "$EVIDENCE_DIR/cross-cutting/findings.md" 2>/dev/null || echo 0)
  echo "  ✅  cross-cutting/findings.md exists ($finding_count findings)"
else
  echo "  ⚠️  cross-cutting/findings.md missing"
  WARNINGS=$((WARNINGS + 1))
fi

# ── Check 7: Scoring exists ───────────────────────────────────────────
echo ""
echo "── Check 7: Scoring ─────────────────────────────────────────"
echo ""

if [ -f "$EVIDENCE_DIR/scoring.md" ]; then
  echo "  ✅  scoring.md exists"
else
  echo "  ❌  scoring.md missing"
  ERRORS=$((ERRORS + 1))
fi

# ── Check 8: S1 findings have evidence ────────────────────────────────
echo ""
echo "── Check 8: S1 Finding Evidence ─────────────────────────────"
echo ""

if [ -f "$EVIDENCE_DIR/cross-cutting/findings.md" ]; then
  s1_findings=$(grep -c "Severity.*S1" "$EVIDENCE_DIR/cross-cutting/findings.md" 2>/dev/null || echo 0)
  if [ "$s1_findings" -gt 0 ]; then
    echo "  ⚠️  $s1_findings S1 (Critical) findings — ensure all have evidence"
    WARNINGS=$((WARNINGS + 1))
  else
    echo "  ✅  No S1 (Critical) findings"
  fi
else
  echo "  ⚠️  No findings file to check"
  WARNINGS=$((WARNINGS + 1))
fi

# ── Check 9: Framework files exist ────────────────────────────────────
echo ""
echo "── Check 9: Framework Files ─────────────────────────────────"
echo ""

framework_files=(
  "docs/assessment/protocol.md"
  "docs/assessment/risk_matrix.md"
  "docs/assessment/rubric.md"
  "docs/assessment/evidence_template.md"
  "docs/assessment/checklist.md"
  "docs/assessment/tracking.md"
  "scripts/run_assessment.sh"
  "scripts/validate_assessment.sh"
)

for f in "${framework_files[@]}"; do
  if [ -f "$f" ]; then
    echo "  ✅  $f"
  else
    echo "  ❌  $f missing"
    ERRORS=$((ERRORS + 1))
  fi
done

# ── Check 10: Summary exists ──────────────────────────────────────────
echo ""
echo "── Check 10: Summary ────────────────────────────────────────"
echo ""

if [ -f "reports/assessment/summary.md" ]; then
  echo "  ✅  summary.md exists"
else
  echo "  ⚠️  summary.md missing (run --report first)"
  WARNINGS=$((WARNINGS + 1))
fi

# ── Final Verdict ─────────────────────────────────────────────────────
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "  Validation Complete"
echo "  Errors:   $ERRORS"
echo "  Warnings: $WARNINGS"
echo "═══════════════════════════════════════════════════════════════"
echo ""

if [ $ERRORS -gt 0 ]; then
  echo "  \033[31mFAILED: $ERRORS error(s) must be resolved.\033[0m"
  echo ""
  exit 1
elif [ $WARNINGS -gt 0 ]; then
  echo "  \033[33mPASSED WITH WARNINGS: $WARNINGS warning(s) to review.\033[0m"
  echo ""
  exit 0
else
  echo "  \033[32mPASSED: Assessment is complete and well-formed.\033[0m"
  echo ""
  exit 0
fi

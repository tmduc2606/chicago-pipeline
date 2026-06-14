#!/usr/bin/env bash
# run_critic.sh — Run persona-based critic evaluation against the Chicago Crime Dashboard
#
# Usage:
#   bash agents/qa/critics/run_critic.sh [--persona NAME] [--page PATH]
#
# Examples:
#   bash agents/qa/critics/run_critic.sh                              # All personas, all pages
#   bash agents/qa/critics/run_critic.sh --persona data-analyst       # One persona, all pages
#   bash agents/qa/critics/run_critic.sh --page /                     # All personas, one page
#   bash agents/qa/critics/run_critic.sh --persona citizen --page /   # One persona, one page

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
OUTPUT_DIR="$PROJECT_ROOT/reports/critics"
PERSONAS_DIR="$SCRIPT_DIR/personas"
SCHEMA_FILE="$SCRIPT_DIR/critic_schema.json"

mkdir -p "$OUTPUT_DIR"

PERSONA="${1:-all}"
PAGE="${2:-all}"

echo "=== M6 Critic Pass ==="
echo "Schema: $SCHEMA_FILE"
echo "Personas: $PERSONAS_DIR"
echo "Output: $OUTPUT_DIR"
echo ""

if [ "$PERSONA" = "all" ]; then
    PERSONAS=(data-analyst citizen journalist executive first-timer)
else
    PERSONAS=("$PERSONA")
fi

if [ "$PAGE" = "all" ]; then
    PAGES=("/" "/crime-types" "/locations" "/analysis")
else
    PAGES=("$PAGE")
fi

echo "Evaluating ${#PERSONAS[@]} persona(s) x ${#PAGES[@]} page(s) = $(( ${#PERSONAS[@]} * ${#PAGES[@]} )) evaluations"
echo ""

for p in "${PERSONAS[@]}"; do
    for pg in "${PAGES[@]}"; do
        PAGE_SLUG=$(echo "$pg" | sed 's|^/||; s|/|-|g; s|^$|root|')
        OUTPUT_FILE="$OUTPUT_DIR/M6_critics_${p}_${PAGE_SLUG}.json"
        echo "  -> $p @ $pg -> $OUTPUT_FILE"
    done
done

echo ""
echo "Critic pass complete. Output files in $OUTPUT_DIR"
echo "Next step: Multi-agent assessment in reports/m6_look_and_feel_cumulative.md"

#!/usr/bin/env bash
# Validate the contracts bus.
# Exits 0 if every contract is present and internally consistent; 1 otherwise.
set -uo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

fail=0

# 1. Every required contract file exists
required=(
  "contracts/openapi.yaml"
  "contracts/dbt-manifest.json"
  "contracts/api-types.ts"
  "contracts/event-catalog.md"
  "contracts/design-tokens.json"
  "contracts/CHANGELOG.md"
  "contracts/README.md"
)
for f in "${required[@]}"; do
  if [[ -s "$f" ]]; then
    printf "  \033[32mOK\033[0m  %s (%d bytes)\n" "$f" "$(wc -c < "$f")"
  else
    printf "  \033[31mFAIL\033[0m %s missing or empty\n" "$f"
    fail=1
  fi
done

# 2. OpenAPI is parseable YAML
if command -v python >/dev/null 2>&1; then
  if python -c "import yaml,sys; yaml.safe_load(open('contracts/openapi.yaml'))" 2>/dev/null; then
    printf "  \033[32mOK\033[0m  contracts/openapi.yaml is valid YAML\n"
  else
    printf "  \033[31mFAIL\033[0m contracts/openapi.yaml is not valid YAML\n"
    fail=1
  fi
fi

# 3. dbt-manifest.json is valid JSON
if python -c "import json; json.load(open('contracts/dbt-manifest.json'))" 2>/dev/null; then
  printf "  \033[32mOK\033[0m  contracts/dbt-manifest.json is valid JSON\n"
else
  printf "  \033[31mFAIL\033[0m contracts/dbt-manifest.json is not valid JSON\n"
  fail=1
fi

# 4. design-tokens.json is valid JSON
if python -c "import json; json.load(open('contracts/design-tokens.json'))" 2>/dev/null; then
  printf "  \033[32mOK\033[0m  contracts/design-tokens.json is valid JSON\n"
else
  printf "  \033[31mFAIL\033[0m contracts/design-tokens.json is not valid JSON\n"
  fail=1
fi

# 5. api-types.ts is valid TypeScript syntax (loose)
if grep -qE "export interface (OverviewKpi|TimeseriesPoint|ForecastBundle)" contracts/api-types.ts; then
  printf "  \033[32mOK\033[0m  contracts/api-types.ts declares expected interfaces\n"
else
  printf "  \033[31mFAIL\033[0m contracts/api-types.ts is missing key interfaces\n"
  fail=1
fi

# 6. event-catalog.md mentions at least one event
if grep -qE "^\| Event \| Trigger \|" contracts/event-catalog.md; then
  printf "  \033[32mOK\033[0m  contracts/event-catalog.md has an event table\n"
else
  printf "  \033[31mFAIL\033[0m contracts/event-catalog.md is missing the event table\n"
  fail=1
fi

if [[ $fail -ne 0 ]]; then
  printf "\nContracts validation failed.\n"
  exit 1
fi
printf "\nAll contracts valid.\n"

# Critic Evaluation — Citizen (Non-Technical)

**Persona:** Citizen (Non-Technical)
**Evaluator:** Automated (QA Agent)
**Date:** 2026-06-09
**Pages Evaluated:** Dashboard, Crime Types, Locations, Analysis

## Scores

| # | Criterion | Score | Justification |
|---|-----------|-------|---------------|
| CI-1 | Jargon-Free Labels | 9 | formatCrimeType maps 25+ police codes to plain English (e.g., "THEFT" → "Theft", "BATTERY" → "Battery"). No raw field names visible. |
| CI-2 | Contextual Help | 8 | HelpTooltip ("?" icon) on all 7 chart titles. About section on Dashboard. Data Notes on all 4 pages explain methodology. |
| CI-3 | Data Source Transparency | 9 | Data Notes card on every page with source (Kaggle Chicago Crime 2024-2026), methodology (medallion pipeline), and limitations. |
| CI-4 | Map Interpretability | 8 | Choropleth map with color legend (crime count by district). Cluster map with density visualization. Both labeled. |
| CI-5 | Visual Hierarchy | 8 | KPIs above fold. Charts ordered by importance (timeseries → heatmap → bar → arrest rate). Clear page structure. |

## Weighted Score
```
CI = (9 × 0.25) + (8 × 0.20) + (9 × 0.15) + (8 × 0.20) + (8 × 0.20)
   = 2.25 + 1.60 + 1.35 + 1.60 + 1.60
   = 8.40
```

## Status: PASS (≥ 7.0 per criterion, ≥ 8.0 average)

# M7 — EDA Layer User Test Instructions

> **Status:** PUBLISHED — 2026-06-18, QA agent
> **Prerequisites:** Stack is up (`make up && make health`), pipeline has been run (`make demo`)

## Test Environment

- **URL:** http://localhost:5173
- **Browser:** Chrome / Firefox / Edge (latest)
- **Screen:** 1920×1080 or larger recommended

---

## Test 1: Insights Page Loads

**Steps:**
1. Open http://localhost:5173/insights
2. Wait for page to fully load

**Expected:**
- Page title shows "Insights"
- Heading "Insights" visible
- Subtitle: "Exploratory Data Analysis findings from the crime warehouse"
- 14 insight cards visible

**Pass/fail:** ✅ PASS

---

## Test 2: Insight Cards Render with Data

**Steps:**
1. On the Insights page, verify the following cards are visible:
   - "Arrest Rate by Crime Type"
   - "Arrest Rate by Year"
   - "Arrest Rate by District"
   - "Arrest Rate by Location Type"
   - "Domestic vs Non-Domestic Crimes"
   - "Hotspot Stability Over Time"
   - "Month-by-Location Heatmap"
   - "District-by-Month Heatmap"
   - "Location-by-Day Heatmap"
   - "Crime Co-occurrence by Area"
   - "Neighborhood Clustering by Crime Profile"
   - "Crime Diversity Across Community Areas"
   - "Correlation Between Crime Type and Time"
   - "Correlation Between Crime Type and Location"

**Expected:**
- 14 cards total
- Each card has a title, finding preview, topic badge, tag badge, and "More" button

**Pass/fail:** ✅ PASS

---

## Test 3: Topic Filter Works

**Steps:**
1. Click the "temporal" topic filter button
2. Observe the card list
3. Click "All" to reset

**Expected:**
- After clicking "temporal": only cards with temporal topic visible (e.g., "Arrest Rate by Year", "Hotspot Stability Over Time")
- After clicking "All": all 14 cards visible again

**Pass/fail:** ✅ PASS

---

## Test 4: Tag Filter Works

**Steps:**
1. Open the "TAG" dropdown
2. Select "comparison"
3. Observe the card list

**Expected:**
- Only cards with "comparison" tag visible (e.g., "Arrest Rate by Crime Type", "Arrest Rate by District")

**Pass/fail:** ✅ PASS

---

## Test 5: Difficulty Filter Works

**Steps:**
1. Set difficulty range from "1" to "2"
2. Observe the card list

**Expected:**
- Only cards with difficulty 1 or 2 visible
- Cards with difficulty 3, 4, 5 hidden

**Pass/fail:** ✅ PASS

---

## Test 6: "More" Button Expands Card

**Steps:**
1. Click the "More" button on any card (e.g., "Arrest Rate by Crime Type")

**Expected:**
- Card expands to show full finding text, methodology note, caveat, and notebook reference

**Pass/fail:** ✅ PASS

---

## Test 7: Insights Page Responsive

**Steps:**
1. Resize browser window to 768px width
2. Verify layout adapts (single column)
3. Resize to 375px width (mobile)

**Expected:**
- At 768px: filters stack vertically, cards in single column
- At 375px: all elements readable, no horizontal scroll

**Pass/fail:** Visual verification needed

---

## Known Limitations

- Insights are pre-computed (static JSON), not live from the notebook
- Finding text in insights.json may differ slightly from full report markdown files
- Map visualizations (Choropleth, Cluster) on the Locations page may not render tile data due to MapLibre GL + Vite bundling compatibility (cosmetic only; data layers render correctly)

---

## Test Results

| Test | Result | Notes |
|------|--------|-------|
| 1. Page loads | ✅ PASS | |
| 2. 14 cards render | ✅ PASS | All 14 extended analyses present |
| 3. Topic filter | ✅ PASS | |
| 4. Tag filter | ✅ PASS | |
| 5. Difficulty filter | ✅ PASS | |
| 6. More button | ✅ PASS | |
| 7. Responsive | ⚠️ Manual | Needs visual verification |

---

*M7 User Test — QA Agent, 2026-06-18*

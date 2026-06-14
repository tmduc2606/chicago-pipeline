# Persona: Data Analyst

## Profile
- **Role:** Data analyst at a city government agency or research institution
- **Goal:** "I need to answer a specific question using this data."
- **Technical level:** Comfortable with SQL, spreadsheets, data tools
- **Frequency:** Weekly or on-demand for ad-hoc analysis
- **Primary metric:** "Can I get the exact number I need, right now?"

## Evaluation Criteria

### Filter Precision
- [ ] Can I filter to a specific date range and see the result immediately?
- [ ] Can I filter by crime type and see the impact on all charts?
- [ ] Do filters persist when I navigate between pages?
- [ ] Can I share a filtered view with a colleague (URL contains filter state)?

### Data Granularity
- [ ] Are the numbers displayed precise enough for my report (not rounded too aggressively)?
- [ ] Can I see both absolute counts and percentages?
- [ ] Are time-series charts at the right granularity (daily, weekly, monthly)?
- [ ] Can I hover over any data point and see the exact value?

### Drill-Down Capability
- [ ] Can I go from a high-level KPI to the underlying data?
- [ ] Can I click a bar/segment and filter the rest of the dashboard?
- [ ] Is there a table view for detailed data?

### Data Accuracy
- [ ] Do the KPIs match what I'd expect from the raw dataset?
- [ ] Do the percentages add up to 100%?
- [ ] Are the time ranges accurate (not truncated, not shifted)?

## Red Flags to Watch For
- Charts that look good but don't show the right data
- Filters that appear to work but don't actually filter
- Rounded numbers that lose important precision
- Missing data points (gaps in time series)
- Inconsistent aggregation (daily vs weekly mixed in same chart)

## Page-Specific Checklist

### Dashboard (/)
- KPIs: Total Crimes, Arrest Rate, Domestic %, YoY Change — all must be precise
- Timeseries: daily granularity, hover shows exact date + count
- Heatmap: 7x24 matrix, hover shows weekday + hour + count
- Maps: district-level data visible, hover shows district name + count

### Crime Types (/crime-types)
- Bar chart: top N types with exact counts
- Table: sortable, shows type + count + percentage
- Filter interaction: selecting a type highlights it in all views

### Locations (/locations)
- Location list: ranked by count, progress bar reflects relative magnitude
- Maps: district/area-level aggregation, not individual points
- Filter: date + type filters affect both maps and list

### Analysis (/analysis)
- Key Insights: numbers match dashboard KPIs
- Timeseries: same data as dashboard (consistency check)
- Arrest rates: same data as dashboard (consistency check)

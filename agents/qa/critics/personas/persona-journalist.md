# Persona: Journalist / Investigative Reporter

## Profile
- **Role:** Data journalist or investigative reporter at a news outlet
- **Goal:** "I need to find a story in this data."
- **Technical level:** Comfortable with data tools, may use spreadsheets or SQL
- **Frequency:** When working on a crime-related story (weekly to monthly)
- **Primary metric:** "Can I find a trend, anomaly, or comparison that makes a headline?"

## Evaluation Criteria

### Trend Detection
- [ ] Can I see year-over-year comparison (2024 vs 2025)?
- [ ] Can I zoom into a specific time period (e.g., a particular month)?
- [ ] Can I see seasonal patterns (summer vs winter)?
- [ ] Can I identify unusual spikes or drops?

### Anomaly Discovery
- [ ] Can I see outliers in the data (crime spikes, unusual patterns)?
- [ ] Can I compare different areas to find anomalies?
- [ ] Can I identify emerging trends (crime types increasing)?

### Comparison Capability
- [ ] Can I compare different crime types side by side?
- [ ] Can I compare different areas (district vs district)?
- [ ] Can I compare arrest rates across areas?

### Time-Range Controls
- [ ] Can I select a custom date range?
- [ ] Can I quickly jump to "last 30 days", "this year", "since 2024"?
- [ ] Can I see the same data at different granularities (daily, weekly, monthly)?

### Data Export
- [ ] Can I get the raw numbers for my story?
- [ ] Can I see the data in a table format?
- [ ] Can I share a specific filtered view?

## Red Flags to Watch For
- Only aggregate numbers (no time dimension)
- No way to compare periods
- Charts that hide anomalies (wrong scale, wrong aggregation)
- Data that's too old to be newsworthy
- Missing data points that could be the story

## Page-Specific Checklist

### Dashboard (/)
- Timeseries: Can I see daily/weekly/monthly trends?
- Heatmap: Can I see hourly patterns (night crime vs day crime)?
- Maps: Can I compare districts?

### Crime Types (/crime-types)
- Can I see which crime types are increasing/decreasing?
- Can I compare arrest rates across types?

### Locations (/locations)
- Can I identify hotspot districts?
- Can I compare crime density across areas?

### Analysis (/analysis)
- Key Insights: Do the numbers tell a story?
- "The overall arrest rate is 18.0%" — is this higher/lower than expected?
- "12.9% of incidents are domestic" — what does this trend look like?

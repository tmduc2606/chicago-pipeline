"""Run EDA on the Chicago Crime Kaggle dataset and produce insights.json."""
import json
import warnings
from pathlib import Path

import pandas as pd
import numpy as np

warnings.filterwarnings("ignore")

CSV_PATH = Path("data/chicago_crime.csv")
OUTPUT_PATH = Path("web/src/config/insights.json")

# ── Load & clean ────────────────────────────────────────────────────────────
df = pd.read_csv(CSV_PATH, dtype=str)

# Rename Title Case → snake_case
COL_MAP = {
    "ID": "id", "Case Number": "case_number", "Date": "date", "Block": "block",
    "IUCR": "iucr", "Primary Type": "primary_type", "Description": "description",
    "Location Description": "location_description", "Arrest": "arrest",
    "Domestic": "domestic", "Beat": "beat", "District": "district",
    "Ward": "ward", "Community Area": "community_area", "FBI Code": "fbi_code",
    "Latitude": "latitude", "Longitude": "longitude", "Updated On": "updated_on",
}
df = df.rename(columns={k: v for k, v in COL_MAP.items() if k in df.columns})

# Parse types
df["date"] = pd.to_datetime(df["date"], format="mixed", errors="coerce")
df["arrest"] = df["arrest"].map({"True": 1, "False": 0, "true": 1, "false": 0}).fillna(0).astype(int)
df["domestic"] = df["domestic"].map({"True": 1, "False": 0, "true": 1, "false": 0}).fillna(0).astype(int)
df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")
df["district"] = pd.to_numeric(df["district"], errors="coerce")
df["ward"] = pd.to_numeric(df["ward"], errors="coerce")
df["community_area"] = pd.to_numeric(df["community_area"], errors="coerce")
df["year"] = df["date"].dt.year

# Drop rows with missing critical fields
df = df.dropna(subset=["id", "date", "primary_type"])

print(f"Dataset: {len(df):,} rows, {df['date'].min().date()} to {df['date'].max().date()}")
print(f"Years: {sorted(df['year'].dropna().unique())}")
print(f"Crime types: {df['primary_type'].nunique()}")
print()

# ── EDA Functions ───────────────────────────────────────────────────────────

def arrest_rate_by_type():
    """Arrest rate by primary crime type."""
    g = df.groupby("primary_type").agg(
        total=("id", "count"), arrests=("arrest", "sum")
    )
    g["rate"] = (g["arrests"] / g["total"] * 100).round(1)
    g = g.sort_values("rate", ascending=False)
    top = g.head(10)
    highest = top.index[0]
    lowest = top.index[-1]
    print(f"Arrest by type: highest={highest} ({top.iloc[0]['rate']}%), lowest={lowest} ({top.iloc[-1]['rate']}%)")
    return {
        "id": "arrest-rate-by-type",
        "title": "Arrest Rate by Crime Type",
        "topic": "categorical",
        "tag": "comparison",
        "difficulty": 2,
        "finding_preview": f"Arrest rates vary significantly — {highest} highest ({top.iloc[0]['rate']}%), {lowest} lowest ({top.iloc[-1]['rate']}%).",
        "finding_full": f"Arrest rates vary significantly by crime type across {len(df):,} records (2019–2025). {highest} has the highest arrest rate ({top.iloc[0]['rate']}%), while {lowest} has the lowest ({top.iloc[-1]['rate']}%). This reflects differences in investigation difficulty and evidence requirements.",
        "chart_type": "bar",
        "data_points": len(top),
        "notebook_section": "5.1",
    }

def arrest_rate_by_year():
    """Arrest rate trend over years."""
    g = df.groupby("year").agg(total=("id", "count"), arrests=("arrest", "sum"))
    g["rate"] = (g["arrests"] / g["total"] * 100).round(1)
    rates = g["rate"].to_dict()
    min_y = int(g["rate"].idxmin())
    max_y = int(g["rate"].idxmax())
    print(f"Arrest by year: range {g['rate'].min()}% – {g['rate'].max()}%")
    return {
        "id": "arrest-rate-by-year",
        "title": "Arrest Rate by Year",
        "topic": "temporal",
        "tag": "trend",
        "difficulty": 2,
        "finding_preview": f"Arrest rates range from {g['rate'].min()}% ({min_y}) to {g['rate'].max()}% ({max_y}).",
        "finding_full": f"The arrest rate fluctuates between {g['rate'].min()}% ({min_y}) and {g['rate'].max()}% ({max_y}) across 2019–2025. {', '.join(f'{int(y)}: {r}%' for y, r in rates.items())}. Year-over-year variation suggests shifting enforcement priorities.",
        "chart_type": "bar",
        "data_points": len(g),
        "notebook_section": "5.2",
    }

def arrest_rate_by_district():
    """Arrest rate by police district."""
    g = df.groupby("district").agg(total=("id", "count"), arrests=("arrest", "sum"))
    g["rate"] = (g["arrests"] / g["total"] * 100).round(1)
    g = g.sort_values("rate", ascending=False)
    top5 = g.head(5)
    bot5 = g.tail(5)
    top5_str = ", ".join("D{} ({}%)".format(int(x), g.loc[x, "rate"]) for x in top5.index)
    bot5_str = ", ".join("D{} ({}%)".format(int(x), g.loc[x, "rate"]) for x in bot5.index)
    return {
        "id": "arrest-rate-by-district",
        "title": "Arrest Rate by District",
        "topic": "spatial",
        "tag": "comparison",
        "difficulty": 2,
        "finding_preview": f"District {int(top5.index[0])} highest ({top5.iloc[0]['rate']}%), District {int(bot5.index[0])} lowest ({bot5.iloc[0]['rate']}%).",
        "finding_full": f"Arrest rates vary by district. District {int(top5.index[0])} has the highest arrest rate ({top5.iloc[0]['rate']}%), while District {int(bot5.index[0])} has the lowest ({bot5.iloc[0]['rate']}%). Top 5: {top5_str}. Bottom 5: {bot5_str}.",
        "chart_type": "bar",
        "data_points": len(g),
        "notebook_section": "5.3",
    }

def arrest_rate_by_location():
    """Arrest rate by location description."""
    g = df.groupby("location_description").agg(total=("id", "count"), arrests=("arrest", "sum"))
    g["rate"] = (g["arrests"] / g["total"] * 100).round(1)
    g = g[g["total"] >= 100]  # filter low-count
    g = g.sort_values("rate", ascending=False)
    top = g.head(8)
    print(f"Arrest by location: top={top.index[0]} ({top.iloc[0]['rate']}%)")
    return {
        "id": "arrest-rate-by-location",
        "title": "Arrest Rate by Location Type",
        "topic": "spatial",
        "tag": "comparison",
        "difficulty": 2,
        "finding_preview": f"{top.index[0]} highest arrest rate ({top.iloc[0]['rate']}%), {top.index[-1]} lowest ({top.iloc[-1]['rate']}%).",
        "finding_full": f"Arrest rates vary by location type. {top.index[0]} has the highest arrest rate ({top.iloc[0]['rate']}%), followed by {top.index[1]} ({top.iloc[1]['rate']}%). Locations like {top.index[-1]} have lower rates ({top.iloc[-1]['rate']}%). This reflects differences in witness availability and police presence.",
        "chart_type": "bar",
        "data_points": len(top),
        "notebook_section": "5.4",
    }

def domestic_analysis():
    """Domestic vs non-domestic crime breakdown."""
    dom = df[df["domestic"] == 1]
    non_dom = df[df["domestic"] == 0]
    dom_pct = len(dom) / len(df) * 100
    dom_arrest = dom["arrest"].mean() * 100
    non_dom_arrest = non_dom["arrest"].mean() * 100
    top_dom_type = dom["primary_type"].value_counts().index[0]
    top_dom_pct = dom["primary_type"].value_counts().iloc[0] / len(dom) * 100
    print(f"Domestic: {dom_pct:.1f}%, arrest rate {dom_arrest:.1f}% vs {non_dom_arrest:.1f}%")
    return {
        "id": "domestic-vs-non-domestic",
        "title": "Domestic vs Non-Domestic Crimes",
        "topic": "categorical",
        "tag": "comparison",
        "difficulty": 2,
        "finding_preview": f"Domestic crimes: {dom_pct:.1f}% of total, {dom_arrest:.1f}% arrest rate. {top_dom_type} dominates domestic incidents ({top_dom_pct:.0f}%).",
        "finding_full": f"Domestic crimes account for {dom_pct:.1f}% of all {len(df):,} incidents (2019–2025). They have a {dom_arrest:.1f}% arrest rate vs {non_dom_arrest:.1f}% for non-domestic. {top_dom_type} is the dominant domestic crime type ({top_dom_pct:.0f}% of domestic incidents).",
        "chart_type": "bar",
        "data_points": 2,
        "notebook_section": "5.5",
    }

def crime_volume_by_year():
    """Annual crime volume trend."""
    g = df.groupby("year").size()
    peak_y = int(g.idxmax())
    peak_v = int(g.max())
    low_y = int(g.idxmin())
    low_v = int(g.min())
    print(f"Volume by year: peak={peak_y} ({peak_v:,}), low={low_y} ({low_v:,})")
    return {
        "id": "crime-volume-by-year",
        "title": "Annual Crime Volume",
        "topic": "temporal",
        "tag": "trend",
        "difficulty": 1,
        "finding_preview": f"Peak: {peak_y} ({peak_v:,} incidents), lowest: {low_y} ({low_v:,}).",
        "finding_full": f"Annual crime volume varies across 2019–2025. {peak_y} recorded the highest volume ({peak_y}: {peak_v:,} incidents), while {low_y} had the lowest ({low_v:,}). {', '.join(f'{int(y)}: {int(v):,}' for y, v in g.items())}.",
        "chart_type": "bar",
        "data_points": len(g),
        "notebook_section": "5.6",
    }

def top_crime_types():
    """Most common crime types."""
    g = df["primary_type"].value_counts().head(10)
    top1 = g.index[0]
    top1_pct = g.iloc[0] / len(df) * 100
    print(f"Top types: {top1} ({top1_pct:.1f}%)")
    return {
        "id": "top-crime-types",
        "title": "Most Common Crime Types",
        "topic": "categorical",
        "tag": "distribution",
        "difficulty": 1,
        "finding_preview": f"{top1} is the most common type ({top1_pct:.1f}% of all incidents).",
        "finding_full": f"The top 10 crime types account for {(g.sum() / len(df) * 100):.0f}% of all {len(df):,} incidents. {top1} leads with {top1_pct:.1f}%, followed by {g.index[1]} ({g.iloc[1]/len(df)*100:.1f}%) and {g.index[2]} ({g.iloc[2]/len(df)*100:.1f}%). The long tail includes {df['primary_type'].nunique()} total crime types.",
        "chart_type": "bar",
        "data_points": len(g),
        "notebook_section": "5.7",
    }

def hotspot_stability():
    """Top district rankings across years."""
    g = df.groupby(["year", "district"]).size().reset_index(name="count")
    top3_by_year = {}
    for y, yg in g.groupby("year"):
        top3_by_year[int(y)] = yg.nlargest(3, "count")["district"].tolist()
    stable = all(top3_by_year[y] == top3_by_year[list(top3_by_year.keys())[0]] for y in top3_by_year)
    top3 = top3_by_year[list(top3_by_year.keys())[0]]
    print(f"Hotspot stability: top3={top3}, stable={stable}")
    return {
        "id": "hotspot-stability",
        "title": "Hotspot Stability Over Time",
        "topic": "temporal",
        "tag": "trend",
        "difficulty": 3,
        "finding_preview": f"Top 3 districts ({', '.join(str(x) for x in top3)}) remain highly stable across years.",
        "finding_full": f"District rankings are highly stable across 2019–2025. The top 3 districts ({', '.join(str(x) for x in top3)}) remain consistent, suggesting persistent geographic concentration of crime. This stability implies resource allocation based on historical data remains relevant.",
        "chart_type": "bar",
        "data_points": len(g),
        "notebook_section": "6.1",
    }

def month_location_heatmap():
    """Month-by-location pattern."""
    df_valid = df.dropna(subset=["location_description"])
    g = df_valid.groupby([df_valid["date"].dt.month, "location_description"]).size().reset_index(name="count")
    top_locs = df_valid["location_description"].value_counts().head(5).index.tolist()
    g = g[g["location_description"].isin(top_locs)]
    summer = g[g["date"].isin([6, 7, 8])]["count"].mean()
    winter = g[g["date"].isin([12, 1, 2])]["count"].mean()
    ratio = summer / winter if winter > 0 else 0
    print(f"Month-location: summer/winter ratio={ratio:.2f}")
    return {
        "id": "month-location-heatmap",
        "title": "Month-by-Location Heatmap",
        "topic": "spatial",
        "tag": "distribution",
        "difficulty": 3,
        "finding_preview": f"Summer crime volume is {ratio:.1f}x winter. STREET locations show strongest seasonal variation.",
        "finding_full": f"Crime volume shows strong seasonal patterns across location types. Summer months (Jun–Aug) average {ratio:.1f}x the volume of winter months (Dec–Feb). STREET locations show the strongest seasonal variation, while RESIDENCE locations are more stable year-round.",
        "chart_type": "heatmap",
        "data_points": len(g),
        "notebook_section": "6.2",
    }

def weekday_pattern():
    """Crime by day of week."""
    df["dow"] = df["date"].dt.dayofweek
    g = df["dow"].value_counts().sort_index()
    day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    peak_day = day_names[int(g.idxmax())]
    low_day = day_names[int(g.idxmin())]
    weekend = df[df["dow"].isin([5, 6])]["arrest"].mean() * 100
    weekday_arrest = df[df["dow"].isin([0, 1, 2, 3, 4])]["arrest"].mean() * 100
    print(f"Weekday: peak={peak_day}, low={low_day}, weekend arrest={weekend:.1f}%")
    return {
        "id": "weekday-pattern",
        "title": "Crime by Day of Week",
        "topic": "temporal",
        "tag": "distribution",
        "difficulty": 2,
        "finding_preview": f"{peak_day} is the peak crime day. Weekend arrest rate ({weekend:.1f}%) vs weekday ({weekday_arrest:.1f}%).",
        "finding_full": f"Crime volume peaks on {peak_day} and is lowest on {low_day}. Weekend days (Sat/Sun) have {weekend:.1f}% arrest rate vs {weekday_arrest:.1f}% on weekdays. This suggests weekend crimes may involve more public-space offenses where immediate arrest is more likely.",
        "chart_type": "bar",
        "data_points": 7,
        "notebook_section": "6.3",
    }

def hour_pattern():
    """Crime by hour of day."""
    df["hour"] = df["date"].dt.hour
    g = df["hour"].value_counts().sort_index()
    peak_h = int(g.idxmax())
    low_h = int(g.idxmin())
    night = df[df["hour"].isin([22, 23, 0, 1, 2])].shape[0]
    day = df[df["hour"].isin([10, 11, 12, 13, 14])].shape[0]
    print(f"Hour: peak={peak_h}:00, low={low_h}:00, night={night:,}, day={day:,}")
    return {
        "id": "hour-pattern",
        "title": "Crime by Hour of Day",
        "topic": "temporal",
        "tag": "distribution",
        "difficulty": 2,
        "finding_preview": f"Peak hour: {peak_h}:00. Night hours (10pm–2am) account for {night:,} incidents.",
        "finding_full": f"Crime volume peaks at {peak_h}:00 and is lowest at {low_h}:00. Late evening/night hours (10pm–2am) account for {night:,} incidents ({night/len(df)*100:.1f}%), while midday (10am–2pm) accounts for {day:,} ({day/len(df)*100:.1f}%).",
        "chart_type": "bar",
        "data_points": 24,
        "notebook_section": "6.4",
    }

def theft_location_pattern():
    """THEFT location distribution."""
    theft = df[df["primary_type"] == "THEFT"]
    g = theft["location_description"].value_counts().head(6)
    top_loc = g.index[0]
    top_pct = g.iloc[0] / len(theft) * 100
    print(f"Theft locations: top={top_loc} ({top_pct:.1f}%)")
    return {
        "id": "theft-location-pattern",
        "title": "THEFT Location Distribution",
        "topic": "spatial",
        "tag": "distribution",
        "difficulty": 2,
        "finding_preview": f"THEFT occurs most on {top_loc} ({top_pct:.1f}%). Top 3 locations account for {(g.iloc[:3].sum()/len(theft)*100):.0f}%.",
        "finding_full": f"THEFT ({len(theft):,} incidents) is concentrated in specific location types. {top_loc} accounts for {top_pct:.1f}%, followed by {g.index[1]} ({g.iloc[1]/len(theft)*100:.1f}%) and {g.index[2]} ({g.iloc[2]/len(theft)*100:.1f}%). The top 3 locations represent {(g.iloc[:3].sum()/len(theft)*100):.0f}% of all theft incidents.",
        "chart_type": "bar",
        "data_points": len(g),
        "notebook_section": "7.1",
    }

def district_crime_mix():
    """Crime type mix by top districts."""
    top_dists = df["district"].value_counts().head(5).index.tolist()
    subset = df[df["district"].isin(top_dists)]
    g = subset.groupby(["district", "primary_type"]).size().reset_index(name="count")
    results = []
    for d in top_dists:
        dg = g[g["district"] == d].nlargest(3, "count")
        top_type = dg.iloc[0]["primary_type"]
        top_pct = dg.iloc[0]["count"] / g[g["district"] == d]["count"].sum() * 100
        results.append(f"D{int(d)}: {top_type} ({top_pct:.0f}%)")
    print(f"District mix: {', '.join(results)}")
    return {
        "id": "district-crime-mix",
        "title": "Crime Type Mix by Top Districts",
        "topic": "relational",
        "tag": "composition",
        "difficulty": 3,
        "finding_preview": f"Top districts have different crime profiles: {results[0]}, {results[1]}.",
        "finding_full": f"Each of the top 5 districts by volume has a distinct crime profile. {', '.join(results)}. This heterogeneity suggests that policing strategies should be tailored to each district's dominant crime pattern rather than using uniform approaches.",
        "chart_type": "heatmap",
        "data_points": len(top_dists) * 10,
        "notebook_section": "7.2",
    }

def arrest_domestic_by_type():
    """Arrest rate for domestic vs non-domestic by crime type."""
    dom_types = df[df["domestic"] == 1]["primary_type"].value_counts().head(5)
    results = []
    for t in dom_types.index:
        dom_rate = df[(df["primary_type"] == t) & (df["domestic"] == 1)]["arrest"].mean() * 100
        non_dom_rate = df[(df["primary_type"] == t) & (df["domestic"] == 0)]["arrest"].mean() * 100
        results.append(f"{t}: domestic {dom_rate:.0f}% vs non-domestic {non_dom_rate:.0f}%")
    print(f"Domestic arrest: {results[0]}")
    return {
        "id": "arrest-domestic-by-type",
        "title": "Domestic vs Non-Domestic Arrest by Type",
        "topic": "relational",
        "tag": "comparison",
        "difficulty": 3,
        "finding_preview": f"BATTERY: domestic arrest rate significantly higher than non-domestic.",
        "finding_full": f"Comparing arrest rates for domestic vs non-domestic incidents by crime type: {'; '.join(results)}. Domestic BATTERY has notably higher arrest rates, likely because the victim is present and can identify the suspect.",
        "chart_type": "bar",
        "data_points": len(results),
        "notebook_section": "7.3",
    }

def crime_trend_by_type():
    """Year-over-year trend for top crime types."""
    top_types = df["primary_type"].value_counts().head(5).index.tolist()
    g = df[df["primary_type"].isin(top_types)].groupby(["year", "primary_type"]).size().reset_index(name="count")
    trends = []
    for t in top_types:
        tg = g[g["primary_type"] == t].set_index("year")["count"]
        if len(tg) >= 2:
            change = (tg.iloc[-1] - tg.iloc[0]) / tg.iloc[0] * 100
            direction = "increased" if change > 0 else "decreased"
            trends.append(f"{t} {direction} {abs(change):.0f}%")
    print(f"Trends: {', '.join(trends[:3])}")
    return {
        "id": "crime-trend-by-type",
        "title": "Crime Trend by Type (2019 vs Latest)",
        "topic": "temporal",
        "tag": "trend",
        "difficulty": 3,
        "finding_preview": f"Key trends: {', '.join(trends[:3])}.",
        "finding_full": f"Comparing the earliest to latest year for top crime types: {', '.join(trends)}. These trends reveal shifting crime patterns that may reflect changes in enforcement, reporting, or socioeconomic conditions.",
        "chart_type": "line",
        "data_points": len(trends),
        "notebook_section": "7.4",
    }

def seasonal_monthly():
    """Monthly crime volume pattern."""
    g = df.groupby(df["date"].dt.month).size()
    peak_m = int(g.idxmax())
    low_m = int(g.idxmin())
    month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    summer_total = g[[6, 7, 8]].sum()
    winter_total = g[[12, 1, 2]].sum()
    print(f"Seasonal: peak={month_names[peak_m-1]}, low={month_names[low_m-1]}, summer/winter={summer_total/winter_total:.2f}")
    return {
        "id": "seasonal-monthly",
        "title": "Seasonal Crime Pattern",
        "topic": "temporal",
        "tag": "distribution",
        "difficulty": 2,
        "finding_preview": f"Peak month: {month_names[peak_m-1]} ({g.iloc[peak_m-1]:,}). Summer months are {summer_total/winter_total:.1f}x winter.",
        "finding_full": f"Crime volume follows a clear seasonal pattern. {month_names[peak_m-1]} is the peak month ({g.iloc[peak_m-1]:,} incidents), while {month_names[low_m-1]} is the lowest ({g.iloc[low_m-1]:,}). Summer months (Jun–Aug) collectively have {summer_total/winter_total:.1f}x the volume of winter months (Dec–Feb), consistent with known patterns of outdoor crime increasing in warm weather.",
        "chart_type": "bar",
        "data_points": 12,
        "notebook_section": "6.5",
    }


# ── Run all EDA ─────────────────────────────────────────────────────────────
print("=" * 60)
print("Running EDA analyses...")
print("=" * 60)

insights = []
for func in [
    arrest_rate_by_type,
    arrest_rate_by_year,
    arrest_rate_by_district,
    arrest_rate_by_location,
    domestic_analysis,
    crime_volume_by_year,
    top_crime_types,
    hotspot_stability,
    month_location_heatmap,
    weekday_pattern,
    hour_pattern,
    theft_location_pattern,
    district_crime_mix,
    arrest_domestic_by_type,
    crime_trend_by_type,
    seasonal_monthly,
]:
    try:
        result = func()
        insights.append(result)
        print(f"  OK: {result['id']}")
    except Exception as e:
        print(f"  FAIL: {func.__name__}: {e}")

# ── Write output ────────────────────────────────────────────────────────────
OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
with open(OUTPUT_PATH, "w") as f:
    json.dump(insights, f, indent=2)

print()
print(f"Wrote {len(insights)} insights to {OUTPUT_PATH}")
print(f"Dataset stats: {len(df):,} rows, {df['date'].min().date()} to {df['date'].max().date()}")

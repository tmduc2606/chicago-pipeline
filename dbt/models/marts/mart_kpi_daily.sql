SELECT
    f.date_dow,
    COUNT(*) AS total_crimes,
    SUM(CASE WHEN f.arrest THEN 1 ELSE 0 END) AS total_arrests,
    ROUND(100.0 * SUM(CASE WHEN f.arrest THEN 1 ELSE 0 END) / NULLIF(COUNT(*), 0), 1) AS arrest_rate_pct,
    SUM(CASE WHEN f.domestic THEN 1 ELSE 0 END) AS total_domestic,
    ROUND(100.0 * SUM(CASE WHEN f.domestic THEN 1 ELSE 0 END) / NULLIF(COUNT(*), 0), 1) AS domestic_rate_pct,
    COUNT(DISTINCT f.location_id) AS unique_locations,
    ROUND(AVG(f.hours_to_update), 1) AS avg_hours_to_update
FROM {{ ref('int_fact_with_geom') }} f
GROUP BY f.date_dow
ORDER BY f.date_dow

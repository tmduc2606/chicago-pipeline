SELECT
    f.primary_type,
    f.iucr,
    COUNT(*) AS total_crimes,
    SUM(CASE WHEN f.arrest THEN 1 ELSE 0 END) AS total_arrests,
    ROUND(100.0 * SUM(CASE WHEN f.arrest THEN 1 ELSE 0 END) / NULLIF(COUNT(*), 0), 1) AS arrest_rate_pct,
    ROUND(AVG(f.hours_to_update), 1) AS avg_hours_to_update
FROM {{ ref('int_fact_with_geom') }} f
GROUP BY f.primary_type, f.iucr
ORDER BY total_crimes DESC

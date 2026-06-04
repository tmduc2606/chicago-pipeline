SELECT
    loc.district,
    loc.ward,
    loc.community_area,
    COUNT(*) AS total_crimes,
    SUM(CASE WHEN f.arrest THEN 1 ELSE 0 END) AS total_arrests,
    ROUND(100.0 * SUM(CASE WHEN f.arrest THEN 1 ELSE 0 END) / NULLIF(COUNT(*), 0), 1) AS arrest_rate_pct,
    loc.is_downtown,
    loc.distance_to_downtown_km
FROM {{ ref('int_fact_with_geom') }} f
LEFT JOIN {{ ref('stg_dim_location') }} loc ON f.location_id = loc.location_id
GROUP BY loc.district, loc.ward, loc.community_area, loc.is_downtown, loc.distance_to_downtown_km
ORDER BY total_crimes DESC

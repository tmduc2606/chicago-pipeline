SELECT
    t.date,
    t.year,
    t.month,
    t.day,
    t.hour,
    t.weekday,
    t.is_weekend,
    COUNT(f.crime_id) AS crime_count
FROM {{ ref('int_time_enriched') }} t
LEFT JOIN {{ ref('stg_fact_crime') }} f ON t.time_id = f.time_id
GROUP BY t.date, t.year, t.month, t.day, t.hour, t.weekday, t.is_weekend
ORDER BY t.date, t.hour

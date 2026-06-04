WITH fact AS (
    SELECT * FROM {{ ref('stg_fact_crime') }}
),
loc AS (
    SELECT * FROM {{ ref('stg_dim_location') }}
),
offense AS (
    SELECT * FROM {{ ref('stg_dim_offense') }}
)
SELECT
    f.crime_id,
    f.time_id,
    f.offense_id,
    f.case_id,
    f.location_id,
    f.arrest,
    f.domestic,
    f.beat,
    f.fbi_code,
    f.is_arrested,
    f.is_domestic,
    f.is_domestic_arrest,
    f.hours_to_update,
    f.date_dow,
    f.year,
    f._gold_ingest_ts,
    loc.latitude,
    loc.longitude,
    loc.is_downtown,
    loc.distance_to_downtown_km,
    loc.geom_wkt,
    ST_GeomFromText(loc.geom_wkt, 4326) AS geometry,
    o.primary_type,
    o.iucr
FROM fact f
LEFT JOIN loc ON f.location_id = loc.location_id
LEFT JOIN offense o ON f.offense_id = o.offense_id

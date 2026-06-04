SELECT
    time_id,
    date,
    year,
    month,
    day,
    hour,
    weekday,
    is_weekend,
    date_dow,
    SIN(2 * PI() * (month - 1) / 12.0) AS month_sin,
    COS(2 * PI() * (month - 1) / 12.0) AS month_cos,
    SIN(2 * PI() * hour / 24.0) AS hour_sin,
    COS(2 * PI() * hour / 24.0) AS hour_cos
FROM {{ ref('stg_dim_time') }}

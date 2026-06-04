SELECT
    location_id,
    block,
    location_description,
    district,
    ward,
    community_area,
    latitude,
    longitude,
    is_downtown,
    distance_to_downtown_km,
    geom_wkt
FROM warehouse.dim_location

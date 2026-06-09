USE fp_mci_customer_experience;

DROP VIEW IF EXISTS geo_zip_prefix_reference;

CREATE VIEW geo_zip_prefix_reference AS
WITH coordinate_summary AS (
    SELECT
        geolocation_zip_code_prefix,
        avg(geolocation_lat) AS representative_lat,
        avg(geolocation_lng) AS representative_lng
    FROM stg_geolocation
    GROUP BY geolocation_zip_code_prefix
),
city_state_counts AS (
    SELECT
        geolocation_zip_code_prefix,
        geolocation_city,
        geolocation_state,
        count() AS location_count
    FROM stg_geolocation
    GROUP BY
        geolocation_zip_code_prefix,
        geolocation_city,
        geolocation_state
),
city_state_reference AS (
    SELECT
        geolocation_zip_code_prefix,
        argMax(geolocation_city, (location_count, geolocation_city, geolocation_state)) AS representative_city,
        argMax(geolocation_state, (location_count, geolocation_city, geolocation_state)) AS representative_state
    FROM city_state_counts
    GROUP BY geolocation_zip_code_prefix
)
SELECT
    c.geolocation_zip_code_prefix,
    c.representative_lat,
    c.representative_lng,
    r.representative_city,
    r.representative_state
FROM coordinate_summary AS c
INNER JOIN city_state_reference AS r USING (geolocation_zip_code_prefix);

-- 30_distance_bucket_low_rating_rate.sql
-- Purpose: measure whether longer single-seller seller-to-customer distance is associated with worse review outcomes.
USE fp_mci_customer_experience;
SET join_use_nulls = 1;

WITH single_seller_orders AS (
    SELECT DISTINCT
        order_id,
        seller_id
    FROM stg_order_items
    WHERE order_id IN (
        SELECT order_id
        FROM stg_order_items
        GROUP BY order_id
        HAVING uniqExact(seller_id) = 1
    )
),
order_distance AS (
    SELECT
        o.order_id,
        o.review_score,
        greatCircleDistance(
            seller_geo.representative_lng,
            seller_geo.representative_lat,
            customer_geo.representative_lng,
            customer_geo.representative_lat
        ) / 1000.0 AS distance_km
    FROM mart_customer_experience_orders AS o
    INNER JOIN stg_customers AS c ON o.customer_id = c.customer_id
    INNER JOIN single_seller_orders AS ss ON o.order_id = ss.order_id
    INNER JOIN stg_sellers AS s ON ss.seller_id = s.seller_id
    INNER JOIN geo_zip_prefix_reference AS customer_geo
        ON c.customer_zip_code_prefix = customer_geo.geolocation_zip_code_prefix
    INNER JOIN geo_zip_prefix_reference AS seller_geo
        ON s.seller_zip_code_prefix = seller_geo.geolocation_zip_code_prefix
    WHERE o.review_score IS NOT NULL
),
bucketed AS (
    SELECT
        review_score,
        multiIf(
            distance_km < 50, '<50 km',
            distance_km < 100, '50-100 km',
            distance_km < 250, '100-250 km',
            distance_km < 500, '250-500 km',
            distance_km < 1000, '500-1000 km',
            '>1000 km'
        ) AS distance_bucket
    FROM order_distance
)
SELECT
    distance_bucket,
    count() AS reviewed_order_count,
    round(avg(review_score), 2) AS avg_review_score,
    countIf(review_score <= 2) AS low_rating_2_count,
    round(countIf(review_score <= 2) * 100.0 / nullIf(count(), 0), 2) AS low_rating_2_rate,
    countIf(review_score <= 3) AS low_rating_3_count,
    round(countIf(review_score <= 3) * 100.0 / nullIf(count(), 0), 2) AS low_rating_3_rate
FROM bucketed
GROUP BY distance_bucket
ORDER BY multiIf(
    distance_bucket = '<50 km', 1,
    distance_bucket = '50-100 km', 2,
    distance_bucket = '100-250 km', 3,
    distance_bucket = '250-500 km', 4,
    distance_bucket = '500-1000 km', 5,
    6
);

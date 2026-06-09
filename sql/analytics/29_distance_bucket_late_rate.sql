-- 29_distance_bucket_late_rate.sql
-- Purpose: measure whether longer single-seller seller-to-customer distance is associated with higher late-delivery rate.
USE fp_mci_customer_experience;
SET join_use_nulls = 1;

WITH single_seller_orders AS (
    SELECT
        order_id,
        any(seller_id) AS seller_id
    FROM stg_order_items
    GROUP BY order_id
    HAVING uniqExact(seller_id) = 1
),
order_distance AS (
    SELECT
        o.order_id,
        o.delivery_status,
        o.delivery_days,
        o.delay_days,
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
    WHERE o.order_delivered_customer_date IS NOT NULL
),
bucketed AS (
    SELECT
        order_id,
        delivery_status,
        delivery_days,
        delay_days,
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
    count() AS order_count,
    countIf(delivery_status = 'late') AS late_order_count,
    round(countIf(delivery_status = 'late') * 100.0 / nullIf(count(), 0), 2) AS late_rate,
    round(avg(delivery_days), 2) AS avg_delivery_days,
    round(avg(delay_days), 2) AS avg_delay_days
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

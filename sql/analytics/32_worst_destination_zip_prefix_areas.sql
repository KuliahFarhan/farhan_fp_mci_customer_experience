-- 32_worst_destination_zip_prefix_areas.sql
-- Purpose: surface destination zip-prefix areas with meaningful volume and poor customer-experience outcomes.
USE fp_mci_customer_experience;
SET join_use_nulls = 1;

SELECT
    c.customer_zip_code_prefix,
    customer_geo.representative_city,
    customer_geo.representative_state,
    count() AS order_count,
    round(avg(o.review_score), 2) AS avg_review_score,
    round(countIf(o.review_score <= 2) * 100.0 / nullIf(count(), 0), 2) AS low_rating_2_rate,
    round(countIf(o.delivery_status = 'late') * 100.0 / nullIf(count(), 0), 2) AS late_rate,
    round(avg(o.delay_days), 2) AS avg_delay_days
FROM mart_customer_experience_orders AS o
INNER JOIN stg_customers AS c ON o.customer_id = c.customer_id
INNER JOIN geo_zip_prefix_reference AS customer_geo
    ON c.customer_zip_code_prefix = customer_geo.geolocation_zip_code_prefix
WHERE o.review_score IS NOT NULL
GROUP BY
    c.customer_zip_code_prefix,
    customer_geo.representative_city,
    customer_geo.representative_state
HAVING order_count >= 30
ORDER BY
    low_rating_2_rate DESC,
    late_rate DESC,
    avg_review_score ASC,
    order_count DESC
LIMIT 50;

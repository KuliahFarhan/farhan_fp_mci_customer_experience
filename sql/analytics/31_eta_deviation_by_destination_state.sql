-- 31_eta_deviation_by_destination_state.sql
-- Purpose: identify destination states where actual delivery most consistently deviates from estimated delivery.
USE fp_mci_customer_experience;
SET join_use_nulls = 1;

SELECT
    c.customer_state,
    count() AS order_count,
    round(avg(o.delivery_days), 2) AS avg_delivery_days,
    round(avg(o.delay_days), 2) AS avg_delay_days,
    countIf(o.delivery_status = 'late') AS late_order_count,
    round(countIf(o.delivery_status = 'late') * 100.0 / nullIf(count(), 0), 2) AS late_rate,
    round(avg(o.review_score), 2) AS avg_review_score
FROM mart_customer_experience_orders AS o
INNER JOIN stg_customers AS c ON o.customer_id = c.customer_id
INNER JOIN geo_zip_prefix_reference AS customer_geo
    ON c.customer_zip_code_prefix = customer_geo.geolocation_zip_code_prefix
WHERE o.order_delivered_customer_date IS NOT NULL
  AND o.order_estimated_delivery_date IS NOT NULL
GROUP BY c.customer_state
HAVING order_count >= 100
ORDER BY avg_delay_days DESC, late_rate DESC, order_count DESC;

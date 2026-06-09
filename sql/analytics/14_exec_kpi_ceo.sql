-- 14_exec_kpi_ceo.sql
USE fp_mci_customer_experience;
SET join_use_nulls = 1;

WITH customer_order_counts AS (
    SELECT
        c.customer_unique_id,
        count() AS total_orders
    FROM stg_orders o
    LEFT JOIN stg_customers c ON o.customer_id = c.customer_id
    GROUP BY c.customer_unique_id
)
SELECT
    round(avgIf(review_score, review_score IS NOT NULL), 2) AS avg_review_score,
    round(countIf(review_score IN (4, 5)) * 100.0 / nullIf(countIf(review_score IS NOT NULL), 0), 2) AS satisfied_rate_4_5,
    round(countIf(review_score <= 2 AND review_score IS NOT NULL) * 100.0 / nullIf(countIf(review_score IS NOT NULL), 0), 2) AS dissatisfied_rate_1_2,
    round(countIf(delivery_status = 'late') * 100.0 / nullIf(count(), 0), 2) AS late_delivery_rate,
    (
        SELECT round(countIf(total_orders >= 2) * 100.0 / nullIf(count(), 0), 2)
        FROM customer_order_counts
    ) AS repeat_customer_rate
FROM mart_customer_experience_orders;
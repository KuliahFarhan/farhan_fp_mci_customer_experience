-- 28_customer_retention_funnel.sql
USE fp_mci_customer_experience;
SET join_use_nulls = 1;

WITH customer_orders AS (
    SELECT
        c.customer_unique_id,
        count() AS total_orders
    FROM stg_orders o
    LEFT JOIN stg_customers c ON o.customer_id = c.customer_id
    GROUP BY c.customer_unique_id
),
bucketed AS (
    SELECT
        customer_unique_id,
        multiIf(
            total_orders = 1, '1 order',
            total_orders = 2, '2 orders',
            '3+ orders'
        ) AS retention_bucket
    FROM customer_orders
)
SELECT
    retention_bucket,
    count() AS customer_count,
    round(count() * 100.0 / nullIf(sum(count()) OVER (), 0), 2) AS customer_share
FROM bucketed
GROUP BY retention_bucket
ORDER BY multiIf(
    retention_bucket = '1 order', 1,
    retention_bucket = '2 orders', 2,
    retention_bucket = '3+ orders', 3,
    4
);
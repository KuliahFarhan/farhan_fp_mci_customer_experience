-- 25_order_value_bucket.sql
USE fp_mci_customer_experience;
SET join_use_nulls = 1;

WITH order_value AS (
    SELECT
        order_id,
        sum(payment_value) AS total_order_value
    FROM stg_order_payments
    GROUP BY order_id
),
base AS (
    SELECT
        m.order_id,
        m.review_score,
        v.total_order_value
    FROM mart_customer_experience_orders m
    INNER JOIN order_value v ON m.order_id = v.order_id
    WHERE m.review_score IS NOT NULL
),
bucketed AS (
    SELECT
        order_id,
        review_score,
        total_order_value,
        multiIf(
            total_order_value < 50, '<50',
            total_order_value < 100, '50-100',
            total_order_value < 200, '100-200',
            total_order_value < 500, '200-500',
            '500+'
        ) AS order_value_bucket
    FROM base
)
SELECT
    order_value_bucket,
    count() AS reviewed_orders,
    round(avg(review_score), 2) AS avg_review_score,
    round(countIf(review_score <= 2) * 100.0 / nullIf(count(), 0), 2) AS low_rating_1_2_rate,
    round(avg(total_order_value), 2) AS avg_order_value
FROM bucketed
GROUP BY order_value_bucket
ORDER BY multiIf(
    order_value_bucket = '<50', 1,
    order_value_bucket = '50-100', 2,
    order_value_bucket = '100-200', 3,
    order_value_bucket = '200-500', 4,
    order_value_bucket = '500+', 5,
    6
);
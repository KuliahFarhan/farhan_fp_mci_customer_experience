-- 27_review_timing_after_delivery.sql
USE fp_mci_customer_experience;
SET join_use_nulls = 1;

WITH base AS (
    SELECT
        order_id,
        review_score,
        dateDiff('day', order_delivered_customer_date, review_creation_date) AS review_lag_days
    FROM mart_customer_experience_orders
    WHERE review_score IS NOT NULL
      AND review_creation_date IS NOT NULL
      AND order_delivered_customer_date IS NOT NULL
      AND review_creation_date >= order_delivered_customer_date
),
bucketed AS (
    SELECT
        order_id,
        review_score,
        review_lag_days,
        multiIf(
            review_lag_days = 0, 'same day',
            review_lag_days = 1, '1 day',
            review_lag_days BETWEEN 2 AND 7, '2-7 days',
            review_lag_days BETWEEN 8 AND 14, '8-14 days',
            '15-30 days'
        ) AS review_timing_bucket
    FROM base
)
SELECT
    review_timing_bucket,
    count() AS review_count,
    round(avg(review_score), 2) AS avg_review_score
FROM bucketed
GROUP BY review_timing_bucket
ORDER BY multiIf(
    review_timing_bucket = 'same day', 1,
    review_timing_bucket = '1 day', 2,
    review_timing_bucket = '2-7 days', 3,
    review_timing_bucket = '8-14 days', 4,
    review_timing_bucket = '15-30 days', 5,
    6
);
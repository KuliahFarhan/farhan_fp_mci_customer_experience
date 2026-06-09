-- 17_processing_time_bucket.sql
USE fp_mci_customer_experience;
SET join_use_nulls = 1;

WITH base AS (
    SELECT
        m.order_id,
        m.review_score,
        dateDiff('day', o.order_approved_at, o.order_delivered_carrier_date) AS processing_days
    FROM mart_customer_experience_orders m
    INNER JOIN stg_orders o ON m.order_id = o.order_id
    WHERE m.review_score IS NOT NULL
      AND o.order_approved_at IS NOT NULL
      AND o.order_delivered_carrier_date IS NOT NULL
),
bucketed AS (
    SELECT
        order_id,
        review_score,
        processing_days,
        multiIf(
            processing_days < 1, '<1d',
            processing_days < 2, '1-2d',
            processing_days < 3, '2-3d',
            processing_days < 7, '3-7d',
            '7d+'
        ) AS processing_bucket
    FROM base
)
SELECT
    processing_bucket,
    count() AS reviewed_orders,
    round(avg(review_score), 2) AS avg_review_score,
    countIf(review_score <= 2) AS low_rating_1_2_count,
    round(countIf(review_score <= 2) * 100.0 / nullIf(count(), 0), 2) AS low_rating_1_2_rate,
    round(avg(processing_days), 2) AS avg_processing_days
FROM bucketed
GROUP BY processing_bucket
ORDER BY multiIf(
    processing_bucket = '<1d', 1,
    processing_bucket = '1-2d', 2,
    processing_bucket = '2-3d', 3,
    processing_bucket = '3-7d', 4,
    processing_bucket = '7d+', 5,
    6
);
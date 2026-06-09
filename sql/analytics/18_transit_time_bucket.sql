-- 18_transit_time_bucket.sql
USE fp_mci_customer_experience;
SET join_use_nulls = 1;

WITH base AS (
    SELECT
        m.order_id,
        m.review_score,
        dateDiff('day', o.order_delivered_carrier_date, o.order_delivered_customer_date) AS transit_days
    FROM mart_customer_experience_orders m
    INNER JOIN stg_orders o ON m.order_id = o.order_id
    WHERE m.review_score IS NOT NULL
      AND o.order_delivered_carrier_date IS NOT NULL
      AND o.order_delivered_customer_date IS NOT NULL
),
bucketed AS (
    SELECT
        order_id,
        review_score,
        transit_days,
        multiIf(
            transit_days < 3, '<3d',
            transit_days < 5, '3-5d',
            transit_days < 7, '5-7d',
            transit_days < 10, '7-10d',
            '>10d'
        ) AS transit_bucket
    FROM base
)
SELECT
    transit_bucket,
    count() AS reviewed_orders,
    round(avg(review_score), 2) AS avg_review_score,
    countIf(review_score <= 2) AS low_rating_1_2_count,
    round(countIf(review_score <= 2) * 100.0 / nullIf(count(), 0), 2) AS low_rating_1_2_rate,
    round(avg(transit_days), 2) AS avg_transit_days
FROM bucketed
GROUP BY transit_bucket
ORDER BY multiIf(
    transit_bucket = '<3d', 1,
    transit_bucket = '3-5d', 2,
    transit_bucket = '5-7d', 3,
    transit_bucket = '7-10d', 4,
    transit_bucket = '>10d', 5,
    6
);
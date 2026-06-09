-- 23_multi_seller_order_effect.sql
USE fp_mci_customer_experience;
SET join_use_nulls = 1;

WITH order_seller_counts AS (
    SELECT
        order_id,
        uniqExact(seller_id) AS seller_count
    FROM stg_order_items
    GROUP BY order_id
),
base AS (
    SELECT
        m.order_id,
        m.review_score,
        m.delivery_days,
        s.seller_count
    FROM mart_customer_experience_orders m
    INNER JOIN order_seller_counts s ON m.order_id = s.order_id
    WHERE m.review_score IS NOT NULL
),
bucketed AS (
    SELECT
        order_id,
        review_score,
        delivery_days,
        seller_count,
        multiIf(
            seller_count = 1, '1 seller',
            seller_count = 2, '2 sellers',
            seller_count = 3, '3 sellers',
            '4+ sellers'
        ) AS seller_count_bucket
    FROM base
)
SELECT
    seller_count_bucket,
    count() AS reviewed_orders,
    round(avg(review_score), 2) AS avg_review_score,
    round(countIf(review_score <= 2) * 100.0 / nullIf(count(), 0), 2) AS low_rating_1_2_rate,
    round(avg(delivery_days), 2) AS avg_delivery_days
FROM bucketed
GROUP BY seller_count_bucket
ORDER BY multiIf(
    seller_count_bucket = '1 seller', 1,
    seller_count_bucket = '2 sellers', 2,
    seller_count_bucket = '3 sellers', 3,
    seller_count_bucket = '4+ sellers', 4,
    5
);
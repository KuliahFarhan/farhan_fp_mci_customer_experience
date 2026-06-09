-- 22_item_count_effect.sql
USE fp_mci_customer_experience;
SET join_use_nulls = 1;

WITH order_item_counts AS (
    SELECT
        order_id,
        count() AS item_count
    FROM stg_order_items
    GROUP BY order_id
),
base AS (
    SELECT
        m.order_id,
        m.review_score,
        i.item_count
    FROM mart_customer_experience_orders m
    INNER JOIN order_item_counts i ON m.order_id = i.order_id
    WHERE m.review_score IS NOT NULL
),
bucketed AS (
    SELECT
        order_id,
        review_score,
        item_count,
        multiIf(
            item_count = 1, '1 item',
            item_count = 2, '2 items',
            item_count = 3, '3 items',
            '4+ items'
        ) AS item_count_bucket
    FROM base
)
SELECT
    item_count_bucket,
    count() AS reviewed_orders,
    round(avg(review_score), 2) AS avg_review_score,
    round(countIf(review_score <= 2) * 100.0 / nullIf(count(), 0), 2) AS low_rating_1_2_rate
FROM bucketed
GROUP BY item_count_bucket
ORDER BY multiIf(
    item_count_bucket = '1 item', 1,
    item_count_bucket = '2 items', 2,
    item_count_bucket = '3 items', 3,
    item_count_bucket = '4+ items', 4,
    5
);
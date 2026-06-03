USE fp_mci_customer_experience;

SET join_use_nulls = 1;

TRUNCATE TABLE mart_customer_experience_orders;

INSERT INTO mart_customer_experience_orders
WITH latest_reviews AS (
    SELECT 
        *
    FROM (
        SELECT 
            *,
            row_number() OVER (
                PARTITION BY order_id 
                ORDER BY review_answer_timestamp DESC, review_creation_date DESC
            ) as rn
        FROM stg_order_reviews
    )
    WHERE rn = 1
)
SELECT
    o.order_id,
    o.customer_id,
    o.order_status,
    r.review_id,
    r.review_score as review_score,
    r.review_creation_date as review_creation_date,
    if(r.review_creation_date IS NULL, NULL, toStartOfMonth(r.review_creation_date)) as review_month,
    c.customer_city,
    c.customer_state,
    o.order_purchase_timestamp,
    o.order_delivered_customer_date,
    o.order_estimated_delivery_date,
    -- Delivery and Delay Calculations
    CASE 
        WHEN o.order_purchase_timestamp IS NOT NULL AND o.order_delivered_customer_date IS NOT NULL 
        THEN dateDiff('day', o.order_purchase_timestamp, o.order_delivered_customer_date)
        ELSE NULL 
    END AS delivery_days,
    CASE 
        WHEN o.order_estimated_delivery_date IS NOT NULL AND o.order_delivered_customer_date IS NOT NULL 
        THEN dateDiff('day', o.order_estimated_delivery_date, o.order_delivered_customer_date)
        ELSE NULL 
    END AS delay_days,
    -- Status and Buckets
    CASE 
        WHEN o.order_delivered_customer_date IS NULL OR o.order_estimated_delivery_date IS NULL THEN 'unknown'
        WHEN dateDiff('day', o.order_estimated_delivery_date, o.order_delivered_customer_date) > 0 THEN 'late'
        ELSE 'on_time_or_early'
    END AS delivery_status,
    CASE 
        WHEN o.order_delivered_customer_date IS NULL OR o.order_estimated_delivery_date IS NULL THEN 'unknown'
        WHEN dateDiff('day', o.order_estimated_delivery_date, o.order_delivered_customer_date) <= 0 THEN 'early_or_on_time'
        WHEN dateDiff('day', o.order_estimated_delivery_date, o.order_delivered_customer_date) BETWEEN 1 AND 3 THEN 'late_1_3_days'
        WHEN dateDiff('day', o.order_estimated_delivery_date, o.order_delivered_customer_date) BETWEEN 4 AND 7 THEN 'late_4_7_days'
        WHEN dateDiff('day', o.order_estimated_delivery_date, o.order_delivered_customer_date) BETWEEN 8 AND 14 THEN 'late_8_14_days'
        ELSE 'late_15plus_days'
    END AS delay_bucket,
    -- Low Rating Flags
    if(r.review_score IS NOT NULL AND r.review_score <= 2, 1, 0) as is_low_rating_2,
    if(r.review_score IS NOT NULL AND r.review_score <= 3, 1, 0) as is_low_rating_3
FROM stg_orders o
LEFT JOIN latest_reviews r ON o.order_id = r.order_id
LEFT JOIN stg_customers c ON o.customer_id = c.customer_id;

USE fp_mci_customer_experience;

SET join_use_nulls = 1;

TRUNCATE TABLE mart_delivery_performance;

INSERT INTO mart_delivery_performance
SELECT
    delivery_status,
    delay_bucket,
    count() as order_count,
    avg(review_score) as avg_review_score,
    sum(is_low_rating_2) as low_rating_2_orders,
    sum(is_low_rating_3) as low_rating_3_orders,
    sum(is_low_rating_2) / count() as low_rating_2_rate,
    sum(is_low_rating_3) / count() as low_rating_3_rate,
    avg(delivery_days) as avg_delivery_days,
    avg(delay_days) as avg_delay_days
FROM mart_customer_experience_orders
GROUP BY delivery_status, delay_bucket;

-- 15_non_delivered_orders_by_status.sql
USE fp_mci_customer_experience;
SET join_use_nulls = 1;

SELECT
    order_status,
    count() AS order_count,
    round(avgIf(review_score, review_score IS NOT NULL), 2) AS avg_review_score,
    countIf(review_score = 1) AS score_1_count,
    round(countIf(review_score = 1) * 100.0 / nullIf(countIf(review_score IS NOT NULL), 0), 2) AS score_1_rate,
    countIf(review_score <= 2 AND review_score IS NOT NULL) AS low_rating_1_2_count,
    round(countIf(review_score <= 2 AND review_score IS NOT NULL) * 100.0 / nullIf(countIf(review_score IS NOT NULL), 0), 2) AS low_rating_1_2_rate
FROM mart_customer_experience_orders
WHERE order_status != 'delivered'
GROUP BY order_status
ORDER BY order_count DESC;
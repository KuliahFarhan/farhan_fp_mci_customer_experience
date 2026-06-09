-- 19_late_rate_by_customer_state.sql
USE fp_mci_customer_experience;
SET join_use_nulls = 1;

SELECT
    customer_state,
    count() AS order_count,
    countIf(delivery_status = 'late') AS late_orders,
    round(countIf(delivery_status = 'late') * 100.0 / nullIf(count(), 0), 2) AS late_rate,
    round(avg(delivery_days), 2) AS avg_delivery_days,
    round(avg(review_score), 2) AS avg_review_score
FROM mart_customer_experience_orders
WHERE customer_state IS NOT NULL
GROUP BY customer_state
HAVING order_count >= 100
ORDER BY late_rate DESC, order_count DESC;
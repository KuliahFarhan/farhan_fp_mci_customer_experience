-- 20_problem_routes.sql
USE fp_mci_customer_experience;
SET join_use_nulls = 1;

SELECT
    concat(seller_state, ' -> ', customer_state) AS route,
    seller_state,
    customer_state,
    uniqExact(order_id) AS order_count,
    round(uniqExactIf(order_id, delivery_status = 'late') * 100.0 / nullIf(uniqExact(order_id), 0), 2) AS late_rate,
    round(avg(review_score), 2) AS avg_review_score,
    round(avg(delivery_days), 2) AS avg_delivery_days
FROM mart_customer_experience_items
WHERE review_score IS NOT NULL
  AND seller_state IS NOT NULL
  AND customer_state IS NOT NULL
GROUP BY seller_state, customer_state
HAVING order_count >= 100
ORDER BY late_rate DESC, order_count DESC
LIMIT 20;
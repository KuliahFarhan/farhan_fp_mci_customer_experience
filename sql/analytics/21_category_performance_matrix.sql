-- 21_category_performance_matrix.sql
USE fp_mci_customer_experience;
SET join_use_nulls = 1;

SELECT
    coalesce(product_category_name_english, product_category_name, 'unknown') AS product_category,
    uniqExact(order_id) AS order_count,
    round(avg(review_score), 2) AS avg_review_score,
    round(uniqExactIf(order_id, review_score <= 2) * 100.0 / nullIf(uniqExact(order_id), 0), 2) AS low_rating_1_2_rate,
    round(uniqExactIf(order_id, review_score <= 3) * 100.0 / nullIf(uniqExact(order_id), 0), 2) AS low_rating_1_3_rate
FROM mart_customer_experience_items
WHERE review_score IS NOT NULL
GROUP BY product_category
HAVING order_count >= 50
ORDER BY order_count DESC;
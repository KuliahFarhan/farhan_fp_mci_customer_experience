USE fp_mci_customer_experience;

WITH category_review_scores AS (
    SELECT
        coalesce(product_category_name_english, product_category_name, 'unknown') AS product_category,
        order_id,
        any(review_score) AS review_score
    FROM mart_customer_experience_items
    WHERE review_score IS NOT NULL
    GROUP BY
        product_category,
        order_id
)
SELECT
    product_category,
    uniqExact(order_id) AS order_count,
    count() AS item_count,
    avg_review_score,
    uniqExactIf(order_id, review_score <= 2) AS low_rating_2_count,
    round(uniqExactIf(order_id, review_score <= 2) * 100.0 / nullIf(uniqExact(order_id), 0), 2) AS low_rating_2_rate,
    uniqExactIf(order_id, review_score <= 3) AS low_rating_3_count,
    round(uniqExactIf(order_id, review_score <= 3) * 100.0 / nullIf(uniqExact(order_id), 0), 2) AS low_rating_3_rate,
    uniqExactIf(order_id, delivery_status = 'late') AS late_order_count,
    round(uniqExactIf(order_id, delivery_status = 'late') * 100.0 / nullIf(uniqExact(order_id), 0), 2) AS late_rate,
    round(avg(delay_days), 2) AS avg_delay_days
FROM (
    SELECT
        *,
        coalesce(product_category_name_english, product_category_name, 'unknown') AS product_category
    FROM mart_customer_experience_items
    WHERE review_score IS NOT NULL
) AS category_items
INNER JOIN (
    SELECT
        product_category,
        round(avg(review_score), 2) AS avg_review_score
    FROM category_review_scores
    GROUP BY product_category
) AS category_review_score_summary USING (product_category)
GROUP BY product_category, avg_review_score
HAVING order_count >= 50
ORDER BY
    low_rating_2_count DESC,
    low_rating_2_rate DESC
LIMIT 50;

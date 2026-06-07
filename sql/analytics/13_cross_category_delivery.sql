USE fp_mci_customer_experience;

WITH category_summary AS (
    SELECT
        coalesce(product_category_name_english, product_category_name, 'unknown') AS product_category,
        uniqExact(order_id) AS order_count,
        round(avg(review_score), 2) AS avg_review_score,
        round(uniqExactIf(order_id, review_score <= 2) * 100.0 / nullIf(uniqExact(order_id), 0), 2) AS low_rating_2_rate,
        round(uniqExactIf(order_id, delivery_status = 'late') * 100.0 / nullIf(uniqExact(order_id), 0), 2) AS late_rate,
        round(avg(delay_days), 2) AS avg_delay_days
    FROM mart_customer_experience_items
    WHERE review_score IS NOT NULL
    GROUP BY product_category
    HAVING order_count >= 50
)
SELECT
    product_category,
    order_count,
    avg_review_score,
    low_rating_2_rate,
    late_rate,
    avg_delay_days,
    multiIf(
        low_rating_2_rate >= 25 AND late_rate >= 15, 'High risk category',
        late_rate >= 15, 'Delivery issue category',
        low_rating_2_rate >= 25, 'Review issue category',
        'Monitor'
    ) AS risk_label
FROM category_summary
ORDER BY
    low_rating_2_rate DESC,
    late_rate DESC
LIMIT 50;

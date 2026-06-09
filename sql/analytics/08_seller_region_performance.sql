USE fp_mci_customer_experience;

WITH seller_state_review_scores AS (
    SELECT
        seller_state,
        order_id,
        any(review_score) AS review_score
    FROM mart_customer_experience_items
    WHERE review_score IS NOT NULL
    GROUP BY
        seller_state,
        order_id
)
SELECT
    seller_state,
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
FROM mart_customer_experience_items
INNER JOIN (
    SELECT
        seller_state,
        round(avg(review_score), 2) AS avg_review_score
    FROM seller_state_review_scores
    GROUP BY seller_state
) AS seller_state_review_score_summary USING (seller_state)
WHERE review_score IS NOT NULL
GROUP BY seller_state, avg_review_score
HAVING order_count >= 100
ORDER BY
    low_rating_2_rate DESC,
    order_count DESC;

USE fp_mci_customer_experience;

WITH seller_summary AS (
    SELECT
        seller_id,
        seller_city,
        seller_state,
        uniqExact(order_id) AS order_count,
        round(avg(review_score), 2) AS avg_review_score,
        round(uniqExactIf(order_id, review_score <= 2) * 100.0 / nullIf(uniqExact(order_id), 0), 2) AS low_rating_2_rate,
        round(uniqExactIf(order_id, delivery_status = 'late') * 100.0 / nullIf(uniqExact(order_id), 0), 2) AS late_rate,
        round(avg(delay_days), 2) AS avg_delay_days
    FROM mart_customer_experience_items
    WHERE review_score IS NOT NULL
    GROUP BY
        seller_id,
        seller_city,
        seller_state
    HAVING order_count >= 30
)
SELECT
    seller_id,
    seller_city,
    seller_state,
    order_count,
    avg_review_score,
    low_rating_2_rate,
    late_rate,
    avg_delay_days,
    -- Heuristic dashboard cutoffs: >=25% low-rating and >=15% late-rate mark review and delivery risk; review against observed distributions before operational use.
    multiIf(
        low_rating_2_rate >= 25 AND late_rate >= 15, 'High risk seller',
        late_rate >= 15, 'Delivery issue seller',
        low_rating_2_rate >= 25, 'Review issue seller',
        'Monitor'
    ) AS risk_label
FROM seller_summary
ORDER BY
    low_rating_2_rate DESC,
    late_rate DESC
LIMIT 50;

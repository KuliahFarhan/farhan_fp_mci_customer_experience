USE fp_mci_customer_experience;

WITH segment_summary AS (
    SELECT
        'seller' AS segment_type,
        seller_id AS segment_name,
        uniqExact(order_id) AS order_count,
        round(avg(review_score), 2) AS avg_review_score,
        uniqExactIf(order_id, review_score <= 2) AS low_rating_2_count,
        round(uniqExactIf(order_id, review_score <= 2) * 100.0 / nullIf(uniqExact(order_id), 0), 2) AS low_rating_2_rate,
        round(uniqExactIf(order_id, delivery_status = 'late') * 100.0 / nullIf(uniqExact(order_id), 0), 2) AS late_rate,
        round(avg(delay_days), 2) AS avg_delay_days
    FROM mart_customer_experience_items
    WHERE review_score IS NOT NULL
    GROUP BY seller_id
    HAVING order_count >= 30

    UNION ALL

    SELECT
        'product_category' AS segment_type,
        coalesce(product_category_name_english, product_category_name, 'unknown') AS segment_name,
        uniqExact(order_id) AS order_count,
        round(avg(review_score), 2) AS avg_review_score,
        uniqExactIf(order_id, review_score <= 2) AS low_rating_2_count,
        round(uniqExactIf(order_id, review_score <= 2) * 100.0 / nullIf(uniqExact(order_id), 0), 2) AS low_rating_2_rate,
        round(uniqExactIf(order_id, delivery_status = 'late') * 100.0 / nullIf(uniqExact(order_id), 0), 2) AS late_rate,
        round(avg(delay_days), 2) AS avg_delay_days
    FROM mart_customer_experience_items
    WHERE review_score IS NOT NULL
    GROUP BY segment_name
    HAVING order_count >= 50

    UNION ALL

    SELECT
        'customer_state' AS segment_type,
        customer_state AS segment_name,
        count() AS order_count,
        round(avg(review_score), 2) AS avg_review_score,
        sum(is_low_rating_2) AS low_rating_2_count,
        round(sum(is_low_rating_2) * 100.0 / nullIf(count(), 0), 2) AS low_rating_2_rate,
        round(countIf(delivery_status = 'late') * 100.0 / nullIf(count(), 0), 2) AS late_rate,
        round(avg(delay_days), 2) AS avg_delay_days
    FROM mart_customer_experience_orders
    WHERE review_score IS NOT NULL
    GROUP BY customer_state
    HAVING order_count >= 100
)
SELECT
    segment_type,
    segment_name,
    order_count,
    avg_review_score,
    low_rating_2_count,
    low_rating_2_rate,
    late_rate,
    avg_delay_days,
    -- Impact-aware prioritization: sqrt volume keeps large segments important without letting raw count dominate rates.
    round(sqrt(low_rating_2_count) * 5 + low_rating_2_rate * 10 + late_rate * 5, 2) AS priority_score,
    multiIf(
        late_rate >= 15, 'Delivery SLA / logistics review',
        segment_type = 'seller', 'Seller monitoring and coaching',
        segment_type = 'product_category', 'Product category quality audit',
        segment_type = 'customer_state', 'Regional delivery experience review',
        'Customer experience monitoring'
    ) AS action_focus
FROM segment_summary
ORDER BY priority_score DESC
LIMIT 50;

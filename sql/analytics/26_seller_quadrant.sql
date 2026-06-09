-- 26_seller_quadrant.sql
USE fp_mci_customer_experience;
SET join_use_nulls = 1;

WITH seller_summary AS (
    SELECT
        seller_id,
        seller_state,
        uniqExact(order_id) AS order_count,
        round(avg(review_score), 2) AS avg_review_score,
        round(uniqExactIf(order_id, review_score <= 2) * 100.0 / nullIf(uniqExact(order_id), 0), 2) AS low_rating_1_2_rate
    FROM mart_customer_experience_items
    WHERE review_score IS NOT NULL
    GROUP BY seller_id, seller_state
    HAVING order_count >= 50
),
thresholds AS (
    SELECT
        quantileExact(0.5)(order_count) AS median_order_count,
        quantileExact(0.5)(avg_review_score) AS median_review_score
    FROM seller_summary
)
SELECT
    s.seller_id,
    s.seller_state,
    s.order_count,
    s.avg_review_score,
    s.low_rating_1_2_rate,
    multiIf(
        s.order_count >= t.median_order_count AND s.avg_review_score >= t.median_review_score, 'Stars',
        s.order_count >= t.median_order_count AND s.avg_review_score < t.median_review_score, 'Risk zone',
        s.order_count < t.median_order_count AND s.avg_review_score >= t.median_review_score, 'Sleepers',
        'Problematic'
    ) AS seller_quadrant
FROM seller_summary s
CROSS JOIN thresholds t
ORDER BY order_count DESC, avg_review_score ASC;
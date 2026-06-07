USE fp_mci_customer_experience;

SELECT
    count() AS total_orders,
    countIf(review_score IS NOT NULL) AS reviewed_orders,
    round(avgIf(review_score, review_score IS NOT NULL), 2) AS avg_review_score,
    countIf(review_score IS NOT NULL AND review_score <= 2) AS low_rating_2_orders,
    round(countIf(review_score IS NOT NULL AND review_score <= 2) * 100.0 / nullIf(countIf(review_score IS NOT NULL), 0), 2) AS low_rating_2_rate,
    countIf(review_score IS NOT NULL AND review_score <= 3) AS low_rating_3_orders,
    round(countIf(review_score IS NOT NULL AND review_score <= 3) * 100.0 / nullIf(countIf(review_score IS NOT NULL), 0), 2) AS low_rating_3_rate,
    countIf(delivery_status = 'late') AS late_orders,
    round(countIf(delivery_status = 'late') * 100.0 / nullIf(count(), 0), 2) AS late_order_rate,
    round(avg(delivery_days), 2) AS avg_delivery_days,
    round(avg(delay_days), 2) AS avg_delay_days
FROM mart_customer_experience_orders;

USE fp_mci_customer_experience;

SELECT
    review_month,
    count() AS reviewed_orders,
    countIf(delivery_status = 'late') AS late_orders,
    round(countIf(delivery_status = 'late') * 100.0 / nullIf(count(), 0), 2) AS late_rate,
    round(avg(review_score), 2) AS avg_review_score,
    round(sum(is_low_rating_2) * 100.0 / nullIf(count(), 0), 2) AS low_rating_2_rate,
    round(avg(delay_days), 2) AS avg_delay_days
FROM mart_customer_experience_orders
WHERE review_score IS NOT NULL
  AND review_month IS NOT NULL
GROUP BY review_month
ORDER BY review_month;

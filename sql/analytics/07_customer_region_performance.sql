USE fp_mci_customer_experience;

SELECT
    customer_state,
    count() AS order_count,
    round(avg(review_score), 2) AS avg_review_score,
    sum(is_low_rating_2) AS low_rating_2_count,
    round(sum(is_low_rating_2) * 100.0 / nullIf(count(), 0), 2) AS low_rating_2_rate,
    sum(is_low_rating_3) AS low_rating_3_count,
    round(sum(is_low_rating_3) * 100.0 / nullIf(count(), 0), 2) AS low_rating_3_rate,
    countIf(delivery_status = 'late') AS late_order_count,
    round(countIf(delivery_status = 'late') * 100.0 / nullIf(count(), 0), 2) AS late_rate,
    round(avg(delivery_days), 2) AS avg_delivery_days,
    round(avg(delay_days), 2) AS avg_delay_days
FROM mart_customer_experience_orders
WHERE review_score IS NOT NULL
GROUP BY customer_state
HAVING order_count >= 100
ORDER BY
    low_rating_2_rate DESC,
    order_count DESC;

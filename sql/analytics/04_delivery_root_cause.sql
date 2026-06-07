USE fp_mci_customer_experience;

-- A. Summary by delivery_status
SELECT
    delivery_status,
    count() AS order_count,
    round(avg(review_score), 2) AS avg_review_score,
    sum(is_low_rating_2) AS low_rating_2_count,
    round(sum(is_low_rating_2) * 100.0 / nullIf(count(), 0), 2) AS low_rating_2_rate,
    sum(is_low_rating_3) AS low_rating_3_count,
    round(sum(is_low_rating_3) * 100.0 / nullIf(count(), 0), 2) AS low_rating_3_rate,
    round(avg(delivery_days), 2) AS avg_delivery_days,
    round(avg(delay_days), 2) AS avg_delay_days
FROM mart_customer_experience_orders
WHERE review_score IS NOT NULL
GROUP BY delivery_status
ORDER BY multiIf(
    delivery_status = 'on_time_or_early', 1,
    delivery_status = 'late', 2,
    delivery_status = 'unknown', 3,
    4
);

-- B. Summary by delay_bucket
SELECT
    delay_bucket,
    count() AS order_count,
    round(avg(review_score), 2) AS avg_review_score,
    sum(is_low_rating_2) AS low_rating_2_count,
    round(sum(is_low_rating_2) * 100.0 / nullIf(count(), 0), 2) AS low_rating_2_rate,
    sum(is_low_rating_3) AS low_rating_3_count,
    round(sum(is_low_rating_3) * 100.0 / nullIf(count(), 0), 2) AS low_rating_3_rate,
    round(avg(delivery_days), 2) AS avg_delivery_days,
    round(avg(delay_days), 2) AS avg_delay_days
FROM mart_customer_experience_orders
WHERE review_score IS NOT NULL
GROUP BY delay_bucket
ORDER BY multiIf(
    delay_bucket = 'early_or_on_time', 1,
    delay_bucket = 'late_1_3_days', 2,
    delay_bucket = 'late_4_7_days', 3,
    delay_bucket = 'late_8_14_days', 4,
    delay_bucket = 'late_15plus_days', 5,
    delay_bucket = 'unknown', 6,
    7
);

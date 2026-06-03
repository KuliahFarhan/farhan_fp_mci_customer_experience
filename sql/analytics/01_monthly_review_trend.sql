USE fp_mci_customer_experience;

TRUNCATE TABLE mart_monthly_review;

INSERT INTO mart_monthly_review
SELECT
    assumeNotNull(review_month) as review_month,
    count() as reviewed_orders,
    avg(review_score) as avg_review_score,
    sum(is_low_rating_2) as low_rating_2_orders,
    sum(is_low_rating_3) as low_rating_3_orders,
    sum(is_low_rating_2) / count() as low_rating_2_rate,
    sum(is_low_rating_3) / count() as low_rating_3_rate
FROM mart_customer_experience_orders
WHERE review_score IS NOT NULL 
  AND review_month IS NOT NULL
GROUP BY review_month;

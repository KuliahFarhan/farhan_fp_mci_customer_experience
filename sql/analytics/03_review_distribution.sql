USE fp_mci_customer_experience;

SELECT
    review_score,
    count() AS review_count,
    round(count() * 100.0 / nullIf(sum(count()) OVER (), 0), 2) AS percentage
FROM mart_customer_experience_orders
WHERE review_score IS NOT NULL
GROUP BY review_score
ORDER BY review_score;

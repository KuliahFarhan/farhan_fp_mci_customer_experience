-- 24_installment_vs_review.sql
USE fp_mci_customer_experience;
SET join_use_nulls = 1;

WITH payment_base AS (
    SELECT
        order_id,
        maxIf(payment_installments, payment_type = 'credit_card') AS cc_installments,
        sumIf(payment_value, payment_type = 'credit_card') AS cc_payment_value
    FROM stg_order_payments
    GROUP BY order_id
),
base AS (
    SELECT
        m.order_id,
        m.review_score,
        p.cc_installments,
        p.cc_payment_value
    FROM mart_customer_experience_orders m
    INNER JOIN payment_base p ON m.order_id = p.order_id
    WHERE m.review_score IS NOT NULL
      AND p.cc_installments > 0
),
bucketed AS (
    SELECT
        order_id,
        review_score,
        cc_payment_value,
        multiIf(
            cc_installments = 1, '1x',
            cc_installments BETWEEN 2 AND 3, '2-3x',
            cc_installments BETWEEN 4 AND 6, '4-6x',
            cc_installments BETWEEN 7 AND 12, '7-12x',
            '13-24x'
        ) AS installment_bucket
    FROM base
)
SELECT
    installment_bucket,
    count() AS reviewed_orders,
    round(avg(review_score), 2) AS avg_review_score,
    round(avg(cc_payment_value), 2) AS avg_order_value
FROM bucketed
GROUP BY installment_bucket
ORDER BY multiIf(
    installment_bucket = '1x', 1,
    installment_bucket = '2-3x', 2,
    installment_bucket = '4-6x', 3,
    installment_bucket = '7-12x', 4,
    installment_bucket = '13-24x', 5,
    6
);
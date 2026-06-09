-- 16_delivery_phase_breakdown.sql
USE fp_mci_customer_experience;
SET join_use_nulls = 1;

SELECT
    phase,
    median_days,
    avg_days
FROM
(
    SELECT
        'approval' AS phase,
        round(medianOrNull(dateDiff('hour', order_purchase_timestamp, order_approved_at)) / 24.0, 2) AS median_days,
        round(avgOrNull(dateDiff('hour', order_purchase_timestamp, order_approved_at)) / 24.0, 2) AS avg_days
    FROM stg_orders
    WHERE order_purchase_timestamp IS NOT NULL
      AND order_approved_at IS NOT NULL

    UNION ALL

    SELECT
        'seller_processing' AS phase,
        round(medianOrNull(dateDiff('hour', order_approved_at, order_delivered_carrier_date)) / 24.0, 2) AS median_days,
        round(avgOrNull(dateDiff('hour', order_approved_at, order_delivered_carrier_date)) / 24.0, 2) AS avg_days
    FROM stg_orders
    WHERE order_approved_at IS NOT NULL
      AND order_delivered_carrier_date IS NOT NULL

    UNION ALL

    SELECT
        'transit' AS phase,
        round(medianOrNull(dateDiff('hour', order_delivered_carrier_date, order_delivered_customer_date)) / 24.0, 2) AS median_days,
        round(avgOrNull(dateDiff('hour', order_delivered_carrier_date, order_delivered_customer_date)) / 24.0, 2) AS avg_days
    FROM stg_orders
    WHERE order_delivered_carrier_date IS NOT NULL
      AND order_delivered_customer_date IS NOT NULL
)
ORDER BY multiIf(
    phase = 'approval', 1,
    phase = 'seller_processing', 2,
    phase = 'transit', 3,
    4
);
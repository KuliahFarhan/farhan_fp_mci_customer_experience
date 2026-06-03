USE fp_mci_customer_experience;

TRUNCATE TABLE mart_customer_experience_items;

INSERT INTO mart_customer_experience_items
SELECT
    m.order_id,
    CAST(i.order_item_id, 'Int32') as order_item_id,
    m.customer_id,
    i.seller_id,
    i.product_id,
    m.review_score,
    m.review_creation_date,
    m.review_month,
    m.customer_city,
    m.customer_state,
    s.seller_city,
    s.seller_state,
    p.product_category_name,
    coalesce(t.product_category_name_english, p.product_category_name, 'unknown') as product_category_name_english,
    i.price,
    i.freight_value,
    m.delivery_days,
    m.delay_days,
    m.delivery_status,
    m.delay_bucket,
    m.is_low_rating_2,
    m.is_low_rating_3
FROM mart_customer_experience_orders m
INNER JOIN stg_order_items i ON m.order_id = i.order_id
LEFT JOIN stg_sellers s ON i.seller_id = s.seller_id
LEFT JOIN stg_products p ON i.product_id = p.product_id
LEFT JOIN stg_category_translation t ON p.product_category_name = t.product_category_name;

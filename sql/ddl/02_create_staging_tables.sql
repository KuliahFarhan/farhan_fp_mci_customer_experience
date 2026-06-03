USE fp_mci_customer_experience;

-- 1. Orders Staging Table
DROP TABLE IF EXISTS stg_orders;
CREATE TABLE stg_orders (
    order_id String,
    customer_id String,
    order_status String,
    order_purchase_timestamp Nullable(DateTime),
    order_approved_at Nullable(DateTime),
    order_delivered_carrier_date Nullable(DateTime),
    order_delivered_customer_date Nullable(DateTime),
    order_estimated_delivery_date Nullable(DateTime)
) ENGINE = MergeTree()
ORDER BY order_id;

-- 2. Order Reviews Staging Table
DROP TABLE IF EXISTS stg_order_reviews;
CREATE TABLE stg_order_reviews (
    review_id String,
    order_id String,
    review_score Float64,
    review_comment_title Nullable(String),
    review_comment_message Nullable(String),
    review_creation_date Nullable(DateTime),
    review_answer_timestamp Nullable(DateTime)
) ENGINE = MergeTree()
ORDER BY review_id;

-- 3. Order Items Staging Table
DROP TABLE IF EXISTS stg_order_items;
CREATE TABLE stg_order_items (
    order_id String,
    order_item_id String,
    product_id String,
    seller_id String,
    shipping_limit_date Nullable(DateTime),
    price Float64,
    freight_value Float64
) ENGINE = MergeTree()
ORDER BY (order_id, order_item_id);

-- 4. Customers Staging Table
DROP TABLE IF EXISTS stg_customers;
CREATE TABLE stg_customers (
    customer_id String,
    customer_unique_id String,
    customer_zip_code_prefix String,
    customer_city String,
    customer_state String
) ENGINE = MergeTree()
ORDER BY customer_id;

-- 5. Sellers Staging Table
DROP TABLE IF EXISTS stg_sellers;
CREATE TABLE stg_sellers (
    seller_id String,
    seller_zip_code_prefix String,
    seller_city String,
    seller_state String
) ENGINE = MergeTree()
ORDER BY seller_id;

-- 6. Products Staging Table
DROP TABLE IF EXISTS stg_products;
CREATE TABLE stg_products (
    product_id String,
    product_category_name Nullable(String),
    product_name_lenght Nullable(Float64),
    product_description_lenght Nullable(Float64),
    product_photos_qty Nullable(Float64),
    product_weight_g Nullable(Float64),
    product_length_cm Nullable(Float64),
    product_height_cm Nullable(Float64),
    product_width_cm Nullable(Float64)
) ENGINE = MergeTree()
ORDER BY product_id;

-- 7. Category Translation Staging Table
DROP TABLE IF EXISTS stg_category_translation;
CREATE TABLE stg_category_translation (
    product_category_name String,
    product_category_name_english String
) ENGINE = MergeTree()
ORDER BY product_category_name;

-- 8. Order Payments Staging Table
DROP TABLE IF EXISTS stg_order_payments;
CREATE TABLE stg_order_payments (
    order_id String,
    payment_sequential Float64,
    payment_type String,
    payment_installments Float64,
    payment_value Float64
) ENGINE = MergeTree()
ORDER BY order_id;

USE fp_mci_customer_experience;

-- A. Mart Customer Experience Orders (Order Level)
DROP TABLE IF EXISTS mart_customer_experience_orders;
CREATE TABLE mart_customer_experience_orders (
    order_id String,
    customer_id String,
    order_status String,
    review_id Nullable(String),
    review_score Nullable(Int32),
    review_creation_date Nullable(DateTime),
    review_month Nullable(Date),
    customer_city String,
    customer_state String,
    order_purchase_timestamp Nullable(DateTime),
    order_delivered_customer_date Nullable(DateTime),
    order_estimated_delivery_date Nullable(DateTime),
    delivery_days Nullable(Int32),
    delay_days Nullable(Int32),
    delivery_status String,
    delay_bucket String,
    is_low_rating_2 UInt8,
    is_low_rating_3 UInt8
) ENGINE = MergeTree()
ORDER BY (review_month, order_id)
SETTINGS allow_nullable_key = 1;

-- B. Mart Customer Experience Items (Item Level)
DROP TABLE IF EXISTS mart_customer_experience_items;
CREATE TABLE mart_customer_experience_items (
    order_id String,
    order_item_id Int32,
    customer_id String,
    seller_id String,
    product_id String,
    review_score Nullable(Int32),
    review_creation_date Nullable(DateTime),
    review_month Nullable(Date),
    customer_city String,
    customer_state String,
    seller_city String,
    seller_state String,
    product_category_name Nullable(String),
    product_category_name_english Nullable(String),
    price Float64,
    freight_value Float64,
    delivery_days Nullable(Int32),
    delay_days Nullable(Int32),
    delivery_status String,
    delay_bucket String,
    is_low_rating_2 UInt8,
    is_low_rating_3 UInt8
) ENGINE = MergeTree()
ORDER BY (review_month, seller_id, product_category_name_english, order_id)
SETTINGS allow_nullable_key = 1;

-- C. Mart Monthly Review Trend
DROP TABLE IF EXISTS mart_monthly_review;
CREATE TABLE mart_monthly_review (
    review_month Date,
    reviewed_orders UInt64,
    avg_review_score Float64,
    low_rating_2_orders UInt64,
    low_rating_3_orders UInt64,
    low_rating_2_rate Float64,
    low_rating_3_rate Float64
) ENGINE = MergeTree()
ORDER BY review_month;

-- D. Mart Delivery Performance
DROP TABLE IF EXISTS mart_delivery_performance;
CREATE TABLE mart_delivery_performance (
    delivery_status String,
    delay_bucket String,
    order_count UInt64,
    avg_review_score Float64,
    low_rating_2_orders UInt64,
    low_rating_3_orders UInt64,
    low_rating_2_rate Float64,
    low_rating_3_rate Float64,
    avg_delivery_days Float64,
    avg_delay_days Float64
) ENGINE = MergeTree()
ORDER BY (delivery_status, delay_bucket);

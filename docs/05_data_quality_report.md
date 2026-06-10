# 05 Data Quality Report

## 1. Tujuan Data Quality Check

Tahap ini dilakukan untuk memastikan dataset layak digunakan sebelum masuk ke EDA, pemuatan ke ClickHouse, orkestrasi Airflow, dan pembuatan dashboard Metabase. Fokusnya adalah memastikan kelengkapan data kunci, konsistensi relasi antar tabel, serta kualitas kolom tanggal yang dibutuhkan untuk analisis customer experience.

Catatan status: dokumen ini adalah data quality report tahap awal. Pada repository final, `geolocation.csv` sudah masuk pipeline sebagai staging table dan helper view `geo_zip_prefix_reference`, tetapi tetap diperlakukan sebagai supporting layer untuk analisis spasial, bukan core mart utama.

## 2. Dataset Inventory

Angka di bawah dihitung ulang dari CSV pada data mentah untuk melengkapi output notebook.

| Tabel                    | Baris   | Kolom | Duplicate Rows | Total Missing Values | Catatan                            |
| ------------------------ | ------- | ----- | -------------- | -------------------- | ---------------------------------- |
| category_translation.csv | 71      | 2     | 0              | 0                    | Pendukung kategori produk          |
| closed_deals.csv         | 842     | 14    | 0              | 3300                 | Non-prioritas Day 1 (marketing)    |
| customers.csv            | 99441   | 5     | 0              | 0                    | Utama                              |
| geolocation.csv          | 1000163 | 5     | 261831         | 0                    | Non-prioritas Day 1 (sangat besar) |
| mql.csv                  | 8000    | 4     | 0              | 60                   | Non-prioritas Day 1 (marketing)    |
| order_items.csv          | 112650  | 7     | 0              | 0                    | Utama                              |
| order_payments.csv       | 103886  | 5     | 0              | 0                    | Tambahan                           |
| order_reviews.csv        | 99224   | 7     | 0              | 145903               | Utama                              |
| orders.csv               | 99441   | 8     | 0              | 4908                 | Utama                              |
| products.csv             | 32951   | 9     | 0              | 2448                 | Utama                              |
| sellers.csv              | 3095    | 4     | 0              | 0                    | Utama                              |

## 3. Missing Value Summary

- orders.csv: missing terbesar pada `order_delivered_customer_date` (2965), `order_delivered_carrier_date` (1783), `order_approved_at` (160).
- order_reviews.csv: missing dominan pada `review_comment_title` (87656) dan `review_comment_message` (58247).
- products.csv: missing pada `product_category_name` (610), `product_name_lenght` (610), `product_description_lenght` (610), `product_photos_qty` (610), serta ukuran fisik (masing-masing 2 pada `product_weight_g`, `product_length_cm`, `product_height_cm`, `product_width_cm`).
- customers.csv: tidak ada missing values.
- sellers.csv: tidak ada missing values.
- order_items.csv: tidak ada missing values.

## 4. Duplicate Check

- Duplicate full rows: seluruh tabel 0, kecuali geolocation.csv memiliki 261831 baris duplikat penuh.
- Duplicate key penting:
  - orders.csv: `order_id` unik (0 duplikat).
  - order_reviews.csv: `review_id` memiliki 789 nilai yang muncul lebih dari sekali (814 baris duplikat berdasarkan `review_id`). `order_id` memiliki 547 order yang muncul lebih dari sekali (551 baris duplikat berdasarkan `order_id`). Ini menunjukkan potensi lebih dari satu review per order.
  - customers.csv: `customer_id` unik (0 duplikat).
  - sellers.csv: `seller_id` unik (0 duplikat).
  - products.csv: `product_id` unik (0 duplikat).
  - order_items.csv: `order_id` dan `product_id` memiliki banyak duplikat karena satu order dapat berisi banyak item dan satu produk bisa muncul di banyak order; ini bukan duplicate row penuh.

## 5. Datetime Column Check

- orders.csv (missing setelah parsing tanggal):
  - `order_purchase_timestamp`: 0
  - `order_approved_at`: 160
  - `order_delivered_carrier_date`: 1783
  - `order_delivered_customer_date`: 2965
  - `order_estimated_delivery_date`: 0
- order_reviews.csv:
  - `review_creation_date`: 0
  - `review_answer_timestamp`: 0

Kolom tanggal yang dipakai:

- Delivery duration: `order_delivered_customer_date` - `order_purchase_timestamp`.
- Delivery delay: `order_delivered_customer_date` dibandingkan `order_estimated_delivery_date`.
- Tren review score: `review_creation_date` sebagai waktu pencatatan review.

## 6. Abnormal Order Check

Definisi tanggal penting: lima kolom tanggal pada orders.csv.

| Kondisi                                                                      | Jumlah Order | Implikasi                                                                     |
| ---------------------------------------------------------------------------- | ------------ | ----------------------------------------------------------------------------- |
| Status delivered tetapi `order_delivered_customer_date` kosong             | 8            | Perlu dikeluarkan dari analisis delivery karena tanggal terima tidak tersedia |
| Status bukan delivered tetapi `order_delivered_customer_date` terisi       | 6            | Perlu validasi status atau perlakuan khusus saat analisis delivery            |
| `order_delivered_customer_date` melewati `order_estimated_delivery_date` | 7827         | Indikasi keterlambatan pengiriman                                             |
| Ada tanggal penting yang kosong (setidaknya satu kolom tanggal kosong)       | 2980         | Perlu filter subset untuk analisis berbasis waktu                             |

## 7. Order-Review Join Check

| Kondisi                             | Jumlah | Implikasi                                                                          |
| ----------------------------------- | ------ | ---------------------------------------------------------------------------------- |
| Order tanpa review                  | 768    | Tidak dipakai untuk analisis review score, namun dapat dipakai untuk konteks order |
| Review tanpa order                  | 0      | Konsistensi relasi baik                                                            |
| Order dengan lebih dari satu review | 547    | Perlu strategi pemilihan review (terbaru) atau agregasi per `order_id`           |

# Dashboard Query Findings - Customer Experience Root Cause Analysis

Generated at: `2026-06-10T07:14:03`
ClickHouse database: `fp_mci_customer_experience`
Script: `scripts/export_dashboard_findings.py`

Note: hasil angka bergantung pada kondisi data mart saat script dijalankan.

## Query execution warnings

- Tidak ada query warning.

## 1. Executive Overview

### KPI Summary

**Query/source table:** `mart_customer_experience_orders`

**CSV output:** `docs/query_outputs/kpi_summary.csv`

**Key numbers and table:**

| avg_review_score | low_rating_2_rate | low_rating_3_rate | late_order_rate | average_late_days | reviewed_orders |
| ---------------- | ----------------- | ----------------- | --------------- | ----------------- | --------------- |
| 4.09             | 14.69             | 22.93             | 6.57            | 10.62             | 98673.00        |

**Interpretation:**

Rata-rata review score tercatat 4.09, dengan low rating <=2 sebesar 14.69% dan low rating <=3 sebesar 22.93%. Late order rate berada di 6.57% dari order, sementara jumlah order yang memiliki review valid adalah 98,673.

**Business implication:**

KPI ini memberi baseline kesehatan customer experience dan menjadi acuan untuk menilai segmen risiko.

### Monthly Review Trend

**Query/source table:** `mart_monthly_review`

**CSV output:** `docs/query_outputs/monthly_review_trend.csv`

**Key numbers and table:**

| review_month        | reviewed_orders | avg_review_score | low_rating_2_orders | low_rating_2_rate | low_rating_3_rate |
| ------------------- | --------------- | ---------------- | ------------------- | ----------------- | ----------------- |
| 2016-10-01 00:00:00 | 177             | 4.05             | 29                  | 16.38             | 23.73             |
| 2016-11-01 00:00:00 | 101             | 3.19             | 38                  | 37.62             | 45.54             |
| 2016-12-01 00:00:00 | 45              | 2.36             | 29                  | 64.44             | 66.67             |
| 2017-01-01 00:00:00 | 236             | 4.33             | 20                  | 8.47              | 18.22             |
| 2017-02-01 00:00:00 | 1403            | 4.28             | 134                 | 9.55              | 17.89             |
| 2017-03-01 00:00:00 | 2467            | 4.03             | 389                 | 15.77             | 24.56             |
| 2017-04-01 00:00:00 | 2049            | 4.04             | 313                 | 15.28             | 24.74             |
| 2017-05-01 00:00:00 | 3678            | 4.10             | 509                 | 13.84             | 22.73             |
| 2017-06-01 00:00:00 | 3402            | 4.13             | 447                 | 13.14             | 22.08             |
| 2017-07-01 00:00:00 | 3476            | 4.18             | 418                 | 12.03             | 20.66             |
| 2017-08-01 00:00:00 | 4459            | 4.23             | 511                 | 11.46             | 19.08             |
| 2017-09-01 00:00:00 | 4164            | 4.18             | 515                 | 12.37             | 19.72             |

**Interpretation:**

Hasil berisi 23 baris. Kolom `reviewed_orders` berada pada rentang 45.00 sampai 8983.00. Baris teratas adalah `2016-10-01 00:00:00` berdasarkan urutan query.

**Business implication:**

Trend bulanan membantu membedakan pola stabil dari lonjakan risiko pada periode tertentu.

### Review Score Distribution

**Query/source table:** `mart_customer_experience_orders`

**CSV output:** `docs/query_outputs/review_score_distribution.csv`

**Key numbers and table:**

| review_score | review_count | percentage |
| ------------ | ------------ | ---------- |
| 1            | 11363        | 11.52      |
| 2            | 3131         | 3.17       |
| 3            | 8133         | 8.24       |
| 4            | 19038        | 19.29      |
| 5            | 57008        | 57.77      |

**Interpretation:**

Hasil berisi 5 baris. Kolom `review_score` berada pada rentang 1.00 sampai 5.00. Baris teratas adalah `1.0` berdasarkan urutan query.

**Business implication:**

Distribusi skor menunjukkan apakah stagnasi rating berasal dari dominasi skor netral/rendah atau campuran skor ekstrem.

### Delivery Status Impact

**Query/source table:** `mart_delivery_performance`

**CSV output:** `docs/query_outputs/delivery_status_impact.csv`

**Key numbers and table:**

| delivery_status  | order_count | avg_review_score | low_rating_2_orders | low_rating_2_rate | avg_delivery_days | avg_delay_days |
| ---------------- | ----------- | ---------------- | ------------------- | ----------------- | ----------------- | -------------- |
| unknown          | 2843        | 1.75             | 2218                | 78.02             | 0.00              | 0.00           |
| late             | 6382        | 2.20             | 3983                | 62.41             | 35.21             | 11.75          |
| on_time_or_early | 89448       | 4.29             | 8293                | 9.27              | 10.93             | -13.51         |

**Interpretation:**

Hasil berisi 3 baris. Kolom `order_count` berada pada rentang 2843.00 sampai 89448.00. Baris teratas adalah `unknown` berdasarkan urutan query.

**Business implication:**

Perbandingan status delivery membantu menilai apakah keterlambatan berkaitan dengan rating rendah.

### Delay Bucket Impact

**Query/source table:** `mart_delivery_performance`

**CSV output:** `docs/query_outputs/delay_bucket_impact.csv`

**Key numbers and table:**

| delay_bucket     | order_count | avg_review_score | low_rating_2_orders | low_rating_2_rate | avg_delay_days |
| ---------------- | ----------- | ---------------- | ------------------- | ----------------- | -------------- |
| early_or_on_time | 89448       | 4.29             | 8293                | 9.27              | -13.51         |
| late_1_3_days    | 1852        | 3.29             | 595                 | 32.13             | 1.83           |
| late_4_7_days    | 1748        | 2.10             | 1183                | 67.68             | 5.52           |
| late_8_14_days   | 1447        | 1.67             | 1159                | 80.10             | 10.59          |
| late_15plus_days | 1335        | 1.72             | 1046                | 78.35             | 29.04          |
| unknown          | 2843        | 1.75             | 2218                | 78.02             | 0.00           |

**Interpretation:**

Hasil berisi 6 baris. Kolom `order_count` berada pada rentang 1335.00 sampai 89448.00. Baris teratas adalah `early_or_on_time` berdasarkan urutan query.

**Business implication:**

Bucket delay memudahkan identifikasi ambang keterlambatan yang mulai berkaitan dengan pengalaman buruk.

### Priority CX Segments

**Query/source table:** `mart_customer_experience_items, mart_customer_experience_orders`

**CSV output:** `docs/query_outputs/priority_cx_segments.csv`

**Key numbers and table:**

| segment_type   | segment_name                     | order_count | avg_review_score | low_rating_2_count | low_rating_2_rate | late_rate | avg_delay_days | priority_score |
| -------------- | -------------------------------- | ----------- | ---------------- | ------------------ | ----------------- | --------- | -------------- | -------------- |
| seller         | 1ca7077d890b907f89be8c954a02686a | 114         | 2.20             | 70                 | 61.40             | 15.79     | -6.91          | 734.78         |
| seller         | 54965bbe3e4f07ae045b90b0b8541f52 | 74          | 2.94             | 33                 | 44.59             | 27.03     | -2.33          | 609.77         |
| seller         | 2eb70248d66e0e3ef83659f71b244378 | 198         | 2.72             | 99                 | 50.00             | 10.10     | -10.17         | 600.25         |
| seller         | ad781527c93d00d89a11eecd9dcad7c1 | 44          | 3.07             | 18                 | 40.91             | 27.27     | -9.08          | 566.66         |
| seller         | a49928bcdf77c55c6d6e05e09a9b4ca5 | 98          | 2.95             | 40                 | 40.82             | 21.43     | -4.59          | 546.97         |
| customer_state | RJ                               | 12687       | 3.88             | 2625               | 20.69             | 11.48     | -11.83         | 520.47         |
| seller         | bbad7e518d7af88a0897397ffdca1979 | 68          | 3.04             | 28                 | 41.18             | 16.18     | -7.02          | 519.16         |
| seller         | 2a1348e9addc1af5aaa619b1a3679d6b | 51          | 3.00             | 19                 | 37.25             | 23.53     | -2.90          | 511.94         |
| customer_state | SP                               | 41472       | 4.17             | 5242               | 12.64             | 4.31      | -11.10         | 509.96         |
| seller         | 972d0f9cf61b499a4812cf0bfa3ad3c4 | 79          | 2.96             | 33                 | 41.77             | 11.39     | -9.67          | 503.37         |
| seller         | 602044f2c16190c2c6e45eb35c2e21cb | 49          | 2.89             | 19                 | 38.78             | 14.29     | -8.63          | 481.04         |
| seller         | 712e6ed8aa4aa1fa65dab41fed5737e4 | 78          | 3.45             | 27                 | 34.62             | 19.23     | -10.33         | 468.33         |
| seller         | 835f0f7810c76831d6c7d24c7a646d4d | 44          | 3.30             | 14                 | 31.82             | 25.00     | -5.67          | 461.91         |
| seller         | ede0c03645598cdfc63ca8237acbe73d | 44          | 3.62             | 13                 | 29.55             | 29.55     | -4.87          | 461.28         |
| seller         | dc8798cbf453b7e0f98745e396cc5616 | 41          | 3.12             | 17                 | 41.46             | 4.88      | -9.40          | 459.62         |

**Interpretation:**

Hasil berisi 50 baris. Kolom `order_count` berada pada rentang 31.00 sampai 41472.00. Baris teratas adalah `seller` berdasarkan urutan query.

**Business implication:**

Ranking ini membantu memilih segmen investigasi yang mempertimbangkan volume dampak dan intensitas risiko.

## 2. Delivery Fulfillment

### Monthly Late Rate vs Low Rating

**Query/source table:** `mart_customer_experience_orders`

**CSV output:** `docs/query_outputs/monthly_late_vs_low_rating.csv`

**Key numbers and table:**

| review_month        | reviewed_orders | late_rate | low_rating_2_rate | avg_delay_days |
| ------------------- | --------------- | --------- | ----------------- | -------------- |
| 2016-10-01 00:00:00 | 177             | 0.56      | 16.38             | -41.94         |
| 2016-11-01 00:00:00 | 101             | 1.98      | 37.62             | -24.14         |
| 2016-12-01 00:00:00 | 45              | 0.00      | 64.44             | -45.07         |
| 2017-01-01 00:00:00 | 236             | 0.00      | 8.47              | -30.15         |
| 2017-02-01 00:00:00 | 1403            | 0.64      | 9.55              | -25.07         |
| 2017-03-01 00:00:00 | 2467            | 2.72      | 15.77             | -13.93         |
| 2017-04-01 00:00:00 | 2049            | 4.59      | 15.28             | -13.66         |
| 2017-05-01 00:00:00 | 3678            | 4.79      | 13.84             | -12.29         |
| 2017-06-01 00:00:00 | 3402            | 2.62      | 13.14             | -13.57         |
| 2017-07-01 00:00:00 | 3476            | 2.68      | 12.03             | -12.38         |
| 2017-08-01 00:00:00 | 4459            | 2.44      | 11.46             | -13.08         |
| 2017-09-01 00:00:00 | 4164            | 3.05      | 12.37             | -11.41         |

**Interpretation:**

Hasil berisi 23 baris. Kolom `reviewed_orders` berada pada rentang 45.00 sampai 8983.00. Baris teratas adalah `2016-10-01 00:00:00` berdasarkan urutan query.

**Business implication:**

Membandingkan late rate dan low-rating rate bulanan membantu melihat apakah shock operasional muncul bersamaan dengan penurunan review.

### Non-delivered Orders by Status

**Query/source table:** `mart_customer_experience_orders`

**CSV output:** `docs/query_outputs/non_delivered_orders_by_status.csv`

**Key numbers and table:**

| order_status | order_count | avg_review_score | score_1_count | score_1_rate | low_rating_1_2_count | low_rating_1_2_rate |
| ------------ | ----------- | ---------------- | ------------- | ------------ | -------------------- | ------------------- |
| shipped      | 1107        | 2.00             | 639           | 61.92        | 718                  | 69.57               |
| canceled     | 625         | 1.80             | 421           | 69.59        | 465                  | 76.86               |
| unavailable  | 609         | 1.53             | 462           | 77.65        | 505                  | 84.87               |
| invoiced     | 314         | 1.63             | 230           | 74.43        | 256                  | 82.85               |
| processing   | 301         | 1.26             | 256           | 86.78        | 274                  | 92.88               |
| created      | 5           | 2.33             | 2             | 66.67        | 2                    | 66.67               |
| approved     | 2           | 2.50             | 1             | 50.00        | 1                    | 50.00               |

**Interpretation:**

Hasil berisi 7 baris. Kolom `order_count` berada pada rentang 2.00 sampai 1107.00. Baris teratas adalah `shipped` berdasarkan urutan query.

**Business implication:**

Status non-delivered mengindikasikan potensi friksi fulfilment yang dapat berkaitan dengan rating sangat rendah.

### Delivery Phase Breakdown

**Query/source table:** `stg_orders`

**CSV output:** `docs/query_outputs/delivery_phase_breakdown.csv`

**Key numbers and table:**

| phase             | median_days | avg_days |
| ----------------- | ----------- | -------- |
| approval          | 0.04        | 0.43     |
| seller_processing | 1.79        | 2.81     |
| transit           | 7.12        | 9.33     |

**Interpretation:**

Hasil berisi 3 baris. Kolom `median_days` berada pada rentang 0.04 sampai 7.12. Baris teratas adalah `approval` berdasarkan urutan query.

**Business implication:**

Breakdown fase delivery membantu memisahkan masalah approval, seller processing, dan transit.

### Seller Processing Time Bucket

**Query/source table:** `stg_orders, mart_customer_experience_orders`

**CSV output:** `docs/query_outputs/seller_processing_time_bucket.csv`

**Key numbers and table:**

| processing_bucket | reviewed_orders | avg_review_score | low_rating_1_2_rate | avg_processing_days |
| ----------------- | --------------- | ---------------- | ------------------- | ------------------- |
| <1d               | 15761           | 4.26             | 10.65               | -0.08               |
| 1-2d              | 28319           | 4.24             | 11.02               | 1.00                |
| 2-3d              | 16751           | 4.16             | 12.70               | 2.00                |
| 3-7d              | 28540           | 4.07             | 14.63               | 4.01                |
| 7d+               | 7542            | 3.60             | 25.70               | 11.49               |

**Interpretation:**

Hasil berisi 5 baris. Kolom `reviewed_orders` berada pada rentang 7542.00 sampai 28540.00. Baris teratas adalah `<1d` berdasarkan urutan query.

**Business implication:**

Bucket processing menunjukkan apakah waktu seller sebelum pickup berkaitan dengan risiko review.

### Transit Time Bucket

**Query/source table:** `stg_orders, mart_customer_experience_orders`

**CSV output:** `docs/query_outputs/transit_time_bucket.csv`

**Key numbers and table:**

| transit_bucket | reviewed_orders | avg_review_score | low_rating_1_2_rate | avg_transit_days |
| -------------- | --------------- | ---------------- | ------------------- | ---------------- |
| <3d            | 13594           | 4.38             | 8.32                | 1.36             |
| 3-5d           | 13087           | 4.34             | 9.13                | 3.48             |
| 5-7d           | 16116           | 4.33             | 8.98                | 5.55             |
| 7-10d          | 20035           | 4.28             | 9.76                | 7.77             |
| >10d           | 32997           | 3.83             | 19.84               | 17.49            |

**Interpretation:**

Hasil berisi 5 baris. Kolom `reviewed_orders` berada pada rentang 13087.00 sampai 32997.00. Baris teratas adalah `<3d` berdasarkan urutan query.

**Business implication:**

Transit bucket memberi sinyal apakah durasi carrier berkaitan dengan customer dissatisfaction.

### Delivery Performance Matrix

**Query/source table:** `mart_delivery_performance`

**CSV output:** `docs/query_outputs/delivery_performance_matrix.csv`

**Key numbers and table:**

| delivery_status  | delay_bucket     | order_count | avg_review_score | low_rating_2_orders | low_rating_2_rate | avg_delivery_days | avg_delay_days |
| ---------------- | ---------------- | ----------- | ---------------- | ------------------- | ----------------- | ----------------- | -------------- |
| late             | late_15plus_days | 1335        | 1.72             | 1046                | 78.35             | 54.46             | 29.04          |
| late             | late_1_3_days    | 1852        | 3.29             | 595                 | 32.13             | 23.29             | 1.83           |
| late             | late_4_7_days    | 1748        | 2.10             | 1183                | 67.68             | 28.16             | 5.52           |
| late             | late_8_14_days   | 1447        | 1.67             | 1159                | 80.10             | 34.93             | 10.59          |
| on_time_or_early | early_or_on_time | 89448       | 4.29             | 8293                | 9.27              | 10.93             | -13.51         |
| unknown          | unknown          | 2843        | 1.75             | 2218                | 78.02             | 0.00              | 0.00           |

**Interpretation:**

Hasil berisi 6 baris. Kolom `order_count` berada pada rentang 1335.00 sampai 89448.00. Baris teratas adalah `late` berdasarkan urutan query.

**Business implication:**

Matrix ini menghubungkan status delivery dan delay bucket pada satu tampilan operasional.

### Seller Delivery Risk Label

**Query/source table:** `mart_customer_experience_items`

**CSV output:** `docs/query_outputs/seller_delivery_risk_label.csv`

**Key numbers and table:**

| seller_id                        | seller_city           | seller_state | order_count | avg_review_score | low_rating_2_rate | late_rate | avg_delay_days | risk_label          |
| -------------------------------- | --------------------- | ------------ | ----------- | ---------------- | ----------------- | --------- | -------------- | ------------------- |
| 1ca7077d890b907f89be8c954a02686a | santana de parnaiba   | SP           | 114         | 2.20             | 61.40             | 15.79     | -6.91          | High risk seller    |
| 2eb70248d66e0e3ef83659f71b244378 | campinas              | SP           | 198         | 2.72             | 50.00             | 10.10     | -10.17         | Review issue seller |
| 54965bbe3e4f07ae045b90b0b8541f52 | foz do iguacu         | PR           | 74          | 2.94             | 44.59             | 27.03     | -2.33          | High risk seller    |
| 972d0f9cf61b499a4812cf0bfa3ad3c4 | brusque               | SC           | 79          | 2.96             | 41.77             | 11.39     | -9.67          | Review issue seller |
| dc8798cbf453b7e0f98745e396cc5616 | sao paulo             | SP           | 41          | 3.12             | 41.46             | 4.88      | -9.40          | Review issue seller |
| bbad7e518d7af88a0897397ffdca1979 | sao paulo             | SP           | 68          | 3.04             | 41.18             | 16.18     | -7.02          | High risk seller    |
| ad781527c93d00d89a11eecd9dcad7c1 | sao jose do rio preto | SP           | 44          | 3.07             | 40.91             | 27.27     | -9.08          | High risk seller    |
| a49928bcdf77c55c6d6e05e09a9b4ca5 | sao paulo             | SP           | 98          | 2.95             | 40.82             | 21.43     | -4.59          | High risk seller    |
| 602044f2c16190c2c6e45eb35c2e21cb | ibitinga              | SP           | 49          | 2.89             | 38.78             | 14.29     | -8.63          | Review issue seller |
| 2a1348e9addc1af5aaa619b1a3679d6b | belo horizonte        | MG           | 51          | 3.00             | 37.25             | 23.53     | -2.90          | High risk seller    |
| 6fd52c528dcb38be2eea044946b811f8 | sao paulo             | SP           | 66          | 3.50             | 36.36             | 13.64     | -11.21         | Review issue seller |
| 0b35c634521043bf4b47e21547b99ab5 | teixeira soares       | PR           | 50          | 3.49             | 36.00             | 14.00     | -15.21         | Review issue seller |
| 070d165398b553f3b4b851c216b8a358 | sao paulo             | SP           | 31          | 3.50             | 35.48             | 12.90     | -8.76          | Review issue seller |
| 8444e55c1f13cd5c179851e5ca5ebd00 | congonhal             | MG           | 99          | 3.07             | 35.35             | 6.06      | -21.27         | Review issue seller |
| 712e6ed8aa4aa1fa65dab41fed5737e4 | videira               | SC           | 78          | 3.45             | 34.62             | 19.23     | -10.33         | High risk seller    |

**Interpretation:**

Hasil berisi 50 baris. Kolom `order_count` berada pada rentang 31.00 sampai 976.00. Baris teratas adalah `1ca7077d890b907f89be8c954a02686a` berdasarkan urutan query.

**Business implication:**

Risk label seller membantu memisahkan seller dengan isu delivery, review, atau kombinasi keduanya.

### Category Delivery Risk Label

**Query/source table:** `mart_customer_experience_items`

**CSV output:** `docs/query_outputs/category_delivery_risk_label.csv`

**Key numbers and table:**

| product_category          | order_count | avg_review_score | low_rating_2_rate | late_rate | avg_delay_days | risk_label            |
| ------------------------- | ----------- | ---------------- | ----------------- | --------- | -------------- | --------------------- |
| fashion_male_clothing     | 111         | 3.64             | 26.13             | 3.60      | -12.86         | Review issue category |
| office_furniture          | 1263        | 3.49             | 22.64             | 7.84      | -11.86         | Monitor               |
| audio                     | 347         | 3.83             | 21.90             | 11.53     | -10.10         | Monitor               |
| construction_tools_safety | 166         | 3.84             | 20.48             | 2.41      | -12.31         | Monitor               |
| unknown                   | 1439        | 3.84             | 20.08             | 6.95      | -11.42         | Monitor               |
| home_confort              | 395         | 3.83             | 19.24             | 9.37      | -9.81          | Monitor               |
| fixed_telephony           | 214         | 3.68             | 18.69             | 4.21      | -14.70         | Monitor               |
| fashion_underwear_beach   | 120         | 3.98             | 18.33             | 9.17      | -10.95         | Monitor               |
| home_construction         | 487         | 3.94             | 17.66             | 5.95      | -11.48         | Monitor               |
| dvds_blu_ray              | 58          | 4.08             | 17.24             | 6.90      | -13.36         | Monitor               |
| bed_bath_table            | 9313        | 3.90             | 16.76             | 7.17      | -11.69         | Monitor               |
| furniture_decor           | 6398        | 3.91             | 16.68             | 6.88      | -12.46         | Monitor               |
| air_conditioning          | 249         | 3.97             | 16.47             | 3.61      | -14.27         | Monitor               |
| computers_accessories     | 6649        | 3.93             | 16.09             | 6.12      | -12.46         | Monitor               |
| baby                      | 2861        | 4.01             | 16.01             | 7.69      | -11.73         | Monitor               |

**Interpretation:**

Hasil berisi 50 baris. Kolom `order_count` berada pada rentang 53.00 sampai 9313.00. Baris teratas adalah `fashion_male_clothing` berdasarkan urutan query.

**Business implication:**

Risk label category mengarahkan audit kategori produk yang berkaitan dengan pengalaman buruk.

## 3. Segment Risk

### Top Risk Sellers by Low Rating Contribution

**Query/source table:** `mart_customer_experience_items`

**CSV output:** `docs/query_outputs/top_risk_sellers.csv`

**Key numbers and table:**

| seller_id                        | seller_city           | seller_state | order_count | item_count | avg_review_score | low_rating_2_count | low_rating_2_rate | low_rating_contribution_score |
| -------------------------------- | --------------------- | ------------ | ----------- | ---------- | ---------------- | ------------------ | ----------------- | ----------------------------- |
| 4a3ca9315b744ce9f8e9374361493884 | ibitinga              | SP           | 1785        | 1962       | 3.80             | 342                | 19.16             | 2.46                          |
| 6560211a19b47992c3666cc44a7e94c0 | sao paulo             | SP           | 1838        | 2014       | 3.91             | 319                | 17.36             | 2.30                          |
| cc419e0650a3c5ba77189a1882b7556a | santo andre           | SP           | 1698        | 1767       | 4.06             | 256                | 15.08             | 1.84                          |
| 7c67e1448b00f6e969d365cea6b010ab | itaquaquecetuba       | SP           | 976         | 1356       | 3.35             | 251                | 25.72             | 1.81                          |
| 1f50f920176fa81dab994f9023523100 | sao jose do rio preto | SP           | 1399        | 1923       | 3.99             | 198                | 14.15             | 1.43                          |
| ea8482cd71df3c1969d7b9473ff13abc | sao paulo             | SP           | 1140        | 1196       | 3.95             | 176                | 15.44             | 1.27                          |
| 1025f0e2d44d7041d6cf58b6550e0bfa | sao paulo             | SP           | 907         | 1416       | 3.85             | 158                | 17.42             | 1.14                          |
| da8622b14eb17ae2831f4ac5b9dab84a | piracicaba            | SP           | 1308        | 1545       | 4.07             | 155                | 11.85             | 1.12                          |
| 4869f7a5dfa277a7dca6462dcf3b52b2 | guariba               | SP           | 1124        | 1148       | 4.12             | 152                | 13.52             | 1.09                          |
| 955fee9216a65b617aa5c0531780ce60 | sao paulo             | SP           | 1277        | 1487       | 4.05             | 146                | 11.43             | 1.05                          |
| cca3071e3e9bb7d12640c9fbe2301306 | ibitinga              | SP           | 700         | 812        | 3.85             | 141                | 20.14             | 1.01                          |
| 8b321bb669392f5163d04c59e235e066 | sao paulo             | SP           | 939         | 1014       | 4.00             | 141                | 15.02             | 1.01                          |
| 3d871de0142ce09b7081e2b9d1733cb1 | campo limpo paulista  | SP           | 1069        | 1135       | 4.11             | 123                | 11.51             | 0.89                          |
| 7a67c85e85bb2ce8582c35f2203ad736 | sao paulo             | SP           | 1151        | 1162       | 4.24             | 122                | 10.60             | 0.88                          |
| d2374cbcbb3ca4ab1086534108cc3ab7 | ibitinga              | SP           | 518         | 623        | 3.69             | 105                | 20.27             | 0.76                          |

**Interpretation:**

Hasil berisi 50 baris. Kolom `order_count` berada pada rentang 114.00 sampai 1838.00. Baris teratas adalah `4a3ca9315b744ce9f8e9374361493884` berdasarkan urutan query.

**Business implication:**

Seller dengan kontribusi low-rating tinggi menjadi kandidat monitoring dan coaching prioritas.

### Seller Risk Quadrant

**Query/source table:** `mart_customer_experience_items`

**CSV output:** `docs/query_outputs/seller_risk_quadrant.csv`

**Key numbers and table:**

| seller_id                        | seller_state | order_count | avg_review_score | low_rating_1_2_rate | seller_quadrant |
| -------------------------------- | ------------ | ----------- | ---------------- | ------------------- | --------------- |
| 6560211a19b47992c3666cc44a7e94c0 | SP           | 1838        | 3.91             | 17.36               | Risk zone       |
| 4a3ca9315b744ce9f8e9374361493884 | SP           | 1785        | 3.80             | 19.16               | Risk zone       |
| cc419e0650a3c5ba77189a1882b7556a | SP           | 1698        | 4.06             | 15.08               | Risk zone       |
| 1f50f920176fa81dab994f9023523100 | SP           | 1399        | 3.99             | 14.15               | Risk zone       |
| da8622b14eb17ae2831f4ac5b9dab84a | SP           | 1308        | 4.07             | 11.85               | Risk zone       |
| 955fee9216a65b617aa5c0531780ce60 | SP           | 1277        | 4.05             | 11.43               | Risk zone       |
| 7a67c85e85bb2ce8582c35f2203ad736 | SP           | 1151        | 4.24             | 10.60               | Stars           |
| ea8482cd71df3c1969d7b9473ff13abc | SP           | 1140        | 3.95             | 15.44               | Risk zone       |
| 4869f7a5dfa277a7dca6462dcf3b52b2 | SP           | 1124        | 4.12             | 13.52               | Stars           |
| 3d871de0142ce09b7081e2b9d1733cb1 | SP           | 1069        | 4.11             | 11.51               | Stars           |
| 7c67e1448b00f6e969d365cea6b010ab | SP           | 976         | 3.35             | 25.72               | Risk zone       |
| 8b321bb669392f5163d04c59e235e066 | SP           | 939         | 4.00             | 15.02               | Risk zone       |
| 1025f0e2d44d7041d6cf58b6550e0bfa | SP           | 907         | 3.85             | 17.42               | Risk zone       |
| 620c87c171fb2a6dd6e8bb4dec959fc6 | RJ           | 733         | 4.21             | 12.55               | Stars           |
| a1043bafd471dff536d0c462352beb48 | MG           | 715         | 4.19             | 10.91               | Stars           |

**Interpretation:**

Hasil berisi 50 baris. Kolom `order_count` berada pada rentang 318.00 sampai 1838.00. Baris teratas adalah `6560211a19b47992c3666cc44a7e94c0` berdasarkan urutan query.

**Business implication:**

Quadrant seller mendukung segmentasi action plan berdasarkan volume dan rating.

### Top Risk Categories by Low Rating Contribution

**Query/source table:** `mart_customer_experience_items`

**CSV output:** `docs/query_outputs/top_risk_categories.csv`

**Key numbers and table:**

| product_category      | order_count | item_count | avg_review_score | low_rating_2_count | low_rating_2_rate | late_order_count | late_rate |
| --------------------- | ----------- | ---------- | ---------------- | ------------------ | ----------------- | ---------------- | --------- |
| bed_bath_table        | 9313        | 10982      | 3.90             | 1561               | 16.76             | 668              | 7.17      |
| health_beauty         | 8771        | 9588       | 4.14             | 1114               | 12.70             | 634              | 7.23      |
| computers_accessories | 6649        | 7782       | 3.93             | 1070               | 16.09             | 407              | 6.12      |
| furniture_decor       | 6398        | 8250       | 3.91             | 1067               | 16.68             | 440              | 6.88      |
| sports_leisure        | 7669        | 8581       | 4.11             | 998                | 13.01             | 487              | 6.35      |
| watches_gifts         | 5576        | 5940       | 4.02             | 848                | 15.21             | 395              | 7.08      |
| housewares            | 5843        | 6918       | 4.05             | 772                | 13.21             | 300              | 5.13      |
| telephony             | 4168        | 4512       | 3.95             | 645                | 15.48             | 287              | 6.89      |
| auto                  | 3877        | 4192       | 4.06             | 562                | 14.50             | 273              | 7.04      |
| toys                  | 3853        | 4083       | 4.16             | 489                | 12.69             | 232              | 6.02      |
| garden_tools          | 3496        | 4315       | 4.05             | 470                | 13.44             | 221              | 6.32      |
| baby                  | 2861        | 3040       | 4.01             | 458                | 16.01             | 220              | 7.69      |
| cool_stuff            | 3599        | 3762       | 4.15             | 450                | 12.50             | 205              | 5.70      |
| perfumery             | 3150        | 3405       | 4.17             | 420                | 13.33             | 200              | 6.35      |
| electronics           | 2531        | 2748       | 4.04             | 356                | 14.07             | 190              | 7.51      |

**Interpretation:**

Hasil berisi 50 baris. Kolom `order_count` berada pada rentang 111.00 sampai 9313.00. Baris teratas adalah `bed_bath_table` berdasarkan urutan query.

**Business implication:**

Kategori berisiko dapat diarahkan ke audit kualitas, packaging, dan ekspektasi pelanggan.

### Category Performance Matrix

**Query/source table:** `mart_customer_experience_items`

**CSV output:** `docs/query_outputs/category_performance_matrix.csv`

**Key numbers and table:**

| product_category      | order_count | avg_review_score | low_rating_1_2_rate | low_rating_1_3_rate |
| --------------------- | ----------- | ---------------- | ------------------- | ------------------- |
| bed_bath_table        | 9313        | 3.90             | 16.76               | 26.82               |
| health_beauty         | 8771        | 4.14             | 12.70               | 20.49               |
| sports_leisure        | 7669        | 4.11             | 13.01               | 20.26               |
| computers_accessories | 6649        | 3.93             | 16.09               | 24.23               |
| furniture_decor       | 6398        | 3.91             | 16.68               | 25.49               |
| housewares            | 5843        | 4.05             | 13.21               | 21.75               |
| watches_gifts         | 5576        | 4.02             | 15.21               | 23.80               |
| telephony             | 4168        | 3.95             | 15.48               | 25.48               |
| auto                  | 3877        | 4.06             | 14.50               | 22.29               |
| toys                  | 3853        | 4.16             | 12.69               | 20.30               |
| cool_stuff            | 3599        | 4.15             | 12.50               | 20.53               |
| garden_tools          | 3496        | 4.05             | 13.44               | 21.42               |
| perfumery             | 3150        | 4.17             | 13.33               | 20.00               |
| baby                  | 2861        | 4.01             | 16.01               | 24.64               |
| electronics           | 2531        | 4.04             | 14.07               | 21.93               |

**Interpretation:**

Hasil berisi 50 baris. Kolom `order_count` berada pada rentang 126.00 sampai 9313.00. Baris teratas adalah `bed_bath_table` berdasarkan urutan query.

**Business implication:**

Matrix category memisahkan kategori besar yang stabil dari kategori yang memerlukan mitigasi CX.

### Customer Region Risk

**Query/source table:** `mart_customer_experience_orders`

**CSV output:** `docs/query_outputs/customer_region_risk.csv`

**Key numbers and table:**

| customer_state | order_count | avg_review_score | low_rating_2_count | low_rating_2_rate | late_orders | late_rate | avg_delay_days |
| -------------- | ----------- | ---------------- | ------------------ | ----------------- | ----------- | --------- | -------------- |
| AL             | 410         | 3.76             | 98                 | 23.90             | 82          | 20.00     | -8.82          |
| MA             | 742         | 3.76             | 162                | 21.83             | 122         | 16.44     | -9.65          |
| SE             | 349         | 3.81             | 76                 | 21.78             | 50          | 14.33     | -10.07         |
| RJ             | 12687       | 3.88             | 2625               | 20.69             | 1456        | 11.48     | -11.83         |
| CE             | 1326        | 3.86             | 261                | 19.68             | 174         | 13.12     | -10.85         |
| PA             | 962         | 3.85             | 188                | 19.54             | 100         | 10.40     | -14.19         |
| BA             | 3340        | 3.86             | 631                | 18.89             | 384         | 11.50     | -10.90         |
| PI             | 490         | 3.92             | 90                 | 18.37             | 65          | 13.27     | -11.30         |
| PE             | 1635        | 4.01             | 274                | 16.76             | 149         | 9.11      | -13.36         |
| PB             | 530         | 4.02             | 88                 | 16.60             | 52          | 9.81      | -13.45         |
| RO             | 252         | 4.05             | 39                 | 15.48             | 7           | 2.78      | -20.09         |
| DF             | 2128        | 4.06             | 321                | 15.08             | 118         | 5.55      | -12.04         |
| ES             | 2006        | 4.04             | 300                | 14.96             | 205         | 10.22     | -10.68         |
| GO             | 2007        | 4.04             | 296                | 14.75             | 124         | 6.18      | -12.25         |
| SC             | 3609        | 4.07             | 528                | 14.63             | 284         | 7.87      | -11.58         |

**Interpretation:**

Hasil berisi 24 baris. Kolom `order_count` berada pada rentang 146.00 sampai 41472.00. Baris teratas adalah `AL` berdasarkan urutan query.

**Business implication:**

Region pelanggan membantu mengidentifikasi area pengalaman yang konsisten lebih berisiko.

### Seller Region Risk

**Query/source table:** `mart_customer_experience_items`

**CSV output:** `docs/query_outputs/seller_region_risk.csv`

**Key numbers and table:**

| seller_state | order_count | item_count | avg_review_score | low_rating_2_count | low_rating_2_rate | late_order_count | late_rate | avg_delay_days |
| ------------ | ----------- | ---------- | ---------------- | ------------------ | ----------------- | ---------------- | --------- | -------------- |
| MA           | 388         | 398        | 4.00             | 65                 | 16.75             | 71               | 18.30     | -11.44         |
| DF           | 823         | 898        | 4.03             | 126                | 15.31             | 43               | 5.22      | -13.18         |
| SP           | 69643       | 79661      | 4.01             | 10338              | 14.84             | 4914             | 7.06      | -11.33         |
| ES           | 314         | 367        | 4.01             | 45                 | 14.33             | 18               | 5.73      | -13.57         |
| RJ           | 4318        | 4773       | 4.10             | 612                | 14.17             | 292              | 6.76      | -12.54         |
| PR           | 7615        | 8610       | 4.07             | 1065               | 13.99             | 389              | 5.11      | -14.26         |
| SC           | 3644        | 4045       | 4.10             | 498                | 13.67             | 171              | 4.69      | -14.22         |
| BA           | 567         | 641        | 4.09             | 74                 | 13.05             | 26               | 4.59      | -12.85         |
| MG           | 7872        | 8747       | 4.11             | 984                | 12.50             | 356              | 4.52      | -13.56         |
| PE           | 403         | 445        | 4.13             | 45                 | 11.17             | 14               | 3.47      | -16.26         |
| GO           | 460         | 517        | 4.25             | 46                 | 10.00             | 13               | 2.83      | -14.36         |
| RS           | 1971        | 2177       | 4.22             | 194                | 9.84              | 59               | 2.99      | -16.37         |
| MT           | 137         | 145        | 4.17             | 11                 | 8.03              | 5                | 3.65      | -15.63         |

**Interpretation:**

Hasil berisi 13 baris. Kolom `order_count` berada pada rentang 137.00 sampai 69643.00. Baris teratas adalah `MA` berdasarkan urutan query.

**Business implication:**

Seller region risk memberi sinyal wilayah seller yang memerlukan monitoring operasional.

## 4. Customer Order Behavior

### Customer Retention Funnel

**Query/source table:** `stg_orders, stg_customers`

**CSV output:** `docs/query_outputs/customer_retention_funnel.csv`

**Key numbers and table:**

| retention_bucket | customer_count | customer_share |
| ---------------- | -------------- | -------------- |
| 1 order          | 93099          | 96.88          |
| 2 orders         | 2745           | 2.86           |
| 3+ orders        | 252            | 0.26           |

**Interpretation:**

Hasil berisi 3 baris. Kolom `customer_count` berada pada rentang 252.00 sampai 93099.00. Baris teratas adalah `1 order` berdasarkan urutan query.

**Business implication:**

Retention funnel menunjukkan struktur pembelian ulang yang menjadi konteks customer experience.

### Multi-seller Order Effect

**Query/source table:** `stg_order_items, mart_customer_experience_orders`

**CSV output:** `docs/query_outputs/multi_seller_order_effect.csv`

**Key numbers and table:**

| seller_count_bucket | reviewed_orders | avg_review_score | low_rating_1_2_rate | avg_delivery_days |
| ------------------- | --------------- | ---------------- | ------------------- | ----------------- |
| 1 seller            | 96653           | 4.12             | 13.76               | 12.50             |
| 2 sellers           | 1205            | 2.89             | 46.47               | 9.09              |
| 3 sellers           | 54              | 2.35             | 61.11               | 8.07              |
| 4+ sellers          | 5               | 1.00             | 100.00              | 11.00             |

**Interpretation:**

Hasil berisi 4 baris. Kolom `reviewed_orders` berada pada rentang 5.00 sampai 96653.00. Baris teratas adalah `1 seller` berdasarkan urutan query.

**Business implication:**

Multi-seller bucket menguji apakah kompleksitas fulfilment berkaitan dengan rating dan delivery days.

### Item Count Effect

**Query/source table:** `stg_order_items, mart_customer_experience_orders`

**CSV output:** `docs/query_outputs/item_count_effect.csv`

**Key numbers and table:**

| item_count_bucket | reviewed_orders | avg_review_score | low_rating_1_2_rate |
| ----------------- | --------------- | ---------------- | ------------------- |
| 1 item            | 88227           | 4.16             | 12.71               |
| 2 items           | 7440            | 3.65             | 26.32               |
| 3 items           | 1300            | 3.51             | 29.77               |
| 4+ items          | 950             | 3.32             | 35.37               |

**Interpretation:**

Hasil berisi 4 baris. Kolom `reviewed_orders` berada pada rentang 950.00 sampai 88227.00. Baris teratas adalah `1 item` berdasarkan urutan query.

**Business implication:**

Item count membantu membaca apakah kompleksitas order berkaitan dengan customer dissatisfaction.

### Order Value Bucket Risk

**Query/source table:** `stg_order_payments, mart_customer_experience_orders`

**CSV output:** `docs/query_outputs/order_value_bucket_risk.csv`

**Key numbers and table:**

| order_value_bucket | reviewed_orders | avg_review_score | low_rating_1_2_rate | avg_order_value |
| ------------------ | --------------- | ---------------- | ------------------- | --------------- |
| <50                | 16811           | 4.18             | 11.84               | 36.86           |
| 50-100             | 30120           | 4.13             | 13.57               | 73.28           |
| 100-200            | 31653           | 4.08             | 14.89               | 141.98          |
| 200-500            | 15842           | 3.98             | 17.71               | 290.14          |
| 500+               | 4246            | 3.88             | 21.13               | 928.37          |

**Interpretation:**

Hasil berisi 5 baris. Kolom `reviewed_orders` berada pada rentang 4246.00 sampai 31653.00. Baris teratas adalah `<50` berdasarkan urutan query.

**Business implication:**

Order value bucket membantu melihat apakah nilai transaksi berkaitan dengan risiko rating.

### Installment vs Review Score

**Query/source table:** `stg_order_payments, mart_customer_experience_orders`

**CSV output:** `docs/query_outputs/installment_vs_review.csv`

**Key numbers and table:**

| installment_bucket | reviewed_orders | avg_review_score | avg_order_value |
| ------------------ | --------------- | ---------------- | --------------- |
| 1x                 | 25164           | 4.15             | 96.18           |
| 2-3x               | 22609           | 4.09             | 134.68          |
| 4-6x               | 16079           | 4.06             | 181.74          |
| 7-12x              | 11874           | 4.00             | 334.53          |
| 13-24x             | 182             | 3.85             | 393.92          |

**Interpretation:**

Hasil berisi 5 baris. Kolom `reviewed_orders` berada pada rentang 182.00 sampai 25164.00. Baris teratas adalah `1x` berdasarkan urutan query.

**Business implication:**

Installment bucket dapat menjadi indikator perilaku pembayaran dan ekspektasi order value.

### Review Timing After Delivery

**Query/source table:** `stg_order_reviews, mart_customer_experience_orders`

**CSV output:** `docs/query_outputs/review_timing_after_answer.csv`

**Key numbers and table:**

| review_answer_timing_bucket | review_count | avg_review_score |
| --------------------------- | ------------ | ---------------- |
| same day                    | 959          | 4.20             |
| 1 day                       | 19674        | 4.30             |
| 2-7 days                    | 65344        | 4.28             |
| 8-14 days                   | 3229         | 4.19             |
| 15+ days                    | 1970         | 4.12             |

**Interpretation:**

Hasil berisi 5 baris. Kolom `review_count` berada pada rentang 959.00 sampai 65344.00. Baris teratas adalah `same day` berdasarkan urutan query.

**Business implication:**

Timing berbasis `review_answer_timestamp` membantu membaca kapan feedback diproses setelah delivery.

### Order Complexity Risk Matrix

**Query/source table:** `stg_order_items, mart_customer_experience_orders`

**CSV output:** `docs/query_outputs/order_complexity_risk_matrix.csv`

**Key numbers and table:**

| item_count_bucket | seller_count_bucket | reviewed_orders | avg_review_score | low_rating_1_2_rate | avg_delivery_days |
| ----------------- | ------------------- | --------------- | ---------------- | ------------------- | ----------------- |
| 4+ items          | 4+ sellers          | 5               | 1.00             | 100.00              | 11.00             |
| 4+ items          | 3 sellers           | 22              | 2.05             | 72.73               | 7.45              |
| 4+ items          | 2 sellers           | 87              | 2.69             | 54.02               | 8.60              |
| 3 items           | 3 sellers           | 32              | 2.56             | 53.12               | 8.50              |
| 3 items           | 2 sellers           | 169             | 2.95             | 46.15               | 9.16              |
| 2 items           | 2 sellers           | 949             | 2.90             | 45.84               | 9.12              |
| 4+ items          | 1 seller            | 836             | 3.43             | 32.06               | 12.46             |
| 3 items           | 1 seller            | 1099            | 3.62             | 26.57               | 11.98             |
| 2 items           | 1 seller            | 6491            | 3.76             | 23.46               | 12.11             |
| 1 item            | 1 seller            | 88227           | 4.16             | 12.71               | 12.54             |

**Interpretation:**

Hasil berisi 10 baris. Kolom `reviewed_orders` berada pada rentang 5.00 sampai 88227.00. Baris teratas adalah `4+ items` berdasarkan urutan query.

**Business implication:**

Matrix kompleksitas order menggabungkan jumlah item dan seller untuk membaca potensi friksi fulfilment.

## 5. Geolocation

### Customer State Late Hotspot

**Query/source table:** `mart_customer_experience_orders`

**CSV output:** `docs/query_outputs/customer_state_late_hotspot.csv`

**Key numbers and table:**

| customer_state | order_count | late_orders | late_rate | avg_delivery_days | avg_review_score |
| -------------- | ----------- | ----------- | --------- | ----------------- | ---------------- |
| AL             | 413         | 85          | 20.58     | 24.50             | 3.76             |
| MA             | 747         | 125         | 16.73     | 21.51             | 3.76             |
| SE             | 350         | 51          | 14.57     | 21.46             | 3.81             |
| PI             | 495         | 66          | 13.33     | 19.39             | 3.92             |
| CE             | 1336        | 176         | 13.17     | 21.20             | 3.86             |
| BA             | 3380        | 396         | 11.72     | 19.28             | 3.86             |
| RJ             | 12852       | 1495        | 11.63     | 15.24             | 3.88             |
| PA             | 975         | 106         | 10.87     | 23.73             | 3.85             |
| ES             | 2033        | 214         | 10.53     | 15.72             | 4.04             |
| PB             | 536         | 54          | 10.07     | 20.39             | 4.02             |
| TO             | 280         | 27          | 9.64      | 17.60             | 4.10             |
| MS             | 715         | 68          | 9.51      | 15.54             | 4.11             |
| PE             | 1652        | 153         | 9.26      | 18.40             | 4.01             |
| RN             | 485         | 44          | 9.07      | 19.22             | 4.11             |
| SC             | 3637        | 291         | 8.00      | 14.91             | 4.07             |

**Interpretation:**

Hasil berisi 24 baris. Kolom `order_count` berada pada rentang 148.00 sampai 41746.00. Baris teratas adalah `AL` berdasarkan urutan query.

**Business implication:**

Hotspot late rate per state membantu menentukan wilayah tujuan yang perlu ditelusuri lebih lanjut.

### Problem Routes Flow/Ranking

**Query/source table:** `mart_customer_experience_items`

**CSV output:** `docs/query_outputs/problem_routes.csv`

**Key numbers and table:**

| route    | seller_state | customer_state | order_count | late_rate | avg_review_score | avg_delivery_days |
| -------- | ------------ | -------------- | ----------- | --------- | ---------------- | ----------------- |
| SP -> AL | SP           | AL             | 264         | 22.35     | 3.58             | 24.48             |
| MA -> SP | MA           | SP             | 124         | 19.35     | 3.90             | 15.93             |
| SP -> MA | SP           | MA             | 505         | 18.22     | 3.61             | 21.97             |
| SP -> SE | SP           | SE             | 212         | 16.04     | 3.75             | 21.25             |
| SP -> PI | SP           | PI             | 339         | 15.63     | 3.84             | 20.31             |
| PR -> BA | PR           | BA             | 146         | 13.70     | 3.71             | 21.44             |
| SP -> RJ | SP           | RJ             | 8353        | 13.47     | 3.73             | 15.98             |
| SP -> CE | SP           | CE             | 1000        | 13.10     | 3.82             | 20.80             |
| SP -> BA | SP           | BA             | 2359        | 12.34     | 3.76             | 19.64             |
| SP -> MS | SP           | MS             | 484         | 12.19     | 3.97             | 15.88             |
| SP -> ES | SP           | ES             | 1476        | 11.79     | 3.95             | 15.58             |
| PR -> RJ | PR           | RJ             | 992         | 11.29     | 3.76             | 16.70             |
| SP -> PA | SP           | PA             | 692         | 11.27     | 3.74             | 23.13             |
| SP -> TO | SP           | TO             | 200         | 10.50     | 4.08             | 17.47             |
| RJ -> BA | RJ           | BA             | 136         | 10.29     | 4.03             | 16.74             |

**Interpretation:**

Hasil berisi 50 baris. Kolom `order_count` berada pada rentang 100.00 sampai 31285.00. Baris teratas adalah `SP -> AL` berdasarkan urutan query.

**Business implication:**

Route ranking menunjukkan pasangan wilayah seller-customer yang berkaitan dengan risiko delivery.

### Distance Bucket vs Late Rate

**Query/source table:** `geo_zip_prefix_reference, stg_customers, stg_sellers, stg_order_items, mart_customer_experience_orders`

**CSV output:** `docs/query_outputs/distance_bucket_late_rate.csv`

**Key numbers and table:**

| distance_bucket | order_count | late_order_count | late_rate | avg_delivery_days | avg_delay_days |
| --------------- | ----------- | ---------------- | --------- | ----------------- | -------------- |
| <50 km          | 11619       | 519              | 4.47      | 6.11              | -9.40          |
| 50-100 km       | 6083        | 277              | 4.55      | 7.12              | -9.61          |
| 100-250 km      | 9256        | 455              | 4.92      | 9.36              | -11.38         |
| 250-500 km      | 27201       | 1796             | 6.60      | 12.23             | -12.23         |
| 500-1000 km     | 25381       | 1825             | 7.19      | 14.30             | -12.62         |
| >1000 km        | 15191       | 1606             | 10.57     | 19.14             | -12.72         |

**Interpretation:**

Hasil berisi 6 baris. Kolom `order_count` berada pada rentang 6083.00 sampai 27201.00. Baris teratas adalah `<50 km` berdasarkan urutan query.

**Business implication:**

Distance bucket memperlihatkan apakah jarak seller-customer berkaitan dengan keterlambatan.

### Distance Bucket vs Low-Rating Rate

**Query/source table:** `geo_zip_prefix_reference, stg_customers, stg_sellers, stg_order_items, mart_customer_experience_orders`

**CSV output:** `docs/query_outputs/distance_bucket_low_rating_rate.csv`

**Key numbers and table:**

| distance_bucket | reviewed_order_count | avg_review_score | low_rating_2_count | low_rating_2_rate | low_rating_3_count | low_rating_3_rate |
| --------------- | -------------------- | ---------------- | ------------------ | ----------------- | ------------------ | ----------------- |
| <50 km          | 11837                | 4.23             | 1370               | 11.57             | 2245               | 18.97             |
| 50-100 km       | 6173                 | 4.22             | 732                | 11.86             | 1174               | 19.02             |
| 100-250 km      | 9370                 | 4.26             | 1006               | 10.74             | 1714               | 18.29             |
| 250-500 km      | 27623                | 4.11             | 3919               | 14.19             | 6182               | 22.38             |
| 500-1000 km     | 25718                | 4.09             | 3629               | 14.11             | 5855               | 22.77             |
| >1000 km        | 15451                | 3.98             | 2576               | 16.67             | 3932               | 25.45             |

**Interpretation:**

Hasil berisi 6 baris. Kolom `reviewed_order_count` berada pada rentang 6173.00 sampai 27623.00. Baris teratas adalah `<50 km` berdasarkan urutan query.

**Business implication:**

Distance vs rating membantu membaca apakah jarak jauh juga berkaitan dengan persepsi pelanggan.

### ETA Deviation by Destination State

**Query/source table:** `mart_customer_experience_orders, stg_customers, geo_zip_prefix_reference`

**CSV output:** `docs/query_outputs/eta_deviation_destination_state.csv`

**Key numbers and table:**

| c.customer_state | order_count | avg_delivery_days | avg_delay_days | late_order_count | late_rate | avg_review_score |
| ---------------- | ----------- | ----------------- | -------------- | ---------------- | --------- | ---------------- |
| AL               | 396         | 24.53             | -8.68          | 85               | 21.46     | 3.84             |
| MA               | 714         | 21.44             | -9.64          | 123              | 17.23     | 3.84             |
| SE               | 334         | 21.46             | -9.99          | 51               | 15.27     | 3.91             |
| ES               | 1989        | 15.69             | -10.53         | 211              | 10.61     | 4.08             |
| CE               | 1275        | 21.22             | -10.78         | 176              | 13.80     | 3.94             |
| BA               | 3248        | 19.26             | -10.82         | 393              | 12.10     | 3.93             |
| MS               | 701         | 15.54             | -11.05         | 68               | 9.70      | 4.16             |
| SP               | 40481       | 8.70              | -11.08         | 1819             | 4.49      | 4.25             |
| PI               | 473         | 19.40             | -11.34         | 66               | 13.95     | 3.99             |
| SC               | 3547        | 14.91             | -11.51         | 291              | 8.20      | 4.13             |
| RJ               | 12340       | 15.24             | -11.77         | 1495             | 12.12     | 3.96             |
| DF               | 1917        | 12.88             | -12.08         | 110              | 5.74      | 4.13             |
| TO               | 273         | 17.62             | -12.09         | 27               | 9.89      | 4.15             |
| GO               | 1948        | 15.54             | -12.18         | 128              | 6.57      | 4.11             |
| MG               | 11346       | 11.94             | -13.25         | 518              | 4.57      | 4.19             |

**Interpretation:**

Hasil berisi 24 baris. Kolom `order_count` berada pada rentang 145.00 sampai 40481.00. Baris teratas adalah `AL` berdasarkan urutan query.

**Business implication:**

ETA deviation state membantu mengidentifikasi wilayah tujuan dengan estimasi delivery yang relatif kurang stabil.

### Worst Destination ZIP Prefix Areas

**Query/source table:** `mart_customer_experience_orders, stg_customers, geo_zip_prefix_reference`

**CSV output:** `docs/query_outputs/worst_destination_zip_prefix_areas.csv`

**Key numbers and table:**

| customer_zip_code_prefix | representative_city    | representative_state | order_count | avg_review_score | low_rating_2_rate | late_rate | avg_delay_days |
| ------------------------ | ---------------------- | -------------------- | ----------- | ---------------- | ----------------- | --------- | -------------- |
| 22621                    | rio de janeiro         | RJ                   | 33          | 3.06             | 42.42             | 24.24     | -0.85          |
| 22753                    | rio de janeiro         | RJ                   | 65          | 3.03             | 41.54             | 10.77     | -9.32          |
| 45810                    | porto seguro           | BA                   | 40          | 3.38             | 37.50             | 25.00     | -9.29          |
| 22723                    | rio de janeiro         | RJ                   | 44          | 3.36             | 36.36             | 25.00     | -3.56          |
| 28893                    | rio das ostras         | RJ                   | 37          | 3.35             | 35.14             | 21.62     | -5.94          |
| 65075                    | sao luis               | MA                   | 35          | 3.23             | 34.29             | 20.00     | -6.91          |
| 22793                    | rio de janeiro         | RJ                   | 120         | 3.42             | 34.17             | 29.17     | -5.69          |
| 22713                    | rio de janeiro         | RJ                   | 36          | 3.50             | 33.33             | 19.44     | -9.77          |
| 24030                    | niteroi                | RJ                   | 33          | 3.58             | 33.33             | 9.09      | -13.62         |
| 22770                    | rio de janeiro         | RJ                   | 50          | 3.40             | 32.00             | 20.00     | -8.47          |
| 35790                    | curvelo                | MG                   | 44          | 3.52             | 31.82             | 6.82      | -13.12         |
| 22710                    | rio de janeiro         | RJ                   | 54          | 3.57             | 31.48             | 14.81     | -7.82          |
| 47850                    | luis eduardo magalhaes | BA                   | 36          | 3.56             | 30.56             | 19.44     | -9.11          |
| 23075                    | rio de janeiro         | RJ                   | 33          | 3.70             | 30.30             | 18.18     | -8.48          |
| 13056                    | campinas               | SP                   | 40          | 3.38             | 30.00             | 22.50     | -3.95          |

**Interpretation:**

Hasil berisi 50 baris. Kolom `customer_zip_code_prefix` berada pada rentang 8773.00 sampai 88058.00. Baris teratas adalah `22621` berdasarkan urutan query.

**Business implication:**

ZIP prefix table berguna sebagai daftar area tujuan yang layak ditelusuri, dengan batas volume minimum agar tidak terlalu noisy.

### Destination ZIP Prefix Risk Table

**Query/source table:** `mart_customer_experience_orders, stg_customers, geo_zip_prefix_reference`

**CSV output:** `docs/query_outputs/destination_zip_prefix_risk_table.csv`

**Key numbers and table:**

| representative_state | representative_city    | customer_zip_code_prefix | reviewed_orders | avg_review_score | low_rating_2_rate | late_rate | zip_risk_score |
| -------------------- | ---------------------- | ------------------------ | --------------- | ---------------- | ----------------- | --------- | -------------- |
| RJ                   | rio de janeiro         | 22621                    | 33              | 3.06             | 42.42             | 24.24     | 564.16         |
| RJ                   | rio de janeiro         | 22793                    | 120             | 3.42             | 34.17             | 29.17     | 519.52         |
| BA                   | porto seguro           | 45810                    | 40              | 3.38             | 37.50             | 25.00     | 519.36         |
| RJ                   | rio de janeiro         | 22723                    | 44              | 3.36             | 36.36             | 25.00     | 508.64         |
| RJ                   | rio de janeiro         | 22753                    | 65              | 3.03             | 41.54             | 10.77     | 495.21         |
| RJ                   | rio das ostras         | 28893                    | 37              | 3.35             | 35.14             | 21.62     | 477.49         |
| MA                   | sao luis               | 65075                    | 35              | 3.23             | 34.29             | 20.00     | 460.18         |
| RJ                   | rio de janeiro         | 22713                    | 36              | 3.50             | 33.33             | 19.44     | 447.88         |
| RJ                   | rio de janeiro         | 22770                    | 50              | 3.40             | 32.00             | 20.00     | 440.00         |
| SP                   | campinas               | 13056                    | 40              | 3.38             | 30.00             | 22.50     | 429.82         |
| BA                   | luis eduardo magalhaes | 47850                    | 36              | 3.56             | 30.56             | 19.44     | 419.36         |
| RJ                   | rio de janeiro         | 22743                    | 51              | 3.53             | 29.41             | 19.61     | 411.52         |
| RJ                   | rio de janeiro         | 23075                    | 33              | 3.70             | 30.30             | 18.18     | 409.75         |
| RJ                   | rio de janeiro         | 22710                    | 54              | 3.57             | 31.48             | 14.81     | 409.50         |
| RJ                   | niteroi                | 24030                    | 33              | 3.58             | 33.33             | 9.09      | 395.37         |

**Interpretation:**

Hasil berisi 100 baris. Kolom `customer_zip_code_prefix` berada pada rentang 8773.00 sampai 90040.00. Baris teratas adalah `RJ` berdasarkan urutan query.

**Business implication:**

Risk score area tujuan membantu memilih lokasi prioritas untuk investigasi delivery dan customer experience.

## 6. Monthly Rating Anomaly Diagnosis

### Monthly Rating Anomaly Diagnosis

**Query/source table:** `mart_customer_experience_orders`

**CSV output:** `docs/query_outputs/monthly_rating_anomaly_diagnosis.csv`

**Key numbers and table:**

| review_month        | reviewed_orders | avg_review_score | low_rating_2_rate | late_rate | non_delivered_rate | score_1_rate | suspected_cause                       |
| ------------------- | --------------- | ---------------- | ----------------- | --------- | ------------------ | ------------ | ------------------------------------- |
| 2016-10-01 00:00:00 | 177             | 4.05             | 16.38             | 0.56      | 3.95               | 14.12        | Low sample / early-period instability |
| 2016-11-01 00:00:00 | 101             | 3.19             | 37.62             | 1.98      | 19.80              | 33.66        | Low sample / early-period instability |
| 2016-12-01 00:00:00 | 45              | 2.36             | 64.44             | 0.00      | 71.11              | 64.44        | Low sample / early-period instability |
| 2017-01-01 00:00:00 | 236             | 4.33             | 8.47              | 0.00      | 0.85               | 7.20         | Low sample / early-period instability |
| 2017-02-01 00:00:00 | 1403            | 4.28             | 9.55              | 0.64      | 1.07               | 6.77         | Normal monitoring                     |
| 2017-03-01 00:00:00 | 2467            | 4.03             | 15.77             | 2.72      | 6.93               | 12.65        | Normal monitoring                     |
| 2017-04-01 00:00:00 | 2049            | 4.04             | 15.28             | 4.59      | 5.66               | 11.81        | Normal monitoring                     |
| 2017-05-01 00:00:00 | 3678            | 4.10             | 13.84             | 4.79      | 3.10               | 10.30        | Normal monitoring                     |
| 2017-06-01 00:00:00 | 3402            | 4.13             | 13.14             | 2.62      | 4.26               | 10.23        | Normal monitoring                     |
| 2017-07-01 00:00:00 | 3476            | 4.18             | 12.03             | 2.68      | 3.65               | 8.89         | Normal monitoring                     |
| 2017-08-01 00:00:00 | 4459            | 4.23             | 11.46             | 2.44      | 2.89               | 8.45         | Normal monitoring                     |
| 2017-09-01 00:00:00 | 4164            | 4.18             | 12.37             | 3.05      | 3.70               | 9.37         | Normal monitoring                     |
| 2017-10-01 00:00:00 | 4398            | 4.18             | 12.26             | 3.93      | 2.61               | 9.25         | Normal monitoring                     |
| 2017-11-01 00:00:00 | 4752            | 4.11             | 13.43             | 4.08      | 3.43               | 10.61        | Normal monitoring                     |
| 2017-12-01 00:00:00 | 7925            | 3.93             | 18.54             | 11.19     | 3.05               | 14.93        | Delivery delay shock                  |
| 2018-01-01 00:00:00 | 6151            | 4.06             | 14.97             | 5.93      | 1.95               | 11.45        | Normal monitoring                     |
| 2018-02-01 00:00:00 | 6051            | 4.01             | 16.11             | 6.31      | 3.02               | 12.84        | Normal monitoring                     |
| 2018-03-01 00:00:00 | 7715            | 3.73             | 23.51             | 17.56     | 2.83               | 19.59        | Delivery delay shock                  |
| 2018-04-01 00:00:00 | 7274            | 3.92             | 19.08             | 12.76     | 2.42               | 15.33        | Delivery delay shock                  |
| 2018-05-01 00:00:00 | 7445            | 4.19             | 12.09             | 4.15      | 1.96               | 9.31         | Normal monitoring                     |
| 2018-06-01 00:00:00 | 6710            | 4.20             | 12.27             | 5.56      | 1.30               | 9.20         | Normal monitoring                     |
| 2018-07-01 00:00:00 | 5612            | 4.29             | 10.39             | 1.62      | 1.55               | 8.09         | Normal monitoring                     |
| 2018-08-01 00:00:00 | 8983            | 4.21             | 12.16             | 6.21      | 3.03               | 9.36         | Normal monitoring                     |

**Interpretation:**

Bulan yang perlu diperiksa lebih lanjut adalah 2016-10-01 00:00:00, 2016-11-01 00:00:00, 2016-12-01 00:00:00. Klasifikasi ini bersifat diagnostik deskriptif dan perlu dibaca bersama konteks operasional.

**Business implication:**

Diagnosis anomali bulanan membantu membedakan masalah ukuran sampel dari pola operasional yang perlu ditelusuri.

## 7. Overall Root Cause Summary

- Bukti deskriptif menunjukkan bahwa keterlambatan delivery berkaitan dengan review score yang lebih rendah dan low-rating rate yang lebih tinggi.
- Risiko customer experience tidak hanya muncul dari delivery delay. Seller, kategori produk, wilayah pelanggan, kompleksitas order, dan jarak geografi juga menunjukkan pola risiko yang perlu dimonitor.
- Temuan ini tidak menyatakan hubungan kausal absolut. Angka-angka mendukung interpretasi bahwa beberapa faktor operasional dan segmentasi berkaitan dengan pengalaman pelanggan yang lebih buruk.
- Rekomendasi CEO: prioritaskan monitoring seller dan kategori berisiko tinggi, perbaiki SLA untuk route/wilayah bermasalah, audit area ZIP prefix dengan low-rating rate tinggi, dan pantau anomali bulanan sebagai early warning.
- Untuk eksekusi bisnis, gunakan dashboard sebagai triage, lalu validasi tindakan dengan drill-down order, seller operation review, dan follow-up customer feedback.

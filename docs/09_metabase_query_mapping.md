# 09 Metabase Query Mapping

## 1. Purpose

Dokumen ini memetakan file SQL analytics ke struktur final dashboard Metabase **Customer Experience Root Cause Dashboard**. Tujuannya adalah memastikan setiap chart, card, dan tabel memiliki sumber query yang jelas, menjawab business question yang relevan, serta konsisten dengan persona **Customer Experience Analyst**.

Mapping ini digunakan sebagai panduan saved questions di Metabase, penyusunan dashboard, screenshot demo, dan traceability ke evidence output di `docs/query_outputs/`.

Catatan: rate pada query analytics ditampilkan sebagai persentase 0-100. Contoh: `14.69` berarti 14.69%, bukan 0.1469.

## 2. Final Dashboard Tabs

Dashboard final terdiri dari 5 tab:

1. **Executive Overview**
2. **Delivery Fulfillment**
3. **Segment Risk**
4. **Customer Order Behavior**
5. **Geolocation**

Dashboard dirancang untuk interpretasi non-teknis/CEO-level: mulai dari baseline review score, lalu bergerak ke kandidat root cause pada journey pelanggan.

## 3. Query Mapping Table

| Dashboard Tab | Chart/Card | SQL File / Source | Visualization Type | Business Question Answered |
| --- | --- | --- | --- | --- |
| Executive Overview | KPI Cards | `sql/analytics/10_dashboard_kpi_summary.sql` | KPI card | Bagaimana kondisi umum customer experience platform? |
| Executive Overview | Review Score Distribution | `sql/analytics/03_review_distribution.sql` | Bar chart | Bagaimana distribusi review score pelanggan? |
| Executive Overview | Monthly Average Review Score | `sql/analytics/01_monthly_review_trend.sql` atau `mart_monthly_review` | Line chart | Apakah review score menunjukkan tren meningkat, turun, atau stagnan? |
| Executive Overview | Monthly Low Rating Rate | `sql/analytics/01_monthly_review_trend.sql` atau `mart_monthly_review` | Line chart | Apakah proporsi low rating turun secara konsisten dari waktu ke waktu? |
| Executive Overview | Priority CX Segments | `sql/analytics/09_priority_segments.sql` | Table | Segmen mana yang paling layak diprioritaskan untuk investigasi awal? |
| Delivery Fulfillment | Delivery Status Impact | `sql/analytics/04_delivery_root_cause.sql` atau `mart_delivery_performance` | Bar chart | Apakah delivery status berasosiasi dengan review rendah? |
| Delivery Fulfillment | Delay Bucket Impact | `sql/analytics/04_delivery_root_cause.sql` atau `mart_delivery_performance` | Bar chart | Apakah delay yang lebih panjang berkaitan dengan review score yang lebih buruk? |
| Delivery Fulfillment | Monthly Late vs Low Rating | `sql/analytics/11_monthly_late_rate.sql` | Line chart | Bagaimana late rate dan low rating rate bergerak per bulan? |
| Delivery Fulfillment | Non-Delivered Orders by Status | `sql/analytics/15_non_delivered_orders_by_status.sql` | Bar/table | Status order mana yang menjadi blind spot fulfillment? |
| Delivery Fulfillment | Delivery Phase Breakdown | `sql/analytics/16_delivery_phase_breakdown.sql` | Bar/table | Fase delivery mana yang paling panjang atau berisiko? |
| Delivery Fulfillment | Seller Processing Time Bucket | `sql/analytics/17_processing_time_bucket.sql` | Bar/table | Apakah processing time seller berasosiasi dengan low rating? |
| Delivery Fulfillment | Transit Time Bucket | `sql/analytics/18_transit_time_bucket.sql` | Bar/table | Apakah transit time berasosiasi dengan low rating? |
| Segment Risk | Top Risk Sellers | `sql/analytics/05_seller_performance.sql` | Table / horizontal bar | Seller mana yang memiliki kontribusi low rating paling besar? |
| Segment Risk | Top Risk Categories | `sql/analytics/06_category_performance.sql` | Table / horizontal bar | Kategori produk mana yang memiliki risiko low rating tinggi? |
| Segment Risk | Customer Region Risk | `sql/analytics/07_customer_region_performance.sql` | Bar chart / table | Wilayah customer mana yang perlu diperhatikan dari sisi review dan delivery? |
| Segment Risk | Seller Region Risk | `sql/analytics/08_seller_region_performance.sql` | Bar chart / table | Wilayah seller mana yang berasosiasi dengan low rating atau delivery issue? |
| Segment Risk | Seller Delivery Risk Label | `sql/analytics/12_cross_seller_delivery.sql` | Table | Seller mana yang memiliki kombinasi low rating rate dan late rate tinggi? |
| Segment Risk | Category Delivery Risk Label | `sql/analytics/13_cross_category_delivery.sql` | Table | Kategori mana yang memiliki kombinasi low rating rate dan late rate tinggi? |
| Segment Risk | Seller Risk Quadrant | `sql/analytics/26_seller_quadrant.sql` | Scatter/table | Seller mana yang perlu diprioritaskan berdasarkan volume dan low rating? |
| Segment Risk | Category Performance Matrix | `sql/analytics/21_category_performance_matrix.sql` | Matrix/table | Kategori mana yang memiliki kombinasi volume, low rating, dan delivery risk? |
| Customer Order Behavior | Item Count Effect | `sql/analytics/22_item_count_effect.sql` | Bar chart | Apakah jumlah item dalam order berasosiasi dengan review rendah? |
| Customer Order Behavior | Multi-Seller Order Effect | `sql/analytics/23_multi_seller_order_effect.sql` | Bar/table | Apakah order multi-seller memiliki pola risiko berbeda? |
| Customer Order Behavior | Installment vs Review | `sql/analytics/24_installment_vs_review.sql` | Bar/table | Apakah pola cicilan pembayaran berasosiasi dengan review score? |
| Customer Order Behavior | Order Value Bucket Risk | `sql/analytics/25_order_value_bucket.sql` | Bar/table | Apakah nilai order tertentu lebih sering berkaitan dengan low rating? |
| Customer Order Behavior | Review Timing After Delivery | `sql/analytics/27_review_timing_after_delivery.sql` | Bar/table | Apakah waktu review setelah delivery berkaitan dengan skor review? |
| Customer Order Behavior | Customer Retention Funnel | `sql/analytics/28_customer_retention_funnel.sql` | Funnel/table | Seberapa besar customer yang melakukan repeat order? |
| Geolocation | Customer State Late Hotspot | `sql/analytics/19_late_rate_by_customer_state.sql` | Map/bar | Customer state mana yang memiliki late rate tinggi? |
| Geolocation | Problem Routes | `sql/analytics/20_problem_routes.sql` | Table | Rute seller-customer mana yang memiliki indikasi delivery risk? |
| Geolocation | Distance Bucket Late Rate | `sql/analytics/29_distance_bucket_late_rate.sql` | Bar/line | Apakah jarak seller-customer berasosiasi dengan late rate? |
| Geolocation | Distance Bucket Low Rating Rate | `sql/analytics/30_distance_bucket_low_rating_rate.sql` | Bar/line | Apakah jarak seller-customer berasosiasi dengan low rating? |
| Geolocation | ETA Deviation by Destination State | `sql/analytics/31_eta_deviation_by_destination_state.sql` | Bar/table | Destination state mana yang memiliki deviation dan late rate tinggi? |
| Geolocation | Worst Destination Zip Prefix Areas | `sql/analytics/32_worst_destination_zip_prefix_areas.sql` | Table | Zip prefix mana yang menjadi kandidat area risiko? |

## 4. Recommended Dashboard Flow

Urutan demo dashboard:

1. **Executive Overview**: mulai dari average review score, low rating rate, dan trend untuk menjawab concern CEO.
2. **Delivery Fulfillment**: tunjukkan asosiasi delivery status, delay bucket, dan unknown delivery status dengan low rating.
3. **Segment Risk**: drilldown ke seller, category, customer region, seller region, dan priority segments.
4. **Customer Order Behavior**: tambahkan konteks perilaku order seperti item count, multi-seller order, payment, dan retention.
5. **Geolocation**: tutup dengan indikasi spasial seperti distance bucket, destination state, route, dan zip prefix risk.

Flow ini dibuat agar pengguna dashboard bergerak dari gambaran umum ke diagnosis, lalu ke prioritas investigasi.

## 5. Filter Plan

Filter yang disarankan:

- `review_month`
- `delivery_status`
- `delay_bucket`
- `customer_state`
- `seller_state`
- `product_category`
- `seller_id`
- `distance_bucket`

Filter waktu sebaiknya ditempatkan sebagai filter utama. Filter delivery, region, category, seller, dan distance dapat digunakan untuk drilldown ketika user ingin memahami segmen tertentu.

## 6. Chart Design Notes

- Gunakan KPI card untuk executive overview agar angka utama mudah dibaca.
- Gunakan line chart untuk tren bulanan seperti average review score, low rating rate, dan late rate.
- Gunakan bar chart untuk review score distribution, delay bucket, dan distance bucket.
- Gunakan table untuk detail seller, category, region, route, zip prefix, dan priority segments karena user perlu membaca ranking dan metrik pendukung.
- Setiap chart harus menjawab pertanyaan bisnis yang jelas, bukan hanya menampilkan data.
- Unknown delivery status perlu diberi label sebagai operational blind spot, bukan disembunyikan.
- NLP dan ML tidak menjadi mandatory Metabase tabs kecuali nanti dibuat integrasi eksplisit. Keduanya tetap supporting extensions untuk interpretasi.

## 7. Evidence and Validation

Sumber angka dashboard sebaiknya divalidasi terhadap:

```text
docs/12_dashboard_query_findings.md
docs/query_outputs/
```

Jika query di Metabase diubah, jalankan ulang export findings agar evidence log tetap konsisten.

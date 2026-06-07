# 09 Metabase Query Mapping

## 1. Purpose

Dokumen ini memetakan file SQL analytics Day 3 ke komponen dashboard Metabase. Tujuannya adalah memastikan setiap chart, card, dan tabel dalam dashboard memiliki sumber query yang jelas, menjawab business question yang relevan, serta konsisten dengan persona Customer Experience Analyst.

Mapping ini digunakan sebagai panduan saat membuat saved questions di Metabase, menyusun dashboard, dan menyiapkan screenshot untuk PPT serta paper.

## 2. Dashboard Sections

Dashboard Metabase disarankan dibagi menjadi beberapa section berikut:

- Executive Overview: menampilkan KPI utama seperti total reviewed orders, average review score, low rating rate, late order rate, dan average delay.
- Review Overview: menampilkan distribusi review score dan tren review bulanan.
- Delivery Impact: menampilkan hubungan delivery status dan delay bucket terhadap review rendah.
- Seller Performance: menampilkan seller dengan kontribusi low rating dan late rate yang perlu dipantau.
- Product Category Performance: menampilkan kategori produk dengan low rating rate tinggi dan volume relevan.
- Region Performance: menampilkan performa customer region dan seller region.
- Priority Matrix: menampilkan segmen prioritas berdasarkan volume, low rating, dan late rate.

## 3. Query Mapping Table

| Dashboard Section | Chart/Card | SQL File | Visualization Type | Business Question Answered |
| --- | --- | --- | --- | --- |
| Executive Overview | KPI Cards | `sql/analytics/10_dashboard_kpi_summary.sql` | KPI card | Bagaimana kondisi umum customer experience platform? |
| Review Overview | Review Score Distribution | `sql/analytics/03_review_distribution.sql` | Bar chart | Bagaimana distribusi review score pelanggan? |
| Review Overview | Monthly Average Review Score | `sql/analytics/01_monthly_review_trend.sql` atau `mart_monthly_review` | Line chart | Apakah review score menunjukkan tren meningkat, turun, atau stagnan? |
| Review Overview | Monthly Low Rating Rate | `sql/analytics/01_monthly_review_trend.sql` atau `mart_monthly_review` | Line chart | Apakah proporsi low rating turun secara konsisten dari waktu ke waktu? |
| Delivery Impact | Delivery Status Impact | `sql/analytics/04_delivery_root_cause.sql` | Bar chart | Apakah delivery status berasosiasi dengan review rendah? |
| Delivery Impact | Delay Bucket Impact | `sql/analytics/04_delivery_root_cause.sql` | Bar chart | Apakah delay yang lebih panjang berkaitan dengan review score yang lebih buruk? |
| Delivery Impact | Monthly Late Rate | `sql/analytics/11_monthly_late_rate.sql` | Line chart | Bagaimana tren late order rate dan low rating rate per bulan? |
| Seller Performance | Seller Ranking | `sql/analytics/05_seller_performance.sql` | Table / horizontal bar | Seller mana yang memiliki kontribusi low rating paling besar? |
| Product Category Performance | Category Ranking | `sql/analytics/06_category_performance.sql` | Table / horizontal bar | Kategori produk mana yang memiliki risiko low rating tinggi? |
| Region Performance | Customer Region Performance | `sql/analytics/07_customer_region_performance.sql` | Bar chart / table | Wilayah customer mana yang perlu diperhatikan dari sisi review dan delivery? |
| Region Performance | Seller Region Performance | `sql/analytics/08_seller_region_performance.sql` | Bar chart / table | Wilayah seller mana yang berasosiasi dengan low rating atau delivery issue? |
| Priority Matrix | Priority Segments | `sql/analytics/09_priority_segments.sql` | Table / scatter plot | Segmen mana yang paling layak diprioritaskan untuk intervensi customer experience? |
| Priority Matrix | Seller Delivery Cross Analysis | `sql/analytics/12_cross_seller_delivery.sql` | Table | Seller mana yang memiliki kombinasi low rating rate dan late rate tinggi? |
| Priority Matrix | Category Delivery Cross Analysis | `sql/analytics/13_cross_category_delivery.sql` | Table | Kategori mana yang memiliki kombinasi low rating rate dan late rate tinggi? |

## 4. Recommended Dashboard Layout

Urutan layout dashboard yang disarankan:

1. KPI cards untuk memberi gambaran cepat kondisi customer experience.
2. Review trend dan review distribution untuk menunjukkan pola kepuasan pelanggan.
3. Delivery root cause untuk membandingkan on-time, late, unknown, dan delay bucket.
4. Seller, category, dan region problem untuk menemukan segmen yang perlu dipantau.
5. Priority matrix and recommendations untuk membantu menentukan area intervensi.

Layout ini dibuat agar pengguna dashboard bergerak dari gambaran umum ke diagnosis, lalu ke prioritas tindakan.

## 5. Filter Plan

Filter yang disarankan untuk dashboard:

- `review_month`
- `delivery_status`
- `delay_bucket`
- `customer_state`
- `seller_state`
- `product_category`
- `seller_id`

Filter waktu sebaiknya ditempatkan sebagai filter utama. Filter delivery, region, category, dan seller dapat digunakan untuk drill-down ketika user ingin memahami segmen tertentu.

## 6. Chart Design Notes

- Gunakan KPI card untuk executive overview agar angka utama mudah dibaca.
- Gunakan line chart untuk tren bulanan, seperti average review score, low rating rate, dan late rate.
- Gunakan bar chart untuk review score distribution dan delay bucket comparison.
- Gunakan table untuk detail seller, category, region, dan priority segments karena user perlu membaca ranking dan metrik pendukung.
- Jangan menaruh terlalu banyak chart di halaman utama. Prioritaskan chart yang langsung menjawab business question.
- Setiap chart harus menjawab pertanyaan bisnis yang jelas, bukan hanya menampilkan data.
- Untuk query `04_delivery_root_cause.sql`, gunakan SELECT pertama untuk chart delivery status dan SELECT kedua untuk chart delay bucket.
- Rate di query Day 3 sudah berbentuk persen 0-100, sehingga dapat langsung diformat sebagai percentage di Metabase.

## 7. Next Step

- Connect Metabase ke ClickHouse database `fp_mci_customer_experience`.
- Buat saved questions dari SQL analytics Day 3.
- Susun dashboard sesuai layout yang direkomendasikan.
- Validasi angka dashboard dengan hasil query ClickHouse.
- Ambil screenshot dashboard untuk PPT presentasi dan paper.

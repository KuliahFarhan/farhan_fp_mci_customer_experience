# 03 Dashboard Plan

## 1. Dashboard Objective

Dashboard ini bertujuan untuk membantu tim Product dan Customer Experience dalam memahami kondisi kepuasan pelanggan melalui metrik _review score_, mengidentifikasi apakah terjadi stagnasi atau penurunan kualitas pengalaman pelanggan, serta menentukan prioritas area perbaikan berdasarkan faktor-faktor yang berasosiasi dengan _rating_ rendah.

**Tujuan Utama:**
"Dashboard ini dirancang untuk menjawab mengapa _review score_ pelanggan sulit meningkat dengan membedah kontribusi _delivery delay_, _seller_, kategori produk, dan wilayah terhadap _review_ rendah."

## 2. Dashboard Audience

Target pengguna dashboard ini meliputi:

- **CEO / Leadership**: Untuk pemantauan KPI strategis dan kesehatan platform secara umum.
- **Product Manager**: Untuk memahami bagaimana fitur dan layanan mempengaruhi kepuasan.
- **Customer Experience Analyst**: Sebagai alat utama dalam melakukan eksplorasi akar masalah.
- **Operations Team**: Untuk memantau dampak performa logistik terhadap pengalaman pelanggan.
- **Seller Management Team**: Untuk mengidentifikasi penjual yang membutuhkan intervensi atau pembinaan.

Dashboard dirancang dengan visualisasi yang intuitif sehingga mudah dibaca oleh audiens non-teknis tanpa memerlukan pemahaman SQL atau statistik yang mendalam.

## 3. Main Business Questions Answered by Dashboard

| No  | Business Question                                                                       | Dashboard Section              |
| :-- | :-------------------------------------------------------------------------------------- | :----------------------------- |
| 1   | Bagaimana kondisi umum _review score_ pelanggan?                                        | Section 1 — Executive Overview |
| 2   | Apakah _review score_ benar-benar stagnan atau tidak menunjukkan peningkatan konsisten? | Section 2 — Review Score Trend |
| 3   | Apakah _delivery delay_ berasosiasi dengan _review_ rendah?                             | Section 3 — Delivery Impact    |
| 4   | _Seller_ mana yang paling berkontribusi terhadap _review_ rendah?                       | Section 4 — Segment Problems   |
| 5   | Kategori produk mana yang memiliki risiko _review_ rendah tinggi?                       | Section 4 — Segment Problems   |
| 6   | Wilayah _customer_ / _seller_ mana yang perlu diperhatikan?                             | Section 4 — Segment Problems   |
| 7   | Area mana yang paling layak diprioritaskan untuk perbaikan?                             | Section 5 — Priority Matrix    |

## 4. KPI Cards

| KPI Card                | Definition                                        | Data Source                       | Business Meaning                                         | Baseline Value  |
| :---------------------- | :------------------------------------------------ | :-------------------------------- | :------------------------------------------------------- | :-------------- |
| Average Review Score    | Rata-rata `review_score` (1-5)                    | `mart_monthly_review`             | Indikator umum kesehatan _customer experience_.          | 4.09            |
| Low Rating Rate         | Persentase order dengan `review_score` ≤ 2        | `mart_monthly_review`             | Proporsi pengalaman pelanggan yang sangat buruk.         | 14.69%          |
| Late Order Rate         | Persentase order dengan `delay_days` > 0          | `mart_delivery_performance`       | Efisiensi logistik dan akurasi estimasi pengiriman.      | ~6.57%          |
| Average Delivery Delay  | Rata-rata `delay_days` untuk order yang terlambat | `mart_delivery_performance`       | Seberapa jauh keterlambatan terjadi dari janji estimasi. | To be finalized |
| Total Reviewed Orders   | Jumlah unik pesanan yang memiliki ulasan          | `mart_customer_experience_orders` | Volume data yang digunakan untuk analisis.               | 98,673          |
| Total Low Rating Orders | Jumlah pesanan dengan `review_score` ≤ 2          | `mart_customer_experience_orders` | Skala absolut masalah yang perlu ditangani.              | 14,494          |

## 5. Dashboard Sections

### Section 1 — Executive Overview

**Tujuan:** Memberikan ringkasan cepat mengenai kondisi terkini pengalaman pelanggan.
**Komponen:**

- KPI Cards (rata-rata skor, % low rating, volume review).
- Distribusi skor ulasan (Bar Chart 1-5).
- Perbandingan rata-rata skor bulan ini vs bulan lalu.
  **Pesan Bisnis:** _Average score_ saja tidak cukup; _low rating rate_ perlu dipantau secara ketat karena mewakili pelanggan yang berisiko meninggalkan platform (_churn_).

### Section 2 — Review Score Trend

**Tujuan:** Menguji hipotesis stagnasi skor ulasan.
**Chart:**

- Line Chart: Tren bulanan `Average Review Score`.
- Line Chart: Tren bulanan `Low Rating Rate (%)`.
  **Interpretasi:** Memperhatikan apakah fluktuasi skor konsisten di angka tertentu tanpa tren perbaikan (stagnasi) atau justru menunjukkan degradasi pada periode tertentu.

### Section 3 — Delivery Impact

**Tujuan:** Mengonfirmasi hubungan antara performa logistik dan kepuasan.
**Chart:**

- Bar Chart: `Average Review Score` berdasarkan `delivery_status` (_late_ vs _on-time_).
- Bar Chart: `Low Rating Rate` berdasarkan `delay_bucket`.
  **Pesan Bisnis:** Jika keterlambatan menyebabkan lonjakan drastis pada _low rating_ (misal: skor turun dari 4.3 ke 2.2), maka perbaikan logistik adalah prioritas utama.

### Section 4 — Seller, Product Category, and Region Problems

**Tujuan:** Menemukan lokalisasi masalah pada segmen spesifik.
**Chart/Table:**

- Table: Top Sellers dengan jumlah ulasan rendah terbanyak (min. 30 order).
- Table: Kategori produk dengan _low rating rate_ tertinggi (min. 50 order).
- Map/Bar: _Low rating rate_ berdasarkan negara bagian (_State_) pelanggan.
  **Catatan:** Fokus pada segmen dengan volume relevan untuk menghindari bias data kecil.

### Section 5 — Priority Matrix

**Tujuan:** Mengarahkan tindakan operasional ke segmen yang paling berdampak.
**Komponen:**

- Tabel Matriks Prioritas: Segmentasi berbasis High Volume & High Low-Rating Rate.
- Kolom: Segment Name, Order Count, Low Rating Rate, Late Rate, Recommended Action.
  **Pesan Bisnis:** Memberikan fokus pada 20% area yang menyumbang 80% masalah pengalaman pelanggan.

## 6. Chart Plan

| Chart ID | Chart Name                          | Type       | Metric           | Dimension          | Purpose                                                      |
| :------- | :---------------------------------- | :--------- | :--------------- | :----------------- | :----------------------------------------------------------- |
| C01      | Review Score Distribution           | Bar Chart  | Order Count      | `review_score`     | Melihat sebaran kepuasan pelanggan secara makro.             |
| C02      | Monthly Average Review Score        | Line Chart | Avg Score        | `review_month`     | Mengidentifikasi tren kenaikan atau stagnasi skor.           |
| C03      | Monthly Low Rating Rate             | Line Chart | % Low Rating     | `review_month`     | Memantau perubahan proporsi ketidakpuasan ekstrem.           |
| C04      | Avg Review Score by Delivery Status | Bar Chart  | Avg Score        | `delivery_status`  | Memvalidasi dampak keterlambatan terhadap persepsi.          |
| C05      | Low Rating Rate by Delivery Status  | Bar Chart  | % Low Rating     | `delivery_status`  | Melihat risiko fatal akibat keterlambatan.                   |
| C06      | Avg Review Score by Delay Bucket    | Bar Chart  | Avg Score        | `delay_bucket`     | Mengetahui batas toleransi keterlambatan pelanggan.          |
| C07      | Top Problematic Sellers             | Table      | Low Rating Count | `seller_id`        | Mengidentifikasi penjual yang merusak reputasi platform.     |
| C08      | Category Low Rating Analysis        | Table      | % Low Rating     | `product_category` | Menemukan kategori produk yang sulit dipenuhi ekspektasinya. |
| C09      | Customer Region Low Rating Analysis | Bar Chart  | % Low Rating     | `customer_state`   | Menilai efisiensi layanan berdasarkan letak geografis.       |
| C10      | Priority Segment Matrix             | Table      | Beragam          | `segment`          | Daftar prioritas intervensi bisnis harian.                   |

## 7. Filter Plan

| Filter          | Column             | Applies To      | Purpose                                                 |
| :-------------- | :----------------- | :-------------- | :------------------------------------------------------ |
| Time Period     | `review_month`     | All Charts      | Analisis performa pada rentang waktu tertentu.          |
| Region          | `customer_state`   | All Charts      | Fokus pada wilayah geografis tertentu.                  |
| Category        | `category_english` | All Charts      | Spesifik ke kategori produk yang dikelola.              |
| Delivery Status | `delivery_status`  | Section 1, 2, 4 | Memfilter data untuk melihat tren jika logistik lancar. |

## 8. Required Data Mart / Tables for Metabase

| Mart / Table       | Granularity       | Purpose                                                 |
| :----------------- | :---------------- | :------------------------------------------------------ |
| `mart_cx_orders`   | One row per order | Analisis trend review, status delivery, dan geografi.   |
| `mart_cx_items`    | One row per item  | Analisis mendalam seller dan performa kategori produk.  |
| `mart_monthly_kpi` | Monthly           | Penyajian tren cepat untuk dashboard tingkat eksekutif. |
| `mart_seller_perf` | Per seller        | Ranking performa seller untuk tim Seller Management.    |

## 9. Dashboard Storyline

"Dashboard menunjukkan bahwa _customer experience_ tidak cukup dinilai dari _average review score_ saja. Untuk memahami mengapa skor sulit meningkat, dashboard membedah proporsi _low rating_, performa _delivery_, _seller_, kategori produk, dan wilayah. Segmen dengan volume transaksi besar dan _low rating rate_ tinggi akan menjadi prioritas perbaikan karena memiliki dampak bisnis paling besar."

**Narasi Alur:**

1. **Overview**: Cek skor rata-rata platform saat ini.
2. **Trend**: Apakah skor bergerak naik bulan ini? Atau justru stagnan/turun?
3. **Diagnosis Logistik**: Seberapa jauh _late delivery_ menghancurkan skor ulasan?
4. **Segmentation**: Siapa yang paling bermasalah? Penjual tertentukah, atau kategori produk yang spesifik?
5. **Action**: Segmen mana yang harus dihubungi oleh tim Ops besok pagi?

## 10. Design Principles

- **Action-Oriented**: Setiap grafik harus memprovokasi pertanyaan "apa yang harus kita lakukan?".
- **At-a-glance Summary**: Gunakan KPI cards untuk informasi kritikal.
- **Contextual Ranking**: Gunakan tabel ranking dengan _threshold_ volume agar data valid.
- **Low Noise**: Hindari pengulangan informasi yang sama dalam visual yang berbeda.
- **Drill-down Capability**: Memungkinkan pengguna melihat detail dari level wilayah hingga level seller.

## 11. Actionable Recommendation Mapping

| Finding Type                                 | Possible Business Action                                          |
| :------------------------------------------- | :---------------------------------------------------------------- |
| Keterlambatan tinggi di wilayah tertentu     | Evaluasi partner logistik lokal atau tambah sentra distribusi.    |
| Seller dengan rating rendah kronis           | Berlakukan pembatasan akun (_account suspension_) atau pelatihan. |
| Kategori produk tertentu banyak ulasan buruk | Audit kualitas produk atau perjelas deskripsi produk di platform. |
| Low rating rate tidak kunjung turun          | Investigasi ulang kebijakan _customer support_ dan kompensasi.    |

## 12. Next Step

- Merancang skema tabel data mart di ClickHouse.
- Implementasi ETL/agregasi data menggunakan Airflow.
- Membuat query SQL final untuk visualisasi Metabase.
- Penyusunan filter dan interaktivitas dashboard.

# 02 Hypothesis Mapping

## 1. Purpose

Dokumen ini berisi pemetaan hipotesis awal untuk analisis Customer Experience pada DustiniaDelixia Groceria. Hipotesis digunakan untuk mengarahkan proses EDA, query analitik, desain dashboard Metabase, dan penyusunan rekomendasi bisnis.

Fokus utama project adalah memahami faktor-faktor yang berhubungan dengan review score pelanggan, terutama pada kasus review rendah dan stagnasi skor review dari waktu ke waktu.

Hipotesis dalam dokumen ini belum dianggap sebagai kesimpulan. Semua hipotesis harus diuji menggunakan data aktual melalui proses exploratory data analysis, query SQL, dan visualisasi dashboard.

## 2. Main Business Problem

Permasalahan utama yang dianalisis adalah:

> Review score pelanggan sulit meningkat dan perusahaan belum memahami faktor utama yang berhubungan dengan rendahnya pengalaman pelanggan.

Analisis diarahkan untuk menjawab apakah review rendah lebih banyak berkaitan dengan keterlambatan pengiriman, gap estimasi pengiriman, performa seller, kategori produk, atau karakteristik wilayah pelanggan.

## 3. Business Questions

| No  | Business Question                                                                                   | Analytical Direction                       |
| --- | --------------------------------------------------------------------------------------------------- | ------------------------------------------ |
| BQ1 | Bagaimana distribusi review score pelanggan?                                                        | Review distribution analysis               |
| BQ2 | Apakah review score menunjukkan pola stagnan dari waktu ke waktu?                                   | Monthly review trend analysis              |
| BQ3 | Apakah keterlambatan pengiriman berhubungan dengan review score rendah?                             | Delivery performance analysis              |
| BQ4 | Seller, kategori produk, atau wilayah mana yang paling banyak berkontribusi terhadap review rendah? | Segment/root-cause analysis                |
| BQ5 | Faktor apa yang paling layak diprioritaskan untuk meningkatkan customer experience?                 | Business recommendation and prioritization |

## 4. Hypothesis Mapping

| ID | Hypothesis                                                                                                                    | Reasoning                                                                                                             | Required Tables                                                                                | Key Columns                                                                                       | Metrics                                                              | Validation Approach                                                     | Expected Dashboard Output                   |
| -- | ----------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------- | ----------------------------------------------------------------------- | ------------------------------------------- |
| H1 | Pesanan yang terlambat diterima pelanggan berasosiasi dengan review score yang lebih rendah.                                  | Keterlambatan pengiriman dapat membuat pengalaman pelanggan tidak sesuai ekspektasi.                                  | `orders`,`order_reviews`                                                                   | `order_id`,`order_delivered_customer_date`,`order_estimated_delivery_date`,`review_score` | average review score, low rating rate, late order rate               | Bandingkan review score antara order on-time dan late.                  | Chart review score by delivery status       |
| H2 | Semakin besar gap antara estimasi dan tanggal pengiriman aktual, semakin tinggi risiko review rendah.                         | Pelanggan kemungkinan membandingkan pengalaman aktual dengan estimasi yang dijanjikan.                                | `orders`,`order_reviews`                                                                   | `order_delivered_customer_date`,`order_estimated_delivery_date`,`review_score`              | delay days, average review score, low rating rate                    | Kelompokkan delay ke beberapa bucket dan bandingkan rating.             | Chart review score by delay bucket          |
| H3 | Seller tertentu berkontribusi secara tidak proporsional terhadap review rendah.                                               | Performa seller dapat berbeda dalam kualitas fulfillment, kecepatan proses, atau konsistensi layanan.                 | `orders`,`order_items`,`sellers`,`order_reviews`                                       | `order_id`,`seller_id`,`seller_city`,`seller_state`,`review_score`                      | average review score per seller, low rating count, order count       | Hitung seller dengan order cukup banyak dan low rating tinggi.          | Top problematic sellers table               |
| H4 | Kategori produk tertentu memiliki risiko review rendah lebih tinggi dibanding kategori lain.                                  | Beberapa kategori mungkin lebih rentan terhadap ekspektasi produk, kualitas barang, atau masalah pengiriman.          | `order_items`,`products`,`category_translation`,`order_reviews`                        | `product_id`,`product_category_name`,`product_category_name_english`,`review_score`       | average review score per category, low rating rate, order count      | Bandingkan kategori berdasarkan rating dan volume order.                | Problematic product category chart          |
| H5 | Wilayah customer atau seller tertentu berasosiasi dengan pengalaman pelanggan yang lebih buruk.                               | Jarak, kondisi logistik, atau konsentrasi seller/customer di wilayah tertentu dapat memengaruhi pengalaman transaksi. | `orders`,`customers`,`order_items`,`sellers`,`order_reviews`                         | `customer_city`,`customer_state`,`seller_city`,`seller_state`,`review_score`            | average review score by region, late rate by region, low rating rate | Bandingkan review dan delay berdasarkan state/city customer dan seller. | Region-level review and delay chart         |
| H6 | Review score yang stagnan dapat disebabkan oleh proporsi review rendah yang tidak turun secara konsisten dari waktu ke waktu. | Average review score bisa terlihat stagnan jika low rating rate tetap tinggi pada bulan-bulan tertentu.               | `order_reviews`,`orders`                                                                   | `review_creation_date`,`order_purchase_timestamp`,`review_score`                            | monthly average review, monthly low rating rate                      | Analisis tren bulanan review score dan low rating rate.                 | Review trend and low-rating trend           |
| H7 | Kombinasi seller, kategori produk, dan keterlambatan pengiriman dapat membentuk area prioritas perbaikan customer experience. | Root cause kemungkinan tidak berdiri sendiri; seller atau kategori bermasalah bisa diperburuk oleh delay.             | `orders`,`order_reviews`,`order_items`,`sellers`,`products`,`category_translation` | `seller_id`,`product_category_name`,`delay_days`,`review_score`                           | low rating contribution, late rate, order volume                     | Buat segmentasi berdasarkan kombinasi seller/category/delivery status.  | Priority matrix for business recommendation |

## 5. Metric Definition

| Metric                  | Definition                                                                             | Purpose                                             |
| ----------------------- | -------------------------------------------------------------------------------------- | --------------------------------------------------- |
| Average Review Score    | Rata-rata `review_score`pada kelompok tertentu.                                      | Mengukur kualitas pengalaman pelanggan secara umum. |
| Low Rating Rate         | Persentase order dengan `review_score <= 2`atau `review_score <= 3`.               | Mengukur proporsi pengalaman buruk.                 |
| Delivery Duration       | Selisih antara `order_delivered_customer_date`dan `order_purchase_timestamp`.      | Mengukur lama total pengiriman sejak order dibuat.  |
| Delivery Delay          | Selisih antara `order_delivered_customer_date`dan `order_estimated_delivery_date`. | Mengukur keterlambatan terhadap estimasi.           |
| Late Order Rate         | Persentase order dengan `delivery_delay > 0`.                                        | Mengukur proporsi order yang terlambat.             |
| Order Volume            | Jumlah order pada seller, kategori, atau wilayah tertentu.                             | Menghindari bias dari sampel kecil.                 |
| Low Rating Contribution | Jumlah review rendah dari suatu segmen dibanding total review rendah.                  | Mengukur kontribusi segmen terhadap masalah utama.  |

## 6. Required Dataset Mapping

| Analysis Area             | Main Tables                                                             | Join Key                                 | Notes                                                            |
| ------------------------- | ----------------------------------------------------------------------- | ---------------------------------------- | ---------------------------------------------------------------- |
| Review analysis           | `order_reviews`,`orders`                                            | `order_id`                             | Dipakai untuk distribusi rating dan tren review.                 |
| Delivery analysis         | `orders`,`order_reviews`                                            | `order_id`                             | Hanya gunakan order dengan timestamp delivery lengkap.           |
| Seller analysis           | `orders`,`order_items`,`sellers`,`order_reviews`                | `order_id`,`seller_id`               | Perlu memperhatikan order dengan lebih dari satu item.           |
| Product category analysis | `order_items`,`products`,`category_translation`,`order_reviews` | `product_id`,`product_category_name` | Kategori tanpa nama perlu diberi label `unknown`.              |
| Region analysis           | `orders`,`customers`,`order_items`,`sellers`,`order_reviews`  | `customer_id`,`seller_id`            | Analisis awal cukup memakai city/state tanpa geolocation detail. |

## 7. Analytical Cautions

Beberapa batasan perlu diperhatikan agar hasil analisis tidak bias:

1. Hipotesis ini bersifat asosiatif, bukan kausal. Jika ditemukan bahwa order terlambat memiliki review lebih rendah, hasil tersebut belum otomatis membuktikan keterlambatan sebagai satu-satunya penyebab review rendah.
2. Seller atau kategori dengan order sangat sedikit tidak boleh langsung dianggap buruk hanya karena rata-rata rating rendah. Analisis harus menggunakan batas minimum order volume.
3. Order dengan lebih dari satu review perlu diperlakukan secara konsisten, misalnya menggunakan review terbaru berdasarkan `review_answer_timestamp` atau agregasi per `order_id`.
4. Analisis delivery hanya valid untuk order dengan timestamp pengiriman lengkap.
5. Missing komentar review tidak menjadi hambatan utama karena fokus awal adalah `review_score`, bukan analisis sentimen teks.
6. Region analysis perlu hati-hati karena city/state tidak selalu cukup menjelaskan jarak logistik atau kualitas layanan pengiriman.

## 8. Prioritization Logic

Prioritas rekomendasi bisnis tidak hanya ditentukan oleh rata-rata review score yang rendah. Segmen yang diprioritaskan harus memenuhi beberapa kriteria:

1. Memiliki review score rendah.
2. Memiliki low rating rate tinggi.
3. Memiliki order volume cukup besar.
4. Berkontribusi besar terhadap total review rendah.
5. Masih dapat ditindaklanjuti oleh perusahaan, misalnya melalui seller monitoring, SLA pengiriman, perbaikan estimasi delivery, atau intervensi kategori produk tertentu.

Dengan demikian, rekomendasi akhir tidak hanya menjawab “segmen mana yang buruk”, tetapi juga “segmen mana yang paling layak diperbaiki terlebih dahulu”.

## 9. Expected Output for Next Step

Setelah hypothesis mapping selesai, langkah berikutnya adalah membuat EDA awal untuk menguji sinyal dari setiap hipotesis. Output EDA yang dibutuhkan:

1. Distribusi review score.
2. Tren average review score per bulan.
3. Tren low rating rate per bulan.
4. Perbandingan review score antara on-time dan late delivery.
5. Review score berdasarkan delay bucket.
6. Top seller dengan low rating contribution tinggi.
7. Top product category dengan low rating rate tinggi.
8. Region dengan average review score rendah dan late rate tinggi.
9. Priority matrix untuk rekomendasi bisnis.

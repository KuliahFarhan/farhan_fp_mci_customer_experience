# 08 Business Analysis Summary

## 1. Objective

Analisis bisnis Day 3 bertujuan untuk menerjemahkan hasil pipeline dan mart analytics menjadi insight customer experience yang siap digunakan untuk dashboard Metabase, paper, dan presentasi. Fokus utama analisis adalah memahami pola review score pelanggan, proporsi low rating, serta faktor-faktor yang berasosiasi dengan review rendah, terutama delivery delay, seller performance, product category, dan region.

Analisis ini tidak dimaksudkan untuk membuktikan hubungan kausal secara final. Hasil yang disajikan digunakan sebagai indikasi awal dan kandidat root cause yang perlu dipantau lebih lanjut melalui dashboard dan validasi bisnis.

## 2. Executive Summary

- Average review score platform berada pada 4.09, sehingga secara agregat terlihat cukup baik. Namun low rating rate masih signifikan, yaitu 14.69% untuk review score <= 2 dan 22.93% untuk review score <= 3.
- Review score 5 mendominasi dengan 57,008 review atau 57.77%, tetapi review score 1 masih cukup besar dengan 11,363 review atau 11.52%. Hal ini menunjukkan bahwa pengalaman pelanggan tidak merata.
- Late delivery memiliki asosiasi kuat dengan review rendah. Order on-time atau early memiliki average review score 4.29, sedangkan order late hanya 2.27.
- Semakin panjang delay, semakin buruk review score dan semakin tinggi low rating rate. Bucket late 8-14 hari dan late 15+ hari menunjukkan tingkat low rating yang sangat tinggi.
- Unknown delivery status perlu diperhatikan karena memiliki average review score 1.75 dan low_rating_2_rate 78.02%. Status ini dapat mengindikasikan masalah data completeness atau pengalaman pengiriman yang tidak tercatat dengan baik.
- Seller, product category, customer region, dan seller region digunakan sebagai segmentasi lanjutan untuk menentukan prioritas intervensi customer experience.

## 3. Review Score Overview

Dataset mart yang tervalidasi memiliki 99,441 total orders, dengan 98,673 reviewed orders dan 768 order tanpa review. Order tanpa review tetap dipertahankan pada order-level mart, tetapi tidak dihitung dalam analisis review score agar tidak menjadi low rating palsu.

Distribusi review score menunjukkan bahwa pelanggan yang sangat puas masih menjadi kelompok terbesar. Review score 5 berjumlah 57,008 review atau 57.77%, diikuti score 4 sebanyak 19,038 review atau 19.29%. Namun, proporsi review rendah tetap perlu diperhatikan. Review score 1 berjumlah 11,363 atau 11.52%, sedangkan score 2 berjumlah 3,131 atau 3.17%.

Secara bisnis, average review score 4.09 tidak cukup untuk menyimpulkan bahwa pengalaman pelanggan sudah stabil. Low rating rate sebesar 14.69% untuk score <= 2 menunjukkan adanya kelompok pelanggan yang mengalami pengalaman buruk secara signifikan. Oleh karena itu, dashboard sebaiknya tidak hanya menampilkan average review score, tetapi juga low rating rate dan jumlah low rating order.

## 4. Delivery Root Cause Signal

Delivery performance menjadi sinyal terkuat dalam analisis awal customer experience. Order dengan delivery status on_time_or_early berjumlah 89,448 order, memiliki average review score 4.29, low_rating_2_rate 9.27%, dan low_rating_3_rate 17.35%. Sebaliknya, order late berjumlah 6,382 order, memiliki average review score 2.27, low_rating_2_rate 62.41%, dan low_rating_3_rate 73.30%.

Perbedaan ini menunjukkan bahwa keterlambatan pengiriman berasosiasi kuat dengan review rendah. Average delivery days pada order late mencapai 33.78 hari, sedangkan on-time atau early sebesar 10.93 hari. Dari sisi delay terhadap estimasi, order late memiliki avg_delay_days 10.52, sementara on-time atau early memiliki avg_delay_days -13.51.

Analisis delay bucket memperkuat indikasi tersebut. Order late_1_3_days masih memiliki average review score 3.29 dengan low_rating_2_rate 32.13%. Ketika delay meningkat menjadi late_4_7_days, average review score turun menjadi 2.10 dan low_rating_2_rate naik menjadi 67.68%. Pada late_8_14_days, average review score menjadi 1.67 dengan low_rating_2_rate 80.10%. Bucket late_15plus_days juga sangat buruk, dengan average review score 1.72 dan low_rating_2_rate 78.35%.

Selain order late, kelompok unknown juga perlu ditelusuri. Unknown delivery status memiliki 2,843 order, average review score 1.75, dan low_rating_2_rate 78.02%. Kelompok ini belum dapat langsung disimpulkan sebagai masalah operasional, tetapi menjadi kandidat penting untuk investigasi data quality dan proses fulfillment.

## 5. Seller, Category, and Region Analysis

Analisis seller, category, dan region disiapkan melalui query Day 3 agar dashboard dapat menampilkan ranking segmen yang paling berkontribusi terhadap review rendah. Detail seller performance tersedia pada `sql/analytics/05_seller_performance.sql`, dengan metrik seperti order_count, item_count, avg_review_score, low_rating_2_rate, late_rate, avg_delay_days, dan low_rating_contribution_score.

Analisis product category tersedia pada `sql/analytics/06_category_performance.sql`. Query ini menggunakan fallback kategori agar produk tanpa terjemahan tetap masuk sebagai kategori valid. Metrik utama yang digunakan adalah order_count, item_count, avg_review_score, low_rating rate, late_rate, dan avg_delay_days.

Analisis customer region tersedia pada `sql/analytics/07_customer_region_performance.sql`, sedangkan seller region tersedia pada `sql/analytics/08_seller_region_performance.sql`. Kedua query ini digunakan untuk melihat apakah wilayah tertentu memiliki indikasi pengalaman pelanggan yang lebih rendah, terutama bila low rating rate dan late rate sama-sama tinggi.

Seluruh query segmentasi menggunakan minimum volume threshold untuk mengurangi bias dari sampel kecil. Dengan pendekatan ini, dashboard dapat membantu memprioritaskan segmen yang tidak hanya buruk secara rate, tetapi juga memiliki volume yang cukup relevan secara bisnis.

## 6. Priority Root Cause Candidates

Berdasarkan hasil analisis awal, kandidat root cause yang perlu diprioritaskan adalah:

1. Delivery delay, karena order late memiliki average review score jauh lebih rendah dibanding on-time atau early.
2. Long delay bucket, terutama late_4_7_days, late_8_14_days, dan late_15plus_days yang menunjukkan low_rating_2_rate sangat tinggi.
3. Unknown atau incomplete delivery status, karena kelompok ini memiliki review sangat rendah dan perlu validasi data/process lebih lanjut.
4. Seller dengan low rating contribution tinggi, terutama bila juga memiliki late rate yang tinggi.
5. Product category dan region dengan low rating rate tinggi, volume order besar, dan indikasi delivery issue.

Kandidat tersebut perlu dilihat sebagai prioritas investigasi, bukan kesimpulan kausal final. Dashboard priority matrix akan membantu memilih segmen yang paling layak ditindaklanjuti terlebih dahulu.

## 7. Initial Business Recommendations

- Prioritaskan audit order yang mengalami keterlambatan 4 hari atau lebih, karena bucket late_4_7_days, late_8_14_days, dan late_15plus_days menunjukkan asosiasi kuat dengan low rating.
- Evaluasi estimasi pengiriman dan SLA delivery, terutama untuk rute atau segmen yang sering masuk ke delay bucket panjang.
- Buat monitoring seller berbasis low rating contribution, low rating rate, dan late rate agar seller bermasalah dapat dipantau secara lebih objektif.
- Audit kategori produk dengan volume besar dan low rating tinggi, terutama jika kategori tersebut juga memiliki late rate atau avg_delay_days tinggi.
- Review wilayah customer dan seller dengan kombinasi low rating rate dan late rate tinggi untuk memahami indikasi masalah pengalaman regional.
- Jangan hanya menggunakan average review score sebagai KPI utama. Low rating rate, jumlah low rating order, dan late order rate perlu dipantau bersama agar risiko pengalaman buruk tidak tertutup oleh dominasi review score 5.

## 8. Analytical Cautions

- Hasil analisis ini bersifat asosiatif dan belum membuktikan hubungan kausal final antara delivery delay, seller, category, region, dan review score.
- Unknown delivery status perlu ditelusuri lebih lanjut sebelum dijadikan dasar keputusan operasional, karena dapat berasal dari missing timestamp, status order yang tidak lengkap, atau kondisi fulfillment tertentu.
- Analisis seller, category, dan region harus menggunakan threshold volume agar ranking tidak bias oleh segmen dengan order sangat sedikit.
- Review text dan NLP belum menjadi core analysis karena komentar review banyak missing dan sebagian besar teks menggunakan bahasa Portugis.
- Item-level mart dapat menggandakan konteks review pada order multi-item. Oleh karena itu, query segmentasi menggunakan `uniqExact(order_id)` untuk metrik order_count dan low rating count.

## 9. Next Step

- Membuat dashboard Metabase berdasarkan query analytics Day 3.
- Memvalidasi chart dashboard dengan hasil query ClickHouse.
- Menyusun narasi insight utama untuk paper IEEE dan PPT presentasi.
- Menggunakan priority matrix sebagai dasar rekomendasi awal customer experience.

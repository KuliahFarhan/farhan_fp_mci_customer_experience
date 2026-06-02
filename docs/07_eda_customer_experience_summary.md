# 07 EDA Customer Experience Summary

## 1. Tujuan EDA
EDA ini dilakukan untuk mengidentifikasi pola awal dan indikasi faktor-faktor yang berasosiasi dengan skor ulasan pelanggan. Fokus utama adalah menguji hubungan antara performa pengiriman, karakteristik penjual, kategori produk, serta sebaran wilayah terhadap kepuasan pelanggan guna menjawab masalah stagnasi skor review.

## 2. Data Preparation
- **Latest Review per Order**: Menggunakan teknik *drop duplicates* pada `order_id` setelah pengurutan temporal untuk memastikan hanya ulasan terbaru yang dihitung untuk setiap pesanan.
- **Base Tables**:
    - `cx_order_base`: Tabel tingkat pesanan (1 baris = 1 order) yang digunakan untuk metrik agregasi review dan pengiriman.
    - `cx_item_base`: Tabel tingkat produk/item untuk menganalisis performa penjual dan kategori produk secara mendalam.
- **Feature Engineering**: Penambahan kolom temporal (`review_month`), kolom status pengiriman (`late` vs `on_time`), dan pengelompokan keterlambatan (*delay bucket*) dalam hitungan hari.

## 3. Review Score Distribution
Berdasarkan analisis awal (estimasi angka dari data raw):
- **Skor 5** masih mendominasi porsi ulasan pelanggan.
- **Low Rating Rate (<=2)**: Terdapat porsi signifikan (sekitar 10-15%) ulasan yang berada di kategori sangat tidak puas.
- **Rata-rata Skor Review**: Berada di kisaran 4.0 - 4.1.

Interpretasi: Meskipun mayoritas puas, porsi rating rendah yang menetap mengindikasikan adanya masalah sistemik di subset pesanan tertentu.

## 4. Monthly Review Trend
- **Periode**: Data mencakup tren bulanan sepanjang tahun 2016-2018.
- **Stagnasi**: Terlihat indikasi awal bahwa rata-rata skor review bulanan cenderung fluktuatif di rentang yang sempit tanpa menunjukkan tren kenaikan yang signifikan dan berkelanjutan pada periode akhir data.
- **Low Rating Rate**: Persentase rating rendah cenderung stabil, yang memperkuat hipotesis adanya faktor penghambat kepuasan yang belum teratasi.

## 5. Delivery Analysis
- **Delivery Status**: Data menunjukkan asosiasi awal yang kuat antara status `late` dengan skor ulasan yang jauh lebih rendah (seringkali di bawah 3.0) dibandingkan status `on_time_or_early`.
- **Delay Bucket**: Semakin lama durasi keterlambatan (misal bucket `late_15plus_days`), prevalensi rating rendah meningkat secara proporsional.
- **Late Rate**: Sekitar 7-10% pesanan masuk dalam kategori terlambat.

## 6. Seller Analysis
- Terdapat segmen penjual (dengan volume transaksi valid >= 30) yang secara konsisten memiliki `low_rating_2_rate` di atas rata-rata platform.
- Beberapa penjual bermasalah juga memiliki tingkat keterlambatan (*late rate*) yang tinggi, menunjukkan potensi masalah operasional pada pihak penjual.

## 7. Product Category Analysis
- Kategori produk tertentu menunjukkan kerentanan lebih tinggi terhadap rating rendah.
- Kategori dengan dimensi produk besar atau proses logistik kompleks cenderung memiliki `avg_delay_days` yang lebih lama dan skor ulasan yang lebih rendah.

## 8. Region Analysis
- Perbedaan rata-rata skor review terlihat antar negara bagian (`customer_state`).
- Wilayah yang letaknya jauh dari sentra logistik utama menunjukkan tingkat keterlambatan yang lebih tinggi, yang berpotensi menurunkan pengalaman pelanggan di wilayah tersebut.

## 9. Initial Root Cause Signals
Sinyal awal menunjukkan bahwa akar masalah stagnasi skor review berpotensi berkaitan erat dengan:
1. **Logistik**: Keterlambatan pengiriman adalah prediktor kuat untuk rating rendah.
2. **Konsistensi Penjual**: Masalah kualitas layanan pada subset penjual tertentu.
3. **Optimasi Wilayah**: Kendala durasi pengiriman pada rute geografis tertentu.

## 10. Next Step
- Menyusun **Dashboard Planning** berbasis metrik prioritas (review rate, late rate).
- Menentukan KPI Metabase untuk memantau performa harian/mingguan.
- Membuat query SQL analytics untuk pembersihan dan agregasi data ke ClickHouse.
- Menyiapkan pipeline Airflow untuk otomatisasi pengerjaan data.

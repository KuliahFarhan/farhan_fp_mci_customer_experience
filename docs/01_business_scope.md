# 01 Business Scope

## 1. Persona Project

Persona yang digunakan dalam final project ini adalah  **Customer Experience Analyst** .

Sebagai Customer Experience Analyst, fokus analisis diarahkan pada pemahaman faktor-faktor yang memengaruhi pengalaman pelanggan di marketplace DustiniaDelixia Groceria. Metrik utama yang dianalisis adalah  **review score** , karena skor ulasan pelanggan menjadi indikator penting dalam menilai kualitas pengalaman transaksi dan tingkat kepercayaan pembeli terhadap platform.

Project ini tidak hanya bertujuan untuk menampilkan skor review secara agregat, tetapi juga membedah penyebab di balik skor tersebut berdasarkan data transaksi, pengiriman, seller, produk, wilayah, dan review pelanggan.

## 2. Problem Statement

DustiniaDelixia Groceria menghadapi masalah berupa  **review score yang sulit meningkat dan cenderung stagnan** . Selama ini perusahaan hanya memantau skor review secara keseluruhan tanpa memahami secara detail faktor-faktor apa saja yang menyebabkan pelanggan memberikan review rendah.

Masalah utama dalam project ini adalah:

> Perusahaan belum memiliki pemahaman berbasis data mengenai faktor-faktor utama yang menyebabkan review score pelanggan sulit meningkat, khususnya dari sisi pengalaman pengiriman, performa seller, kategori produk, dan karakteristik wilayah pelanggan.

Oleh karena itu, analisis ini dilakukan untuk mengidentifikasi pola dan akar masalah yang memengaruhi review score, sehingga perusahaan dapat menentukan area perbaikan yang paling berdampak terhadap customer experience.

## 3. Business Questions

Project ini akan menjawab beberapa pertanyaan bisnis utama berikut:

1. Bagaimana distribusi review score pelanggan pada DustiniaDelixia Groceria?
2. Apakah review score benar-benar menunjukkan pola stagnan dari waktu ke waktu?
3. Apakah keterlambatan pengiriman berhubungan dengan rendahnya review score pelanggan?
4. Seller, kategori produk, atau wilayah mana yang paling sering berkontribusi terhadap review score rendah?
5. Faktor apa yang paling layak diprioritaskan oleh perusahaan untuk meningkatkan customer experience dan menurunkan risiko review buruk?

## 4. Mandatory Components

Komponen wajib yang harus diselesaikan dalam project ini adalah:

1. **Airflow DAG**
   Digunakan untuk menjalankan pipeline ETL secara end-to-end, mulai dari membaca dataset, melakukan transformasi, hingga memuat data ke database.
2. **ClickHouse**
   Digunakan sebagai database analitik untuk menyimpan data hasil transformasi dan mendukung query dashboard dengan performa yang baik.
3. **Metabase Dashboard**
   Digunakan untuk menyajikan insight kepada audiens non-teknis melalui visualisasi yang menjawab permasalahan bisnis.
4. **GitHub Repository**
   Berisi struktur project, kode, SQL, dokumentasi, README, dan instruksi menjalankan project.
5. **PPT Presentasi**
   Digunakan untuk menjelaskan problem, metode, pipeline, insight, rekomendasi, dan hasil akhir project saat demo.
6. **Paper Format IEEE**
   Digunakan untuk mendokumentasikan latar belakang, metode, hasil analisis, pembahasan, dan kesimpulan project secara akademik.

## 5. Bonus Component

Komponen tambahan yang direncanakan sebagai nilai tambah adalah:

**Customer Experience Simulator berbasis web.**

Web simulator ini akan digunakan untuk mensimulasikan risiko review rendah berdasarkan beberapa faktor seperti status pengiriman, delay pengiriman, seller, kategori produk, dan wilayah. Simulator ini bersifat opsional dan hanya akan dikembangkan setelah seluruh komponen wajib selesai.

Prioritas project tetap berada pada pipeline data, dashboard, analisis bisnis, dan deliverable wajib.

## 6. Scope Boundary

Agar analisis tidak melebar, batasan project ditetapkan sebagai berikut:

1. Analisis difokuskan pada **review score pelanggan** sebagai metrik utama customer experience.
2. Faktor utama yang dianalisis adalah:
   * pengiriman,
   * keterlambatan terhadap estimasi,
   * performa seller,
   * kategori produk,
   * wilayah customer atau seller,
   * tren waktu review score.
3. Analisis tidak difokuskan pada optimasi pembayaran, karena area tersebut lebih sesuai untuk persona Finance Analyst.
4. Analisis tidak difokuskan pada efisiensi biaya distribusi secara mendalam, karena area tersebut lebih sesuai untuk persona Operational Analyst.
5. Model machine learning bukan prioritas utama pada tahap awal. Project ini lebih mengutamakan  **business analytics, root cause analysis, dan dashboard decision support** .
6. Web simulator hanya dikerjakan apabila komponen wajib sudah berjalan dengan baik.

## 7. Expected Final Insight

Insight akhir yang ingin dihasilkan bukan hanya berupa grafik, tetapi jawaban bisnis yang konkret, misalnya:

* Apakah pelanggan yang menerima pesanan terlambat cenderung memberi review lebih rendah?
* Apakah ada seller tertentu yang secara konsisten menghasilkan review buruk?
* Apakah kategori produk tertentu memiliki risiko review rendah lebih tinggi?
* Apakah wilayah tertentu memiliki pengalaman pelanggan yang lebih buruk?
* Area mana yang sebaiknya diprioritaskan perusahaan untuk meningkatkan review score?

## 8. Success Criteria

Project dianggap berhasil apabila mampu menghasilkan:

1. Pipeline data yang dapat berjalan dari Airflow ke ClickHouse tanpa error.
2. Dashboard Metabase yang dapat digunakan saat demo dan mudah dipahami audiens non-teknis.
3. Analisis yang mampu menjelaskan faktor penyebab review score rendah atau stagnan.
4. Rekomendasi bisnis yang konkret dan dapat ditindaklanjuti.
5. Dokumentasi repository yang jelas.
6. Paper dan PPT yang konsisten dengan hasil analisis.
7. Jika waktu memungkinkan, web simulator sebagai implementasi tambahan yang memperkuat nilai project.

## 9. Initial Working Assumption

Sebelum dilakukan eksplorasi data, asumsi awal project adalah bahwa review score rendah kemungkinan dipengaruhi oleh beberapa faktor berikut:

1. Pesanan yang terlambat sampai ke pelanggan.
2. Perbedaan performa antar seller.
3. Kategori produk tertentu yang lebih rentan menimbulkan ketidakpuasan.
4. Perbedaan pengalaman pelanggan antar wilayah.
5. Ekspektasi pelanggan yang tidak terpenuhi akibat gap antara estimasi pengiriman dan pengiriman aktual.

Asumsi ini belum dianggap sebagai kesimpulan. Asumsi akan diuji menggunakan data melalui proses data understanding, data quality check, exploratory data analysis, dan dashboard analytics.

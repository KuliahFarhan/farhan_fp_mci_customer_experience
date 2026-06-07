# Customer Experience Root Cause Dashboard

## Overview

Dashboard Metabase ini dibuat untuk mendukung Final Project MCI dengan persona **Customer Experience Analyst**. Tujuan utama dashboard adalah membantu analisis faktor-faktor yang berasosiasi dengan review score rendah pada DustiniaDelixia Groceria.

Dashboard berfokus pada review score, low rating rate, delivery delay, seller performance, product category, customer/seller region, dan priority segments. Seluruh visualisasi menggunakan data dari ClickHouse database `fp_mci_customer_experience`.

- Dashboard name: Customer Experience Root Cause Dashboard
- Local Metabase URL: `http://localhost:3002`
- Database connection: FP MCI Customer Experience / ClickHouse
- Main database: `fp_mci_customer_experience`

## Dashboard Structure

Dashboard dibagi menjadi dua tab utama.

### 1. Executive Overview

Tab ini memberikan ringkasan kondisi customer experience secara umum dan sinyal utama terkait review rendah.

Komponen:

- KPI - Average Review Score
- KPI - Low Rating Rate <= 2
- KPI - Low Rating Rate <= 3
- KPI - Late Order Rate
- KPI - Average Late Days
- KPI - Reviewed Orders
- Review Score Distribution
- Monthly Average Review Score
- Monthly Low Rating Rate <= 2
- Delivery Status Impact
- Delay Bucket Impact

### 2. Root Cause Segments

Tab ini digunakan untuk mengidentifikasi kandidat root cause berdasarkan seller, kategori produk, wilayah, dan kombinasi risiko delivery.

Komponen:

- Top Problematic Sellers
- Problematic Product Categories
- Customer Region Performance
- Seller Region Performance
- Priority Segments
- Cross Seller Delivery Risk
- Cross Category Delivery Risk

## Main KPI Results

Hasil KPI utama dari mart analytics:

| KPI | Value |
| --- | ---: |
| Total Orders | 99,441 |
| Reviewed Orders | 98,673 |
| Average Review Score | 4.09 |
| Low Rating Rate <= 2 | 14.69% |
| Low Rating Rate <= 3 | 22.93% |
| Late Order Rate | 6.57% |
| Average Delivery Days | 12.5 |
| Average Delay Days | -11.88 |

Catatan: order tanpa review tidak dihitung sebagai review buruk. Review score valid berada pada rentang 1-5.

## Key Business Insights

- Average review score terlihat cukup tinggi, tetapi low rating rate masih signifikan. Hal ini menunjukkan bahwa pengalaman buruk pada sebagian pelanggan tetap perlu dipantau.
- Review score 5 mendominasi distribusi, tetapi review score 1 masih memiliki porsi yang cukup besar.
- Delivery status berasosiasi kuat dengan review rendah. Order late memiliki average review score lebih rendah dibanding order on-time atau early.
- Delay bucket yang lebih panjang menunjukkan indikasi pengalaman pelanggan yang lebih buruk, terutama pada keterlambatan 4 hari atau lebih.
- Unknown delivery status perlu ditelusuri karena memiliki review score rendah dan dapat berkaitan dengan data completeness atau proses fulfillment.
- Seller, category, dan region digunakan sebagai kandidat root cause untuk menentukan prioritas intervensi customer experience.

## How to Access Dashboard Locally

1. Jalankan service Docker Compose.

```bash
docker compose up -d
```

2. Buka Metabase di browser.

```text
http://localhost:3002
```

3. Pastikan Metabase sudah terhubung ke database ClickHouse:

```text
FP MCI Customer Experience / ClickHouse
```

4. Buka dashboard:

```text
Customer Experience Root Cause Dashboard
```

## Notes for Demo

- Mulai demo dari tab **Executive Overview** untuk menjelaskan kondisi umum review score, low rating rate, dan delivery impact.
- Tekankan bahwa average review score saja tidak cukup; low rating rate perlu dipantau sebagai indikator pengalaman buruk.
- Gunakan chart delivery status dan delay bucket untuk menunjukkan indikasi asosiasi antara keterlambatan pengiriman dan review rendah.
- Lanjutkan ke tab **Root Cause Segments** untuk menunjukkan kandidat prioritas berdasarkan seller, category, region, dan cross delivery risk.
- Hindari menyampaikan klaim kausal absolut. Gunakan istilah seperti "berasosiasi", "indikasi", dan "kandidat root cause".

## Screenshots

Tambahkan screenshot dashboard setelah layout final di Metabase selesai.

Rekomendasi screenshot:

- Executive Overview full page
- Root Cause Segments full page
- KPI cards close-up
- Priority Segments table

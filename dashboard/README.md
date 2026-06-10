# Customer Experience Root Cause Dashboard

## Overview

Dashboard Metabase ini dibuat untuk mendukung Final Project MCI 2026 dengan persona **Customer Experience Analyst**. Tujuan utamanya adalah membantu stakeholder non-teknis, termasuk CEO, memahami mengapa review score sulit meningkat dan faktor customer journey apa saja yang berasosiasi dengan low rating.

Dashboard ini tidak hanya memantau angka review secara agregat. Setiap tab disusun untuk bergerak dari executive summary menuju drilldown root-cause candidate berbasis delivery fulfillment, seller/category/region segment, customer order behavior, dan geolocation pattern.

- Dashboard name: Customer Experience Root Cause Dashboard
- Local Metabase URL: `http://localhost:3002`
- Database connection: FP MCI Customer Experience / ClickHouse
- Main database: `fp_mci_customer_experience`
- Main evidence source: `sql/analytics/`, `docs/query_outputs/`, dan `docs/12_dashboard_query_findings.md`

Catatan metodologis: hasil dashboard bersifat asosiatif. Gunakan istilah "berasosiasi", "indikasi", dan "kandidat root cause", bukan klaim kausal absolut.

## Dashboard Structure

Dashboard final terdiri dari 5 tab.

### 1. Executive Overview

Tab ini memberi ringkasan CEO-level mengenai kondisi review score, low rating rate, late order rate, tren bulanan, distribusi review, dan alert awal untuk area yang perlu ditelusuri.

Contoh komponen:

- KPI - Average Review Score
- KPI - Low Rating Rate <= 2
- KPI - Low Rating Rate <= 3
- KPI - Late Order Rate
- KPI - Average Late Days
- KPI - Reviewed Orders
- Review Score Distribution
- Monthly Average Review Score
- Monthly Low Rating Rate <= 2
- Priority CX Segments

### 2. Delivery Fulfillment

Tab ini menelusuri apakah fulfillment dan delivery experience berasosiasi dengan low rating. Fokusnya adalah membandingkan order on-time, late, unknown delivery status, delay bucket, non-delivered order, processing time, dan transit time.

Contoh komponen:

- Delivery Status Impact
- Delay Bucket Impact
- Monthly Late Rate vs Low Rating Rate
- Non-Delivered Orders by Status
- Delivery Phase Breakdown
- Seller Processing Time Bucket
- Transit Time Bucket

### 3. Segment Risk

Tab ini membantu Customer Experience Analyst menemukan kandidat segmen prioritas berdasarkan seller, product category, customer region, seller region, dan kombinasi risk label.

Contoh komponen:

- Top Risk Sellers
- Top Risk Categories
- Customer Region Risk
- Seller Region Risk
- Seller Risk Quadrant
- Category Performance Matrix
- Seller Delivery Risk Label
- Category Delivery Risk Label

### 4. Customer Order Behavior

Tab ini memberi konteks perilaku order agar analisis tidak hanya bergantung pada delivery. Fokusnya adalah repeat order, multi-seller order, item count, order value, payment installment, dan review timing.

Contoh komponen:

- Customer Retention Funnel
- Multi-Seller Order Effect
- Item Count Effect
- Order Value Bucket Risk
- Installment vs Review
- Order Complexity Risk Matrix
- Review Timing After Delivery

### 5. Geolocation

Tab ini menambahkan perspektif spasial secara konservatif. Tujuannya adalah melihat indikasi area, rute, jarak, dan destination zip prefix yang berasosiasi dengan late rate atau low rating, bukan membangun sistem optimasi logistik penuh.

Contoh komponen:

- Customer State Late Hotspot
- Problem Routes
- Distance Bucket Late Rate
- Distance Bucket Low Rating Rate
- ETA Deviation by Destination State
- Destination Zip Prefix Risk
- Worst Destination Zip Prefix Areas

## Main KPI Results

Hasil KPI utama dari query output saat ini:

| KPI                  |  Value |
| -------------------- | -----: |
| Reviewed Orders      | 98,673 |
| Average Review Score |   4.09 |
| Low Rating Rate <= 2 | 14.69% |
| Low Rating Rate <= 3 | 22.93% |
| Late Order Rate      |  6.57% |
| Average Late Days    |  10.62 |

Catatan: order tanpa review tidak dihitung sebagai review buruk. Review score valid berada pada rentang 1-5, dan rate ditampilkan sebagai persentase 0-100.

## How to Interpret Each Tab

### Executive Overview

- **What it shows:** KPI utama, review distribution, monthly trends, anomaly diagnosis, dan priority CX segments.
- **How to read it:** Average review score 4.09 harus dibaca bersama low_rating_2_rate 14.69% dan low_rating_3_rate 22.93%.
- **Decision support:** Gunakan tab ini sebagai entry point sebelum drilldown ke tab operasional.

### Delivery Fulfillment

- **What it shows:** Delivery status, delay bucket, non-delivered status, transit time, seller processing time, dan delivery risk labels.
- **How to read it:** Bandingkan on-time/early, late, dan unknown delivery status. Unknown status adalah operational blind spot, bukan sekadar data quality issue.
- **Decision support:** Monitor late order, unknown delivery status, seller processing 7d+, dan transit >10d.

### Segment Risk

- **What it shows:** Seller, category, customer region, seller region, priority segment, dan risk quadrant.
- **How to read it:** Prioritaskan kombinasi volume dan rate. High rate pada volume kecil tidak selalu lebih penting dibanding kontribusi low rating besar.
- **Decision support:** Buat seller/category watchlist dan audit segmen dengan low-rating contribution tinggi.

### Customer Order Behavior

- **What it shows:** Retention funnel, multi-seller effect, item count, order value, installment, review timing, dan complexity matrix.
- **How to read it:** Order yang lebih kompleks cenderung lebih fragile, terutama multi-seller, multi-item, dan high-value baskets.
- **Decision support:** Buat monitoring untuk complex orders dan escalation rule untuk order bernilai tinggi atau multi-seller.

### Geolocation

- **What it shows:** Distance bucket, problem routes, customer state hotspot, ETA deviation, dan destination ZIP prefix risk.
- **How to read it:** Geolocation digunakan sebagai spatial risk lens. Jangan menyimpulkan geography sebagai penyebab tunggal low rating.
- **Decision support:** Monitor long-distance lanes, SP-origin routes, RJ destination ZIP prefixes, dan destination state dengan ETA deviation tinggi.

## Key Business Insights

- Average review score terlihat cukup tinggi, tetapi low rating rate <= 2 sebesar 14.69% tetap menunjukkan pocket pengalaman buruk yang bermakna.
- Delivery status berasosiasi kuat dengan low rating. Order late memiliki average review score 2.20 dan low rating rate <= 2 sebesar 62.41%.
- Unknown delivery status memiliki average review score 1.75 dan low rating rate <= 2 sebesar 78.02%, sehingga perlu dibaca sebagai operational blind spot sekaligus kandidat isu data/process.
- Delay bucket yang lebih panjang menunjukkan indikasi pengalaman pelanggan yang lebih buruk, terutama mulai late 4-7 hari ke atas.
- Seller, category, region, customer behavior, dan geolocation digunakan sebagai layer drilldown untuk menentukan kandidat root cause dan prioritas investigasi.

## NLP and ML Extensions

NLP dan ML tidak menjadi komponen wajib dashboard Metabase saat ini. Keduanya adalah value-added supporting components:

- NLP membantu membaca teks review Portugis Brazil melalui TF-IDF, BERTopic, dan thematic category analysis.
- ML menyediakan post-fulfillment risk simulator berbasis Calibrated LightGBM, bukan model kausal dan bukan pre-order prediction system.

Insight dari NLP/ML dapat digunakan untuk mendukung interpretasi dashboard, tetapi dashboard final tetap berbasis Airflow, ClickHouse, SQL analytics, dan Metabase.

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

## Screenshots

Screenshot final dashboard tersedia di:

```text
docs/assets/dashbord/
```

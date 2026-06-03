# FP MCI 2026 - Customer Experience Analysis

Final Project Lab MCI 2026 dengan persona  **Customer Experience Analyst** . Project ini berfokus pada analisis customer experience di marketplace DustiniaDelixia Groceria dengan metrik utama berupa **review score** pelanggan.

## 1. Project Overview

DustiniaDelixia Groceria merupakan marketplace e-commerce yang memiliki data transaksi, pengiriman, seller, produk, pelanggan, pembayaran, dan review. Permasalahan bisnis utama yang dianalisis adalah mengapa  **review score pelanggan sulit meningkat atau tidak menunjukkan kenaikan yang konsisten** .

Project ini membangun pipeline analitik end-to-end menggunakan  **Airflow** ,  **ClickHouse** , dan **Metabase** untuk mengolah data mentah menjadi mart analytics yang siap digunakan untuk dashboard dan pengambilan keputusan bisnis.

Fokus utama analisis:

* review score pelanggan,
* tren review bulanan,
* low rating rate,
* delivery delay,
* seller performance,
* product category,
* customer/seller region.

## 2. Persona

Persona yang digunakan adalah  **Customer Experience Analyst** .

Sebagai Customer Experience Analyst, analisis diarahkan untuk memahami faktor-faktor yang berhubungan dengan pengalaman pelanggan, terutama pada order dengan review rendah. Output utama project bukan hanya visualisasi data, tetapi insight yang dapat membantu tim bisnis menentukan prioritas perbaikan customer experience.

## 3. Business Questions

Project ini menjawab beberapa pertanyaan bisnis utama:

1. Bagaimana distribusi review score pelanggan?
2. Apakah review score tidak meningkat konsisten dari waktu ke waktu?
3. Apakah delivery delay berasosiasi dengan review rendah?
4. Seller mana yang paling berkontribusi terhadap review rendah?
5. Kategori produk mana yang memiliki risiko review rendah tinggi?
6. Wilayah customer atau seller mana yang perlu diperhatikan?
7. Area mana yang paling layak diprioritaskan untuk meningkatkan customer experience?

## 4. Tech Stack

Project ini menggunakan:

* **Apache Airflow** untuk orkestrasi pipeline ETL.
* **ClickHouse** sebagai analytical database.
* **Metabase** untuk dashboard business intelligence.
* **Python** untuk data loading dan scripting.
* **Docker Compose** untuk menjalankan service lokal.
* **Pandas** untuk pembacaan dan preprocessing CSV.
* **clickhouse-connect** untuk koneksi Python ke ClickHouse.

## 5. Repository Structure

```text
fp-mci-customer-experience/
├── app/
├── dags/
│   └── dag_customer_experience_pipeline.py
├── dashboard/
├── data/
│   ├── raw/
│   ├── processed/
│   └── sample/
├── docs/
├── notebooks/
├── paper/
├── presentation/
├── scripts/
│   └── load_csv_to_clickhouse.py
├── sql/
│   ├── ddl/
│   ├── etl/
│   └── analytics/
├── docker-compose.yml
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

Keterangan folder:

| Folder              | Fungsi                                                                                |
| ------------------- | ------------------------------------------------------------------------------------- |
| `app/`            | Folder untuk implementasi web atau simulator tambahan jika dikembangkan.              |
| `dags/`           | Berisi DAG Airflow untuk menjalankan pipeline ETL.                                    |
| `dashboard/`      | Catatan atau konfigurasi dashboard Metabase.                                          |
| `data/raw/`       | Tempat menyimpan CSV mentah secara lokal.                                             |
| `data/processed/` | Tempat menyimpan output intermediate atau hasil agregasi lokal.                       |
| `docs/`           | Dokumentasi project, scope, data quality, EDA, dashboard plan, dan architecture plan. |
| `notebooks/`      | Notebook eksplorasi data dan EDA.                                                     |
| `paper/`          | Draft paper IEEE dan referensi.                                                       |
| `presentation/`   | File presentasi project.                                                              |
| `scripts/`        | Script Python untuk loading data ke ClickHouse.                                       |
| `sql/ddl/`        | SQL untuk membuat database dan tabel.                                                 |
| `sql/etl/`        | SQL transformasi dari staging ke mart.                                                |
| `sql/analytics/`  | SQL analytics untuk kebutuhan dashboard.                                              |

## 6. Dataset Setup

Dataset mentah tidak disertakan langsung di repository. Letakkan seluruh file CSV ke folder:

```text
data/raw/
```

File wajib untuk pipeline MVP:

```text
orders.csv
order_reviews.csv
order_items.csv
customers.csv
sellers.csv
products.csv
category_translation.csv
order_payments.csv
```

File yang belum digunakan pada MVP Day 2:

```text
geolocation.csv
mql.csv
closed_deals.csv
```

Catatan:

* `geolocation.csv` belum digunakan pada MVP karena analisis wilayah awal cukup menggunakan `customer_city`, `customer_state`, `seller_city`, dan `seller_state`.
* `mql.csv` dan `closed_deals.csv` lebih relevan untuk marketing/seller funnel, bukan fokus utama persona Customer Experience Analyst.
* Folder `data/raw/` dan `data/processed/` sebaiknya tidak dipush ke GitHub jika berisi data besar.

## 7. Environment Setup

Salin file `.env.example` menjadi `.env`.

Contoh konfigurasi lokal:

```env
CLICKHOUSE_HOST=localhost
CLICKHOUSE_PORT=8123
CLICKHOUSE_DATABASE=fp_mci_customer_experience
CLICKHOUSE_USER=default
CLICKHOUSE_PASSWORD=password

AIRFLOW_UID=50000
```

Install dependency lokal jika ingin menjalankan script Python dari terminal:

```bash
pip install -r requirements.txt
```

Jalankan seluruh service:

```bash
docker compose up -d
```

Cek status container:

```bash
docker compose ps
```

Cek koneksi ClickHouse:

```bash
curl --user default:password "http://localhost:8123/?query=SELECT%201"
```

Output yang diharapkan:

```text
1
```

## 8. Service Access

Service lokal yang digunakan:

| Service         | URL                       |
| --------------- | ------------------------- |
| Airflow UI      | `http://localhost:8085` |
| ClickHouse HTTP | `http://localhost:8123` |
| Metabase UI     | `http://localhost:3000` |

Catatan: Airflow menggunakan port `8085` karena port `8080` lokal sudah digunakan service lain.

## 9. Running the ETL Pipeline

Pipeline dapat dijalankan dengan dua cara: melalui Airflow atau manual.

### Option A — Airflow DAG

1. Pastikan Docker sudah berjalan:

```bash
docker compose up -d
```

2. Buka Airflow UI:

```text
http://localhost:8085
```

3. Login ke Airflow.
4. Cari DAG:

```text
dag_customer_experience_pipeline
```

5. Aktifkan DAG dengan klik  **Unpause** .
6. Klik **Trigger DAG** untuk menjalankan pipeline end-to-end.

DAG akan menjalankan proses:

```text
validate raw files
→ create ClickHouse database
→ create staging tables
→ load CSV to staging
→ create mart tables
→ build customer experience order mart
→ build customer experience item mart
→ build monthly review mart
→ build delivery performance mart
→ validate pipeline outputs
```

### Option B — Manual Script and SQL

Jalankan DDL database:

```bash
docker exec -i fp_mci_clickhouse clickhouse-client \
  --user default \
  --password password \
  < sql/ddl/01_create_database.sql
```

Jalankan DDL staging:

```bash
docker exec -i fp_mci_clickhouse clickhouse-client \
  --user default \
  --password password \
  < sql/ddl/02_create_staging_tables.sql
```

Load CSV ke staging:

```bash
python scripts/load_csv_to_clickhouse.py
```

Jalankan DDL mart:

```bash
docker exec -i fp_mci_clickhouse clickhouse-client \
  --user default \
  --password password \
  < sql/ddl/03_create_mart_tables.sql
```

Bangun mart order-level:

```bash
docker exec -i fp_mci_clickhouse clickhouse-client \
  --user default \
  --password password \
  < sql/etl/02_build_customer_experience_orders.sql
```

Bangun mart item-level:

```bash
docker exec -i fp_mci_clickhouse clickhouse-client \
  --user default \
  --password password \
  < sql/etl/03_build_customer_experience_items.sql
```

Bangun mart review bulanan:

```bash
docker exec -i fp_mci_clickhouse clickhouse-client \
  --user default \
  --password password \
  < sql/analytics/01_monthly_review_trend.sql
```

Bangun mart delivery performance:

```bash
docker exec -i fp_mci_clickhouse clickhouse-client \
  --user default \
  --password password \
  < sql/analytics/02_delivery_performance.sql
```

## 10. Pipeline Output

### Staging Tables

Staging tables menyimpan data mendekati bentuk CSV mentah:

```text
stg_orders
stg_order_reviews
stg_order_items
stg_customers
stg_sellers
stg_products
stg_category_translation
stg_order_payments
```

### Analytics Mart Tables

Mart tables digunakan untuk analisis dan dashboard:

```text
mart_customer_experience_orders
mart_customer_experience_items
mart_monthly_review
mart_delivery_performance
```

Fungsi mart:

| Mart Table                          | Granularity                    | Fungsi                                                   |
| ----------------------------------- | ------------------------------ | -------------------------------------------------------- |
| `mart_customer_experience_orders` | One row per order              | Analisis review, delivery, dan customer region.          |
| `mart_customer_experience_items`  | One row per order item         | Analisis seller dan product category.                    |
| `mart_monthly_review`             | One row per month              | Tren average review score dan low rating rate.           |
| `mart_delivery_performance`       | Delivery status + delay bucket | Analisis hubungan delivery performance dan review score. |

## 11. Validation Result

Validasi terakhir pipeline Day 2:

| Check                                              |  Result |
| -------------------------------------------------- | ------: |
| `stg_orders`                                     |  99,441 |
| `stg_order_reviews`                              |  99,224 |
| `stg_order_items`                                | 112,650 |
| `mart_customer_experience_orders`                |  99,441 |
| `mart_customer_experience_items`                 | 112,650 |
| `review_score IS NULL`pada order-level mart      |     768 |
| Row palsu `1970-01-01`di `mart_monthly_review` |       0 |
| `sum(reviewed_orders)`di `mart_monthly_review` |  98,673 |

Catatan:

* Terdapat 768 order tanpa review.
* Order tanpa review tetap dipertahankan di `mart_customer_experience_orders`.
* Order tanpa review tidak dihitung dalam `mart_monthly_review`.
* `review_score = 0` tidak digunakan karena review score valid berada pada rentang 1–5.
* Perbaikan ini mencegah order tanpa review dihitung sebagai low rating palsu.

Contoh query validasi:

```bash
curl --user default:password "http://localhost:8123/?query=SELECT%20count()%20FROM%20fp_mci_customer_experience.mart_customer_experience_orders%20WHERE%20review_score%20IS%20NULL"
```

```bash
curl --user default:password "http://localhost:8123/?query=SELECT%20*%20FROM%20fp_mci_customer_experience.mart_monthly_review%20WHERE%20review_month%20=%20'1970-01-01'"
```

```bash
curl --user default:password "http://localhost:8123/?query=SELECT%20sum(reviewed_orders)%20FROM%20fp_mci_customer_experience.mart_monthly_review"
```

## 12. Documentation Progress

Dokumentasi yang sudah dibuat:

| File                                           | Isi                                                         |
| ---------------------------------------------- | ----------------------------------------------------------- |
| `docs/01_business_scope.md`                  | Scope bisnis dan persona project.                           |
| `docs/02_hypothesis_mapping.md`              | Pemetaan hipotesis analisis customer experience.            |
| `docs/03_dashboard_plan.md`                  | Rencana KPI, chart, filter, dan storyline dashboard.        |
| `docs/04_architecture_plan.md`               | Desain arsitektur CSV → Airflow → ClickHouse → Metabase. |
| `docs/05_data_quality_report.md`             | Ringkasan data quality check.                               |
| `docs/06_literature_scoping.md`              | Ringkasan literature scouting.                              |
| `docs/07_eda_customer_experience_summary.md` | Ringkasan EDA customer experience.                          |

## 13. Current Project Status

| Task                                  | Status      |
| ------------------------------------- | ----------- |
| Day 1 planning and data understanding | Done        |
| Business scope                        | Done        |
| Data quality check                    | Done        |
| Literature scouting                   | Done        |
| Hypothesis mapping                    | Done        |
| Customer experience EDA               | Done        |
| Dashboard planning                    | Done        |
| Architecture planning                 | Done        |
| Docker infrastructure                 | Done        |
| ClickHouse staging                    | Done        |
| CSV loading to ClickHouse             | Done        |
| Customer experience marts             | Done        |
| Airflow DAG MVP                       | Done        |
| Pipeline validation                   | Done        |
| Metabase dashboard                    | In Progress |
| Paper IEEE                            | Not Started |
| PPT presentation                      | Not Started |
| Optional web simulator                | Not Started |

## 14. Next Step

Day 3 akan difokuskan pada:

1. SQL analytics lanjutan untuk root cause analysis.
2. Analisis seller performance.
3. Analisis product category.
4. Analisis customer/seller region.
5. Penyusunan insight bisnis utama.
6. Persiapan query untuk Metabase dashboard.
7. Penyusunan rekomendasi awal berbasis data.

## 15. Notes on Optional Enhancement

NLP, machine learning, dan web simulator belum menjadi komponen utama pada MVP. Fitur tersebut dapat dikembangkan sebagai tambahan setelah pipeline, dashboard, paper, dan PPT selesai.

Prioritas utama project tetap:

```text
Airflow → ClickHouse → Metabase → Business Insight
```

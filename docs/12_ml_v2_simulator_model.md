# 12 ML v2 Simulator Model

## 1. Objective

ML v2 dibuat sebagai model risiko untuk **Customer Experience Simulator**. Model ini mengestimasi probabilitas sebuah order mendapat review rendah, sehingga tim dapat melakukan monitoring risiko customer experience berbasis fitur structured transaction, delivery, product, customer, seller, dan payment.

Model ini bukan sistem keputusan otomatis. Output model digunakan sebagai risk estimator dan perlu dibaca bersama dashboard root cause.

## 2. Prediction Target

Target model:

```text
low_rating = 1 jika review_score <= 2
low_rating = 0 jika review_score >= 3
```

Order dengan `review_score` kosong dikeluarkan dari supervised training. Pada dataset training v2, terdapat 98,673 order dengan review valid, terdiri dari 84,179 non-low-rating dan 14,494 low-rating.

## 3. Data Source

Dataset diambil dari ClickHouse database `fp_mci_customer_experience`.

Sumber data:

- `mart_customer_experience_orders` untuk fitur order, customer, delivery, dan target.
- `mart_customer_experience_items` untuk agregasi product, seller, price, dan freight per order.
- `stg_orders` untuk fitur timestamp tambahan seperti approval delay, seller handling, carrier delivery, dan estimated delivery window.
- `stg_order_payments` untuk agregasi payment per order.

Query training bersifat read-only dan tidak mengubah data ClickHouse.

## 4. Feature Set

Fitur numerik:

- `delivery_days`
- `delay_days`
- `is_late_delivery`
- `approval_delay_days`
- `seller_handling_days`
- `carrier_delivery_days`
- `estimated_delivery_window_days`
- `purchase_month`
- `purchase_day_of_week`
- `is_weekend_purchase`
- `item_count`
- `seller_count`
- `total_price`
- `total_freight`
- `avg_price`
- `avg_freight`
- `freight_to_price_ratio`
- `total_payment_value`
- `max_payment_installments`
- `payment_method_count`

Fitur kategorikal:

- `delivery_status`
- `delay_bucket`
- `main_payment_type`
- `main_product_category`
- `customer_state`
- `seller_state`
- `same_customer_seller_state`
- `customer_city`

Kolom high-cardinality seperti `customer_city` dan `main_product_category` dikelompokkan di dalam pipeline model menggunakan top training levels dan label `other`. Dengan demikian, artifact model dapat menerima input satu baris dari simulator tanpa preprocessing manual di luar pipeline.

## 5. Leakage Prevention

Review text tidak digunakan sebagai fitur. Kolom seperti `review_comment_title` dan `review_comment_message` muncul setelah pelanggan memberi review, sehingga penggunaannya akan menimbulkan leakage untuk prediksi risiko low rating.

Model juga tidak menggunakan `review_score`, `is_low_rating_2`, `is_low_rating_3`, atau fitur turunan rating sebagai input prediksi. Target hanya dipakai untuk supervised training dan evaluasi.

## 6. Model Candidates

Model yang dibandingkan:

| Model | Purpose |
| --- | --- |
| DummyClassifier | Sanity baseline untuk membandingkan model aktual dengan prior kelas mayoritas. |
| Logistic Regression | Baseline interpretable dengan `class_weight="balanced"`. |
| Random Forest | Stable fallback model dengan `class_weight="balanced_subsample"`. |
| HistGradientBoostingClassifier | Fallback boosting model dari scikit-learn. |
| LightGBM | Candidate boosting model v2.1 dengan konfigurasi konservatif. |

LightGBM tersedia di environment lokal dan ditambahkan sebagai dependency project melalui `requirements.txt`. XGBoost tidak ditambahkan karena tidak termasuk scope ML v2.

## 7. Evaluation Results

Evaluasi menggunakan stratified train-test split 80:20 dengan `random_state=42`.

| Model | ROC-AUC | PR-AUC | Precision Low Rating | Recall Low Rating | F1 Low Rating | Brier Score |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| DummyClassifier | 0.5000 | 0.1469 | 0.0000 | 0.0000 | 0.0000 | 0.1253 |
| Logistic Regression | 0.7892 | 0.5175 | 0.4965 | 0.5571 | 0.5250 | 0.1554 |
| Random Forest | 0.7858 | 0.5445 | 0.5267 | 0.5381 | 0.5323 | 0.1558 |
| HistGradientBoostingClassifier | 0.7974 | 0.5561 | 0.4669 | 0.5961 | 0.5236 | 0.1499 |
| LightGBM | 0.7960 | 0.5570 | 0.4713 | 0.5885 | 0.5234 | 0.1459 |

Setelah evaluasi v2.1, LightGBM dipilih sebagai model final karena memberikan PR-AUC yang sedikit lebih baik, Brier score sebelum kalibrasi yang lebih baik, dan recall threshold yang lebih tinggi setelah kalibrasi. Perubahan ini tetap dibaca sebagai peningkatan model prediktif/asosiatif, bukan bukti kausal.

Perbandingan khusus HistGradientBoosting dan LightGBM disimpan pada:

```text
models/low_rating_lgbm_comparison_v2.json
```

## 8. Calibration and Threshold

Karena simulator akan menampilkan skor risiko, model final dikalibrasi menggunakan `CalibratedClassifierCV` dengan metode sigmoid.

Hasil kalibrasi:

| Metric | Before Calibration | After Calibration |
| --- | ---: | ---: |
| Brier Score | 0.1459 | 0.0889 |

Threshold kandidat yang dievaluasi: 0.30, 0.35, 0.40, 0.45, dan 0.50. Threshold final dipilih pada **0.30** karena memberikan recall tertinggi di antara threshold praktis dengan precision yang masih layak untuk monitoring customer experience.

Pada threshold 0.30:

- Precision low rating: 0.6038
- Recall low rating: 0.5116
- F1 low rating: 0.5539
- Predicted positive rate: 0.1244

Risk level untuk simulator:

- Low: risk < 25%
- Medium: 25% <= risk < 30%
- High: risk >= 30%

## 9. Final Artifacts

Artifact ML v2:

- `models/low_rating_model_v2.pkl`
- `models/low_rating_metrics_v2.json`
- `models/low_rating_feature_schema_v2.json`
- `models/low_rating_thresholds_v2.json`
- `models/low_rating_sample_input_v2.json`
- `models/low_rating_model_card_v2.md`
- `models/low_rating_lgbm_comparison_v2.json`

Helper inferensi:

```bash
python scripts/predict_low_rating_v2.py
```

Untuk input JSON custom:

```bash
python scripts/predict_low_rating_v2.py --input path/to/input.json
```

Output helper berisi estimated low-rating risk percentage dan risk level: Low, Medium, atau High.

## 10. Simulator Usage

Web simulator dapat memuat `low_rating_model_v2.pkl`, membaca `low_rating_thresholds_v2.json`, dan menerima payload sesuai schema `low_rating_feature_schema_v2.json`.

Model sudah menyertakan preprocessing di dalam pipeline, termasuk:

- numeric imputation dan scaling,
- categorical imputation,
- high-cardinality category grouping,
- one-hot encoding,
- calibrated classifier.

Karena pipeline lengkap disimpan dalam artifact, simulator tidak perlu membuat preprocessing manual selain memastikan nama field input sesuai schema.

## 11. Limitations

- Model bersifat prediktif/asosiatif, bukan model kausal.
- Fitur delivery seperti delay days dan delivery status tersedia setelah proses pengiriman, sehingga model lebih cocok untuk post-delivery risk monitoring atau pre-review intervention.
- Model belum menggunakan historical seller risk, historical category risk, atau NLP.
- Review text dikeluarkan untuk mencegah leakage dan akan dianalisis terpisah pada fase NLP/root-cause analysis.
- Threshold 0.30 dipilih untuk kebutuhan monitoring, bukan keputusan otomatis.
- Class imbalance tetap perlu diperhatikan karena low rating adalah kelas minoritas.

## 12. Next Step

- Integrasikan artifact model ke Customer Experience Simulator.
- Tambahkan tampilan risk probability dan risk level Low/Medium/High.
- Bandingkan output model dengan rule-based risk dari dashboard.
- Siapkan ML v3 dengan historical seller/category risk jika diperlukan.
- Jalankan NLP review text sebagai analisis root-cause terpisah, bukan fitur prediksi risiko ML v2.

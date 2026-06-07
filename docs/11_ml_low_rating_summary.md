# 11 ML Low Rating Prediction Summary

## Objective

Eksplorasi Machine Learning ini bertujuan membangun baseline model untuk memprediksi risiko sebuah order mendapat review rendah. Model digunakan sebagai pendukung analisis Customer Experience, terutama untuk membaca indikasi risiko low rating berdasarkan fitur delivery, seller/product summary, dan region.

Model ini tidak menggantikan dashboard root cause, tetapi melengkapi analisis dengan pendekatan prediktif sederhana.

## Target Definition

Target yang digunakan adalah:

```text
is_low_rating_2 = 1 jika review_score <= 2, else 0
```

Training hanya menggunakan order yang memiliki review valid, yaitu `review_score IS NOT NULL`. Kolom `review_score`, `is_low_rating_2`, `is_low_rating_3`, dan turunan rating lain tidak digunakan sebagai fitur agar tidak terjadi target leakage.

## Dataset

Dataset diambil dari ClickHouse database `fp_mci_customer_experience`.

Sumber utama:

- `mart_customer_experience_orders` sebagai base satu baris per order.
- `mart_customer_experience_items` sebagai sumber agregasi item, seller, product category, price, dan freight per order.

Query training bersifat read-only dan tidak mengubah data ClickHouse.

## Features

Fitur numerik kandidat:

- `delivery_days`
- `delay_days`
- `item_count`
- `seller_count`
- `total_price`
- `total_freight`
- `avg_price`
- `avg_freight`

Fitur kategorikal kandidat:

- `delivery_status`
- `delay_bucket`
- `customer_state`
- `customer_city`
- `main_product_category`
- `main_seller_state`

Kode training dibuat robust dengan mengecek kolom yang tersedia dan hanya memakai fitur yang benar-benar ada pada dataset hasil query.

## Model Candidates

Dua baseline model digunakan:

- Logistic Regression dengan `class_weight="balanced"` dan `max_iter=1000`.
- Random Forest dengan `n_estimators=200`, `max_depth=12`, `random_state=42`, dan `class_weight="balanced"`.

## Evaluation Metrics

Evaluasi menggunakan train-test split 80:20 dengan `random_state=42` dan stratifikasi target.

Metrik yang dicatat:

| Model | Accuracy | Precision | Recall | F1-score | ROC-AUC |
| --- | ---: | ---: | ---: | ---: | ---: |
| Logistic Regression | 0.8532 | 0.5002 | 0.5574 | 0.5272 | 0.7882 |
| Random Forest | 0.8748 | 0.5857 | 0.5043 | 0.5420 | 0.7823 |

Karena low rating adalah kelas minoritas, interpretasi model tidak hanya berfokus pada accuracy. Recall dan precision untuk kelas `1` perlu diperhatikan agar risiko review rendah tidak tertutup oleh dominasi kelas non-low-rating.

## Best Model

Script `scripts/train_low_rating_model.py` memilih model terbaik berdasarkan F1-score, dengan recall kelas `1` dan ROC-AUC sebagai pertimbangan tambahan. Pada baseline ini, model terbaik adalah **Random Forest** karena memiliki F1-score kelas low rating lebih tinggi dibanding Logistic Regression.

Logistic Regression memiliki recall kelas `1` yang sedikit lebih tinggi, sehingga tetap berguna sebagai pembanding jika tujuan bisnis lebih menekankan penangkapan sebanyak mungkin order berisiko. Random Forest dipilih sebagai baseline utama karena memberikan trade-off precision dan F1-score yang lebih baik.

Setelah training, model terbaik disimpan ke:

```text
models/low_rating_model.pkl
```

Ringkasan metrik disimpan ke:

```text
models/low_rating_metrics.json
```

## Key Predictive Signals

Sinyal prediktif yang muncul kuat pada baseline Random Forest terutama berkaitan dengan delivery:

- `delivery_status_on_time_or_early`
- `delay_bucket_early_or_on_time`
- `delivery_status_late`
- `delay_days`
- `delivery_days`
- `delivery_status_unknown`
- `delay_bucket_unknown`
- `delay_bucket_late_8_14_days`
- `delay_bucket_late_15plus_days`

Fitur tambahan seperti `item_count`, `seller_count`, `total_freight`, `avg_freight`, dan beberapa kategori/region juga muncul sebagai sinyal pendukung, tetapi kontribusinya lebih kecil dibanding fitur delivery.

Jika feature importance menunjukkan delay bucket, delivery status, atau delay days sebagai fitur kuat, hal tersebut perlu dibaca sebagai indikasi asosiasi prediktif antara performa pengiriman dan risiko low rating.

## Business Interpretation

Baseline model ini dapat digunakan sebagai early warning sederhana setelah proses pengiriman atau sebelum review masuk. Order dengan risiko tinggi dapat diprioritaskan untuk monitoring customer experience, follow-up customer support, atau evaluasi SLA.

Dalam konteks dashboard, model ini dapat dibandingkan dengan rule-based risk dari delivery delay, seller contribution, product category, dan region. Tujuannya adalah membantu tim Customer Experience melihat segmen yang perlu ditindaklanjuti lebih cepat.

## Limitations

- Model bersifat prediktif/asosiatif, bukan bukti kausal.
- Fitur delivery baru tersedia setelah proses pengiriman, sehingga model ini lebih cocok untuk post-delivery risk monitoring atau pre-review intervention, bukan prediksi saat order baru dibuat.
- Review comment dan NLP belum dimasukkan karena komentar banyak missing dan sebagian besar teks menggunakan bahasa Portugis.
- Class imbalance perlu diperhatikan karena proporsi low rating lebih kecil dibanding non-low-rating.
- Model baseline belum melalui hyperparameter tuning mendalam.

## Next Step

- Integrasi ke web simulator sebagai Customer Experience Risk Simulator.
- Tambahkan threshold risk level Low, Medium, dan High.
- Bandingkan hasil model dengan rule-based risk dari dashboard.
- Evaluasi ulang model jika fitur pre-delivery atau customer support data tersedia.

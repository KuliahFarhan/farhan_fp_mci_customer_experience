# 14 NLP and ML Extension Summary

## Purpose

Dokumen ini merangkum NLP dan ML sebagai **value-added supporting components** untuk FP MCI 2026. Core project tetap Airflow, ClickHouse, dan Metabase dashboard. NLP dan ML membantu interpretasi root-cause analysis, tetapi tidak menggantikan pipeline BI utama.

## NLP Extension

NLP digunakan untuk **Portuguese review text mining** pada review comment pelanggan. Analisis ini mendukung interpretasi dashboard dengan membaca tema keluhan yang tidak selalu terlihat dari metrik struktural.

Metode utama:

- preprocessing teks bahasa Portugis Brazil;
- TF-IDF low vs high score keywords;
- BERTopic topic modeling;
- thematic category analysis berbasis domain e-commerce;
- representative review extraction.

Key facts:

- Dataset sumber: `order_reviews.csv`.
- Total reviews: 99,224.
- Text-bearing reviews after filtering: 28,722 atau sekitar 28.9%.
- Overall review average: 4.086.
- Low reviews score 1-2: 14,575 atau sekitar 14.7%.
- High reviews score 4-5: 76,470 atau sekitar 77.1%.
- BERTopic topics: 34.

Generated local outputs:

- `data/processed/nlp/dataset_enriched.csv`
- `data/processed/nlp/insights_bisnis.txt`
- `data/processed/nlp/representative_reviews.json`
- `data/processed/nlp/tabel_skor_per_bertopic.csv`
- `data/processed/nlp/tabel_skor_per_kategori.csv`
- `data/processed/nlp/tabel_tfidf_high.csv`
- `data/processed/nlp/tabel_tfidf_low.csv`
- `data/processed/nlp/tabel_tren_bulanan.csv`
- `docs/assets/nlp/`

Interpretation notes:

- Low-rating text frequently contains delivery/prazo/received/not-received signals.
- Other complaint themes include product quality, seller/service issues, wrong or incomplete item, packaging, and miscellaneous complaint patterns.
- Because many reviews do not contain text, NLP findings should be used as supporting qualitative evidence, not as the sole source of truth.

## ML Extension

ML digunakan sebagai **post-fulfillment risk simulator** untuk memperkirakan risiko low rating setelah sinyal fulfillment/delivery tersedia.

Model role:

- supporting component;
- not a causal model;
- not a pre-order prediction system;
- not a replacement for Airflow, ClickHouse, and Metabase.

Final model:

- Calibrated LightGBM with isotonic calibration.
- Target: `low_rating = 1` jika `review_score <= 2`, selain itu 0.
- Dataset: 95,832 delivered orders with review.
- Feature count: 24 structured features.
- Split: 60% train, 20% calibration-validation, 20% final test.
- Threshold: 0.30.

Final test metrics:

| Metric | Value |
| --- | ---: |
| ROC-AUC | 0.7595 |
| Average Precision | 0.4623 |
| Precision @0.30 | 0.5882 |
| Recall @0.30 | 0.4020 |
| F1 @0.30 | 0.4776 |

Tracked artifacts:

- `models/calibrated_lgbm_low_rating.pkl`
- `models/preprocessor.pkl`
- `models/feature_schema.json`
- `models/sample_inputs.json`
- `models/predict_risk.py`
- `docs/assets/ml/`

Limitations:

- Review text is excluded from model features to keep NLP separate and reduce leakage risk.
- Historical aggregate features based on review score are excluded.
- The model uses post-fulfillment signals, so it should not be described as a pre-order predictor.
- Performance is moderate and suitable for risk simulation, not for fully automated operational decisions.
- Model artifacts are pickle/joblib files and should be loaded with compatible scikit-learn/joblib versions.

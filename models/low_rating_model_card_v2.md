# Low Rating Model v2 Card

## Model Purpose
Model ini mengestimasi risiko sebuah order mendapat review rendah untuk Customer Experience Simulator.

## Target
`low_rating = 1` jika `review_score <= 2`, dan `0` jika `review_score >= 3`. Order tanpa review dikeluarkan dari supervised training.

## Features
Model menggunakan fitur structured transaction, delivery, product, customer, seller, dan payment. Review text tidak digunakan karena muncul setelah pelanggan memberi review.

## Leakage Prevention
Fitur `review_score`, review-derived flags, dan review comments tidak digunakan sebagai fitur prediksi.

## Metrics
Final model: `lightgbm`
Selected threshold: `0.30`
ROC-AUC: `0.7990`
PR-AUC: `0.5610`
Recall low rating: `0.5116`
Precision low rating: `0.6038`
F1 low rating: `0.5539`
Brier score: `0.0889`

## Safe Claims
- Model dapat digunakan sebagai risk estimator untuk monitoring customer experience.
- Output model bersifat prediktif/asosiatif dan perlu dibaca bersama dashboard root cause.

## Unsafe Claims
- Jangan menyatakan model membuktikan penyebab review rendah secara kausal.
- Jangan menggunakan skor risiko sebagai keputusan otomatis tanpa validasi bisnis.

## Limitations
- Banyak fitur delivery tersedia setelah pengiriman, sehingga model lebih cocok untuk post-delivery monitoring atau pre-review intervention.
- Model belum memakai historical seller risk, historical category risk, atau NLP.
- Class imbalance tetap perlu diperhatikan.

# Models

Folder ini digunakan untuk menyimpan artifact Machine Learning baseline untuk prediksi risiko low rating.

Artifact yang dihasilkan oleh script training:

- `low_rating_model.pkl`: pipeline model terbaik yang sudah mencakup preprocessing dan classifier.
- `low_rating_metrics.json`: ringkasan metrik evaluasi, fitur yang digunakan, dan feature importance.
- `low_rating_model_v2.pkl`: pipeline ML v2 untuk Customer Experience Simulator.
- `low_rating_metrics_v2.json`: metrik evaluasi semua kandidat model v2.
- `low_rating_feature_schema_v2.json`: daftar fitur, tipe fitur, contoh nilai kategori, dan sample input.
- `low_rating_thresholds_v2.json`: analisis threshold dan threshold final untuk risk level.
- `low_rating_sample_input_v2.json`: contoh payload valid untuk inferensi simulator.
- `low_rating_model_card_v2.md`: model card singkat untuk model simulator.
- `low_rating_lgbm_comparison_v2.json`: perbandingan khusus HistGradientBoosting dan LightGBM untuk ML v2.1.

File model binary seperti `.pkl` dan `.joblib` diabaikan oleh `.gitignore` agar artifact besar tidak ikut commit. Metrics JSON boleh disimpan sebagai catatan hasil eksperimen bila ukurannya kecil.

Model ini bersifat baseline prediktif/asosiatif untuk monitoring risiko customer experience, bukan bukti kausal final.

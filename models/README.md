# Models

Folder ini digunakan untuk menyimpan artifact Machine Learning baseline untuk prediksi risiko low rating.

Artifact yang dihasilkan oleh script training:

- `low_rating_model.pkl`: pipeline model terbaik yang sudah mencakup preprocessing dan classifier.
- `low_rating_metrics.json`: ringkasan metrik evaluasi, fitur yang digunakan, dan feature importance.

File model binary seperti `.pkl` dan `.joblib` diabaikan oleh `.gitignore` agar artifact besar tidak ikut commit. Metrics JSON boleh disimpan sebagai catatan hasil eksperimen bila ukurannya kecil.

Model ini bersifat baseline prediktif/asosiatif untuk monitoring risiko customer experience, bukan bukti kausal final.

# 06 Literature Scoping

## 1. Purpose

Literature scouting dilakukan sejak tahap awal (Day 1) untuk memastikan bahwa metode analisis dan hipotesis yang diajukan memiliki landasan teoretis dan empiris yang kuat. Hal ini mencegah pengambilan kesimpulan yang bersifat spekulatif serta memastikan arah proyek selaras dengan standar industri dan akademis sebelum masuk ke tahap EDA dan pengembangan pipeline.

## 2. Literature Themes

### Customer Satisfaction in E-commerce

Menitikberatkan pada faktor-faktor fundamental yang membentuk kepuasan pelanggan dalam belanja online, di mana layanan digital yang responsif menjadi kunci utama (Rita et al., 2019; Abdella et al., 2024).

### Online Review and Rating Behavior

Mengkaji bagaimana pelanggan memberikan feedback melalui rating dan ulasan teks sebagai sinyal penting bagi performa bisnis (Mezei et al., 2024; Su et al., 2023).

### Delivery Performance and Logistics Service Quality

Menelaah pengaruh waktu pengiriman, baik keterlambatan maupun ketepatan waktu, terhadap persepsi kualitas layanan pelanggan (Ravula et al., 2022; Rashid et al., 2024).

### Seller and Product Quality

Melihat peran performa penjual dan kategori produk dalam memengaruhi risiko munculnya rating rendah (Sheu & Chang, 2022).

### Business Intelligence and Descriptive Analytics

Fokus pada metodologi pengolahan data mentah menjadi wawasan bisnis melalui pipeline ETL dan visualisasi dashboard yang interaktif (Anandri, 2025; Varsha, 2023).

## 3. Methodological Position

Proyek ini memposisikan diri pada pendekatan **Business Intelligence & Analytics Solutions**. Metode yang digunakan meliputi:

- **Descriptive Analytics**: Untuk menggambarkan kondisi saat ini dari performa customer experience.
- **Root Cause Analysis**: Untuk mengidentifikasi penyebab utama stagnasi skor review pelanggan.
- **Segmentation**: Untuk mengelompokkan penjual atau wilayah yang memerlukan perhatian khusus.
- **KPI-based Dashboard**: Sebagai alat monitor berkelanjutan bagi persona Customer Experience Analyst.

Proyek ini tidak memprioritaskan Machine Learning yang kompleks sebagai output utama karena fokus pada _explainability_ (penjelasan penyebab masalah) lebih krusial bagi stakeholder bisnis dibandingkan model prediksi _black-box_.

## 4. Hypothesis Support from Literature

| Hypothesis                                                                                      | Literature Support    | Dataset Column / Table                                                          |
| :---------------------------------------------------------------------------------------------- | :-------------------- | :------------------------------------------------------------------------------ |
| **H1**: Late delivery is associated with lower review score.                                    | Ravula et al. (2022)  | `order_delivered_customer_date`, `order_estimated_delivery_date` / `orders.csv` |
| **H2**: Larger gap between estimated and actual delivery date increases the risk of low review. | Masuch et al. (2024)  | `order_estimated_delivery_date`, `order_purchase_timestamp` / `orders.csv`      |
| **H3**: Certain sellers contribute disproportionately to low review scores.                     | Sheu & Chang (2022)   | `seller_id` / `sellers.csv`, `order_reviews.csv`                                |
| **H4**: Certain product categories have higher low-rating risk.                                 | Abdella et al. (2024) | `product_category_name` / `products.csv`                                        |
| **H5**: Customer or seller region may affect customer experience.                               | Rashid et al. (2024)  | `customer_state`, `seller_state` / `customers.csv`, `sellers.csv`               |

## 5. Implication for Analysis Design

Berdasarkan tinjauan literatur, tahapan EDA akan diarahkan pada:

- Analisis distribusi dan tren skor review secara temporal.
- Perhitungan metrik keterlambatan pengiriman (delivery delay) dan durasi pengiriman.
- Analisis performa penjual (seller-level) untuk menemukan outlier negatif.
- Pemetaan risiko rating rendah berdasarkan kategori produk dan wilayah geografis.
- Perancangan KPI dashboard yang berfokus pada metrik operasional yang berdampak pada kepuasan pelanggan.

## 6. Next Step

- Melanjutkan ke penyusunan **Hypothesis Mapping** yang lebih detail.
- Melakukan EDA awal pada komponen review dan delivery untuk memvalidasi hipotesis awal.
- Mengintegrasikan referensi ini ke dalam Bab 2 (Related Work) pada draft paper IEEE.

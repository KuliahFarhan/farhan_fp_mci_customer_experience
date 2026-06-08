# 13 NLP Portuguese Review Analysis

## 1. Objective

NLP Portuguese Review Analysis v1 dibuat untuk menjawab pertanyaan bisnis:

> What do customers with low ratings complain about?

Analisis ini berfokus pada teks ulasan pelanggan berbahasa Portugis/Brazilian Portuguese dari dataset e-commerce DustiniaDelixia Groceria. Output NLP digunakan sebagai analisis root-cause deskriptif untuk melengkapi dashboard, SQL analytics, dan model risiko ML v2.1.

## 2. Scope and Leakage Rule

Review text tidak digunakan sebagai fitur prediksi pada model low-rating ML v2.1. Kolom `review_comment_title` dan `review_comment_message` muncul setelah pelanggan mengirim review, sehingga penggunaannya untuk memprediksi low rating akan menciptakan leakage.

Dalam task ini, review text hanya digunakan untuk analisis root-cause setelah review terjadi. Dengan demikian, NLP berperan menjelaskan keluhan pelanggan, bukan memprediksi risiko sebelum review masuk.

## 3. Dataset

Input utama:

```text
data/raw/order_reviews.csv
```

Kolom utama:

- `review_id`
- `order_id`
- `review_score`
- `review_comment_title`
- `review_comment_message`
- `review_creation_date`
- `review_answer_timestamp`

Segmentasi utama:

- Low rating: `review_score <= 2`
- Score 1
- Score 2
- High rating: `review_score >= 4`
- All reviews with text

## 4. Text Preprocessing

Pipeline preprocessing:

1. Menggabungkan `review_comment_title` dan `review_comment_message` menjadi `review_text_raw`.
2. Membersihkan teks dasar dengan lowercase, menghapus newline, whitespace berulang, URL, email, dan HTML-like fragments.
3. Menyimpan `clean_text` dengan karakter dan aksen Portugis tetap terbaca, seperti `não`, `prazo`, `entrega`, dan `péssimo`.
4. Membuat `normalized_text` dengan menghapus aksen untuk keyword matching, misalnya `não` menjadi `nao` dan `devolução` menjadi `devolucao`.
5. Membuat `phrase_text` agar frasa keluhan penting menjadi token underscore seperti `nao_recebi`, `nao_chegou`, `produto_errado`, `fora_prazo`, dan `nao_funciona`.
6. Tokenisasi menggunakan regex yang mendukung huruf Portugis dan underscore phrase tokens.
7. Stopword removal menggunakan stopwords Portugis jika tersedia, dengan fallback lokal bila NLTK resource tidak tersedia.
8. Negation words seperti `não`, `nao`, `nunca`, `nem`, dan `sem` dipertahankan karena mengubah makna keluhan.

Stemming RSLP dari NLTK digunakan hanya sebagai dukungan opsional bila tersedia. Label dashboard dan output bisnis tetap memakai term yang mudah dibaca, bukan stem.

## 5. Theme Tagging

Theme tagging dibuat sebagai sistem rule-based multi-label. Satu review dapat memiliki lebih dari satu tema karena pelanggan dapat mengeluhkan lebih dari satu masalah dalam komentar yang sama.

Tema utama:

- Delivery - Not Received
- Delivery - Delay
- Product - Wrong/Incomplete
- Product - Defect/Quality
- Seller/Service/Refund
- Positive Recommendation
- Other Complaint

Keyword matching dilakukan pada `normalized_text` agar variasi aksen tidak mengganggu pencocokan. Pendekatan rule-based dipilih karena lebih mudah diaudit dan cocok untuk narasi bisnis awal.

## 6. Top Terms

Top terms dibuat menggunakan TF-IDF dengan unigram dan bigram. Segmentasi yang digunakan:

- `review_score_1`
- `review_score_2`
- `low_rating_score_1_2`
- `high_rating_score_4_5`
- `all_text_reviews`

Selain TF-IDF weight, script juga menyimpan raw term count agar interpretasi lebih mudah.

## 7. Topic Modeling

NMF digunakan sebagai topic model utama karena lebih mudah diinterpretasikan pada teks review yang pendek. Model dijalankan pada low-rating reviews dengan teks, menggunakan TF-IDF, `phrase_text`, topic stopwords, dan jumlah topik default 6.

LDA tetap digunakan sebagai validasi eksploratif, bukan output bisnis utama. Setiap topik diberi label manual secara heuristik berdasarkan overlap dengan keyword theme. Jika topik terlihat noisy, interpretasi bisnis tetap diprioritaskan pada rule-based theme tagging dan NMF.

## 8. Output Files

Output disimpan ke `data/processed/`:

- `review_text_cleaned.csv`
- `review_theme_tags.csv`
- `review_theme_summary.csv`
- `review_top_terms_by_score.csv`
- `review_topics_nmf.csv`
- `review_topics_lda.csv`
- `review_nlp_audit.json`

Folder `data/processed/` tidak perlu dipush ke GitHub jika berisi output data besar.

## 9. Business Interpretation

Output utama untuk dashboard dan paper adalah theme summary dan top terms pada low-rating reviews. Analisis ini membantu menjelaskan jenis keluhan pelanggan, misalnya masalah pengiriman, produk tidak diterima, produk rusak, item salah/tidak lengkap, atau isu refund/service.

Hasil NLP bersifat deskriptif dan root-cause oriented. Analisis ini tidak membuktikan kausalitas, tetapi memberi indikasi pola keluhan yang muncul dalam review rendah.

## 10. Current NLP v1 Results

Audit hasil eksekusi script:

| Metric | Value |
| --- | ---: |
| Total reviews | 99,224 |
| Reviews with title | 11,566 |
| Reviews with message | 40,950 |
| Reviews with any text | 42,454 |
| Low-rating reviews | 14,575 |
| Low-rating reviews with text | 10,978 |
| Percentage reviews with text | 42.79% |
| Percentage low-rating with text | 75.32% |
| Median token count, all text reviews | 9 |
| Median token count, low-rating text reviews | 16 |

Top complaint themes among low-rating reviews with text:

| Theme | Review Count | Percentage |
| --- | ---: | ---: |
| Other Complaint | 4,068 | 36.14% |
| Delivery - Not Received | 2,844 | 25.27% |
| Delivery - Delay | 1,909 | 16.96% |
| Seller/Service/Refund | 1,499 | 13.32% |
| Product - Defect/Quality | 1,167 | 10.37% |
| Positive Recommendation | 1,127 | 10.01% |
| Product - Wrong/Incomplete | 1,097 | 9.75% |

Top Portuguese terms and bigrams for low-rating reviews include:

- `nao`
- `produto`
- `nao_recebi`
- `nao_chegou`
- `recebi`
- `ainda`
- `comprei`
- `entregue`
- `entrega`
- `veio`
- `chegou`
- `produto nao`
- `ainda nao`
- `prazo`
- `nao entregue`

The strongest text signals are consistent with delivery and fulfillment complaints, especially "not received", "delivery", "not delivered", and product receipt issues.

NMF topic summary:

| Topic Label | Representative Top Terms | Review Count |
| --- | --- | ---: |
| Product - Wrong/Incomplete | nota, defeito, outro, produto_errado, recomendo | 6,619 |
| Delivery - Not Received | nao_recebi, mercadoria, avaliar, data, prazo | 1,691 |
| Positive Recommendation | pessima, qualidade, ruim, material, foto | 982 |
| Delivery - Not Received | prazo, passou prazo, nao_recebi prazo, nao_chegou prazo | 788 |
| Delivery - Delay | nao_chegou, mercadoria, esperando, mes, correios | 459 |
| Delivery - Not Received | aguardando, retorno, resposta, contato, solucao | 439 |

LDA exploratory topic summary:

| Topic Label | Representative Top Terms | Review Count |
| --- | --- | ---: |
| Delivery - Delay | nao_chegou, nao_recebi, prazo, correios, demora | 2,274 |
| Delivery - Not Received | nao_recebi, aguardando, prazo, contato, problema | 2,108 |
| Delivery - Delay | nota fiscal, correios, valor | 1,780 |
| Product - Defect/Quality | qualidade, dinheiro, pessima, ruim, devolucao | 1,669 |
| Delivery - Not Received | nao_recebi, aguardo, data, retorno | 1,636 |
| Product - Wrong/Incomplete | diferente, produto_errado, foto, anuncio | 1,511 |

## 11. Limitations

- Banyak review tidak memiliki teks komentar.
- Review text pendek, informal, dan dapat mengandung typo.
- Rule-based theme tagging dapat melewatkan keluhan implisit atau frase yang tidak ada di kamus keyword.
- Topic modeling pada short reviews dapat menghasilkan topik yang noisy.
- Analisis ini bersifat deskriptif/root-cause oriented, bukan bukti kausal.
- NLP belum digunakan sebagai fitur prediksi low-rating karena berisiko leakage.
- RSLP stemming tidak dijalankan pada eksekusi saat ini karena resource NLTK `rslp` tidak tersedia secara lokal. Pipeline tetap berjalan tanpa stemming.

## 12. Future Work

- Perluas kamus keyword Portugis berdasarkan hasil audit manual.
- Tambahkan dashboard NLP untuk complaint theme trend dan contoh review.
- Bandingkan rule-based themes dengan model topic modern seperti BERTopic bila waktu dan environment memungkinkan.
- Gabungkan theme output dengan mart order-level untuk melihat asosiasi dengan delivery status, delay bucket, category, dan region.

## References

[1] Olist, "Brazilian E-Commerce Public Dataset by Olist," Kaggle Dataset, 2018.

[2] scikit-learn Developers, "TfidfVectorizer," scikit-learn User Guide and API Reference.

[3] V. M. Orengo and C. Huyck, "A Stemming Algorithm for the Portuguese Language," Proceedings of SPIRE, 2001.

[4] D. M. Blei, A. Y. Ng, and M. I. Jordan, "Latent Dirichlet Allocation," Journal of Machine Learning Research, vol. 3, pp. 993-1022, 2003.

[5] M. Grootendorst, "BERTopic: Neural topic modeling with a class-based TF-IDF procedure," arXiv preprint arXiv:2203.05794, 2022.

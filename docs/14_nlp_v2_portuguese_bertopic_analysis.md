# 14 NLP v2 Portuguese BERTopic Analysis

## 1. Objective

NLP v2 dibuat untuk memperkuat analisis teks review Brazilian Portuguese pada Final Project MCI 2026. Analisis ini menjawab tiga pertanyaan:

1. Apa yang dikeluhkan pelanggan dengan low rating?
2. Bagaimana low-rating reviews berbeda dari high-rating reviews?
3. Apakah semantic topic modeling seperti BERTopic dapat meningkatkan interpretasi dibanding TF-IDF, NMF, dan LDA?

Output ini digunakan untuk root-cause analysis customer experience, bukan untuk prediksi low-rating.

## 2. Leakage Rule

Review text tidak digunakan sebagai input model ML low-rating. Kolom `review_comment_title` dan `review_comment_message` muncul setelah pelanggan mengirim review, sehingga jika digunakan untuk prediksi low rating akan menyebabkan leakage.

Dalam NLP v2, teks review hanya digunakan untuk analisis deskriptif setelah review terjadi.

## 3. Dataset Language

Dataset review berasal dari konteks Brazilian/Olist-style e-commerce sehingga teks komentar diperlakukan sebagai Brazilian Portuguese. Preprocessing mempertahankan aksen pada `clean_text` agar readable, lalu membuat `normalized_text` untuk matching keyword tanpa aksen.

Input utama:

```text
data/raw/order_reviews.csv
```

## 4. Preprocessing Pipeline

Pipeline di notebook `notebooks/05_nlp_portuguese_review_analysis_v2.ipynb` dibuat self-contained dan mencakup:

- Combine `review_comment_title` dan `review_comment_message` menjadi `review_text_raw`.
- Lowercase, hapus URL, email, HTML-like fragments, newline, dan whitespace berulang.
- Buat `clean_text` dengan aksen Portugis tetap dipertahankan.
- Buat `normalized_text` dengan aksen dihapus untuk keyword matching.
- Buat `phrase_text` dengan underscore phrase tokens seperti `nao_recebi`, `nao_chegou`, `nao_entregue`, `produto_errado`, `produto_incompleto`, `fora_prazo`, `nao_funciona`, dan `sem_resposta`.
- Gunakan token pattern `r"[a-z_]+"` agar phrase tokens tetap terbaca sebagai satu token.

## 5. Stopwords and Negation

Notebook menggunakan library-first approach:

- NLTK Portuguese stopwords digunakan jika corpus tersedia.
- Jika NLTK corpus tidak tersedia, fallback Portuguese stopword list digunakan agar notebook tetap dapat berjalan offline.
- Custom domain stopwords hanya digunakan sebagai tambahan.

Negasi seperti `nao`, `não`, `nunca`, `nem`, dan `sem` dilindungi karena makna keluhan berubah drastis ketika negasi dihapus. Phrase tokens penting seperti `nao_recebi`, `nao_chegou`, dan `nao_funciona` juga tidak dihapus dari topic modeling.

## 6. Low vs High Rating Contrast

Low rating didefinisikan sebagai `review_score <= 2`, sedangkan high rating didefinisikan sebagai `review_score >= 4`.

Top low-rating terms menunjukkan keluhan pengiriman dan fulfillment:

- `nao_recebi`
- `nao_chegou`
- `nao_entregue`
- `prazo`
- `entregue`
- `produto nao_entregue`

Top high-rating terms lebih banyak berisi sinyal positif:

- `bom`
- `recomendo`
- `otimo`
- `excelente`
- `antes_prazo`
- `super recomendo`
- `gostei`

Word cloud digunakan sebagai visual eksploratif untuk presentasi, bukan bukti statistik.

NLP v2.1 menambahkan **filtered presentation word cloud**. Versi raw tetap disimpan untuk eksplorasi, sedangkan versi filtered menghapus kata e-commerce umum seperti `produto`, `produtos`, `entrega`, `pedido`, `compra`, `comprei`, `loja`, `dia`, `dias`, `recebi`, `veio`, `chegou`, dan `entregue`. Phrase tokens penting seperti `nao_recebi`, `nao_chegou`, `nao_entregue`, `produto_errado`, `produto_incompleto`, `fora_prazo`, `nao_funciona`, dan `sem_resposta` tetap dipertahankan.

## 6.1 Distinctive Terms

Selain raw frequency dan TF-IDF, NLP v2.1 menambahkan distinctive term analysis. Metrik ini menghitung frekuensi term per 1,000 token pada low-rating dan high-rating, lalu menghitung:

- `low_per_1000`
- `high_per_1000`
- `difference = low_per_1000 - high_per_1000`
- `ratio = (low_per_1000 + smoothing) / (high_per_1000 + smoothing)`

Top distinctive low-rating terms:

| Term | Low per 1,000 | High per 1,000 | Difference |
| --- | ---: | ---: | ---: |
| nao | 68.81 | 15.33 | 53.48 |
| nao_recebi | 21.47 | 0.70 | 20.77 |
| agora | 7.43 | 1.22 | 6.22 |
| nao_chegou | 6.45 | 0.42 | 6.03 |
| ainda | 10.79 | 4.82 | 5.97 |
| quero | 5.73 | 0.46 | 5.27 |
| nem | 5.58 | 0.58 | 5.00 |
| contato | 5.05 | 0.40 | 4.65 |

Top distinctive high-rating terms:

| Term | Low per 1,000 | High per 1,000 | Difference |
| --- | ---: | ---: | ---: |
| prazo | 9.00 | 47.42 | -38.42 |
| recomendo | 5.70 | 42.81 | -37.11 |
| bom | 2.61 | 39.03 | -36.42 |
| antes | 1.83 | 30.53 | -28.69 |
| otimo | 0.28 | 26.08 | -25.80 |
| bem | 2.26 | 20.54 | -18.28 |
| super | 0.80 | 19.03 | -18.23 |
| excelente | 0.16 | 18.34 | -18.18 |

## 7. Rule-Based Multi-Label Themes

Theme tagging adalah output bisnis utama karena mudah diaudit dan cocok untuk dashboard. Satu review dapat memiliki lebih dari satu tema.

Tema NLP v2:

- Delivery - Not Received
- Delivery - Delay
- Product - Wrong/Incomplete
- Product - Defect/Quality
- Seller/Service/Refund
- Packaging Issue
- Positive Recommendation
- Other Complaint

Positive recommendation diperbaiki agar tidak mudah false positive pada frasa negatif seperti `nao recomendo` dan `nao gostei`.

## 8. Audit Statistics

| Metric | Value |
| --- | ---: |
| Total reviews | 99,224 |
| Reviews with any text | 42,687 |
| Low-rating reviews | 14,575 |
| Low-rating reviews with text | 10,994 |
| Percentage reviews with text | 43.02% |
| Percentage low-rating with text | 75.43% |
| Median token count, all text reviews | 9 |
| Median token count, low-rating text reviews | 16 |

## 9. Revised Complaint Themes

Theme summary for low-rating reviews with text:

| Theme | Review Count | Percentage |
| --- | ---: | ---: |
| Other Complaint | 3,598 | 33.18% |
| Delivery - Not Received | 3,293 | 30.36% |
| Delivery - Delay | 1,879 | 17.33% |
| Seller/Service/Refund | 1,572 | 14.50% |
| Product - Defect/Quality | 1,264 | 11.66% |
| Product - Wrong/Incomplete | 1,109 | 10.23% |
| Positive Recommendation | 504 | 4.65% |
| Packaging Issue | 491 | 4.53% |

The strongest complaint signal is delivery not received, followed by delivery delay and seller/service/refund issues. Other Complaint remains high, indicating that future manual audit can expand the theme dictionary.

## 10. Topic Modeling Comparison

| Method | Interpretability | Semantic Capability | Runtime/Dependency | Business Usefulness |
| --- | --- | --- | --- | --- |
| Rule-based themes | High | Low-Medium | Low | Main dashboard output |
| TF-IDF/NMF | Medium-High | Medium | Low | Preferred lightweight topic model |
| LDA | Medium | Low-Medium | Low | Exploratory comparison |
| BERTopic | Variable | High | High | Advanced experiment if dependencies are available |

## 11. NMF Topic Summary

NMF is the preferred topic model for lightweight interpretation.

| Topic Label | Representative Top Terms | Review Count |
| --- | --- | ---: |
| Product - Wrong/Incomplete | nota, defeito, outro, produto_errado, site | 7,310 |
| Delivery - Not Received | nao_recebi, mercadoria, avaliar, data, prazo | 1,556 |
| Delivery - Not Received | prazo, passou prazo, nao_entregue prazo | 732 |
| Delivery - Delay | nao_entregue, presente, data, mes, demora | 479 |
| Delivery - Delay | nao_chegou, mercadoria, esperando, correios | 462 |
| Delivery - Not Received | aguardando, retorno, resposta, contato, solucao | 439 |

NMF improves over the previous noisy LDA because phrase tokens such as `nao_recebi`, `nao_entregue`, `nao_chegou`, and `produto_errado` now appear directly in topic terms.

## 12. LDA Topic Summary

LDA is kept as exploratory comparison.

| Topic Label | Representative Top Terms | Review Count |
| --- | --- | ---: |
| Delivery - Not Received | nao_recebi, nao_chegou, prazo, correios | 2,656 |
| Product - Wrong/Incomplete | nota fiscal, unidades, produto_incompleto | 1,833 |
| Delivery - Not Received | nao_entregue, prazo, falta, ruim | 1,758 |
| Seller/Service/Refund | defeito, troca, produto_errado, devolucao | 1,685 |
| Product - Defect/Quality | qualidade, dinheiro, pessima, ruim | 1,671 |
| Delivery - Not Received | demora, nao_recebi, pessimo, resposta | 1,375 |

LDA is still useful for validation but can mix several complaint dimensions within a single topic.

## 13. BERTopic Attempt

BERTopic is included in the notebook as an advanced semantic topic modeling section. The notebook attempts to import and run BERTopic using multilingual embeddings.

Current execution result after dependency check and rerun:

```text
BERTopic failed with exact error: NameError("name 'nn' is not defined")
```

The runtime log also indicates dependency compatibility issues in the PyTorch/Transformers/NumPy stack:

```text
A module that was compiled using NumPy 1.x cannot be run in NumPy 2.4.2
PyTorch >= 2.4 is required but found 2.1.0+cu118
```

BERTopic-related packages are installed, but BERTopic did not complete successfully because the embedding/model stack is not compatible in the current environment. The notebook/runner continues to save all non-BERTopic outputs. BERTopic can be retried after aligning the dependency stack, for example by using compatible versions of NumPy, PyTorch, Transformers, BERTopic, UMAP, and HDBSCAN.

- `bertopic`
- `sentence-transformers`
- `umap-learn`
- `hdbscan`

## 14. Output Files

CSV/JSON outputs:

- `data/processed/review_text_cleaned_v2.csv`
- `data/processed/review_theme_tags_v2.csv`
- `data/processed/review_theme_summary_v2.csv`
- `data/processed/review_top_terms_by_score_v2.csv`
- `data/processed/review_topics_nmf_v2.csv`
- `data/processed/review_topics_lda_v2.csv`
- `data/processed/review_nlp_audit_v2.json`
- `data/processed/review_topics_bertopic_v2.csv` only if BERTopic runs successfully

Plot outputs:

- `docs/assets/nlp_v2/01_review_score_distribution.png`
- `docs/assets/nlp_v2/02_text_availability.png`
- `docs/assets/nlp_v2/03_word_frequency_low_vs_high.png`
- `docs/assets/nlp_v2/04_tfidf_low_vs_high.png`
- `docs/assets/nlp_v2/05_wordcloud_low_vs_high.png`
- `docs/assets/nlp_v2/05a_wordcloud_raw_low_vs_high.png`
- `docs/assets/nlp_v2/05b_wordcloud_filtered_low_vs_high.png`
- `docs/assets/nlp_v2/06_bigram_low_vs_high.png`
- `docs/assets/nlp_v2/07_theme_distribution_low_rating.png`
- `docs/assets/nlp_v2/08_theme_heatmap_by_score.png`
- `docs/assets/nlp_v2/09_nmf_topic_distribution.png`
- `docs/assets/nlp_v2/10_lda_topic_distribution.png`
- `docs/assets/nlp_v2/11_bertopic_topic_distribution.png` only if BERTopic runs successfully
- `docs/assets/nlp_v2/12_distinctive_low_rating_terms.png`
- `docs/assets/nlp_v2/13_distinctive_high_rating_terms.png`

## 15. Recommended Outputs for Paper and Dashboard

Recommended primary outputs:

- Theme summary for low-rating reviews.
- Theme heatmap by review score.
- Low vs high TF-IDF contrast.
- Word cloud for presentation.
- NMF topic summary as lightweight topic interpretation.

BERTopic should be described as future/advanced semantic exploration unless dependencies are installed and topics are stable.

## 16. Limitations

- Many reviews have no text.
- Review text is short, informal, and may contain typos or slang.
- Rule-based tags may miss implicit complaints.
- Word cloud is exploratory and not statistical proof.
- LDA and NMF are descriptive topic models, not causal proof.
- BERTopic may be sensitive to embedding model, UMAP, HDBSCAN, and runtime environment.
- This analysis is descriptive/root-cause oriented and must not be used as prediction feature input.

## References

[1] Olist, "Brazilian E-Commerce Public Dataset by Olist," Kaggle Dataset, 2018.

[2] NLTK Project, "Natural Language Toolkit Documentation," 2026.

[3] scikit-learn Developers, "TfidfVectorizer," scikit-learn User Guide and API Reference.

[4] scikit-learn Developers, "Topic extraction with Non-negative Matrix Factorization and Latent Dirichlet Allocation," scikit-learn Examples.

[5] D. D. Lee and H. S. Seung, "Learning the parts of objects by non-negative matrix factorization," Nature, vol. 401, pp. 788-791, 1999.

[6] D. M. Blei, A. Y. Ng, and M. I. Jordan, "Latent Dirichlet Allocation," Journal of Machine Learning Research, vol. 3, pp. 993-1022, 2003.

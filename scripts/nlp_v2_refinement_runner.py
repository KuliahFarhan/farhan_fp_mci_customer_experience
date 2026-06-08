import importlib.util
import json
import sys
from collections import Counter
from pathlib import Path

ROOT_FOR_IMPORT = Path(__file__).resolve().parents[1]
if str(ROOT_FOR_IMPORT) not in sys.path:
    sys.path.insert(0, str(ROOT_FOR_IMPORT))

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from wordcloud import WordCloud

from scripts.nlp_portuguese_review_analysis import (
    OUTPUT_DIR,
    ROOT_DIR,
    THEME_LABELS,
    THEME_PATTERNS,
    build_audit,
    build_lda_topics,
    build_nmf_topics,
    build_top_terms,
    load_reviews,
    load_stopwords,
    prepare_cleaned_reviews,
    tag_review_themes,
    tokenize_normalized_text,
)

ASSET_DIR = ROOT_DIR / "docs" / "assets" / "nlp_v2"
ASSET_DIR.mkdir(parents=True, exist_ok=True)

CORE_PACKAGES = ["pandas", "numpy", "matplotlib", "seaborn", "wordcloud", "nltk", "sklearn"]
BERTOPIC_PACKAGES = ["bertopic", "sentence_transformers", "umap", "hdbscan"]

missing_core = [pkg for pkg in CORE_PACKAGES if importlib.util.find_spec(pkg) is None]
missing_bertopic = [pkg for pkg in BERTOPIC_PACKAGES if importlib.util.find_spec(pkg) is None]
if missing_core:
    raise ImportError(f"Missing core dependencies: {missing_core}")
if missing_bertopic:
    raise ImportError(
        "Missing BERTopic dependencies. Install with: "
        "python -m pip install bertopic sentence-transformers umap-learn hdbscan"
    )


def save_barh(df, x, y, path, title, subtitle=None, color="#4E79A7", label_fmt="{:.0f}"):
    plt.figure(figsize=(11, 7))
    ax = sns.barplot(data=df, x=x, y=y, color=color)
    for patch in ax.patches:
        value = patch.get_width()
        ax.text(value, patch.get_y() + patch.get_height() / 2, " " + label_fmt.format(value), va="center", fontsize=8)
    plt.title(title)
    if subtitle:
        plt.suptitle(subtitle, y=0.98, fontsize=10)
    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()


def term_counter(texts, stopwords, ngram=1):
    counts = Counter()
    for text in texts:
        tokens = [t for t in tokenize_normalized_text(text) if t not in stopwords and len(t) > 1]
        if ngram == 1:
            counts.update(tokens)
        else:
            counts.update([" ".join(tokens[i : i + ngram]) for i in range(len(tokens) - ngram + 1)])
    return counts


def make_wordcloud_text(texts, stopwords):
    tokens = []
    for text in texts:
        tokens.extend([t for t in tokenize_normalized_text(text) if t not in stopwords and len(t) > 1])
    return " ".join(tokens)


def save_wordcloud_pair(low_texts, high_texts, stopwords, path, title):
    fig, axes = plt.subplots(1, 2, figsize=(15, 6))
    for ax, texts, subtitle in [(axes[0], low_texts, "Low Rating"), (axes[1], high_texts, "High Rating")]:
        wc_text = make_wordcloud_text(texts, stopwords)
        wc = WordCloud(width=900, height=520, background_color="white", collocations=False, random_state=42).generate(wc_text)
        ax.imshow(wc, interpolation="bilinear")
        ax.set_title(subtitle)
        ax.axis("off")
    fig.suptitle(title + " - exploratory visualization, not statistical proof", fontsize=12)
    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()


def label_topic(top_terms):
    joined = " ".join(top_terms)
    scores = {theme: sum(1 for p in patterns if p in joined) for theme, patterns in THEME_PATTERNS.items()}
    best, score = max(scores.items(), key=lambda item: item[1])
    return THEME_LABELS[best] if score > 0 else "Other Complaint"


def main():
    reviews = load_reviews()
    cleaned = prepare_cleaned_reviews(reviews)
    tokens = [
        token
        for text in cleaned.loc[cleaned["has_text"], "phrase_text"]
        for token in tokenize_normalized_text(text)
    ]
    matching_stopwords, topic_stopwords = load_stopwords(tokens)

    generic = {"produto", "produtos", "entrega", "pedido", "compra", "comprei", "loja", "dia", "dias", "recebi", "veio", "chegou", "entregue"}
    protected = {"nao_recebi", "nao_chegou", "nao_entregue", "produto_errado", "produto_incompleto", "fora_prazo", "nao_funciona", "sem_resposta", "antes_prazo", "chegou_antes", "super_recomendo"}
    filtered_stopwords = (matching_stopwords | generic) - protected

    low = cleaned[cleaned["is_low_rating"] & cleaned["has_text"]].copy()
    high = cleaned[(cleaned["review_score"] >= 4) & cleaned["has_text"]].copy()

    score_counts = reviews["review_score"].value_counts().sort_index()
    plt.figure(figsize=(7, 4.5))
    ax = sns.barplot(x=score_counts.index, y=score_counts.values, color="#4C78A8")
    for patch in ax.patches:
        value = patch.get_height()
        ax.text(patch.get_x() + patch.get_width() / 2, value, f"{int(value):,}", ha="center", va="bottom", fontsize=9)
    plt.title("Review Score Distribution")
    plt.suptitle(f"Based on all reviews, n = {len(reviews):,}", y=0.98, fontsize=10)
    plt.tight_layout()
    plt.savefig(ASSET_DIR / "01_review_score_distribution.png", dpi=150, bbox_inches="tight")
    plt.close()

    any_text = cleaned["has_text"]
    text_availability = pd.Series({"with_text": int(any_text.sum()), "without_text": int((~any_text).sum())})
    plt.figure(figsize=(7, 4.5))
    ax = sns.barplot(x=text_availability.index, y=text_availability.values, hue=text_availability.index, palette=["#59A14F", "#E15759"], legend=False)
    for patch in ax.patches:
        value = patch.get_height()
        ax.text(patch.get_x() + patch.get_width() / 2, value, f"{int(value):,} ({value * 100 / len(reviews):.1f}%)", ha="center", va="bottom", fontsize=9)
    plt.title("Text Availability")
    plt.suptitle(f"Based on all reviews, n = {len(reviews):,}", y=0.98, fontsize=10)
    plt.tight_layout()
    plt.savefig(ASSET_DIR / "02_text_availability.png", dpi=150, bbox_inches="tight")
    plt.close()

    save_wordcloud_pair(low["phrase_text"], high["phrase_text"], matching_stopwords, ASSET_DIR / "05a_wordcloud_raw_low_vs_high.png", "Raw Word Cloud")
    save_wordcloud_pair(low["phrase_text"], high["phrase_text"], filtered_stopwords, ASSET_DIR / "05b_wordcloud_filtered_low_vs_high.png", "Filtered Presentation Word Cloud")
    save_wordcloud_pair(low["phrase_text"], high["phrase_text"], filtered_stopwords, ASSET_DIR / "05_wordcloud_low_vs_high.png", "Filtered Presentation Word Cloud")

    low_counts = term_counter(low["phrase_text"], matching_stopwords)
    high_counts = term_counter(high["phrase_text"], matching_stopwords)
    freq_df = pd.concat([
        pd.DataFrame(low_counts.most_common(18), columns=["term", "count"]).assign(segment="low_rating"),
        pd.DataFrame(high_counts.most_common(18), columns=["term", "count"]).assign(segment="high_rating"),
    ])
    plt.figure(figsize=(12, 8))
    ax = sns.barplot(data=freq_df, x="count", y="term", hue="segment")
    for container in ax.containers:
        ax.bar_label(container, fmt="%d", padding=3, fontsize=8)
    plt.title("Word Frequency: Low vs High Rating")
    plt.suptitle("Raw count, exploratory only", y=0.98, fontsize=10)
    plt.tight_layout()
    plt.savefig(ASSET_DIR / "03_word_frequency_low_vs_high.png", dpi=150, bbox_inches="tight")
    plt.close()

    top_terms = build_top_terms(cleaned, matching_stopwords)
    top_terms.to_csv(OUTPUT_DIR / "review_top_terms_by_score_v2.csv", index=False)
    plot_terms = top_terms[top_terms["segment"].isin(["low_rating_score_1_2", "high_rating_score_4_5"])].groupby("segment").head(12)
    plt.figure(figsize=(12, 8))
    ax = sns.barplot(data=plot_terms, x="score_or_weight", y="term", hue="segment")
    for container in ax.containers:
        ax.bar_label(container, fmt="%.3f", padding=3, fontsize=8)
    plt.title("TF-IDF Top Terms: Low vs High Rating")
    plt.suptitle("Average TF-IDF weight; rounded labels shown", y=0.98, fontsize=10)
    plt.tight_layout()
    plt.savefig(ASSET_DIR / "04_tfidf_low_vs_high.png", dpi=150, bbox_inches="tight")
    plt.close()

    low_bigrams = pd.DataFrame(term_counter(low["phrase_text"], matching_stopwords, 2).most_common(18), columns=["bigram", "count"]).assign(segment="low_rating")
    high_bigrams = pd.DataFrame(term_counter(high["phrase_text"], matching_stopwords, 2).most_common(18), columns=["bigram", "count"]).assign(segment="high_rating")
    bigram_df = pd.concat([low_bigrams, high_bigrams])
    plt.figure(figsize=(12, 8))
    ax = sns.barplot(data=bigram_df, x="count", y="bigram", hue="segment")
    for container in ax.containers:
        ax.bar_label(container, fmt="%d", padding=3, fontsize=8)
    plt.title("Bigram Analysis: Low vs High Rating")
    plt.suptitle("Raw bigram count, exploratory only", y=0.98, fontsize=10)
    plt.tight_layout()
    plt.savefig(ASSET_DIR / "06_bigram_low_vs_high.png", dpi=150, bbox_inches="tight")
    plt.close()

    low_dist_counts, low_total = term_counter(low["phrase_text"], filtered_stopwords), 0
    high_dist_counts, high_total = term_counter(high["phrase_text"], filtered_stopwords), 0
    low_total = sum(low_dist_counts.values())
    high_total = sum(high_dist_counts.values())
    rows = []
    for term in set(low_dist_counts) | set(high_dist_counts):
        low_per = low_dist_counts[term] * 1000 / max(low_total, 1)
        high_per = high_dist_counts[term] * 1000 / max(high_total, 1)
        rows.append({
            "term": term,
            "low_count": int(low_dist_counts[term]),
            "high_count": int(high_dist_counts[term]),
            "low_per_1000": round(low_per, 4),
            "high_per_1000": round(high_per, 4),
            "difference": round(low_per - high_per, 4),
            "ratio": round((low_per + 0.1) / (high_per + 0.1), 4),
        })
    distinctive = pd.DataFrame(rows)
    distinctive = distinctive[(distinctive["low_count"] + distinctive["high_count"]) >= 20]
    distinctive.to_csv(OUTPUT_DIR / "review_distinctive_terms_v2.csv", index=False)
    save_barh(distinctive.sort_values(["difference", "ratio"], ascending=False).head(15), "difference", "term", ASSET_DIR / "12_distinctive_low_rating_terms.png", "Distinctive Low-Rating Terms", "Normalized frequency difference per 1,000 tokens: low - high", "#E15759", "{:.2f}")
    save_barh(distinctive.sort_values(["difference", "ratio"], ascending=True).head(15), "difference", "term", ASSET_DIR / "13_distinctive_high_rating_terms.png", "Distinctive High-Rating Terms", "Normalized frequency difference per 1,000 tokens: low - high", "#59A14F", "{:.2f}")

    tags = tag_review_themes(cleaned)
    low_ids = set(low["review_id"])
    theme_cols = [c for c in tags.columns if c.startswith("theme_") and c not in ["theme_other", "theme_count"]]
    rows = []
    for col in theme_cols + ["theme_other"]:
        matched = tags[tags["review_id"].isin(low_ids) & tags[col]]
        rows.append({
            "theme": THEME_LABELS[col],
            "review_count": int(len(matched)),
            "percentage_of_low_rating_reviews": round(len(matched) * 100 / max(len(low_ids), 1), 2),
            "avg_review_score": round(float(matched["review_score"].mean()), 2) if len(matched) else None,
            "sample_keywords": ", ".join(THEME_PATTERNS.get(col, ["no matched theme"])[:8]),
        })
    theme_summary = pd.DataFrame(rows).sort_values("review_count", ascending=False)
    theme_summary.to_csv(OUTPUT_DIR / "review_theme_summary_v2.csv", index=False)
    save_barh(theme_summary, "review_count", "theme", ASSET_DIR / "07_theme_distribution_low_rating.png", "Theme Distribution in Low-Rating Reviews", f"Denominator = low-rating reviews with text, n = {len(low_ids):,}", "#F28E2B")

    heat_rows = []
    for score in sorted(cleaned["review_score"].dropna().unique()):
        ids = set(cleaned[(cleaned["review_score"] == score) & cleaned["has_text"]]["review_id"])
        row = {"review_score": score}
        for col in theme_cols + ["theme_other"]:
            row[THEME_LABELS[col]] = tags[tags["review_id"].isin(ids) & tags[col]].shape[0] * 100 / max(len(ids), 1)
        heat_rows.append(row)
    heatmap = pd.DataFrame(heat_rows).set_index("review_score")
    plt.figure(figsize=(13, 5.5))
    sns.heatmap(heatmap, annot=True, fmt=".1f", cmap="YlOrRd")
    plt.title("Theme Percentage by Review Score")
    plt.suptitle("Each cell = percentage of text reviews within that score group", y=0.98, fontsize=10)
    plt.tight_layout()
    plt.savefig(ASSET_DIR / "08_theme_heatmap_by_score.png", dpi=150, bbox_inches="tight")
    plt.close()

    cleaned.to_csv(OUTPUT_DIR / "review_text_cleaned_v2.csv", index=False)
    tags.to_csv(OUTPUT_DIR / "review_theme_tags_v2.csv", index=False)
    nmf = build_nmf_topics(cleaned, topic_stopwords)
    lda = build_lda_topics(cleaned, topic_stopwords)
    nmf.to_csv(OUTPUT_DIR / "review_topics_nmf_v2.csv", index=False)
    lda.to_csv(OUTPUT_DIR / "review_topics_lda_v2.csv", index=False)
    save_barh(nmf, "review_count", "manual_topic_label", ASSET_DIR / "09_nmf_topic_distribution.png", "NMF Topic Distribution")
    save_barh(lda, "review_count", "manual_topic_label", ASSET_DIR / "10_lda_topic_distribution.png", "LDA Topic Distribution", color="#59A14F")

    bertopic_status = "not_run"
    bertopic_error = None
    try:
        from bertopic import BERTopic
        sample = low.sample(min(8000, len(low)), random_state=42).copy()
        model = BERTopic(
            embedding_model="paraphrase-multilingual-MiniLM-L12-v2",
            language="multilingual",
            calculate_probabilities=False,
            verbose=True,
            min_topic_size=50,
        )
        topics, _ = model.fit_transform(sample["clean_text"].tolist())
        sample["topic_id"] = topics
        info = model.get_topic_info()
        rows = []
        for _, row in info.iterrows():
            topic_id = int(row["Topic"])
            if topic_id == -1:
                continue
            terms = [term for term, _ in model.get_topic(topic_id)[:12]]
            samples = sample[sample["topic_id"] == topic_id]["clean_text"].head(3).tolist()
            rows.append({
                "topic_id": topic_id,
                "topic_name": row.get("Name", f"Topic {topic_id}"),
                "representative_terms": ", ".join(terms),
                "review_count": int(row["Count"]),
                "sample_reviews": " || ".join(samples),
                "mapped_business_label": label_topic([t.replace(" ", "_") for t in terms]),
            })
        bertopic = pd.DataFrame(rows).sort_values("review_count", ascending=False)
        bertopic.to_csv(OUTPUT_DIR / "review_topics_bertopic_v2.csv", index=False)
        if len(bertopic):
            save_barh(bertopic.head(10), "review_count", "mapped_business_label", ASSET_DIR / "11_bertopic_topic_distribution.png", "BERTopic Topic Distribution", color="#B07AA1")
        bertopic_status = "success"
    except Exception as exc:
        bertopic_status = "failed"
        bertopic_error = repr(exc)
        print("BERTopic failed with exact error:", bertopic_error)

    audit = build_audit(reviews, cleaned)
    audit["bertopic_status"] = bertopic_status
    audit["bertopic_error"] = bertopic_error
    (OUTPUT_DIR / "review_nlp_audit_v2.json").write_text(json.dumps(audit, indent=2), encoding="utf-8")
    print(json.dumps(audit, indent=2))
    print("Top low distinctive terms:")
    print(distinctive.sort_values(["difference", "ratio"], ascending=False).head(10).to_string(index=False))
    print("Top high distinctive terms:")
    print(distinctive.sort_values(["difference", "ratio"], ascending=True).head(10).to_string(index=False))


if __name__ == "__main__":
    main()

import json
import re
import unicodedata
import warnings
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer


ROOT_DIR = Path(__file__).resolve().parents[1]
RAW_REVIEWS_PATH = ROOT_DIR / "data" / "raw" / "order_reviews.csv"
OUTPUT_DIR = ROOT_DIR / "data" / "processed"

CLEANED_PATH = OUTPUT_DIR / "review_text_cleaned.csv"
THEME_TAGS_PATH = OUTPUT_DIR / "review_theme_tags.csv"
THEME_SUMMARY_PATH = OUTPUT_DIR / "review_theme_summary.csv"
TOP_TERMS_PATH = OUTPUT_DIR / "review_top_terms_by_score.csv"
TOPICS_PATH = OUTPUT_DIR / "review_topics_lda.csv"
NMF_TOPICS_PATH = OUTPUT_DIR / "review_topics_nmf.csv"
AUDIT_PATH = OUTPUT_DIR / "review_nlp_audit.json"

TOKEN_PATTERN = r"[a-záàâãéêíóôõúç]+"
NORMALIZED_TOKEN_PATTERN = r"[a-z_]+"
NEGATION_WORDS = {"não", "nao", "nunca", "nem", "sem"}

FALLBACK_PORTUGUESE_STOPWORDS = {
    "a",
    "ao",
    "aos",
    "aquela",
    "aquele",
    "aqueles",
    "as",
    "até",
    "com",
    "como",
    "da",
    "das",
    "de",
    "dela",
    "dele",
    "deles",
    "do",
    "dos",
    "e",
    "ela",
    "elas",
    "ele",
    "eles",
    "em",
    "entre",
    "era",
    "essa",
    "esse",
    "esta",
    "estava",
    "este",
    "eu",
    "foi",
    "foram",
    "há",
    "isso",
    "isto",
    "já",
    "lhe",
    "mais",
    "mas",
    "me",
    "meu",
    "minha",
    "muito",
    "na",
    "nas",
    "no",
    "nos",
    "o",
    "os",
    "ou",
    "para",
    "pela",
    "pelo",
    "por",
    "qual",
    "quando",
    "que",
    "quem",
    "se",
    "seu",
    "sua",
    "também",
    "tem",
    "ter",
    "um",
    "uma",
    "você",
    "vocês",
}

DOMAIN_STOPWORD_CANDIDATES = {
    "lannister",
    "stark",
    "targaryen",
    "baratheon",
}

PHRASE_REPLACEMENTS = [
    ("ainda nao recebi", "nao_recebi"),
    ("nunca recebi", "nao_recebi"),
    ("nao recebi", "nao_recebi"),
    ("produto nao chegou", "nao_chegou"),
    ("pedido nao chegou", "nao_chegou"),
    ("nao chegou", "nao_chegou"),
    ("consta entregue", "consta_entregue"),
    ("marcado como entregue", "marcado_entregue"),
    ("fora do prazo", "fora_prazo"),
    ("dentro do prazo", "dentro_prazo"),
    ("chegou antes", "chegou_antes"),
    ("produto errado", "produto_errado"),
    ("veio errado", "produto_errado"),
    ("veio outro", "produto_errado"),
    ("produto diferente", "produto_diferente"),
    ("veio diferente", "produto_diferente"),
    ("veio faltando", "produto_incompleto"),
    ("produto incompleto", "produto_incompleto"),
    ("tamanho errado", "tamanho_errado"),
    ("cor errada", "cor_errada"),
    ("produto quebrado", "produto_quebrado"),
    ("produto danificado", "produto_danificado"),
    ("qualidade ruim", "qualidade_ruim"),
    ("nao funciona", "nao_funciona"),
    ("nao funcionou", "nao_funciona"),
    ("mal acabado", "mal_acabado"),
    ("sem resposta", "sem_resposta"),
    ("sem retorno", "sem_resposta"),
    ("pedi reembolso", "pedi_reembolso"),
    ("pedi estorno", "pedi_estorno"),
]

THEME_PATTERNS = {
    "theme_delivery_not_received": [
        "nao_recebi",
        "nao_chegou",
        "aguardando",
        "consta entregue",
        "consta_entregue",
        "marcado como entregue",
        "marcado_entregue",
    ],
    "theme_delivery_delay": [
        "atraso",
        "atrasado",
        "atrasada",
        "atrasou",
        "demora",
        "demorou",
        "fora_prazo",
        "prazo",
        "rastreio",
        "transportadora",
        "correios",
    ],
    "theme_product_wrong_incomplete": [
        "produto_errado",
        "produto_diferente",
        "produto_incompleto",
        "faltou",
        "faltando",
        "incompleto",
        "diferente",
        "tamanho_errado",
        "cor_errada",
    ],
    "theme_product_defect_quality": [
        "defeito",
        "defeituoso",
        "defeituosa",
        "quebrado",
        "quebrada",
        "quebrados",
        "danificado",
        "danificada",
        "danificados",
        "qualidade_ruim",
        "pessimo",
        "ruim",
        "nao_funciona",
        "mal_acabado",
    ],
    "theme_seller_service_refund": [
        "reembolso",
        "estorno",
        "devolucao",
        "pedi_reembolso",
        "pedi_estorno",
        "atendimento",
        "sem_resposta",
        "contato",
        "vendedor",
        "reclamei",
        "troca",
    ],
    "theme_positive_recommendation": [
        "recomendo",
        "gostei",
        "otimo",
        "excelente",
        "bom",
        "perfeito",
        "chegou_antes",
        "dentro_prazo",
    ],
}

THEME_LABELS = {
    "theme_delivery_not_received": "Delivery - Not Received",
    "theme_delivery_delay": "Delivery - Delay",
    "theme_product_wrong_incomplete": "Product - Wrong/Incomplete",
    "theme_product_defect_quality": "Product - Defect/Quality",
    "theme_seller_service_refund": "Seller/Service/Refund",
    "theme_positive_recommendation": "Positive Recommendation",
    "theme_other": "Other Complaint",
}


def load_reviews() -> pd.DataFrame:
    if not RAW_REVIEWS_PATH.exists():
        raise FileNotFoundError(f"Required review CSV not found: {RAW_REVIEWS_PATH}")
    return pd.read_csv(RAW_REVIEWS_PATH)


def normalize_accents(text: str) -> str:
    text = unicodedata.normalize("NFKD", str(text))
    return "".join(char for char in text if not unicodedata.combining(char))


def clean_review_text(text: str) -> str:
    text = str(text).lower()
    text = re.sub(r"https?://\S+|www\.\S+", " ", text)
    text = re.sub(r"\S+@\S+", " ", text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"[\r\n\t]+", " ", text)
    text = re.sub(r"[^a-záàâãéêíóôõúç0-9\s.,;:!?/-]", " ", text)
    text = re.sub(r"([!?.,;:/-])\1+", r"\1", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def normalize_for_matching(text: str) -> str:
    text = normalize_accents(text).lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def normalize_pattern(text: str) -> str:
    text = normalize_accents(text).lower()
    text = re.sub(r"[^a-z0-9_\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def apply_phrase_replacements(text: str) -> str:
    phrase_text = f" {normalize_for_matching(text)} "
    for phrase, replacement in PHRASE_REPLACEMENTS:
        phrase_text = phrase_text.replace(f" {phrase} ", f" {replacement} ")
    return re.sub(r"\s+", " ", phrase_text).strip()


def tokenize_clean_text(text: str) -> list[str]:
    return re.findall(TOKEN_PATTERN, str(text).lower())


def tokenize_normalized_text(text: str) -> list[str]:
    return re.findall(NORMALIZED_TOKEN_PATTERN, str(text).lower())


def load_stopwords(tokens: list[str]) -> tuple[set[str], set[str]]:
    stopwords = set(FALLBACK_PORTUGUESE_STOPWORDS)
    try:
        from nltk.corpus import stopwords as nltk_stopwords

        stopwords.update(nltk_stopwords.words("portuguese"))
    except Exception as exc:
        warnings.warn(f"NLTK Portuguese stopwords unavailable; using fallback list. Reason: {exc}")

    matching_stopwords = {normalize_for_matching(word) for word in stopwords}
    matching_stopwords -= {normalize_for_matching(word) for word in NEGATION_WORDS}

    token_counts = Counter(tokens)
    for candidate in DOMAIN_STOPWORD_CANDIDATES:
        if token_counts.get(candidate, 0) >= 50:
            matching_stopwords.add(candidate)

    protected_phrases = {replacement for _, replacement in PHRASE_REPLACEMENTS}
    topic_stopwords = matching_stopwords | {
        "nao",
        "produto",
        "produtos",
        "pedido",
        "compra",
        "comprei",
        "recebi",
        "veio",
        "ainda",
        "agora",
        "momento",
        "apenas",
        "somente",
        "dois",
        "duas",
        "hoje",
        "nada",
        "quero",
        "saber",
        "dia",
        "dias",
        "loja",
        "entrega",
        "entregue",
        "chegou",
        "comprado",
        "comprar",
    }
    topic_stopwords -= protected_phrases

    return matching_stopwords, topic_stopwords


def maybe_get_stemmer():
    try:
        from nltk.stem import RSLPStemmer

        return RSLPStemmer()
    except Exception:
        warnings.warn("RSLPStemmer unavailable; continuing without stemming.")
        return None


def prepare_cleaned_reviews(reviews: pd.DataFrame) -> pd.DataFrame:
    title = reviews["review_comment_title"].fillna("").astype(str)
    message = reviews["review_comment_message"].fillna("").astype(str)
    review_text_raw = (title + " " + message).str.replace(r"\s+", " ", regex=True).str.strip()

    cleaned = reviews[
        [
            "review_id",
            "order_id",
            "review_score",
            "review_comment_title",
            "review_comment_message",
        ]
    ].copy()
    cleaned["review_text_raw"] = review_text_raw
    cleaned["clean_text"] = cleaned["review_text_raw"].apply(clean_review_text)
    cleaned["normalized_text"] = cleaned["clean_text"].apply(normalize_for_matching)
    cleaned["phrase_text"] = cleaned["normalized_text"].apply(apply_phrase_replacements)
    cleaned["token_count"] = cleaned["clean_text"].apply(lambda text: len(tokenize_clean_text(text)))
    cleaned["has_text"] = cleaned["token_count"] > 0
    cleaned["is_low_rating"] = cleaned["review_score"] <= 2

    return cleaned[
        [
            "review_id",
            "order_id",
            "review_score",
            "review_text_raw",
            "clean_text",
            "normalized_text",
            "phrase_text",
            "token_count",
            "has_text",
            "is_low_rating",
        ]
    ]


def tag_review_themes(cleaned: pd.DataFrame) -> pd.DataFrame:
    tags = cleaned[["review_id", "order_id", "review_score", "phrase_text"]].copy()

    for theme, patterns in THEME_PATTERNS.items():
        normalized_patterns = [normalize_pattern(pattern) for pattern in patterns]
        tags[theme] = tags["phrase_text"].apply(
            lambda text: any(pattern in text for pattern in normalized_patterns)
        )

    theme_cols = list(THEME_PATTERNS.keys())
    tags["theme_count"] = tags[theme_cols].sum(axis=1).astype(int)
    tags["theme_other"] = tags["theme_count"] == 0
    tags["theme_count"] = tags[theme_cols + ["theme_other"]].sum(axis=1).astype(int)

    return tags[
        [
            "review_id",
            "order_id",
            "review_score",
            *theme_cols,
            "theme_other",
            "theme_count",
        ]
    ]


def summarize_themes(tags: pd.DataFrame, cleaned: pd.DataFrame) -> pd.DataFrame:
    theme_columns = [*THEME_PATTERNS.keys(), "theme_other"]
    tags_with_text = tags.merge(
        cleaned[["review_id", "has_text"]],
        on="review_id",
        how="left",
    )
    low_rating = tags_with_text[
        (tags_with_text["review_score"] <= 2) & (tags_with_text["has_text"])
    ].copy()
    denominator = max(len(low_rating), 1)
    rows = []

    for theme in theme_columns:
        matched = low_rating[low_rating[theme]]
        rows.append(
            {
                "theme": THEME_LABELS[theme],
                "review_count": int(len(matched)),
                "percentage_of_low_rating_reviews": round(len(matched) * 100.0 / denominator, 2),
                "avg_review_score": round(float(matched["review_score"].mean()), 2)
                if len(matched)
                else None,
                "sample_keywords": ", ".join(THEME_PATTERNS.get(theme, ["no matched theme"])[:8]),
            }
        )

    return pd.DataFrame(rows).sort_values("review_count", ascending=False)


def vectorizer_tokenizer(text: str) -> list[str]:
    return tokenize_normalized_text(text)


def make_vectorizer(stopwords: set[str], kind: str):
    vectorizer_cls = TfidfVectorizer if kind == "tfidf" else CountVectorizer
    return vectorizer_cls(
        tokenizer=vectorizer_tokenizer,
        token_pattern=None,
        stop_words=sorted(stopwords),
        ngram_range=(1, 2),
        min_df=10,
        max_df=0.8,
        max_features=3000,
    )


def get_top_terms_for_segment(segment_name: str, texts: pd.Series, stopwords: set[str], top_n=30):
    if len(texts) == 0:
        return []

    tfidf_vectorizer = make_vectorizer(stopwords, "tfidf")
    count_vectorizer = make_vectorizer(stopwords, "count")

    try:
        tfidf_matrix = tfidf_vectorizer.fit_transform(texts)
        count_matrix = count_vectorizer.fit_transform(texts)
    except ValueError:
        return []

    tfidf_terms = np.array(tfidf_vectorizer.get_feature_names_out())
    count_terms = np.array(count_vectorizer.get_feature_names_out())
    mean_tfidf = np.asarray(tfidf_matrix.mean(axis=0)).ravel()
    raw_counts = np.asarray(count_matrix.sum(axis=0)).ravel()
    count_lookup = dict(zip(count_terms, raw_counts))

    top_indices = mean_tfidf.argsort()[::-1][:top_n]
    rows = []
    for idx in top_indices:
        term = tfidf_terms[idx]
        rows.append(
            {
                "segment": segment_name,
                "term": term,
                "score_or_weight": round(float(mean_tfidf[idx]), 6),
                "raw_count": int(count_lookup.get(term, 0)),
            }
        )
    return rows


def build_top_terms(cleaned: pd.DataFrame, stopwords: set[str]) -> pd.DataFrame:
    text_reviews = cleaned[cleaned["has_text"]].copy()
    segments = {
        "review_score_1": text_reviews[text_reviews["review_score"] == 1],
        "review_score_2": text_reviews[text_reviews["review_score"] == 2],
        "low_rating_score_1_2": text_reviews[text_reviews["review_score"] <= 2],
        "high_rating_score_4_5": text_reviews[text_reviews["review_score"] >= 4],
        "all_text_reviews": text_reviews,
    }

    rows = []
    for segment, data in segments.items():
        rows.extend(get_top_terms_for_segment(segment, data["phrase_text"], stopwords))
    return pd.DataFrame(rows)


def label_topic(top_terms: list[str]) -> str:
    joined = " ".join(top_terms)
    theme_scores = {}
    for theme, patterns in THEME_PATTERNS.items():
        normalized_patterns = [normalize_pattern(pattern) for pattern in patterns]
        theme_scores[theme] = sum(1 for pattern in normalized_patterns if pattern in joined)

    best_theme, score = max(theme_scores.items(), key=lambda item: item[1])
    if score == 0:
        return "Other Complaint"
    return THEME_LABELS[best_theme]


def build_nmf_topics(cleaned: pd.DataFrame, stopwords: set[str], n_topics=6) -> pd.DataFrame:
    low_text = cleaned[(cleaned["is_low_rating"]) & (cleaned["has_text"])].copy()
    if len(low_text) < n_topics:
        return pd.DataFrame(columns=["topic_id", "top_terms", "manual_topic_label", "review_count"])

    vectorizer = TfidfVectorizer(
        tokenizer=vectorizer_tokenizer,
        token_pattern=None,
        stop_words=sorted(stopwords),
        ngram_range=(1, 2),
        min_df=10,
        max_df=0.6,
        max_features=2000,
    )

    try:
        matrix = vectorizer.fit_transform(low_text["phrase_text"])
    except ValueError:
        return pd.DataFrame(columns=["topic_id", "top_terms", "manual_topic_label", "review_count"])

    from sklearn.decomposition import NMF

    nmf = NMF(
        n_components=n_topics,
        random_state=42,
        init="nndsvda",
        max_iter=500,
    )
    doc_topics = nmf.fit_transform(matrix)
    dominant_topics = doc_topics.argmax(axis=1)
    topic_counts = Counter(dominant_topics)
    terms = np.array(vectorizer.get_feature_names_out())

    rows = []
    for topic_id, weights in enumerate(nmf.components_):
        top_terms = terms[weights.argsort()[::-1][:12]].tolist()
        rows.append(
            {
                "topic_id": int(topic_id),
                "top_terms": ", ".join(top_terms),
                "manual_topic_label": label_topic(top_terms),
                "review_count": int(topic_counts.get(topic_id, 0)),
            }
        )

    return pd.DataFrame(rows).sort_values("review_count", ascending=False)


def build_lda_topics(cleaned: pd.DataFrame, stopwords: set[str], n_topics=6) -> pd.DataFrame:
    low_text = cleaned[(cleaned["is_low_rating"]) & (cleaned["has_text"])].copy()
    if len(low_text) < n_topics:
        return pd.DataFrame(columns=["topic_id", "top_terms", "manual_topic_label", "review_count"])

    vectorizer = CountVectorizer(
        tokenizer=vectorizer_tokenizer,
        token_pattern=None,
        stop_words=sorted(stopwords),
        ngram_range=(1, 2),
        min_df=5,
        max_df=0.6,
        max_features=2000,
    )

    try:
        matrix = vectorizer.fit_transform(low_text["phrase_text"])
    except ValueError:
        return pd.DataFrame(columns=["topic_id", "top_terms", "manual_topic_label", "review_count"])

    lda = LatentDirichletAllocation(
        n_components=n_topics,
        random_state=42,
        learning_method="batch",
        max_iter=30,
    )
    doc_topics = lda.fit_transform(matrix)
    dominant_topics = doc_topics.argmax(axis=1)
    topic_counts = Counter(dominant_topics)
    terms = np.array(vectorizer.get_feature_names_out())

    rows = []
    for topic_id, weights in enumerate(lda.components_):
        top_terms = terms[weights.argsort()[::-1][:12]].tolist()
        rows.append(
            {
                "topic_id": int(topic_id),
                "top_terms": ", ".join(top_terms),
                "manual_topic_label": label_topic(top_terms),
                "review_count": int(topic_counts.get(topic_id, 0)),
            }
        )

    return pd.DataFrame(rows).sort_values("review_count", ascending=False)


def build_audit(reviews: pd.DataFrame, cleaned: pd.DataFrame) -> dict:
    reviews_with_title = reviews["review_comment_title"].fillna("").astype(str).str.strip() != ""
    reviews_with_message = reviews["review_comment_message"].fillna("").astype(str).str.strip() != ""
    low_rating = cleaned["is_low_rating"]
    has_text = cleaned["has_text"]

    return {
        "total_reviews": int(len(cleaned)),
        "reviews_with_title": int(reviews_with_title.sum()),
        "reviews_with_message": int(reviews_with_message.sum()),
        "reviews_with_any_text": int(has_text.sum()),
        "low_rating_reviews": int(low_rating.sum()),
        "low_rating_reviews_with_text": int((low_rating & has_text).sum()),
        "percentage_reviews_with_text": round(float(has_text.mean() * 100.0), 2),
        "percentage_low_rating_with_text": round(
            float((low_rating & has_text).sum() * 100.0 / max(low_rating.sum(), 1)),
            2,
        ),
        "median_token_count_all_text": float(cleaned.loc[has_text, "token_count"].median()),
        "median_token_count_low_rating_text": float(
            cleaned.loc[low_rating & has_text, "token_count"].median()
        ),
    }


def write_outputs(
    cleaned: pd.DataFrame,
    tags: pd.DataFrame,
    summary: pd.DataFrame,
    top_terms: pd.DataFrame,
    nmf_topics: pd.DataFrame,
    topics: pd.DataFrame,
    audit: dict,
):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    cleaned.to_csv(CLEANED_PATH, index=False)
    tags.to_csv(THEME_TAGS_PATH, index=False)
    summary.to_csv(THEME_SUMMARY_PATH, index=False)
    top_terms.to_csv(TOP_TERMS_PATH, index=False)
    nmf_topics.to_csv(NMF_TOPICS_PATH, index=False)
    topics.to_csv(TOPICS_PATH, index=False)
    AUDIT_PATH.write_text(json.dumps(audit, indent=2), encoding="utf-8")


def main():
    print("Loading order reviews...")
    reviews = load_reviews()
    cleaned = prepare_cleaned_reviews(reviews)

    all_normalized_tokens = [
        token
        for text in cleaned.loc[cleaned["has_text"], "normalized_text"]
        for token in tokenize_normalized_text(text)
    ]
    matching_stopwords, topic_stopwords = load_stopwords(all_normalized_tokens)
    stemmer = maybe_get_stemmer()
    if stemmer is not None:
        print("RSLPStemmer available for optional stemming support; final labels use readable terms.")

    print("Tagging complaint themes...")
    tags = tag_review_themes(cleaned)
    summary = summarize_themes(tags, cleaned)

    print("Extracting TF-IDF top terms...")
    top_terms = build_top_terms(cleaned, matching_stopwords)

    print("Running preferred NMF topics...")
    nmf_topics = build_nmf_topics(cleaned, topic_stopwords)

    print("Running exploratory LDA topics...")
    topics = build_lda_topics(cleaned, topic_stopwords)

    audit = build_audit(reviews, cleaned)
    write_outputs(cleaned, tags, summary, top_terms, nmf_topics, topics, audit)

    print("\nNLP audit:")
    print(json.dumps(audit, indent=2))

    print("\nTop low-rating complaint themes:")
    print(summary.head(10).to_string(index=False))

    print("\nTop low-rating terms/bigrams:")
    low_terms = top_terms[top_terms["segment"] == "low_rating_score_1_2"].head(15)
    print(low_terms.to_string(index=False))

    print("\nNMF topic summary:")
    print(nmf_topics.to_string(index=False))

    print("\nLDA topic summary:")
    print(topics.to_string(index=False))

    print("\nSaved outputs:")
    for path in [
        CLEANED_PATH,
        THEME_TAGS_PATH,
        THEME_SUMMARY_PATH,
        TOP_TERMS_PATH,
        NMF_TOPICS_PATH,
        TOPICS_PATH,
        AUDIT_PATH,
    ]:
        print(f"- {path.relative_to(ROOT_DIR)}")


if __name__ == "__main__":
    main()

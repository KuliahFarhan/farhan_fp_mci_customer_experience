import json
import os
from pathlib import Path

import clickhouse_connect
import joblib
import matplotlib.pyplot as plt
import pandas as pd
from dotenv import load_dotenv
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import OneHotEncoder


NUMERICAL_FEATURES = [
    "delivery_days",
    "delay_days",
    "item_count",
    "seller_count",
    "total_price",
    "total_freight",
    "avg_price",
    "avg_freight",
]

CATEGORICAL_FEATURES = [
    "delivery_status",
    "delay_bucket",
    "customer_state",
    "customer_city",
    "main_product_category",
    "main_seller_state",
]

TARGET_COLUMN = "is_low_rating_2"
CATEGORICAL_MAX_LEVELS = {
    "customer_city": 100,
    "main_product_category": 80,
}
MODEL_PATH = Path("models/low_rating_model.pkl")
METRICS_PATH = Path("models/low_rating_metrics.json")
FEATURE_IMPORTANCE_PATH = Path("docs/assets/ml_feature_importance.png")


def get_clickhouse_client():
    load_dotenv()
    return clickhouse_connect.get_client(
        host=os.getenv("CLICKHOUSE_HOST", "localhost"),
        port=int(os.getenv("CLICKHOUSE_PORT", 8123)),
        username=os.getenv("CLICKHOUSE_USER", "default"),
        password=os.getenv("CLICKHOUSE_PASSWORD", "password"),
        database=os.getenv("CLICKHOUSE_DATABASE", "fp_mci_customer_experience"),
    )


def build_dataset_query():
    return """
    WITH item_features AS (
        SELECT
            order_id,
            count() AS item_count,
            uniqExact(seller_id) AS seller_count,
            sum(price) AS total_price,
            sum(freight_value) AS total_freight,
            avg(price) AS avg_price,
            avg(freight_value) AS avg_freight,
            argMax(coalesce(nullIf(product_category_name_english, ''), nullIf(product_category_name, ''), 'unknown'), price) AS main_product_category,
            argMax(coalesce(nullIf(seller_state, ''), 'unknown'), price) AS main_seller_state
        FROM mart_customer_experience_items
        WHERE review_score IS NOT NULL
        GROUP BY order_id
    )
    SELECT
        o.order_id,
        o.is_low_rating_2,
        o.delivery_days,
        o.delay_days,
        o.delivery_status,
        o.delay_bucket,
        o.customer_state,
        o.customer_city,
        i.item_count,
        i.seller_count,
        i.total_price,
        i.total_freight,
        i.avg_price,
        i.avg_freight,
        i.main_product_category,
        i.main_seller_state
    FROM mart_customer_experience_orders AS o
    LEFT JOIN item_features AS i ON o.order_id = i.order_id
    WHERE o.review_score IS NOT NULL
    """


def load_dataset():
    client = get_clickhouse_client()
    try:
        result = client.query_df(build_dataset_query())
    finally:
        client.close()
    return result


def get_available_features(df):
    numerical = [col for col in NUMERICAL_FEATURES if col in df.columns]
    categorical = [col for col in CATEGORICAL_FEATURES if col in df.columns]
    return numerical, categorical


def make_one_hot_encoder():
    try:
        return OneHotEncoder(handle_unknown="ignore", sparse_output=True)
    except TypeError:
        return OneHotEncoder(handle_unknown="ignore", sparse=True)


def cap_high_cardinality_categories(df, categorical_features):
    df = df.copy()
    for column in categorical_features:
        if column in df.columns:
            df[column] = df[column].replace("", "unknown").fillna("unknown")
    for column, max_levels in CATEGORICAL_MAX_LEVELS.items():
        if column not in categorical_features:
            continue
        top_values = df[column].value_counts(dropna=True).head(max_levels).index
        df[column] = df[column].where(df[column].isin(top_values), "other")
    return df


def build_preprocessor(numerical_features, categorical_features):
    return ColumnTransformer(
        transformers=[
            (
                "num",
                Pipeline(
                    steps=[
                        ("imputer", SimpleImputer(strategy="median")),
                        ("scaler", StandardScaler()),
                    ]
                ),
                numerical_features,
            ),
            (
                "cat",
                Pipeline(
                    steps=[
                        ("imputer", SimpleImputer(strategy="most_frequent")),
                        ("encoder", make_one_hot_encoder()),
                    ]
                ),
                categorical_features,
            ),
        ]
    )


def build_models(preprocessor):
    return {
        "logistic_regression": Pipeline(
            steps=[
                ("preprocess", preprocessor),
                (
                    "model",
                    LogisticRegression(
                        class_weight="balanced",
                        max_iter=1000,
                        random_state=42,
                    ),
                ),
            ]
        ),
        "random_forest": Pipeline(
            steps=[
                ("preprocess", preprocessor),
                (
                    "model",
                    RandomForestClassifier(
                        n_estimators=80,
                        max_depth=8,
                        random_state=42,
                        class_weight="balanced",
                        n_jobs=-1,
                    ),
                ),
            ]
        ),
    }


def evaluate_model(model, X_test, y_test):
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]
    return {
        "accuracy": accuracy_score(y_test, y_pred),
        "precision": precision_score(y_test, y_pred, zero_division=0),
        "recall": recall_score(y_test, y_pred, zero_division=0),
        "f1_score": f1_score(y_test, y_pred, zero_division=0),
        "roc_auc": roc_auc_score(y_test, y_proba),
        "confusion_matrix": confusion_matrix(y_test, y_pred).tolist(),
        "classification_report": classification_report(y_test, y_pred, zero_division=0),
    }


def get_feature_names(pipeline, numerical_features, categorical_features):
    preprocessor = pipeline.named_steps["preprocess"]
    names = list(numerical_features)
    if categorical_features:
        encoder = preprocessor.named_transformers_["cat"].named_steps["encoder"]
        names.extend(encoder.get_feature_names_out(categorical_features).tolist())
    return names


def get_feature_importance(pipeline, numerical_features, categorical_features):
    model = pipeline.named_steps["model"]
    feature_names = get_feature_names(pipeline, numerical_features, categorical_features)

    if hasattr(model, "feature_importances_"):
        values = model.feature_importances_
    elif hasattr(model, "coef_"):
        values = model.coef_[0]
    else:
        return pd.DataFrame(columns=["feature", "importance"])

    return (
        pd.DataFrame({"feature": feature_names, "importance": values})
        .assign(abs_importance=lambda df: df["importance"].abs())
        .sort_values("abs_importance", ascending=False)
        .drop(columns=["abs_importance"])
    )


def save_feature_importance_chart(feature_importance):
    if feature_importance.empty:
        return

    FEATURE_IMPORTANCE_PATH.parent.mkdir(parents=True, exist_ok=True)
    top_features = feature_importance.head(20).sort_values("importance")

    plt.figure(figsize=(10, 7))
    plt.barh(top_features["feature"], top_features["importance"])
    plt.title("Top ML Feature Importance")
    plt.xlabel("Importance")
    plt.tight_layout()
    plt.savefig(FEATURE_IMPORTANCE_PATH, dpi=150)
    plt.close()


def train_models(df):
    numerical_features, categorical_features = get_available_features(df)
    feature_columns = numerical_features + categorical_features

    if TARGET_COLUMN not in df.columns:
        raise ValueError(f"Missing target column: {TARGET_COLUMN}")
    if not feature_columns:
        raise ValueError("No usable feature columns found.")

    df = cap_high_cardinality_categories(df, categorical_features)
    X = df[feature_columns]
    y = df[TARGET_COLUMN].astype(int)

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y,
    )

    preprocessor = build_preprocessor(numerical_features, categorical_features)
    models = build_models(preprocessor)
    metrics = {}
    fitted_models = {}

    for model_name, model in models.items():
        print(f"\nTraining {model_name}...")
        model.fit(X_train, y_train)
        model_metrics = evaluate_model(model, X_test, y_test)
        metrics[model_name] = model_metrics
        fitted_models[model_name] = model

        print(
            f"{model_name}: "
            f"accuracy={model_metrics['accuracy']:.4f}, "
            f"precision={model_metrics['precision']:.4f}, "
            f"recall={model_metrics['recall']:.4f}, "
            f"f1={model_metrics['f1_score']:.4f}, "
            f"roc_auc={model_metrics['roc_auc']:.4f}"
        )
        print("Confusion matrix:", model_metrics["confusion_matrix"])
        print(model_metrics["classification_report"])

    best_model_name = max(
        metrics,
        key=lambda name: (
            metrics[name]["f1_score"],
            metrics[name]["recall"],
            metrics[name]["roc_auc"],
        ),
    )
    best_model = fitted_models[best_model_name]
    feature_importance = get_feature_importance(
        best_model,
        numerical_features,
        categorical_features,
    )

    return {
        "best_model_name": best_model_name,
        "best_model": best_model,
        "metrics": metrics,
        "numerical_features": numerical_features,
        "categorical_features": categorical_features,
        "feature_importance": feature_importance,
        "target_distribution": y.value_counts().sort_index().to_dict(),
    }


def print_dataset_overview(df):
    numerical_features, categorical_features = get_available_features(df)
    target_counts = df[TARGET_COLUMN].value_counts().sort_index()

    print("Dataset shape:", df.shape)
    print("\nTarget distribution:")
    print(target_counts)
    print("\nTarget distribution (%):")
    print((target_counts * 100.0 / len(df)).round(2))
    print("\nMissing values:")
    print(df.isna().sum().sort_values(ascending=False).head(30))
    print("\nNumerical features:", numerical_features)
    print("Categorical features:", categorical_features)


def main():
    df = load_dataset()
    print_dataset_overview(df)

    result = train_models(df)
    best_model_name = result["best_model_name"]

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(result["best_model"], MODEL_PATH)

    save_feature_importance_chart(result["feature_importance"])

    metrics_payload = {
        "best_model": best_model_name,
        "target": TARGET_COLUMN,
        "target_distribution": result["target_distribution"],
        "numerical_features": result["numerical_features"],
        "categorical_features": result["categorical_features"],
        "metrics": result["metrics"],
        "top_feature_importance": result["feature_importance"].head(20).to_dict(orient="records"),
    }

    with open(METRICS_PATH, "w", encoding="utf-8") as file:
        json.dump(metrics_payload, file, indent=2)

    print(f"\nBest model: {best_model_name}")
    print(f"Saved model to {MODEL_PATH}")
    print(f"Saved metrics to {METRICS_PATH}")
    if FEATURE_IMPORTANCE_PATH.exists():
        print(f"Saved feature importance chart to {FEATURE_IMPORTANCE_PATH}")


if __name__ == "__main__":
    main()

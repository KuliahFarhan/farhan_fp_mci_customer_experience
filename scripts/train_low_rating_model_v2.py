import json
import os
import sys
import warnings
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import clickhouse_connect
import joblib
import numpy as np
import pandas as pd
from dotenv import load_dotenv
from sklearn.base import clone
from sklearn.calibration import CalibratedClassifierCV
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    brier_score_loss,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from scripts.ml_v2_transformers import CategoryCapper

warnings.filterwarnings(
    "ignore",
    message="X does not have valid feature names, but LGBMClassifier was fitted with feature names",
)

try:
    from lightgbm import LGBMClassifier

    LIGHTGBM_AVAILABLE = True
except ImportError:
    LGBMClassifier = None
    LIGHTGBM_AVAILABLE = False


RANDOM_STATE = 42
TARGET_COLUMN = "low_rating"

NUMERIC_FEATURES = [
    "delivery_days",
    "delay_days",
    "is_late_delivery",
    "approval_delay_days",
    "seller_handling_days",
    "carrier_delivery_days",
    "estimated_delivery_window_days",
    "purchase_month",
    "purchase_day_of_week",
    "is_weekend_purchase",
    "item_count",
    "seller_count",
    "total_price",
    "total_freight",
    "avg_price",
    "avg_freight",
    "freight_to_price_ratio",
    "total_payment_value",
    "max_payment_installments",
    "payment_method_count",
]

CATEGORICAL_FEATURES = [
    "delivery_status",
    "delay_bucket",
    "main_payment_type",
    "main_product_category",
    "customer_state",
    "seller_state",
    "same_customer_seller_state",
    "customer_city",
]

CATEGORY_MAX_LEVELS = {
    "customer_city": 100,
    "main_product_category": 80,
}

MODELS_DIR = Path("models")
MODEL_PATH = MODELS_DIR / "low_rating_model_v2.pkl"
METRICS_PATH = MODELS_DIR / "low_rating_metrics_v2.json"
SCHEMA_PATH = MODELS_DIR / "low_rating_feature_schema_v2.json"
THRESHOLDS_PATH = MODELS_DIR / "low_rating_thresholds_v2.json"
SAMPLE_INPUT_PATH = MODELS_DIR / "low_rating_sample_input_v2.json"
MODEL_CARD_PATH = MODELS_DIR / "low_rating_model_card_v2.md"
LGBM_COMPARISON_PATH = MODELS_DIR / "low_rating_lgbm_comparison_v2.json"


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
            sum(freight_value) / nullIf(sum(price), 0) AS freight_to_price_ratio,
            argMax(coalesce(nullIf(product_category_name_english, ''), nullIf(product_category_name, ''), 'unknown'), price) AS main_product_category,
            argMax(coalesce(nullIf(seller_state, ''), 'unknown'), price) AS seller_state
        FROM mart_customer_experience_items
        WHERE review_score IS NOT NULL
        GROUP BY order_id
    ),
    payment_features AS (
        SELECT
            order_id,
            argMax(payment_type, payment_value) AS main_payment_type,
            sum(payment_value) AS total_payment_value,
            max(payment_installments) AS max_payment_installments,
            uniqExact(payment_type) AS payment_method_count
        FROM stg_order_payments
        GROUP BY order_id
    )
    SELECT
        o.order_id,
        if(o.review_score <= 2, 1, 0) AS low_rating,
        o.delivery_days,
        o.delay_days,
        if(o.delivery_status = 'late', 1, 0) AS is_late_delivery,
        o.delivery_status,
        o.delay_bucket,
        o.customer_state,
        o.customer_city,
        dateDiff('day', so.order_purchase_timestamp, so.order_approved_at) AS approval_delay_days,
        dateDiff('day', so.order_approved_at, so.order_delivered_carrier_date) AS seller_handling_days,
        dateDiff('day', so.order_delivered_carrier_date, so.order_delivered_customer_date) AS carrier_delivery_days,
        dateDiff('day', so.order_purchase_timestamp, so.order_estimated_delivery_date) AS estimated_delivery_window_days,
        toMonth(so.order_purchase_timestamp) AS purchase_month,
        toDayOfWeek(so.order_purchase_timestamp) AS purchase_day_of_week,
        if(toDayOfWeek(so.order_purchase_timestamp) IN (6, 7), 1, 0) AS is_weekend_purchase,
        i.item_count,
        i.seller_count,
        i.total_price,
        i.total_freight,
        i.avg_price,
        i.avg_freight,
        i.freight_to_price_ratio,
        i.main_product_category,
        i.seller_state,
        if(o.customer_state = i.seller_state, 'same_state', 'different_state') AS same_customer_seller_state,
        coalesce(nullIf(p.main_payment_type, ''), 'unknown') AS main_payment_type,
        p.total_payment_value,
        p.max_payment_installments,
        p.payment_method_count
    FROM mart_customer_experience_orders AS o
    LEFT JOIN stg_orders AS so ON o.order_id = so.order_id
    LEFT JOIN item_features AS i ON o.order_id = i.order_id
    LEFT JOIN payment_features AS p ON o.order_id = p.order_id
    WHERE o.review_score IS NOT NULL
    """


def load_dataset():
    client = get_clickhouse_client()
    try:
        return client.query_df(build_dataset_query())
    finally:
        client.close()


def make_one_hot_encoder():
    try:
        return OneHotEncoder(handle_unknown="ignore", sparse_output=False)
    except TypeError:
        return OneHotEncoder(handle_unknown="ignore", sparse=False)


def get_available_features(df):
    numeric = [feature for feature in NUMERIC_FEATURES if feature in df.columns]
    categorical = [feature for feature in CATEGORICAL_FEATURES if feature in df.columns]
    return numeric, categorical


def build_preprocessor(numeric_features, categorical_features):
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
                numeric_features,
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


def build_model_candidates(preprocessor, categorical_features, positive_count, negative_count):
    scale_pos_weight = negative_count / max(positive_count, 1)

    def base_steps():
        return [
            ("category_capper", CategoryCapper(categorical_features, CATEGORY_MAX_LEVELS)),
            ("preprocess", clone(preprocessor)),
        ]

    models = {
        "dummy": Pipeline(
            steps=base_steps()
            + [
                (
                    "model",
                    DummyClassifier(strategy="prior", random_state=RANDOM_STATE),
                )
            ]
        ),
        "logistic_regression": Pipeline(
            steps=base_steps()
            + [
                (
                    "model",
                    LogisticRegression(
                        class_weight="balanced",
                        max_iter=1500,
                        random_state=RANDOM_STATE,
                    ),
                )
            ]
        ),
        "random_forest": Pipeline(
            steps=base_steps()
            + [
                (
                    "model",
                    RandomForestClassifier(
                        n_estimators=120,
                        max_depth=10,
                        random_state=RANDOM_STATE,
                        class_weight="balanced_subsample",
                        n_jobs=-1,
                    ),
                )
            ]
        ),
        "hist_gradient_boosting": Pipeline(
            steps=base_steps()
            + [
                (
                    "model",
                    HistGradientBoostingClassifier(
                        max_iter=140,
                        max_leaf_nodes=31,
                        learning_rate=0.08,
                        l2_regularization=0.1,
                        random_state=RANDOM_STATE,
                        class_weight={0: 1.0, 1: scale_pos_weight},
                    ),
                )
            ]
        ),
    }

    if LIGHTGBM_AVAILABLE:
        models["lightgbm"] = Pipeline(
            steps=base_steps()
            + [
                (
                    "model",
                    LGBMClassifier(
                        objective="binary",
                        random_state=RANDOM_STATE,
                        class_weight="balanced",
                        n_estimators=300,
                        learning_rate=0.05,
                        num_leaves=31,
                        max_depth=-1,
                        subsample=0.8,
                        colsample_bytree=0.8,
                        min_child_samples=30,
                        reg_alpha=0.1,
                        reg_lambda=1.0,
                        n_jobs=-1,
                        verbosity=-1,
                    ),
                )
            ]
        )

    return models


def evaluate_probabilities(y_true, y_proba, threshold=0.5):
    y_pred = (y_proba >= threshold).astype(int)
    return {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision_low_rating": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall_low_rating": float(recall_score(y_true, y_pred, zero_division=0)),
        "f1_low_rating": float(f1_score(y_true, y_pred, zero_division=0)),
        "roc_auc": float(roc_auc_score(y_true, y_proba)),
        "pr_auc_average_precision": float(average_precision_score(y_true, y_proba)),
        "brier_score": float(brier_score_loss(y_true, y_proba)),
        "confusion_matrix": confusion_matrix(y_true, y_pred).tolist(),
        "classification_report": classification_report(y_true, y_pred, zero_division=0),
    }


def analyze_thresholds(y_true, y_proba, thresholds):
    rows = []
    for threshold in thresholds:
        y_pred = (y_proba >= threshold).astype(int)
        rows.append(
            {
                "threshold": float(threshold),
                "precision_low_rating": float(precision_score(y_true, y_pred, zero_division=0)),
                "recall_low_rating": float(recall_score(y_true, y_pred, zero_division=0)),
                "f1_low_rating": float(f1_score(y_true, y_pred, zero_division=0)),
                "predicted_positive_rate": float(y_pred.mean()),
                "confusion_matrix": confusion_matrix(y_true, y_pred).tolist(),
            }
        )
    return rows


def choose_threshold(threshold_rows):
    practical = [
        row
        for row in threshold_rows
        if row["precision_low_rating"] >= 0.35 and row["predicted_positive_rate"] <= 0.40
    ]
    candidates = practical or threshold_rows
    return max(
        candidates,
        key=lambda row: (
            row["recall_low_rating"],
            row["f1_low_rating"],
            row["precision_low_rating"],
        ),
    )


def select_model(metrics):
    non_dummy = {name: value for name, value in metrics.items() if name != "dummy"}
    return max(
        non_dummy,
        key=lambda name: (
            non_dummy[name]["roc_auc"],
            non_dummy[name]["pr_auc_average_precision"],
            -non_dummy[name]["brier_score"],
            non_dummy[name]["recall_low_rating"],
            non_dummy[name]["f1_low_rating"],
        ),
    )


def has_meaningful_lgbm_improvement(hist_result, lgbm_result):
    hist_cal = hist_result["calibrated_metrics_threshold_0_5"]
    lgbm_cal = lgbm_result["calibrated_metrics_threshold_0_5"]
    hist_thr = hist_result["selected_threshold_metrics"]
    lgbm_thr = lgbm_result["selected_threshold_metrics"]

    pr_auc_improves = (
        lgbm_cal["pr_auc_average_precision"]
        >= hist_cal["pr_auc_average_precision"] + 0.01
    )
    f1_improves = lgbm_thr["f1_low_rating"] >= hist_thr["f1_low_rating"] + 0.01
    recall_improves_safely = (
        lgbm_thr["recall_low_rating"] >= hist_thr["recall_low_rating"] + 0.03
        and lgbm_thr["precision_low_rating"] >= hist_thr["precision_low_rating"] - 0.05
    )
    brier_stays_good = (
        lgbm_cal["brier_score"] <= hist_cal["brier_score"] + 0.002
        and lgbm_cal["pr_auc_average_precision"] >= hist_cal["pr_auc_average_precision"] - 0.005
        and lgbm_thr["f1_low_rating"] >= hist_thr["f1_low_rating"] - 0.005
    )

    return pr_auc_improves or f1_improves or recall_improves_safely or brier_stays_good


def make_calibrated_classifier(estimator):
    try:
        return CalibratedClassifierCV(estimator=estimator, method="sigmoid", cv=3)
    except TypeError:
        return CalibratedClassifierCV(base_estimator=estimator, method="sigmoid", cv=3)


def build_feature_schema(df, numeric_features, categorical_features, sample_input):
    schema = {
        "target": TARGET_COLUMN,
        "numeric_features": numeric_features,
        "categorical_features": categorical_features,
        "feature_notes": {
            "leakage_prevention": "review_score and review-derived flags are excluded from simulator features.",
            "high_cardinality": "customer_city and main_product_category are grouped to top training levels plus other inside the saved pipeline.",
            "simulator_ready": "The saved pipeline accepts a one-row DataFrame or JSON payload with these feature names.",
        },
        "categorical_values": {},
        "sample_input": sample_input,
    }

    for column in categorical_features:
        values = (
            df[column]
            .replace("", "unknown")
            .fillna("unknown")
            .astype(str)
            .value_counts()
            .head(30)
            .index.tolist()
        )
        schema["categorical_values"][column] = values

    return schema


def create_sample_input(df, feature_columns):
    positive_rows = df[df[TARGET_COLUMN] == 1]
    source = positive_rows.iloc[0] if not positive_rows.empty else df.iloc[0]
    sample = {}
    for column in feature_columns:
        value = source[column]
        if pd.isna(value):
            sample[column] = None
        elif isinstance(value, (np.integer, np.floating)):
            sample[column] = value.item()
        else:
            sample[column] = value
    return sample


def save_model_card(payload):
    lines = [
        "# Low Rating Model v2 Card",
        "",
        "## Model Purpose",
        "Model ini mengestimasi risiko sebuah order mendapat review rendah untuk Customer Experience Simulator.",
        "",
        "## Target",
        "`low_rating = 1` jika `review_score <= 2`, dan `0` jika `review_score >= 3`. Order tanpa review dikeluarkan dari supervised training.",
        "",
        "## Features",
        "Model menggunakan fitur structured transaction, delivery, product, customer, seller, dan payment. Review text tidak digunakan karena muncul setelah pelanggan memberi review.",
        "",
        "## Leakage Prevention",
        "Fitur `review_score`, review-derived flags, dan review comments tidak digunakan sebagai fitur prediksi.",
        "",
        "## Metrics",
        f"Final model: `{payload['selected_model']}`",
        f"Selected threshold: `{payload['selected_threshold']:.2f}`",
        f"ROC-AUC: `{payload['final_metrics']['roc_auc']:.4f}`",
        f"PR-AUC: `{payload['final_metrics']['pr_auc_average_precision']:.4f}`",
        f"Recall low rating: `{payload['final_threshold_metrics']['recall_low_rating']:.4f}`",
        f"Precision low rating: `{payload['final_threshold_metrics']['precision_low_rating']:.4f}`",
        f"F1 low rating: `{payload['final_threshold_metrics']['f1_low_rating']:.4f}`",
        f"Brier score: `{payload['final_metrics']['brier_score']:.4f}`",
        "",
        "## Safe Claims",
        "- Model dapat digunakan sebagai risk estimator untuk monitoring customer experience.",
        "- Output model bersifat prediktif/asosiatif dan perlu dibaca bersama dashboard root cause.",
        "",
        "## Unsafe Claims",
        "- Jangan menyatakan model membuktikan penyebab review rendah secara kausal.",
        "- Jangan menggunakan skor risiko sebagai keputusan otomatis tanpa validasi bisnis.",
        "",
        "## Limitations",
        "- Banyak fitur delivery tersedia setelah pengiriman, sehingga model lebih cocok untuk post-delivery monitoring atau pre-review intervention.",
        "- Model belum memakai historical seller risk, historical category risk, atau NLP.",
        "- Class imbalance tetap perlu diperhatikan.",
    ]
    MODEL_CARD_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def save_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def main():
    print("Loading ML v2 dataset from ClickHouse...")
    df = load_dataset()
    numeric_features, categorical_features = get_available_features(df)
    feature_columns = numeric_features + categorical_features

    if TARGET_COLUMN not in df.columns:
        raise ValueError(f"Missing target column: {TARGET_COLUMN}")
    if not feature_columns:
        raise ValueError("No usable ML v2 features found.")

    print("Dataset shape:", df.shape)
    print("Target distribution:")
    print(df[TARGET_COLUMN].value_counts().sort_index())
    print("Numeric features:", numeric_features)
    print("Categorical features:", categorical_features)
    print("Missing values:")
    print(df[feature_columns + [TARGET_COLUMN]].isna().sum().sort_values(ascending=False).head(40))

    X = df[feature_columns]
    y = df[TARGET_COLUMN].astype(int)
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=RANDOM_STATE,
        stratify=y,
    )

    positive_count = int(y_train.sum())
    negative_count = int((y_train == 0).sum())
    preprocessor = build_preprocessor(numeric_features, categorical_features)
    models = build_model_candidates(preprocessor, categorical_features, positive_count, negative_count)

    metrics = {}
    fitted_models = {}
    for model_name, model in models.items():
        print(f"\nTraining {model_name}...")
        model.fit(X_train, y_train)
        y_proba = model.predict_proba(X_test)[:, 1]
        model_metrics = evaluate_probabilities(y_test, y_proba, threshold=0.5)
        metrics[model_name] = model_metrics
        fitted_models[model_name] = model
        print(
            f"{model_name}: "
            f"roc_auc={model_metrics['roc_auc']:.4f}, "
            f"pr_auc={model_metrics['pr_auc_average_precision']:.4f}, "
            f"precision={model_metrics['precision_low_rating']:.4f}, "
            f"recall={model_metrics['recall_low_rating']:.4f}, "
            f"f1={model_metrics['f1_low_rating']:.4f}, "
            f"brier={model_metrics['brier_score']:.4f}"
        )

    threshold_candidates = [0.30, 0.35, 0.40, 0.45, 0.50]
    comparison_model_names = [
        name
        for name in ["hist_gradient_boosting", "lightgbm"]
        if name in models
    ]
    calibrated_comparison = {}

    for model_name in comparison_model_names:
        print(f"Calibrating {model_name} with sigmoid calibration...")
        calibrated_candidate = make_calibrated_classifier(clone(models[model_name]))
        calibrated_candidate.fit(X_train, y_train)
        calibrated_proba = calibrated_candidate.predict_proba(X_test)[:, 1]
        calibrated_metrics = evaluate_probabilities(y_test, calibrated_proba, threshold=0.5)
        threshold_rows = analyze_thresholds(y_test, calibrated_proba, threshold_candidates)
        chosen_threshold = choose_threshold(threshold_rows)
        selected_threshold_metrics = next(
            row for row in threshold_rows if row["threshold"] == chosen_threshold["threshold"]
        )

        calibrated_comparison[model_name] = {
            "model": calibrated_candidate,
            "calibrated_metrics_threshold_0_5": calibrated_metrics,
            "threshold_analysis": threshold_rows,
            "selected_threshold": chosen_threshold["threshold"],
            "selected_threshold_metrics": selected_threshold_metrics,
            "calibrated_metrics_at_selected_threshold": evaluate_probabilities(
                y_test,
                calibrated_proba,
                threshold=chosen_threshold["threshold"],
            ),
        }

    selected_model_name = "hist_gradient_boosting"
    selection_reason = "HistGradientBoosting remains final ML v2 model."
    lightgbm_became_final = False

    if "lightgbm" in calibrated_comparison and "hist_gradient_boosting" in calibrated_comparison:
        if has_meaningful_lgbm_improvement(
            calibrated_comparison["hist_gradient_boosting"],
            calibrated_comparison["lightgbm"],
        ):
            selected_model_name = "lightgbm"
            selection_reason = "LightGBM showed meaningful improvement over HistGradientBoosting."
            lightgbm_became_final = True
        else:
            selection_reason = "LightGBM did not improve enough to replace HistGradientBoosting."
    elif "hist_gradient_boosting" not in calibrated_comparison:
        selected_model_name = select_model(metrics)
        selection_reason = "Fallback selection used because HistGradientBoosting comparison was unavailable."

    print(f"\nFinal selected model: {selected_model_name}")
    print("Selection reason:", selection_reason)

    selected_result = calibrated_comparison.get(selected_model_name)
    if selected_result:
        calibrated_model = selected_result["model"]
        calibrated_metrics = selected_result["calibrated_metrics_threshold_0_5"]
        threshold_rows = selected_result["threshold_analysis"]
        chosen_threshold = {"threshold": selected_result["selected_threshold"]}
        final_threshold_metrics = selected_result["selected_threshold_metrics"]
        final_metrics_at_threshold = selected_result["calibrated_metrics_at_selected_threshold"]
    else:
        calibrated_model = make_calibrated_classifier(clone(models[selected_model_name]))
        calibrated_model.fit(X_train, y_train)
        calibrated_proba = calibrated_model.predict_proba(X_test)[:, 1]
        calibrated_metrics = evaluate_probabilities(y_test, calibrated_proba, threshold=0.5)
        threshold_rows = analyze_thresholds(y_test, calibrated_proba, threshold_candidates)
        chosen_threshold = choose_threshold(threshold_rows)
        final_threshold_metrics = next(
            row for row in threshold_rows if row["threshold"] == chosen_threshold["threshold"]
        )
        final_metrics_at_threshold = evaluate_probabilities(
            y_test,
            calibrated_proba,
            threshold=chosen_threshold["threshold"],
        )

    uncalibrated_metrics = metrics[selected_model_name]

    lgbm_comparison_payload = {
        "lightgbm_available": LIGHTGBM_AVAILABLE,
        "lightgbm_became_final": lightgbm_became_final,
        "final_selected_model": selected_model_name,
        "selection_reason": selection_reason,
        "hist_gradient_boosting": calibrated_comparison.get("hist_gradient_boosting", {}),
        "lightgbm": calibrated_comparison.get("lightgbm", {}),
    }
    for model_payload in lgbm_comparison_payload.values():
        if isinstance(model_payload, dict):
            model_payload.pop("model", None)

    sample_input = create_sample_input(df, feature_columns)
    schema_payload = build_feature_schema(df, numeric_features, categorical_features, sample_input)

    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(calibrated_model, MODEL_PATH)

    metrics_payload = {
        "selected_model": selected_model_name,
        "selected_model_artifact": str(MODEL_PATH),
        "calibration": {
            "method": "sigmoid",
            "brier_before": uncalibrated_metrics["brier_score"],
            "brier_after": calibrated_metrics["brier_score"],
        },
        "selected_threshold": chosen_threshold["threshold"],
        "train_rows": int(len(X_train)),
        "test_rows": int(len(X_test)),
        "target_distribution": y.value_counts().sort_index().astype(int).to_dict(),
        "features": {
            "numeric": numeric_features,
            "categorical": categorical_features,
        },
        "model_metrics_threshold_0_5": metrics,
        "calibrated_model_comparison": lgbm_comparison_payload,
        "selected_uncalibrated_metrics_threshold_0_5": uncalibrated_metrics,
        "selected_calibrated_metrics_threshold_0_5": calibrated_metrics,
        "selected_calibrated_metrics_at_threshold": final_metrics_at_threshold,
    }
    thresholds_payload = {
        "threshold_candidates": threshold_rows,
        "selected_threshold": chosen_threshold["threshold"],
        "selection_rule": "Choose the highest recall threshold with precision >= 0.35 and predicted_positive_rate <= 0.40; fallback to highest recall/F1.",
        "risk_level_rule": {
            "low": "risk < 0.25",
            "medium": "0.25 <= risk < selected_threshold",
            "high": "risk >= selected_threshold",
        },
    }

    save_json(METRICS_PATH, metrics_payload)
    save_json(LGBM_COMPARISON_PATH, lgbm_comparison_payload)
    save_json(SCHEMA_PATH, schema_payload)
    save_json(THRESHOLDS_PATH, thresholds_payload)
    save_json(SAMPLE_INPUT_PATH, sample_input)
    save_model_card(
        {
            "selected_model": selected_model_name,
            "selected_threshold": chosen_threshold["threshold"],
            "final_metrics": calibrated_metrics,
            "final_threshold_metrics": final_threshold_metrics,
        }
    )

    print("\nFinal calibrated model:", selected_model_name)
    print("Selected threshold:", chosen_threshold["threshold"])
    print(
        "Final threshold metrics: "
        f"precision={final_threshold_metrics['precision_low_rating']:.4f}, "
        f"recall={final_threshold_metrics['recall_low_rating']:.4f}, "
        f"f1={final_threshold_metrics['f1_low_rating']:.4f}"
    )
    print(f"Saved model: {MODEL_PATH}")
    print(f"Saved metrics: {METRICS_PATH}")
    print(f"Saved LightGBM comparison: {LGBM_COMPARISON_PATH}")
    print(f"Saved schema: {SCHEMA_PATH}")
    print(f"Saved thresholds: {THRESHOLDS_PATH}")
    print(f"Saved sample input: {SAMPLE_INPUT_PATH}")
    print(f"Saved model card: {MODEL_CARD_PATH}")


if __name__ == "__main__":
    main()

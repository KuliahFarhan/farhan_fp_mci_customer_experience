import argparse
import json
import sys
import warnings
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import joblib
import pandas as pd

from scripts.ml_v2_transformers import CategoryCapper  # noqa: F401

warnings.filterwarnings(
    "ignore",
    message="X does not have valid feature names, but LGBMClassifier was fitted with feature names",
)


MODEL_PATH = Path("models/low_rating_model_v2.pkl")
THRESHOLDS_PATH = Path("models/low_rating_thresholds_v2.json")
SAMPLE_INPUT_PATH = Path("models/low_rating_sample_input_v2.json")


def load_json(path):
    if not path.exists():
        raise FileNotFoundError(f"Required file not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def risk_level(probability, selected_threshold):
    if probability < 0.25:
        return "Low"
    if probability < selected_threshold:
        return "Medium"
    return "High"


def predict(payload):
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"Model artifact not found: {MODEL_PATH}")

    thresholds = load_json(THRESHOLDS_PATH)
    selected_threshold = float(thresholds["selected_threshold"])
    model = joblib.load(MODEL_PATH)

    input_df = pd.DataFrame([payload])
    probability = float(model.predict_proba(input_df)[:, 1][0])
    return {
        "low_rating_risk": probability,
        "low_rating_risk_percentage": round(probability * 100, 2),
        "selected_threshold": selected_threshold,
        "risk_level": risk_level(probability, selected_threshold),
    }


def main():
    parser = argparse.ArgumentParser(description="Predict low-rating risk with ML v2 model.")
    parser.add_argument(
        "--input",
        type=str,
        default=None,
        help="Optional path to JSON payload. Uses models/low_rating_sample_input_v2.json when omitted.",
    )
    args = parser.parse_args()

    input_path = Path(args.input) if args.input else SAMPLE_INPUT_PATH
    payload = load_json(input_path)
    result = predict(payload)

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

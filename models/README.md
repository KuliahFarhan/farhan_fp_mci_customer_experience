# ML Low-Rating Risk Simulator

## Role

Folder ini berisi artefak **post-fulfillment low-rating risk simulator** untuk FP MCI 2026. Model digunakan sebagai supporting component untuk membantu Customer Experience Analyst mensimulasikan risiko low rating setelah sinyal fulfillment/delivery tersedia.

Model ini bukan causal model, bukan pre-order prediction system, dan bukan pengganti dashboard utama berbasis Airflow, ClickHouse, dan Metabase.

## Model Summary

- Model final: Calibrated LightGBM with isotonic calibration.
- Target: `low_rating = 1` jika `review_score <= 2`, selain itu 0.
- Dataset: 95,832 delivered orders with review.
- Feature count: 24 structured features.
- Split: 60% train, 20% calibration-validation, 20% final test.
- Threshold: 0.30.

## Final Test Metrics

| Metric | Value |
| --- | ---: |
| ROC-AUC | 0.7595 |
| Average Precision | 0.4623 |
| Precision @0.30 | 0.5882 |
| Recall @0.30 | 0.4020 |
| F1 @0.30 | 0.4776 |

## Tracked Artifacts

| File | Purpose |
| --- | --- |
| `calibrated_lgbm_low_rating.pkl` | Final calibrated LightGBM model. |
| `preprocessor.pkl` | Fitted imputer/encoder pipeline. |
| `feature_schema.json` | Feature schema, split metadata, leakage notes, and metrics. |
| `sample_inputs.json` | Example simulator inputs for Low, Medium, and High risk levels. |
| `predict_risk.py` | Helper script for single or batch prediction. |

## Usage

Run the helper from the repository root:

```bash
python models/predict_risk.py
```

By default, the helper loads artifacts from this `models/` folder. To use a different model directory:

```bash
MODEL_DIR=/path/to/models python models/predict_risk.py
```

Compatibility note: model artifacts are Python pickle/joblib files and should be loaded with a compatible scikit-learn version. The artifacts were created with scikit-learn 1.6.1; loading them with newer versions may raise persistence compatibility errors.

## Limitations

- Review text is excluded from model features to keep NLP separate and reduce leakage risk.
- Historical aggregate features based on review score are excluded.
- The model uses post-fulfillment signals, so it should not be described as a pre-order predictor.
- Performance is moderate and suitable for risk simulation, not for fully automated operational decisions.
- If artifact loading fails, check the local scikit-learn/joblib versions before changing the model files.

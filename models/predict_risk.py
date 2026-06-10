"""
predict_risk.py
Helper script untuk prediksi low-rating risk menggunakan model yang sudah di-train.
Model: Post-Delivery Low-Rating Risk Estimator (Calibrated LightGBM)
Framing: Risk scoring tool — bukan sistem prediksi operasional.
"""
import joblib
import json
import numpy as np
import pandas as pd
import os

MODEL_DIR = '/content/drive/MyDrive/FP_MCI_Data/Dataset/models'


def load_artifacts():
    """Load model, preprocessor, dan schema dari Drive."""
    model       = joblib.load(os.path.join(MODEL_DIR, 'calibrated_lgbm_low_rating.pkl'))
    preprocessor = joblib.load(os.path.join(MODEL_DIR, 'preprocessor.pkl'))
    with open(os.path.join(MODEL_DIR, 'feature_schema.json')) as f:
        schema = json.load(f)
    return model, preprocessor, schema


def assign_risk_level(prob):
    if prob >= 0.50:
        return 'High'
    elif prob >= 0.30:
        return 'Medium'
    return 'Low'


def predict_risk(input_dict, model, preprocessor, schema):
    """
    Melakukan prediksi untuk satu order.

    Parameters
    ----------
    input_dict : dict
        Dictionary dengan key = nama fitur (sesuai schema['feature_columns']).
    model : sklearn estimator
        Model calibrated yang sudah di-load.
    preprocessor : ColumnTransformer
        Preprocessor yang sudah di-fit pada training data.
    schema : dict
        Feature schema dari feature_schema.json.

    Returns
    -------
    dict : low_rating_risk, low_rating_risk_percentage, risk_level
    """
    feature_cols = schema['feature_columns']
    input_df = pd.DataFrame([input_dict])[feature_cols]
    X_transformed = preprocessor.transform(input_df)
    feature_names = schema['feature_names_after_transform']
    X_df = pd.DataFrame(X_transformed, columns=feature_names)
    prob = model.predict_proba(X_df)[0, 1]
    risk_level = assign_risk_level(prob)
    return {
        'low_rating_risk':            round(float(prob), 4),
        'low_rating_risk_percentage': round(float(prob) * 100, 2),
        'risk_level':                 risk_level,
    }


def predict_batch(df_input, model, preprocessor, schema):
    """
    Melakukan prediksi batch untuk DataFrame input.

    Parameters
    ----------
    df_input : pd.DataFrame
        DataFrame dengan kolom sesuai schema['feature_columns'].

    Returns
    -------
    pd.DataFrame : DataFrame input + kolom prediksi
    """
    feature_cols = schema['feature_columns']
    X_transformed = preprocessor.transform(df_input[feature_cols])
    feature_names = schema['feature_names_after_transform']
    X_df = pd.DataFrame(X_transformed, columns=feature_names)
    probs = model.predict_proba(X_df)[:, 1]
    result = df_input.copy()
    result['low_rating_risk']            = np.round(probs, 4)
    result['low_rating_risk_percentage'] = np.round(probs * 100, 2)
    result['risk_level']                 = [assign_risk_level(p) for p in probs]
    return result


# Contoh penggunaan
if __name__ == "__main__":
    model, preprocessor, schema = load_artifacts()
    with open(os.path.join(MODEL_DIR, 'sample_inputs.json')) as f:
        samples = json.load(f)
    # Prediksi satu input
    sample = {k: v for k, v in samples[0].items() if not k.startswith('_')}
    result = predict_risk(sample, model, preprocessor, schema)
    print('Sample prediction:', result)
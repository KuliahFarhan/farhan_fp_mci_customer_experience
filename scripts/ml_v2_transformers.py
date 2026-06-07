import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin


class CategoryCapper(BaseEstimator, TransformerMixin):
    """Group rare categories using levels learned from training data."""

    def __init__(self, columns=None, max_levels=None):
        self.columns = columns or []
        self.max_levels = max_levels or {}
        self.allowed_values_ = {}

    def fit(self, X, y=None):
        X = pd.DataFrame(X).copy()
        for column in self.columns:
            if column not in X.columns:
                continue
            values = X[column].replace("", "unknown").fillna("unknown").astype(str)
            max_levels = self.max_levels.get(column)
            if max_levels:
                self.allowed_values_[column] = set(values.value_counts().head(max_levels).index)
            else:
                self.allowed_values_[column] = set(values.unique())
        return self

    def transform(self, X):
        X = pd.DataFrame(X).copy()
        for column in self.columns:
            if column not in X.columns:
                continue
            values = X[column].replace("", "unknown").fillna("unknown").astype(str)
            allowed = self.allowed_values_.get(column)
            if column in self.max_levels and allowed is not None:
                X[column] = values.where(values.isin(allowed), "other")
            else:
                X[column] = values
        return X

from sklearn.base import BaseEstimator, TransformerMixin
import pandas as pd


class LabelMapper(BaseEstimator, TransformerMixin):
    """
    Custom transformer to map target labels from one value to another.
    For example, map -1 to 0.
    """
    def __init__(self, from_value, to_value):
        self.from_value = from_value
        self.to_value = to_value

    def fit(self, X, y=None):
        return self

    def transform(self, y):
        if isinstance(y, pd.Series):
            return y.replace(self.from_value, self.to_value)
        elif isinstance(y, pd.DataFrame):
            return y.apply(lambda col: col.replace(self.from_value, self.to_value))
        else:
            raise ValueError("Unsupported data type for label transformation.")
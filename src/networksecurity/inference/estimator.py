import joblib
from dataclasses import dataclass
from typing import Any
from src.networksecurity.logging import logger
from src.networksecurity.exception.exception import NetworkSecurityError


@dataclass
class NetworkModel:
    model: Any
    x_preprocessor: Any = None
    y_preprocessor: Any = None

    def predict(self, X):
        try:
            if self.x_preprocessor:
                X = self.x_preprocessor.transform(X)
            return self.model.predict(X)
        except Exception as e:
            raise NetworkSecurityError(e, logger)

    @classmethod
    def from_artifacts(cls, model_path, x_preprocessor_path=None, y_preprocessor_path=None):
        try:
            model = joblib.load(model_path)

            x_preprocessor = joblib.load(x_preprocessor_path) if x_preprocessor_path else None
            y_preprocessor = joblib.load(y_preprocessor_path) if y_preprocessor_path else None

            return cls(model=model, x_preprocessor=x_preprocessor, y_preprocessor=y_preprocessor)

        except Exception as e:
            raise NetworkSecurityError(e, logger)

    @classmethod
    def from_objects(cls, model, x_preprocessor=None, y_preprocessor=None):
        try:
            return cls(model=model, x_preprocessor=x_preprocessor, y_preprocessor=y_preprocessor)
        except Exception as e:
            raise NetworkSecurityError(e, logger)

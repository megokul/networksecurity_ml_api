from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler
from sklearn.pipeline import Pipeline

from src.networksecurity.exception.exception import NetworkSecurityError
from src.networksecurity.logging import logger


class ScalerFactory:
    """
    Factory to create scaling transformers.
    Supports: standard, minmax, robust.
    Easily extendable with new scalers.
    """
    _SUPPORTED_METHODS = {
        "standard": StandardScaler,
        "minmax": MinMaxScaler,
        "robust": RobustScaler
    }

    @staticmethod
    def get_scaler_pipeline(method: str, params: dict = None) -> Pipeline:
        try:
            if method in ScalerFactory._SUPPORTED_METHODS:
                scaler_class = ScalerFactory._SUPPORTED_METHODS[method]
                scaler = scaler_class(**(params or {}))
            else:
                raise ValueError(f"Unsupported scaler method: {method}")

            return Pipeline([("scaler", scaler)])

        except Exception as e:
            raise NetworkSecurityError(e, logger) from e

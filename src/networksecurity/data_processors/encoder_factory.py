from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder
from sklearn.pipeline import Pipeline

from src.networksecurity.exception.exception import NetworkSecurityError
from src.networksecurity.logging import logger


class EncoderFactory:
    """
    Factory to build encoding pipelines for categorical features.
    Supports: onehot, ordinal.
    Easily extendable with new encoders.
    """
    _SUPPORTED_METHODS = {
        "onehot": OneHotEncoder,
        "ordinal": OrdinalEncoder
    }

    @staticmethod
    def get_encoder_pipeline(method: str, params: dict = None) -> Pipeline:
        try:
            if method in EncoderFactory._SUPPORTED_METHODS:
                encoder_class = EncoderFactory._SUPPORTED_METHODS[method]
                encoder = encoder_class(**(params or {}))
            else:
                raise ValueError(f"Unsupported encoding method: {method}")

            return Pipeline([("encoder", encoder)])

        except Exception as e:
            raise NetworkSecurityError(e, logger) from e

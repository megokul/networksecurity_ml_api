from sklearn.experimental import enable_iterative_imputer  # noqa: F401
from sklearn.impute import KNNImputer, SimpleImputer, IterativeImputer
from sklearn.pipeline import Pipeline

from src.networksecurity.exception.exception import NetworkSecurityError
from src.networksecurity.logging import logger


class ImputerFactory:
    """
    Factory to generate sklearn-compatible imputer pipelines.
    Supports: knn, simple, iterative, and custom methods.
    Easily extendable with new methods.
    """
    _SUPPORTED_METHODS = {
        "knn": KNNImputer,
        "simple": SimpleImputer,
        "iterative": IterativeImputer,
    }

    @staticmethod
    def get_imputer_pipeline(method: str, params: dict) -> Pipeline:
        try:
            if method == "custom":
                if "custom_callable" not in params:
                    raise ValueError("Custom imputer requires a 'custom_callable' in params.")
                imputer = params["custom_callable"]()
            else:
                imputer_class = ImputerFactory._SUPPORTED_METHODS.get(method)
                if not imputer_class:
                    raise ValueError(f"Unsupported imputation method: {method}")
                imputer = imputer_class(**params)

            return Pipeline([("imputer", imputer)])

        except Exception as e:
            raise NetworkSecurityError(e, logger) from e

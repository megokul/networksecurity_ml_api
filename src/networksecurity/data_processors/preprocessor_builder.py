from sklearn.pipeline import Pipeline
from sklearn.experimental import enable_iterative_imputer
from src.networksecurity.data_processors.imputer_factory import ImputerFactory
from src.networksecurity.data_processors.scaler_factory import ScalerFactory
from src.networksecurity.data_processors.encoder_factory import EncoderFactory
from src.networksecurity.data_processors.label_mapper import LabelMapper
from src.networksecurity.exception.exception import NetworkSecurityError
from src.networksecurity.logging import logger


class PreprocessorBuilder:
    """
    Builds preprocessing pipelines for X and Y using dynamic configuration.
    Skips steps that are explicitly set to "none" or not provided at all.
    """

    STEP_BUILDERS = {
        "imputer": ImputerFactory.get_imputer_pipeline,
        "scaler": ScalerFactory.get_scaler_pipeline,
        "encoder": EncoderFactory.get_encoder_pipeline,
        "label_mapping": lambda method, params: LabelMapper(from_value=params["from"], to_value=params["to"])
    }

    def __init__(self, steps: dict, methods: dict):
        self.steps = steps or {}
        self.methods = methods or {}

    def _build_pipeline(self, section: str) -> Pipeline:
        try:
            pipeline_steps = []
            steps_to_build = self.steps.get(section, {})
            methods = self.methods.get(section, {})

            for step_name, method_name in steps_to_build.items():
                # Skip if explicitly marked as 'none' (case-insensitive)
                if method_name is None or str(method_name).lower() == "none":
                    logger.info(f"Skipping step '{step_name}' for '{section}' as it is set to 'none'.")
                    continue

                builder = self.STEP_BUILDERS.get(step_name)
                if not builder:
                    raise ValueError(f"Unsupported step: {step_name}")

                params = methods.get(step_name, {})
                pipeline_steps.append((step_name, builder(method_name, params)))

            return Pipeline(pipeline_steps)

        except Exception as e:
            raise NetworkSecurityError(e, logger) from e

    def build(self):
        try:
            x_pipeline = self._build_pipeline("x")
            y_pipeline = self._build_pipeline("y")
            return x_pipeline, y_pipeline
        except Exception as e:
            raise NetworkSecurityError(e, logger) from e

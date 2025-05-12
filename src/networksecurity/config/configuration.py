from pathlib import Path
import os

from src.networksecurity.constants.constants import (
    CONFIG_FILE_PATH,
    PARAMS_FILE_PATH,
    SCHEMA_FILE_PATH,
    TEMPLATES_FILE_PATH,
    MONGO_HANDLER_SUBDIR,
    MONGO_JSON_SUBDIR,
    DATA_INGESTION_SUBDIR,
    FEATURESTORE_SUBDIR,
    INGESTED_SUBDIR,
    DATA_VALIDATION_SUBDIR,
    VALIDATED_SUBDIR,
    REPORTS_SUBDIR,
    DATA_TRANSFORMATION_SUBDIR,
    TRANSFORMED_DATA_SUBDIR,
    DATA_TRAIN_SUBDIR,
    DATA_VAL_SUBDIR,
    DATA_TEST_SUBDIR,
    TRANSFORMED_OBJECT_SUBDIR,
    LOGS_ROOT,
    MODEL_TRAINER_SUBDIR,
    MODEL_EVALUATION_SUBDIR,
    PUSHED_MODEL_SUBDIR,
)

from src.networksecurity.entity.config_entity import (
    MongoHandlerConfig,
    DataIngestionConfig,
    DataValidationConfig,
    DataTransformationConfig,
    ModelTrainerConfig,
    ModelEvaluationConfig,
    ModelPusherConfig,
    S3HandlerConfig,
)

from src.networksecurity.utils.core import (
    read_yaml,
    replace_username_password_in_uri,
)
from src.networksecurity.utils.timestamp import get_shared_utc_timestamp
from src.networksecurity.logging import logger


class ConfigurationManager:
    """
    Loads YAML-based configuration and generates paths for all pipeline stages.
    Dynamically sets timestamped artifact directories per run.
    """
    _global_timestamp: str = None

    def __init__(
        self,
        config_filepath: Path = CONFIG_FILE_PATH,
        params_filepath: Path = PARAMS_FILE_PATH,
        schema_filepath: Path = SCHEMA_FILE_PATH,
        templates_filepath: Path = TEMPLATES_FILE_PATH,
    ) -> None:
        self._load_configs(config_filepath, params_filepath, schema_filepath, templates_filepath)
        self._initialize_paths()

    def _load_configs(self, config_filepath: Path, params_filepath: Path, schema_filepath: Path, templates_filepath: Path):
        self.config = read_yaml(config_filepath)
        self.params = read_yaml(params_filepath)
        self.schema = read_yaml(schema_filepath)
        self.templates = read_yaml(templates_filepath)

    def _initialize_paths(self) -> None:
        if ConfigurationManager._global_timestamp is None:
            ConfigurationManager._global_timestamp = get_shared_utc_timestamp()

        timestamp = ConfigurationManager._global_timestamp
        base_artifact_root = Path(self.config.project.artifacts_root)
        self.artifacts_root = base_artifact_root / timestamp

        self.logs_root = Path(LOGS_ROOT) / timestamp

    def get_logs_dir(self) -> Path:
        return self.logs_root

    def get_artifact_root(self) -> Path:
        return self.artifacts_root

    def get_mongo_handler_config(self) -> MongoHandlerConfig:
        mongo_cfg = self.config.mongo_handler
        root_dir = self.artifacts_root / MONGO_HANDLER_SUBDIR
        json_data_dir = root_dir / MONGO_JSON_SUBDIR

        mongodb_uri = replace_username_password_in_uri(
            base_uri=os.getenv("MONGODB_URI_BASE"),
            username=os.getenv("MONGODB_USERNAME"),
            password=os.getenv("MONGODB_PASSWORD"),
        )

        return MongoHandlerConfig(
            root_dir=root_dir,
            input_data_path=Path(mongo_cfg.input_data_path),
            json_data_filename=mongo_cfg.json_data_filename,
            json_data_dir=json_data_dir,
            mongodb_uri=mongodb_uri,
            database_name=mongo_cfg.database_name,
            collection_name=mongo_cfg.collection_name,
        )

    def get_data_ingestion_config(self) -> DataIngestionConfig:
        ingestion_cfg = self.config.data_ingestion
        root_dir = self.artifacts_root / DATA_INGESTION_SUBDIR
        featurestore_dir = root_dir / FEATURESTORE_SUBDIR
        ingested_data_dir = root_dir / INGESTED_SUBDIR

        raw_dvc_path = Path(self.config.data_paths.raw_data_dvc_filepath)

        return DataIngestionConfig(
            root_dir=root_dir,
            featurestore_dir=featurestore_dir,
            raw_data_filename=ingestion_cfg.raw_data_filename,
            ingested_data_dir=ingested_data_dir,
            ingested_data_filename=ingestion_cfg.ingested_data_filename,
            raw_dvc_path=raw_dvc_path,
        )

    def get_data_validation_config(self) -> DataValidationConfig:
        validation_cfg = self.config.data_validation
        root_dir = self.artifacts_root / DATA_VALIDATION_SUBDIR
        validated_dir = root_dir / VALIDATED_SUBDIR
        report_dir = root_dir / REPORTS_SUBDIR

        validated_dvc_path = Path(self.config.data_paths.validated_dvc_filepath)

        return DataValidationConfig(
            root_dir=root_dir,
            validated_dir=validated_dir,
            validated_filename=validation_cfg.validated_filename,
            report_dir=report_dir,
            missing_report_filename=validation_cfg.missing_report_filename,
            duplicates_report_filename=validation_cfg.duplicates_report_filename,
            drift_report_filename=validation_cfg.drift_report_filename,
            validation_report_filename=validation_cfg.validation_report_filename,
            schema=self.schema,
            validated_dvc_path=validated_dvc_path,
            validation_params=self.params.validation_params,
            val_report_template=self.templates.validation_report
        )

    def get_data_transformation_config(self) -> DataTransformationConfig:
        transformation_cfg = self.config.data_transformation
        transformation_params = self.params.transformation_params
        target_column = self.schema.target_column

        root_dir = self.artifacts_root / DATA_TRANSFORMATION_SUBDIR
        train_dir = root_dir / TRANSFORMED_DATA_SUBDIR / DATA_TRAIN_SUBDIR
        val_dir = root_dir / TRANSFORMED_DATA_SUBDIR / DATA_VAL_SUBDIR
        test_dir = root_dir / TRANSFORMED_DATA_SUBDIR / DATA_TEST_SUBDIR
        preprocessor_dir = root_dir / TRANSFORMED_OBJECT_SUBDIR

        train_dvc_dir = Path(self.config.data_paths.train_dvc_dir)
        val_dvc_dir = Path(self.config.data_paths.val_dvc_dir)
        test_dvc_dir = Path(self.config.data_paths.test_dvc_dir)

        return DataTransformationConfig(
            root_dir=root_dir,
            transformation_params=transformation_params,
            train_dir=train_dir,
            val_dir=val_dir,
            test_dir=test_dir,
            target_column=target_column,
            x_train_filename=transformation_cfg.x_train_filename,
            y_train_filename=transformation_cfg.y_train_filename,
            x_val_filename=transformation_cfg.x_val_filename,
            y_val_filename=transformation_cfg.y_val_filename,
            x_test_filename=transformation_cfg.x_test_filename,
            y_test_filename=transformation_cfg.y_test_filename,
            preprocessor_dir=preprocessor_dir,
            x_preprocessor_filename=transformation_cfg.x_preprocessor_filename,
            y_preprocessor_filename=transformation_cfg.y_preprocessor_filename,
            train_dvc_dir=train_dvc_dir,
            val_dvc_dir=val_dvc_dir,
            test_dvc_dir=test_dvc_dir,
        )


    def get_model_trainer_config(self) -> ModelTrainerConfig:
        # static config.yaml entries
        yaml_cfg = self.config.model_trainer
        # dynamic params.yaml entries
        params_cfg = self.params.model_trainer

        # where to write models & reports
        root_dir = self.artifacts_root / MODEL_TRAINER_SUBDIR

        # DVC‐tracked data dirs (under /data/transformed)
        train_dir = Path(self.config.data_paths.train_dvc_dir)
        val_dir = Path(self.config.data_paths.val_dvc_dir)
        test_dir = Path(self.config.data_paths.test_dvc_dir)

        # pull MLflow sub‐box and inject the URI from env
        mlflow_cfg = params_cfg.tracking
        mlflow_cfg.tracking_uri = os.getenv("MLFLOW_TRACKING_URI")

        return ModelTrainerConfig(
            # where to write artifacts
            root_dir=root_dir,
            trained_model_filename=yaml_cfg.trained_model_filename,
            training_report_filename=yaml_cfg.training_report_filename,

            # what to train & how
            models=params_cfg.models,
            optimization=params_cfg.optimization,
            tracking=mlflow_cfg,

            # where to load transformed data from
            train_dir=train_dir,
            val_dir=val_dir,
            test_dir=test_dir,
        )

    def get_model_evaluation_config(self) -> ModelEvaluationConfig:
        eval_cfg = self.config.model_evaluation
        root_dir = self.artifacts_root / MODEL_EVALUATION_SUBDIR

        train_dir = Path(self.config.data_paths.train_dvc_dir)
        val_dir = Path(self.config.data_paths.val_dvc_dir)
        test_dir = Path(self.config.data_paths.test_dvc_dir)

        return ModelEvaluationConfig(
            root_dir=root_dir,
            evaluation_report_filename=eval_cfg.evaluation_report_filename,
            train_dir=train_dir,
            val_dir=val_dir,
            test_dir=test_dir,
        )

    def get_model_pusher_config(self) -> ModelPusherConfig:
        pusher_cfg = self.config.model_pusher
        pusher_params = self.params.model_pusher

        # Local directory to save pushed model
        pushed_model_dir = Path(PUSHED_MODEL_SUBDIR)

        return ModelPusherConfig(
            pushed_model_filename=pusher_cfg.final_model_filename,
            pushed_model_dir=pushed_model_dir,
            upload_to_s3=pusher_params.upload_to_s3,
        )

    def get_s3_handler_config(self) -> S3HandlerConfig:
        s3_cfg = self.config.s3_handler  # your config.yaml has these under model_pusher
        root_dir = self.artifacts_root / "s3_handler"
        aws_region = os.getenv("AWS_REGION")

        return S3HandlerConfig(
            root_dir=root_dir,
            bucket_name=s3_cfg.final_model_s3_bucket,
            aws_region=aws_region,
            local_dir_to_sync=self.artifacts_root,  # assuming you want to sync entire artifacts dir
            s3_artifacts_prefix=s3_cfg.s3_artifacts_prefix,
            s3_final_model_prefix=s3_cfg.s3_final_model_prefix,
        )

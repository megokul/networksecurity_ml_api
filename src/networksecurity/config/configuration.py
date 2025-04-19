from pathlib import Path
import os

from src.networksecurity.constants.constants import (
    CONFIG_FILE_PATH,
    PARAMS_FILE_PATH,
    SCHEMA_FILE_PATH,
    MONGO_HANDLER_SUBDIR,
    MONGO_JSON_SUBDIR,
    DATA_INGESTION_SUBDIR,
    FEATURESTORE_SUBDIR,
    INGESTED_SUBDIR,
    DATA_VALIDATION_SUBDIR,
    VALIDATED_SUBDIR,
    REPORTS_SUBDIR,
    DATA_TRANSFORMATION_SUBDIR,
    TRANSFORMED_SUBDIR,
    TRANSFORMED_OBJECT_SUBDIR,
    LOGS_ROOT,
)

from src.networksecurity.entity.config_entity import (
    MongoHandlerConfig,
    DataIngestionConfig,
    DataValidationConfig,
    DataTransformationConfig,
)

from src.networksecurity.utils.common import (
    read_yaml,
    replace_username_password_in_uri,
)

from src.networksecurity.utils.timestamp import get_shared_utc_timestamp
from src.networksecurity.logging import logger


class ConfigurationManager:
    _global_timestamp: str = None

    def __init__(
        self,
        config_filepath: Path = CONFIG_FILE_PATH,
        params_filepath: Path = PARAMS_FILE_PATH,
        schema_filepath: Path = SCHEMA_FILE_PATH,
    ) -> None:
        self._load_configs(config_filepath, params_filepath, schema_filepath)
        self._initialize_paths()

    def _load_configs(self, config_fp: Path, params_fp: Path, schema_fp: Path) -> None:
        self.config = read_yaml(config_fp)
        self.params = read_yaml(params_fp)
        self.schema = read_yaml(schema_fp)

    def _initialize_paths(self) -> None:
        if ConfigurationManager._global_timestamp is None:
            ConfigurationManager._global_timestamp = get_shared_utc_timestamp()

        timestamp = ConfigurationManager._global_timestamp
        base_artifact_root = Path(self.config.project.artifacts_root)
        self.artifacts_root = base_artifact_root / timestamp

        self.logs_root = Path(LOGS_ROOT) / timestamp
        self.raw_dvc_path = Path(self.config.data_paths.raw_data)
        self.validated_dvc_path = Path(self.config.data_paths.validated_data)

    def get_logs_dir(self) -> Path:
        return self.logs_root

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

        return DataIngestionConfig(
            root_dir=root_dir,
            featurestore_dir=featurestore_dir,
            raw_data_filename=ingestion_cfg.raw_data_filename,
            ingested_data_dir=ingested_data_dir,
            ingested_data_filename=ingestion_cfg.ingested_data_filename,
            raw_dvc_path=self.raw_dvc_path,
        )

    def get_data_validation_config(self) -> DataValidationConfig:
        validation_cfg = self.config.data_validation
        root_dir = self.artifacts_root / DATA_VALIDATION_SUBDIR
        validated_dir = root_dir / VALIDATED_SUBDIR
        report_dir = root_dir / REPORTS_SUBDIR

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
            validated_dvc_path=self.validated_dvc_path,
            validation_params=self.params.validation_params,
        )

    def get_data_transformation_config(self) -> DataTransformationConfig:
        transformation_cfg = self.config.data_transformation
        transformation_params = self.params.transformation_params

        root_dir = self.artifacts_root / DATA_TRANSFORMATION_SUBDIR
        transformed_dir = root_dir / TRANSFORMED_SUBDIR
        preprocessor_dir = root_dir / TRANSFORMED_OBJECT_SUBDIR

        return DataTransformationConfig(
            root_dir=root_dir,
            transformed_dir=transformed_dir,
            transformed_train_filename=transformation_cfg.transformed_train_filename,
            transformed_test_filename=transformation_cfg.transformed_test_filename,
            preprocessor_dir=preprocessor_dir,
            preprocessing_object_filename=transformation_cfg.preprocessing_object_filename,
            transformation_params=transformation_params
        )

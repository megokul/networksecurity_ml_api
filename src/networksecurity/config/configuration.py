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
    DRIFT_REPORT_SUBDIR,
    LOGS_ROOT,
)

from src.networksecurity.entity.config_entity import (
    MongoHandlerConfig,
    DataIngestionConfig,
    DataValidationConfig,
)

from src.networksecurity.utils.common import (
    read_yaml,
    create_directories,
    replace_username_password_in_uri,
)

from src.networksecurity.utils.timestamp import get_shared_utc_timestamp


class ConfigurationManager:
    """
    Central manager for loading config YAMLs and setting up timestamped
    artifact + log directories using a consistent UTC timestamp.
    """

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
        """
        Initializes artifact and log paths using the globally shared UTC timestamp.
        This ensures that all pipeline components refer to the same consistent run ID.
        """
        if ConfigurationManager._global_timestamp is None:
            ConfigurationManager._global_timestamp = get_shared_utc_timestamp()

        timestamp = ConfigurationManager._global_timestamp

        # Artifact Root
        base_artifact_root = Path(self.config.project.artifacts_root)
        self.artifacts_root = base_artifact_root / timestamp
        create_directories(self.artifacts_root)

        # Logs Root
        self.logs_root = Path(LOGS_ROOT) / timestamp
        create_directories(self.logs_root)

    def get_logs_dir(self) -> Path:
        return self.logs_root

    def get_mongohandler_config(self) -> MongoHandlerConfig:
        mongo_cfg = self.config.mongo_handler

        root_dir = self.artifacts_root / MONGO_HANDLER_SUBDIR
        json_data_dir = root_dir / MONGO_JSON_SUBDIR
        create_directories(json_data_dir)

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

    def get_dataingestion_config(self) -> DataIngestionConfig:
        ingestion_cfg = self.config.data_ingestion

        root_dir = self.artifacts_root / DATA_INGESTION_SUBDIR
        featurestore_dir = root_dir / FEATURESTORE_SUBDIR
        ingested_data_dir = root_dir / INGESTED_SUBDIR
        create_directories(featurestore_dir, ingested_data_dir)

        return DataIngestionConfig(
            root_dir=root_dir,
            featurestore_dir=featurestore_dir,
            raw_data_filename=ingestion_cfg.raw_data_filename,
            ingested_data_dir=ingested_data_dir,
            ingested_data_filename=ingestion_cfg.ingested_data_filename,
        )

    def get_datavalidation_config(self) -> DataValidationConfig:
        val_cfg = self.config.data_validation
        schema = self.schema.columns
        params = self.params.drift_detection

        root_dir = self.artifacts_root / DATA_VALIDATION_SUBDIR
        validated_data_dir = root_dir / VALIDATED_SUBDIR
        drift_report_dir = root_dir / DRIFT_REPORT_SUBDIR
        create_directories(validated_data_dir, drift_report_dir)

        return DataValidationConfig(
            root_dir=root_dir,
            validated_data_dir=validated_data_dir,
            validated_data_filename=val_cfg.validated_data_filename,
            drift_report_dir=drift_report_dir,
            drift_report_filename=val_cfg.drift_report_filename,
            schema=schema,
            params=params,
        )

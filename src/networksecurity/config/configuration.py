from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
import os

from src.networksecurity.constants import CONFIG_FILE_PATH, PARAMS_FILE_PATH, SCHEMA_FILE_PATH
from src.networksecurity.entity.config_entity import MongoHandlerConfig, DataIngestionConfig, DataValidationConfig
from src.networksecurity.utils.common import (
    create_directories,
    read_yaml,
    replace_username_password_in_uri,
)


class ConfigurationManager:
    """Manages reading and structuring configuration data from YAML files."""

    _global_timestamp: str = None  # Shared timestamp for all config objects

    def __init__(
        self,
        config_filepath: Path = CONFIG_FILE_PATH,
        params_filepath: Path = PARAMS_FILE_PATH,
        schema_filepath: Path = SCHEMA_FILE_PATH,
    ) -> None:
        self.config = read_yaml(config_filepath)
        self.params = read_yaml(params_filepath)
        self.schema = read_yaml(schema_filepath)

        # Initialize shared timestamp only once
        if ConfigurationManager._global_timestamp is None:
            ConfigurationManager._global_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Create full artifact root with timestamp: artifacts/<timestamp>/
        base_artifacts = Path(self.config.artifacts_root)
        self.artifacts_root = base_artifacts / ConfigurationManager._global_timestamp
        create_directories(self.artifacts_root)

    def get_mongohandler_config(self) -> MongoHandlerConfig:

        load_dotenv()

        config = self.config.mongo_handler

        mongohandler_root_dir = self.artifacts_root / "mongo_handler"
        json_data_dir = mongohandler_root_dir / "JSON_data"

        mongodb_uri_base = os.getenv("MONGODB_URI_BASE")
        mongodb_username = os.getenv("MONGODB_USERNAME")
        mongodb_password = os.getenv("MONGODB_PASSWORD")
        mongodb_uri = replace_username_password_in_uri(
            mongodb_uri_base, mongodb_username, mongodb_password
        )

        create_directories(json_data_dir.parent)

        return MongoHandlerConfig(
            root_dir=mongohandler_root_dir,
            input_data_path=config.input_data_path,
            json_data_filename=config.json_data_filename,
            json_data_dir=json_data_dir,
            mongodb_uri=mongodb_uri,
            database_name=os.getenv("DATABASE_NAME"),
            collection_name=os.getenv("COLLECTION_NAME"),
        )

    def get_dataingestion_config(self) -> DataIngestionConfig:
        config = self.config.data_ingestion

        ingestion_root_dir = self.artifacts_root / "data_ingestion"
        featurestore_dir = ingestion_root_dir / "featurestore"
        ingested_data_dir = ingestion_root_dir / "ingested"

        create_directories(featurestore_dir, ingested_data_dir)

        return DataIngestionConfig(
            root_dir=ingestion_root_dir,
            featurestore_dir=featurestore_dir,
            ingested_data_dir=ingested_data_dir,
            ingested_data_filename=config.ingested_data_filename,
            input_data_filename=config.input_data_filename,
        )

    def get_datavalidation_config(self) -> DataValidationConfig:

        config = self.config.data_validation

        validation_root = self.artifacts_root / "data_validation"
        # validated_data_dir = 


        data_validation_config = DataValidationConfig(
            root_dir = validation_root,
            validated_data_filename = config.validated_data_filename,
            validated_data_dir = "",
            drift_report_filename = config.drift_report_filename,
            drift_report_dir = "",
        )

        return data_validation_config

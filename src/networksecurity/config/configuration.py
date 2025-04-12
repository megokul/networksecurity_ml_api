from pathlib import Path

from src.networksecurity.constants import CONFIG_FILE_PATH, PARAMS_FILE_PATH, SCHEMA_FILE_PATH
from src.networksecurity.entity.config_entity import MongoDBConfig, DataIngestionConfig
from src.networksecurity.utils.common import create_directories, read_yaml, replace_username_password_in_uri
from dotenv import load_dotenv
import os
from urllib.parse import quote_plus

class ConfigurationManager:
    """Manages reading and structuring configuration data from YAML files.

    This class is responsible for:
    - Loading YAML-based configuration, parameter, and schema files.
    - Ensuring required directories exist.
    - Constructing and returning dataclass objects with structured config values.
    """

    def __init__(
        self,
        config_filepath=CONFIG_FILE_PATH,
        params_filepath=PARAMS_FILE_PATH,
        schema_filepath=SCHEMA_FILE_PATH
    ):
        """
        Initializes the ConfigurationManager by loading YAML files and creating the artifact root directory.
        """
        self.config = read_yaml(config_filepath)
        self.params = read_yaml(params_filepath)
        self.schema = read_yaml(schema_filepath)

        create_directories(self.config.artifacts_root)  # Ensure base artifacts directory exists

    def get_mongodb_config(self) -> MongoDBConfig:
        """Construct and return the configuration required for database ingestion.

        This includes:
        - Root directory for storing DB-related files.
        - Path to input data (e.g., CSV file).
        - Filename and full path where JSON output will be saved.

        Returns:
            DataBaseConfig: Dataclass containing structured DB config info.

        """
        load_dotenv()

        config = self.config.mongodb  # Access nested 'database' config block

        # Ensure DB root directory exists
        create_directories(config.root_dir)

        mongodb_uri_base = os.getenv("MONGODB_URI_BASE")
        mongodb_username = os.getenv("MONGODB_USERNAME")
        mongodb_password = os.getenv("MONGODB_PASSWORD")

        mongodb_uri = replace_username_password_in_uri(mongodb_uri_base, mongodb_username, mongodb_password)

        json_data_dir = Path(config.root_dir) / config.json_data_filename

        # Build and return structured DB config object
        mongodb_config = MongoDBConfig(
            root_dir=Path(config.root_dir),
            input_data_path=Path(config.input_data_path),
            json_data_filename=config.json_data_filename,
            json_data_dir=Path(json_data_dir.as_posix()),
            mongodb_uri=mongodb_uri,
            database_name=os.getenv("DATABASE_NAME"),
            collection_name=os.getenv("COLLECTION_NAME"),
        )

        return mongodb_config


    def get_dataingestion_config(self) -> DataIngestionConfig:

        config = self.config.data_ingestion  # Access nested 'database' config block

        # Ensure DB root directory exists
        create_directories(config.root_dir)

        dataingestion_config = DataIngestionConfig(
            root_dir=config.root_dir,
            staging_data_dir=config.staging_data_dir,
            ingested_data_filename=config.ingested_data_filename,
        )

        return dataingestion_config
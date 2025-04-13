from pathlib import Path
from datetime import datetime
from dataclasses import dataclass

@dataclass
class MongoDBConfig:
    """Configuration schema for handling input data and database directory setup.

    Attributes:
        root_dir (Path): Root directory where database-related files will be stored.
        input_data_path (Path): Path to the raw input data file (e.g., CSV).
        json_data_filename (str): Name of the JSON file to which data will be converted.

    """

    root_dir: Path
    input_data_path: Path
    json_data_filename: str
    json_data_dir: Path
    mongodb_uri: str
    database_name: str
    collection_name: str



@dataclass
class DataIngestionConfig:

    root_dir: Path
    featurestore_dir: Path
    ingested_data_dir: Path
    ingested_data_filename: str
    input_data_filename: str
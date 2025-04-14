from pathlib import Path
from datetime import datetime
from dataclasses import dataclass

@dataclass
class MongoHandlerConfig:
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

    def __post_init__(self):
        self.root_dir = Path(self.root_dir)
        self.input_data_path = Path(self.input_data_path)
        self.json_data_dir = Path(self.json_data_dir)

    @property
    def json_data_filepath(self):
        return self.json_data_dir / self.json_data_filename


@dataclass
class DataIngestionConfig:

    root_dir: Path
    featurestore_dir: Path
    raw_data_filename: str
    ingested_data_dir: Path
    ingested_data_filename: str

    def __post_init__(self):
        self.root_dir = Path(self.root_dir)
        self.featurestore_dir = Path(self.featurestore_dir)
        self.ingested_data_dir = Path(self.ingested_data_dir)

    @property
    def raw_data_filepath(self):
        return self.featurestore_dir / self.raw_data_filename

    @property
    def ingested_data_filepath(self):
        return self.ingested_data_dir / self.ingested_data_filename



@dataclass
class DataValidationConfig:

    root_dir: Path
    validated_data_dir: Path
    validated_data_filename: str
    drift_report_dir: Path
    drift_report_filename: str

    def __post_init__(self):
        self.root_dir = Path(self.root_dir)
        self.validated_data_dir = Path(self.validated_data_dir)
        self.drift_report_dir = Path(self.validated_data_dir)

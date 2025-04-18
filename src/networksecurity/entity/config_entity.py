from pathlib import Path
from dataclasses import dataclass


@dataclass
class MongoHandlerConfig:
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
    raw_dvc_path: Path

    def __post_init__(self):
        self.root_dir = Path(self.root_dir)
        self.featurestore_dir = Path(self.featurestore_dir)
        self.ingested_data_dir = Path(self.ingested_data_dir)
        self.raw_dvc_path = Path(self.raw_dvc_path)

    @property
    def raw_data_filepath(self):
        return self.featurestore_dir / self.raw_data_filename

    @property
    def ingested_data_filepath(self):
        return self.ingested_data_dir / self.ingested_data_filename


@dataclass(frozen=True)
class DataValidationConfig:
    root_dir: Path
    validated_dir: Path
    validated_filename: str
    report_dir: Path
    missing_report_filename: str
    drift_report_filename: str
    validation_report_filename: str
    schema: dict
    validation_params: dict
    validated_dvc_path: Path

    @property
    def validated_filepath(self) -> Path:
        return self.validated_dir / self.validated_filename

    @property
    def missing_report_path(self) -> Path:
        return self.report_dir / self.missing_report_filename

    @property
    def drift_report_path(self) -> Path:
        return self.report_dir / self.drift_report_filename

    @property
    def validation_report_path(self) -> Path:
        return self.report_dir / self.validation_report_filename



@dataclass
class DataTransformationConfig:
    root_dir: Path
    transformed_dir: Path
    transformed_train_filename: str
    transformed_test_filename: str
    preprocessor_dir: Path
    preprocessing_object_filename: str

    def __post_init__(self):
        self.root_dir = Path(self.root_dir)
        self.transformed_dir = Path(self.transformed_dir)
        self.preprocessor_dir = Path(self.preprocessor_dir)

    @property
    def transformed_train_filepath(self):
        return self.transformed_dir / self.transformed_train_filename

    @property
    def transformed_test_filepath(self):
        return self.transformed_dir / self.transformed_test_filename

    @property
    def preprocessor_filepath(self):
        return self.preprocessor_dir / self.preprocessing_object_filename


@dataclass
class ModelTrainerConfig:
    root_dir: Path
    trained_model_filename: str
    params: dict

    def __post_init__(self):
        self.root_dir = Path(self.root_dir)

    @property
    def trained_model_filepath(self):
        return self.root_dir / self.trained_model_filename


@dataclass
class ModelEvaluationConfig:
    root_dir: Path
    evaluation_report_filename: str

    def __post_init__(self):
        self.root_dir = Path(self.root_dir)

    @property
    def evaluation_report_filepath(self):
        return self.root_dir / self.evaluation_report_filename


@dataclass
class ModelPredictionConfig:
    root_dir: Path
    prediction_output_filename: str

    def __post_init__(self):
        self.root_dir = Path(self.root_dir)

    @property
    def prediction_output_filepath(self):
        return self.root_dir / self.prediction_output_filename

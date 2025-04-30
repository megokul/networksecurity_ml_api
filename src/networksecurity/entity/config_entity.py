from pathlib import Path
from dataclasses import dataclass
from box import ConfigBox
from typing import List


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
    def json_data_filepath(self) -> Path:
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
    def raw_data_filepath(self) -> Path:
        return self.featurestore_dir / self.raw_data_filename

    @property
    def ingested_data_filepath(self) -> Path:
        return self.ingested_data_dir / self.ingested_data_filename


@dataclass
class DataValidationConfig:
    root_dir: Path
    validated_dir: Path
    validated_filename: str
    report_dir: Path
    missing_report_filename: str
    duplicates_report_filename: str
    drift_report_filename: str
    validation_report_filename: str
    schema: dict
    validation_params: dict
    validated_dvc_path: Path
    val_report_template: dict

    def __post_init__(self) -> Path:
        self.root_dir = Path(self.root_dir)
        self.validated_dir = Path(self.validated_dir)
        self.report_dir = Path(self.report_dir)
        self.validated_dvc_path = Path(self.validated_dvc_path)

    @property
    def validated_filepath(self) -> Path:
        return self.validated_dir / self.validated_filename

    @property
    def missing_report_filepath(self) -> Path:
        return self.report_dir / self.missing_report_filename

    @property
    def duplicates_report_filepath(self) -> Path:
        return self.report_dir / self.duplicates_report_filename

    @property
    def drift_report_filepath(self) -> Path:
        return self.report_dir / self.drift_report_filename

    @property
    def validation_report_filepath(self) -> Path:
        return self.report_dir / self.validation_report_filename


@dataclass
class DataTransformationConfig:
    root_dir: Path
    transformation_params: dict
    train_dir: Path
    val_dir: Path
    test_dir: Path
    x_train_filename: str
    y_train_filename: str
    x_val_filename: str
    y_val_filename: str
    x_test_filename: str
    y_test_filename: str
    preprocessor_dir: Path
    x_preprocessor_filename: str
    y_preprocessor_filename: str
    target_column: str
    train_dvc_dir: Path
    val_dvc_dir: Path
    test_dvc_dir: Path

    def __post_init__(self) -> Path:
        self.root_dir = Path(self.root_dir)
        self.train_dir = Path(self.train_dir)
        self.val_dir = Path(self.val_dir)
        self.test_dir = Path(self.test_dir)
        self.preprocessor_dir = Path(self.preprocessor_dir)

    @property
    def x_train_filepath(self) -> Path:
        return self.train_dir / self.x_train_filename

    @property
    def y_train_filepath(self) -> Path:
        return self.train_dir / self.y_train_filename

    @property
    def x_val_filepath(self) -> Path:
        return self.val_dir / self.x_val_filename

    @property
    def y_val_filepath(self) -> Path:
        return self.val_dir / self.y_val_filename

    @property
    def x_test_filepath(self) -> Path:
        return self.test_dir / self.x_test_filename

    @property
    def y_test_filepath(self) -> Path:
        return self.test_dir / self.y_test_filename

    @property
    def x_preprocessor_filepath(self) -> Path:
        return self.preprocessor_dir / self.x_preprocessor_filename

    @property
    def y_preprocessor_filepath(self) -> Path:
        return self.preprocessor_dir / self.y_preprocessor_filename

    @property
    def x_train_dvc_filepath(self) -> Path:
        return self.train_dvc_dir / self.x_train_filename

    @property
    def y_train_dvc_filepath(self) -> Path:
        return self.train_dvc_dir / self.y_train_filename

    @property
    def x_val_dvc_filepath(self) -> Path:
        return self.val_dvc_dir / self.x_val_filename

    @property
    def y_val_dvc_filepath(self) -> Path:
        return self.val_dvc_dir / self.y_val_filename

    @property
    def x_test_dvc_filepath(self) -> Path:
        return self.test_dvc_dir / self.x_test_filename

    @property
    def y_test_dvc_filepath(self) -> Path:
        return self.test_dvc_dir / self.y_test_filename



@dataclass
class ModelTrainerConfig:
    root_dir: Path
    trained_model_filename: str
    training_report_filename: str
    models: list[dict]
    optimization: dict
    tracking: dict
    models: List[dict]
    optimization: ConfigBox
    tracking: ConfigBox
    # where to load transformed arrays from (DVC-tracked)
    train_dir: Path
    val_dir:   Path
    test_dir:  Path

    def __post_init__(self):
        self.root_dir = Path(self.root_dir)

    @property
    def trained_model_filepath(self) -> Path:
        return self.root_dir / self.trained_model_filename

    @property
    def training_report_filepath(self) -> Path:
        return self.root_dir / self.training_report_filename


@dataclass
class ModelEvaluationConfig:
    root_dir: Path
    evaluation_report_filename: str
    train_dir: Path
    val_dir: Path
    test_dir: Path

    def __post_init__(self):
        self.root_dir = Path(self.root_dir)

    @property
    def evaluation_report_filepath(self) -> Path:
        return self.root_dir / self.evaluation_report_filename


@dataclass
class ModelPusherConfig:
    root_dir: Path
    saved_model_dir: Path
    pushed_model_filename: str
    final_model_dir: Path
    final_model_s3_bucket: str

    def __post_init__(self):
        self.root_dir = Path(self.root_dir)
        self.saved_model_dir = Path(self.saved_model_dir)
        self.final_model_dir = Path(self.final_model_dir)

    @property
    def pushed_model_filepath(self) -> Path:
        return self.saved_model_dir / self.pushed_model_filename

    @property
    def final_model_local_path(self) -> Path:
        return self.final_model_dir / self.pushed_model_filename


@dataclass
class ModelPusherConfig:
    root_dir: Path
    pushed_model_filename: str
    pushed_model_filepath: Path
    final_model_local_path: Path
    final_model_s3_bucket: str
    upload_to_s3: bool = True

    def __post_init__(self):
        self.root_dir = Path(self.root_dir)
        self.pushed_model_filepath = Path(self.pushed_model_filepath)
        self.final_model_local_path = Path(self.final_model_local_path)

    @property
    def pushed_model_dir(self) -> Path:
        return self.root_dir

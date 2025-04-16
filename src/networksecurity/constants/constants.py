from pathlib import Path

# ---------------------------
# Configuration file paths
# ---------------------------

CONFIG_DIR = Path("config")
CONFIG_FILE_PATH = CONFIG_DIR / "config.yaml"
PARAMS_FILE_PATH = CONFIG_DIR / "params.yaml"
SCHEMA_FILE_PATH = CONFIG_DIR / "schema.yaml"

# ---------------------------
# Default placeholder tokens
# ---------------------------

MISSING_VALUE_TOKEN = "na"

# ---------------------------
# MongoDB connection constants
# ---------------------------

MONGODB_CONNECT_TIMEOUT_MS = 5000
MONGODB_SOCKET_TIMEOUT_MS = 5000

# ---------------------------
# Root Directories
# ---------------------------

LOGS_ROOT = "logs"  # Root directory for timestamped logs

# ---------------------------
# Artifact Subdirectory Names
# ---------------------------

MONGO_HANDLER_SUBDIR = "mongo_handler"
MONGO_JSON_SUBDIR = "JSON_data"

DATA_INGESTION_SUBDIR = "data_ingestion"
FEATURESTORE_SUBDIR = "featurestore"
INGESTED_SUBDIR = "ingested"

DATA_VALIDATION_SUBDIR = "data_validation"
VALIDATED_SUBDIR = "validated"
DRIFT_REPORT_SUBDIR = "drift_report"

DATA_TRANSFORMATION_SUBDIR = "data_transformation"
TRANSFORMED_SUBDIR = "transformed"
TRANSFORMED_OBJECT_SUBDIR = "transformed_object"

MODEL_TRAINER_SUBDIR = "model_trainer"
MODEL_EVALUATION_SUBDIR = "model_evaluation"
MODEL_PREDICTION_SUBDIR = "model_prediction"

# ---------------------------
# Common filenames
# ---------------------------

RAW_DATA_FILENAME = "raw_data.csv"
INGESTED_DATA_FILENAME = "ingested_data.csv"
VALIDATED_DATA_FILENAME = "validated_data.csv"
DRIFT_REPORT_FILENAME = "drift_report.yaml"

TRANSFORMED_TRAIN_FILENAME = "train.npy"
TRANSFORMED_TEST_FILENAME = "test.npy"
PREPROCESSING_OBJECT_FILENAME = "preprocessing.pkl"

TRAINED_MODEL_FILENAME = "model.pkl"
EVALUATION_REPORT_FILENAME = "evaluation_report.yaml"
PREDICTION_OUTPUT_FILENAME = "prediction_output.csv"

MONGO_JSON_FILENAME = "input_data.json"

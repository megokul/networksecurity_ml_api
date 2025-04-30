from pathlib import Path

# ---------------------------
# Configuration File Paths
# ---------------------------

CONFIG_DIR = Path("config")
CONFIG_FILE_PATH = CONFIG_DIR / "config.yaml"
PARAMS_FILE_PATH = CONFIG_DIR / "params.yaml"
SCHEMA_FILE_PATH = CONFIG_DIR / "schema.yaml"
TEMPLATES_FILE_PATH = CONFIG_DIR / "templates.yaml"

# ---------------------------
# Generic Constants
# ---------------------------

MISSING_VALUE_TOKEN = "na"

# ---------------------------
# MongoDB Connection Settings
# ---------------------------

MONGODB_CONNECT_TIMEOUT_MS = 40000
MONGODB_SOCKET_TIMEOUT_MS = 40000

# ---------------------------
# Root Directories
# ---------------------------

LOGS_ROOT = "logs"  # Central log directory (outside artifacts)
STABLE_DATA_DIR = Path("data")
RAW_DATA_SUBDIR = "raw"
VALIDATED_DATA_SUBDIR = "validated"
TRANSFORMED_DATA_SUBDIR = "transformed"
MODEL_DIR = "model"
EVALUATION_DIR = "evaluation"
PREDICTIONS_DIR = "predictions"

# ---------------------------
# Artifact Subdirectory Names (Dynamic Timestamped)
# ---------------------------

MONGO_HANDLER_SUBDIR = "mongo_handler"
MONGO_JSON_SUBDIR = "JSON_data"

DATA_INGESTION_SUBDIR = "data_ingestion"
FEATURESTORE_SUBDIR = "featurestore"
INGESTED_SUBDIR = "ingested"

DATA_VALIDATION_SUBDIR = "data_validation"
VALIDATED_SUBDIR = "validated"
REPORTS_SUBDIR = "reports"
SCHEMA_HASH_SUBDIR = "schema_hash"

DATA_TRANSFORMATION_SUBDIR = "data_transformation"
DATA_SUBDIR = "data"
DATA_TRAIN_SUBDIR = "train"
DATA_VAL_SUBDIR = "val"
DATA_TEST_SUBDIR = "test"

TRANSFORMED_OBJECT_SUBDIR = "preprocessor"

MODEL_TRAINER_SUBDIR = "model_trainer"
MODEL_EVALUATION_SUBDIR = "model_evaluation"
MODEL_PREDICTION_SUBDIR = "model_prediction"

# ---------------------------
# Default Filenames (used by config.yaml)
# ---------------------------

DEFAULT_SCHEMA_HASH_FILENAME = "schema_hash.json"
DEFAULT_VALIDATED_FILENAME = "validated_data.csv"
DEFAULT_MISSING_REPORT_FILENAME = "missing_values_report.json"
DEFAULT_DRIFT_REPORT_FILENAME = "drift_report.yaml"
DEFAULT_VALIDATION_REPORT_FILENAME = "validation_report.yaml"

# Logging and output labels
X_TRAIN_LABEL = "X_train"
Y_TRAIN_LABEL = "y_train"
X_VAL_LABEL = "X_val"
Y_VAL_LABEL = "y_val"
X_TEST_LABEL = "X_test"
Y_TEST_LABEL = "y_test"

MODEL_EVALUATION_SUBDIR = "model_evaluation"
MODEL_PUSHER_SUBDIR = "final_model"
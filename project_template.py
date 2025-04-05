import os
from pathlib import Path
import logging


# ==============================
# 🔹 LOGGING SETUP
# ==============================

# ✅ Define the directory where logs will be stored
log_dir = "logs"

# ✅ Define the log file name and full path
log_filepath = os.path.join(log_dir, 'directorygen_logs.log')

# ✅ Define the format for log messages
log_format = '[%(asctime)s] - %(levelname)s - %(module)s - %(message)s'


def setup_logging():
    """
    Sets up a custom logger:
    - Creates the `logs/` directory if it doesn't exist.
    - Configures log messages to be written to both a file and the console.
    - Uses append mode (`"a"`) so logs persist across multiple runs.
    - Ensures handlers are not added multiple times.
    - Logger name: `directory_builder` (used for all logging in this script).

    Returns:
        logging.Logger: Custom logger instance.
    """

    # ✅ Ensure the log directory exists before creating the log file
    os.makedirs(log_dir, exist_ok=True)

    # ✅ Create a custom logger (separate from the root logger)
    logger = logging.getLogger('directory_builder')

    # ✅ Set the logger level to DEBUG (captures all log levels)
    logger.setLevel(logging.DEBUG)

    # ✅ Prevent adding duplicate handlers
    if not logger.hasHandlers():
        formatter = logging.Formatter(log_format)  # ✅ Define the log message format

        # ✅ Create a File Handler (logs INFO and above)
        file_handler = logging.FileHandler(log_filepath, mode='a')  # Append mode ("a")
        file_handler.setFormatter(formatter)  # Apply the log format

        # ✅ Create a Stream Handler (logs DEBUG and above to console)
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)  # Apply the log format

        # ✅ Add handlers to the logger
        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)

    return logger  # ✅ Return the configured logger


# ==============================
# 🔹 PROJECT SETUP
# ==============================

# ✅ Define the project name (used in file paths)
project_name = input("Please enter the project name: ")

# ✅ List of files and directories to be created in the project structure
list_of_files = [
    # 🔹 GitHub workflows (for CI/CD setup)
    ".github/workflows/.gitkeep",
    
    # 🔹 Source Code Structure
    f"src/{project_name}/__init__.py",  # Main package initializer
    f"src/{project_name}/components/__init__.py",  # Components submodule initializer
    f"src/{project_name}/utils/__init__.py",  # Utilities submodule initializer
    f"src/{project_name}/utils/common.py",  # Common utility functions
    f"src/{project_name}/config/__init__.py",  # Configuration submodule
    f"src/{project_name}/config/configuration.py",  # Configuration handling script
    f"src/{project_name}/pipeline/__init__.py",  # Pipeline processing module
    f"src/{project_name}/entity/__init__.py",  # Entity-related module
    f"src/{project_name}/entity/config_entity.py",  # Configuration entity class
    f"src/{project_name}/constants/__init__.py",  # Constants module

    # 🔹 Configuration and Parameter Files
    "config/config.yaml",  # YAML file for configuration settings
    "params.yaml",  # YAML file for parameter tuning
    "schema.yaml",  # YAML file for data schema definition

    # 🔹 Project Execution and Deployment
    "main.py",  # Main entry point of the project
    "Dockerfile",  # Dockerfile for containerization
    "setup.py",  # Setup script for packaging
    "requirements.txt",  # Requirements file for Python dependencies

    # 🔹 Research and Web Components
    "research/research.ipynb",  # Jupyter notebook for exploratory research
    "templates/index.html",  # HTML template file (for a web component)

    # 🔹 Backend API
    "app.py"  # Flask or FastAPI backend application script
]


# ==============================
# 🔹 DIRECTORY & FILE CREATION
# ==============================

def create_file_structure(file_list):
    """
    Creates directories and files based on the given list.
    
    - If a directory does not exist, it is created.
    - If a file does not exist or is empty, it is created.
    - Logs every operation to track what is being created.

    Parameters:
        file_list (list): List of file paths to be created.
    """

    for filepath in file_list:
        filepath = Path(filepath)  # ✅ Convert string path to a `Path` object
        filedir, filename = os.path.split(filepath)  # ✅ Extract directory and filename separately

        # ✅ Ensure the parent directory exists before creating the file
        if filedir:
            os.makedirs(filedir, exist_ok=True)  # ✅ Create directory if it does not exist
            logger.info(f"Creating the directory '{filedir}' for file: '{filename}'")

        # ✅ Check if the file does not exist or is empty, then create it
        if not filepath.exists() or filepath.stat().st_size == 0:
            with open(filepath, 'w'):  # ✅ Create an empty file
                pass  # No content is added, just initializing the file
            logger.info(f"Creating empty file: '{filepath}'")  # ✅ Log file creation
        else:
            logger.info(f"'{filepath}' already exists")  # ✅ Log if the file already exists


# ✅ Initialize the logger
logger = setup_logging()

# ✅ Run the file creation function
create_file_structure(list_of_files)

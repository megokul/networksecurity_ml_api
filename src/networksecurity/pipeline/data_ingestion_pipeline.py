from src.networksecurity.config.configuration import ConfigurationManager
from src.networksecurity.components.data_ingestion import DataIngestion
from src.networksecurity.dbhandler.mongodb_handler import MongoDBHandler
from src.networksecurity.entity.config_entity import DataIngestionConfig, MongoHandlerConfig
from src.networksecurity.entity.artifact_entity import DataIngestionArtifact
from src.networksecurity.logging import logger
from src.networksecurity.exception.exception import NetworkSecurityError


class DataIngestionPipeline:
    """
    Runs the data ingestion stage:
    - Loads configs
    - Instantiates handler and component
    - Triggers ingestion and returns artifact
    """

    def __init__(self):
        try:
            self.config_manager = ConfigurationManager()
            self.ingestion_config: DataIngestionConfig = self.config_manager.get_data_ingestion_config()
            self.mongo_config: MongoHandlerConfig = self.config_manager.get_mongo_handler_config()
            self.mongo_handler = MongoDBHandler(config=self.mongo_config)
        except Exception as e:
            logger.exception("Failed to initialize DataIngestionPipeline")
            raise NetworkSecurityError(e, logger) from e

    def run(self) -> DataIngestionArtifact:
        try:
            logger.info("========== Data Ingestion Stage Started ==========")

            ingestion = DataIngestion(
                config=self.ingestion_config,
                db_handler=self.mongo_handler,
            )
            artifact = ingestion.run_ingestion()

            logger.info(f"Data Ingestion Process Completed. {artifact}")
            logger.info("========== Data Ingestion Stage Completed ==========")

            return artifact

        except Exception as e:
            logger.exception("Data Ingestion Stage Failed")
            raise NetworkSecurityError(e, logger) from e

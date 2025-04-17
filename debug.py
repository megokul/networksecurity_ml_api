from src.networksecurity.config.configuration import ConfigurationManager
from src.networksecurity.dbhandler.mongo_handler import MongoDBHandler
from src.networksecurity.components.data_ingestion import DataIngestion
from dotenv import load_dotenv
load_dotenv()


configmanager = ConfigurationManager()

mongohandler_config = configmanager.get_mongohandler_config()

mongohandler = MongoDBHandler(mongohandler_config)

with mongohandler:
    mongohandler.insert_csv_to_collection(mongohandler_config.input_data_path)

dataingestion_config = configmanager.get_dataingestion_config()

dataingestion = DataIngestion(dataingestion_config, mongohandler)
dataingestion.load_data_from_mongo()

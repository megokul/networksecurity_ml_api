import sys
import os
from dotenv import load_dotenv
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from src.networksecurity.logging import logger
import pandas as pd
import numpy as np
from pathlib import Path
from src.networksecurity.utils.common import csv_to_json_convertor, create_directories

from src.networksecurity.exception.exception import NetworkSecurityError
from src.networksecurity.entity.config_entity import MongoHandlerConfig

class MongoDBHandler:
    def __init__(self, config: MongoHandlerConfig):
        try:
            self.config = config
        except Exception as e:
            raise NetworkSecurityError(e, logger) from e

    def ping_mongodb(self):

        # Create a new client and connect to the server with Server API v1
        client = MongoClient(self.config.mongodb_uri, server_api=ServerApi("1"))

        # Send a ping to confirm a successful connection
        try:
            client.admin.command("ping")
            print("Pinged your deployment. You successfully connected to MongoDB!")
        except Exception as e:
            print(f"Failed to connect to MongoDB: {e}")

    def insert_csv_to_collection(self, csv_filepath: Path) -> int:
        """ Insert a list of JSON records into MongoDB.

        Args:
            records (list[dict]): Records to insert into the database.

        Returns:
            int: Number of records successfully inserted.

        Raises:
            NetworkSecurityError: If MongoDB insertion fails.
        """
        try:
            
            records = csv_to_json_convertor(source_filepath = csv_filepath, destination_filepath = self.config.json_data_filepath)

            # Step 1: Connect to MongoDB
            logger.info("Attempting to connect to MongoDB...")
            mongo_client = MongoClient(self.config.mongodb_uri)
            logger.info("MongoDB connection established.")

            # Step 2: Select database and collection
            database = mongo_client[self.config.database_name]
            logger.info(f"Using database: '{self.config.database_name}'")

            collection = database[self.config.collection_name]
            logger.info(f"Using collection: '{self.config.collection_name}'")

            # Step 3: Insert data
            logger.info(f"Inserting {len(records)} record(s) into MongoDB...")
            result = collection.insert_many(records)
            logger.info(f"{len(result.inserted_ids)} record(s) inserted successfully into MongoDB.")

            return len(result.inserted_ids)

        except Exception as e:
            logger.error(f"Failed to insert data into MongoDB: {e}")
            raise NetworkSecurityError(e, logger) from e


    def export_collection_as_dataframe(self):
        """
        Read data from mongodb
        """
        try:
            database_name=self.config.database_name
            collection_name=self.config.collection_name
            mongo_client=MongoClient(self.config.mongodb_uri)
            collection=mongo_client[database_name][collection_name]

            df=pd.DataFrame(list(collection.find()))
            if "_id" in df.columns.to_list():
                df=df.drop(columns=["_id"],axis=1)

            df.replace({"na":np.nan},inplace=True)
            return df
        except Exception as e:
            raise NetworkSecurityError(e, logger) from e
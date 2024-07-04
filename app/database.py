import os
from typing import List, Dict, Any
from datetime import datetime, timezone
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import UpdateOne
from pymongo.results import InsertOneResult, UpdateResult, BulkWriteResult
from pymongo.cursor import Cursor


class MongoDB:
    def __init__(self) -> None:
        """
        Initialize the MongoDB client and database connection.
        """
        self.client = AsyncIOMotorClient(self.get_mongo_uri())
        self.db = self.client["sdn_screener"]

    def close(self):
        """
        Close the MongoDB client connection.
        """
        self.client.close()

    def get_mongo_uri(self):
        load_dotenv()
        host = os.getenv("MONGO_HOST")
        port = os.getenv("MONGO_PORT")
        user = os.getenv("MONGO_INITDB_ROOT_USERNAME")
        password = os.getenv("MONGO_INITDB_ROOT_PASSWORD")

        return f'mongodb://{user}:{password}@{host}:{port}/'

    def get_collection(self, collection_name: str):
        """
        Return a MongoDB collection by name.

        Args:
            collection_name: The name of the collection to retrieve.

        Returns:
            Collection: The MongoDB collection.
        """
        return self.db[collection_name]

    async def find_documents(self, collection_name: str, query: Dict[str, Any]) -> Cursor:
        """
        Find documents in a collection
        """
        collection = self.get_collection(collection_name)
        return await collection.find(query)

    async def insert_document(
        self,
        collection_name: str,
        document: Dict[str, Any]
    ) -> InsertOneResult:
        """
        Insert a document into a collection.

        Args:
            collection_name: The name of the collection to insert into.
            document: The document to insert.

        Returns:
            InsertOneResult: The result of the insert operation.
        """
        current_time = datetime.now(timezone.utc)
        document['created_at'] = current_time
        document['updated_at'] = current_time
        collection = self.get_collection(collection_name)
        return await collection.insert_one(document)

    async def upsert_document(
            self,
            collection_name: str,
            filter_query: Dict[str, Any],
            update_values: Dict[str, Any]
        ) -> UpdateResult:
        """
        Update a document if it exists, otherwise insert it.

        Args:
            collection_name: The name of the collection to update.
            filter_query: The filter query to find the document.
            update_values: The values to update in the document.

        Returns:
            UpdateResult: The result of the update operation.
        """
        current_time = datetime.now(timezone.utc)
        update_values['updated_at'] = current_time
        collection = self.get_collection(collection_name)
        config = {
            '$set': update_values,
            '$setOnInsert': { 'created_at': current_time }
        }
        result = await collection.update_one(filter_query, config, upsert=True)
        return result

    async def bulk_upsert_documents(
            self,
            collection_name: str,
            operations: List[Dict[str, Dict[str, Any]]]
        ) -> BulkWriteResult:
        """
        Perform bulk updates if documents exist, otherwise insert them.

        Args:
            collection_name: The name of the collection to update.
            operations: A list of operations, each containing a filter query and update values.

        Returns:
            BulkWriteResult: The result of the bulk write operation.
        """
        current_time = datetime.now(timezone.utc)
        collection = self.get_collection(collection_name)

        write_requests = []
        for operation in operations:
            update_values = {
                **operation['update_values'],
                'updated_at': current_time
            }
            config = {
                '$set': update_values,
                '$setOnInsert': { 'created_at': datetime.now(timezone.utc) }
            }
            request = UpdateOne(operation['filter_query'], config, upsert=True)
            write_requests.append(request)

        result = await collection.bulk_write(write_requests)
        return result

"""Weaviate vector database client for RAG operations."""

import json
from typing import Any

import weaviate
from weaviate.classes.config import Configure, Property, DataType
from weaviate.classes.query import MetadataQuery

from test_data_agent.config import Settings
from test_data_agent.utils.logging import get_logger

logger = get_logger(__name__)


class WeaviateClient:
    """Client for Weaviate vector database operations."""

    # Collection names
    COLLECTION_PATTERNS = "TestDataPattern"
    COLLECTION_DEFECTS = "DefectPattern"
    COLLECTION_PROD_SAMPLES = "ProductionSample"

    def __init__(self, settings: Settings):
        """Initialize Weaviate client.

        Args:
            settings: Application settings with Weaviate config
        """
        self.settings = settings
        self.client: weaviate.WeaviateClient | None = None
        logger.info(
            "weaviate_client_initialized",
            url=settings.weaviate_url,
        )

    async def connect(self) -> None:
        """Connect to Weaviate instance."""
        try:
            self.client = weaviate.connect_to_local(
                host=self.settings.weaviate_url.replace("http://", "").replace(":8080", ""),
                port=8080,
            )
            logger.info("weaviate_connected", url=self.settings.weaviate_url)
        except Exception as e:
            logger.error("weaviate_connection_error", error=str(e))
            raise

    async def disconnect(self) -> None:
        """Disconnect from Weaviate instance."""
        if self.client:
            self.client.close()
            logger.info("weaviate_disconnected")

    async def search(
        self,
        collection: str,
        query: str,
        top_k: int = 5,
    ) -> list[dict[str, Any]]:
        """Search for similar vectors in collection.

        Args:
            collection: Collection name (use class constants)
            query: Search query text
            top_k: Number of results to return

        Returns:
            List of results with data and metadata
        """
        if not self.client:
            raise RuntimeError("Client not connected. Call connect() first.")

        try:
            collection_obj = self.client.collections.get(collection)

            # Perform BM25 keyword search (no vectorizer required)
            response = collection_obj.query.bm25(
                query=query,
                limit=top_k,
                return_metadata=MetadataQuery(score=True),
            )

            results = []
            for obj in response.objects:
                result = {
                    "id": str(obj.uuid),
                    "data": obj.properties,
                    "score": obj.metadata.score if obj.metadata else None,
                }
                results.append(result)

            logger.info(
                "weaviate_search_complete",
                collection=collection,
                query_length=len(query),
                results=len(results),
            )

            return results

        except Exception as e:
            logger.error(
                "weaviate_search_error",
                collection=collection,
                error=str(e),
            )
            return []

    async def insert(
        self,
        collection: str,
        data: dict[str, Any],
    ) -> str:
        """Insert a single object into collection.

        Args:
            collection: Collection name
            data: Object properties to insert

        Returns:
            UUID of inserted object
        """
        if not self.client:
            raise RuntimeError("Client not connected. Call connect() first.")

        try:
            collection_obj = self.client.collections.get(collection)

            uuid = collection_obj.data.insert(properties=data)

            logger.info(
                "weaviate_insert_complete",
                collection=collection,
                uuid=str(uuid),
            )

            return str(uuid)

        except Exception as e:
            logger.error(
                "weaviate_insert_error",
                collection=collection,
                error=str(e),
            )
            raise

    async def batch_insert(
        self,
        collection: str,
        data_list: list[dict[str, Any]],
    ) -> list[str]:
        """Insert multiple objects into collection.

        Args:
            collection: Collection name
            data_list: List of object properties to insert

        Returns:
            List of UUIDs for inserted objects
        """
        if not self.client:
            raise RuntimeError("Client not connected. Call connect() first.")

        try:
            collection_obj = self.client.collections.get(collection)

            # Use batch insert for efficiency
            with collection_obj.batch.dynamic() as batch:
                uuids = []
                for data in data_list:
                    uuid = batch.add_object(properties=data)
                    uuids.append(str(uuid))

            logger.info(
                "weaviate_batch_insert_complete",
                collection=collection,
                count=len(uuids),
            )

            return uuids

        except Exception as e:
            logger.error(
                "weaviate_batch_insert_error",
                collection=collection,
                error=str(e),
            )
            raise

    async def delete_collection(self, collection: str) -> None:
        """Delete a collection.

        Args:
            collection: Collection name to delete
        """
        if not self.client:
            raise RuntimeError("Client not connected. Call connect() first.")

        try:
            self.client.collections.delete(collection)
            logger.info("weaviate_collection_deleted", collection=collection)
        except Exception as e:
            logger.warning(
                "weaviate_delete_collection_error",
                collection=collection,
                error=str(e),
            )

    async def collection_exists(self, collection: str) -> bool:
        """Check if collection exists.

        Args:
            collection: Collection name

        Returns:
            True if collection exists
        """
        if not self.client:
            raise RuntimeError("Client not connected. Call connect() first.")

        try:
            return self.client.collections.exists(collection)
        except Exception as e:
            logger.error(
                "weaviate_collection_exists_error",
                collection=collection,
                error=str(e),
            )
            return False

    async def count(self, collection: str) -> int:
        """Count objects in collection.

        Args:
            collection: Collection name

        Returns:
            Number of objects in collection
        """
        if not self.client:
            raise RuntimeError("Client not connected. Call connect() first.")

        try:
            collection_obj = self.client.collections.get(collection)
            # Use aggregate to get count
            response = collection_obj.aggregate.over_all(total_count=True)
            return response.total_count or 0
        except Exception as e:
            logger.error(
                "weaviate_count_error",
                collection=collection,
                error=str(e),
            )
            return 0

"""Weaviate collection schemas for RAG."""

import weaviate
from weaviate.classes.config import Configure, Property, DataType

from test_data_agent.utils.logging import get_logger

logger = get_logger(__name__)


async def ensure_collections(client: weaviate.WeaviateClient) -> None:
    """Ensure all RAG collections exist with proper schemas.

    Args:
        client: Connected Weaviate client
    """
    collections = [
        ("TestDataPattern", _create_test_data_pattern_schema),
        ("DefectPattern", _create_defect_pattern_schema),
        ("ProductionSample", _create_production_sample_schema),
    ]

    for collection_name, schema_fn in collections:
        try:
            if client.collections.exists(collection_name):
                logger.info("weaviate_collection_exists", collection=collection_name)
            else:
                schema_fn(client)
                logger.info("weaviate_collection_created", collection=collection_name)
        except Exception as e:
            logger.error(
                "weaviate_collection_error",
                collection=collection_name,
                error=str(e),
            )
            raise


def _create_test_data_pattern_schema(client: weaviate.WeaviateClient) -> None:
    """Create TestDataPattern collection.

    Stores successful test data examples for pattern matching.
    """
    client.collections.create(
        name="TestDataPattern",
        description="Successful test data patterns for RAG retrieval",
        vectorizer_config=Configure.Vectorizer.none(),
        properties=[
            Property(
                name="domain",
                data_type=DataType.TEXT,
                description="Domain (ecommerce, supply_chain, etc.)",
            ),
            Property(
                name="entity",
                data_type=DataType.TEXT,
                description="Entity type (cart, order, user, etc.)",
            ),
            Property(
                name="scenario",
                data_type=DataType.TEXT,
                description="Test scenario name",
            ),
            Property(
                name="data",
                data_type=DataType.TEXT,
                description="JSON string of test data",
                vectorize_property_name=False,
            ),
            Property(
                name="quality_score",
                data_type=DataType.NUMBER,
                description="Quality score (0-1)",
                vectorize_property_name=False,
            ),
            Property(
                name="usage_count",
                data_type=DataType.INT,
                description="Number of times used",
                vectorize_property_name=False,
            ),
            Property(
                name="created_at",
                data_type=DataType.DATE,
                description="Creation timestamp",
                vectorize_property_name=False,
            ),
        ],
    )


def _create_defect_pattern_schema(client: weaviate.WeaviateClient) -> None:
    """Create DefectPattern collection.

    Stores data patterns that have caused bugs in the past.
    """
    client.collections.create(
        name="DefectPattern",
        description="Data patterns that triggered defects",
        vectorizer_config=Configure.Vectorizer.none(),
        properties=[
            Property(
                name="defect_id",
                data_type=DataType.TEXT,
                description="Unique defect identifier",
            ),
            Property(
                name="domain",
                data_type=DataType.TEXT,
                description="Domain where defect occurred",
            ),
            Property(
                name="entity",
                data_type=DataType.TEXT,
                description="Entity type involved",
            ),
            Property(
                name="trigger_data",
                data_type=DataType.TEXT,
                description="JSON string of data that triggered bug",
                vectorize_property_name=False,
            ),
            Property(
                name="defect_description",
                data_type=DataType.TEXT,
                description="Description of the defect",
            ),
            Property(
                name="severity",
                data_type=DataType.TEXT,
                description="Severity: low, medium, high, critical",
            ),
            Property(
                name="discovered_at",
                data_type=DataType.DATE,
                description="When defect was discovered",
                vectorize_property_name=False,
            ),
        ],
    )


def _create_production_sample_schema(client: weaviate.WeaviateClient) -> None:
    """Create ProductionSample collection.

    Stores anonymized production data patterns and distributions.
    """
    client.collections.create(
        name="ProductionSample",
        description="Anonymized production data patterns",
        vectorizer_config=Configure.Vectorizer.none(),
        properties=[
            Property(
                name="domain",
                data_type=DataType.TEXT,
                description="Domain",
            ),
            Property(
                name="entity",
                data_type=DataType.TEXT,
                description="Entity type",
            ),
            Property(
                name="anonymized_data",
                data_type=DataType.TEXT,
                description="Anonymized JSON data",
                vectorize_property_name=False,
            ),
            Property(
                name="distribution_stats",
                data_type=DataType.TEXT,
                description="Statistical distribution info (JSON)",
                vectorize_property_name=False,
            ),
            Property(
                name="sample_date",
                data_type=DataType.DATE,
                description="When sample was collected",
                vectorize_property_name=False,
            ),
        ],
    )

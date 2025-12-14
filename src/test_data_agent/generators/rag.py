"""RAG-based data generator using vector database patterns."""

import json
import time
from datetime import datetime
from typing import Any
import uuid

from test_data_agent.generators.base import BaseGenerator, GenerationResult
from test_data_agent.clients.weaviate_client import WeaviateClient
from test_data_agent.proto import test_data_pb2
from test_data_agent.utils.logging import get_logger

logger = get_logger(__name__)


class RAGGenerator(BaseGenerator):
    """Generator that retrieves patterns from vector DB for data generation."""

    def __init__(self, weaviate_client: WeaviateClient, top_k: int = 5):
        """Initialize RAG generator.

        Args:
            weaviate_client: Weaviate client for pattern retrieval
            top_k: Number of examples to retrieve
        """
        self.weaviate_client = weaviate_client
        self.top_k = top_k

    async def generate(
        self,
        request: test_data_pb2.GenerateRequest,
        context: dict | None = None,
    ) -> GenerationResult:
        """Generate data using RAG patterns.

        Args:
            request: Generate data request
            context: Optional context

        Returns:
            GenerationResult with generated data
        """
        start_time = time.time()

        logger.info(
            "rag_generate_start",
            request_id=request.request_id,
            count=request.count,
            entity=request.entity,
            defect_triggering=request.defect_triggering,
            production_like=request.production_like,
        )

        # Determine which collection to search
        collection = self._select_collection(request)

        # Build search query
        search_query = self._build_search_query(request)

        # Retrieve patterns
        patterns = await self.weaviate_client.search(
            collection=collection,
            query=search_query,
            top_k=self.top_k,
        )

        if not patterns:
            logger.warning(
                "rag_no_patterns_found",
                request_id=request.request_id,
                collection=collection,
            )
            # Return empty result - caller should fall back to another generator
            return GenerationResult(
                data=[],
                metadata={
                    "generation_path": "rag",
                    "rag_collection": collection,
                    "patterns_found": 0,
                    "generation_time_ms": (time.time() - start_time) * 1000,
                },
            )

        # Generate data from patterns
        data = self._generate_from_patterns(patterns, request)

        duration = time.time() - start_time

        logger.info(
            "rag_generate_success",
            request_id=request.request_id,
            records=len(data),
            patterns_used=len(patterns),
            duration=duration,
        )

        return GenerationResult(
            data=data,
            metadata={
                "generation_path": "rag",
                "rag_collection": collection,
                "patterns_found": len(patterns),
                "generation_time_ms": duration * 1000,
                "coherence_score": 0.0,  # RAG patterns are pre-validated
            },
        )

    async def generate_stream(
        self,
        request: test_data_pb2.GenerateRequest,
        batch_size: int = 50,
        context: dict | None = None,
    ):
        """Stream RAG-generated records in batches.

        Args:
            request: Generate data request
            batch_size: Number of records per batch
            context: Optional context

        Yields:
            GenerationResult for each batch
        """
        # Use default implementation from BaseGenerator
        result = await self.generate(request, context)

        # Yield in batches
        for i in range(0, len(result.data), batch_size):
            batch = result.data[i : i + batch_size]
            yield GenerationResult(
                data=batch,
                metadata={
                    **result.metadata,
                    "batch_index": i // batch_size,
                    "batch_size": len(batch),
                },
            )

    def supports(self, request: test_data_pb2.GenerateRequest) -> bool:
        """Check if RAG generator can handle this request.

        Args:
            request: Generate data request

        Returns:
            True if RAG should be used
        """
        # Use RAG if:
        # - learn_from_history flag set
        # - defect_triggering mode
        # - production_like distributions needed

        if request.learn_from_history:
            return True

        if request.defect_triggering:
            return True

        if request.production_like:
            return True

        return False

    def _select_collection(self, request: test_data_pb2.GenerateRequest) -> str:
        """Select which Weaviate collection to search.

        Args:
            request: Generate data request

        Returns:
            Collection name
        """
        if request.defect_triggering:
            return self.weaviate_client.COLLECTION_DEFECTS

        if request.production_like:
            return self.weaviate_client.COLLECTION_PROD_SAMPLES

        # Default to patterns collection
        return self.weaviate_client.COLLECTION_PATTERNS

    def _build_search_query(self, request: test_data_pb2.GenerateRequest) -> str:
        """Build search query for vector search.

        Args:
            request: Generate data request

        Returns:
            Search query string
        """
        query_parts = []

        if request.domain:
            query_parts.append(f"domain: {request.domain}")

        if request.entity:
            query_parts.append(f"entity: {request.entity}")

        if request.context:
            query_parts.append(request.context)

        # Add scenario descriptions
        for scenario in request.scenarios:
            if scenario.description:
                query_parts.append(scenario.description)

        query = " ".join(query_parts)

        # Fallback to basic query
        if not query:
            query = f"{request.domain} {request.entity} test data"

        logger.debug("rag_search_query", query=query)

        return query

    def _generate_from_patterns(
        self,
        patterns: list[dict[str, Any]],
        request: test_data_pb2.GenerateRequest,
    ) -> list[dict]:
        """Generate new data based on retrieved patterns.

        Args:
            patterns: Retrieved patterns from vector DB
            request: Generate data request

        Returns:
            List of generated records
        """
        generated = []

        # Calculate how many records to generate from each pattern
        records_per_pattern = max(1, request.count // len(patterns))
        remainder = request.count % len(patterns)

        for idx, pattern in enumerate(patterns):
            # Get pattern data
            pattern_data = pattern.get("data", {})

            # Parse JSON if it's a string
            if isinstance(pattern_data, str):
                try:
                    pattern_data = json.loads(pattern_data)
                except json.JSONDecodeError:
                    logger.warning("rag_pattern_parse_error", pattern_id=pattern.get("id"))
                    continue

            # Determine collection-specific data field
            if "data" in pattern_data:
                example_data = pattern_data["data"]
            elif "trigger_data" in pattern_data:
                example_data = pattern_data["trigger_data"]
            elif "anonymized_data" in pattern_data:
                example_data = pattern_data["anonymized_data"]
            else:
                example_data = pattern_data

            # Parse if string
            if isinstance(example_data, str):
                try:
                    example_data = json.loads(example_data)
                except json.JSONDecodeError:
                    example_data = pattern_data

            # Generate variations of this pattern
            num_variations = records_per_pattern + (1 if idx < remainder else 0)

            for i in range(num_variations):
                # Create variation by updating dynamic fields
                variation = self._create_variation(example_data, i)
                generated.append(variation)

                if len(generated) >= request.count:
                    break

            if len(generated) >= request.count:
                break

        # Add metadata fields
        generated = self._add_metadata_fields(generated)

        return generated[:request.count]

    def _create_variation(self, template: dict, index: int) -> dict:
        """Create a variation of a template record.

        Args:
            template: Template record
            index: Variation index

        Returns:
            New record with updated dynamic fields
        """
        variation = template.copy()

        # Update IDs (if present)
        id_fields = [
            "cart_id",
            "order_id",
            "payment_id",
            "user_id",
            "review_id",
            "transaction_id",
        ]
        for field in id_fields:
            if field in variation:
                # Generate new ID keeping the format
                original = variation[field]
                if isinstance(original, str) and "-" in original:
                    # Format like CRT-2025-1234567
                    parts = original.split("-")
                    if len(parts) == 3:
                        # Keep prefix and year, generate new number
                        new_num = str(hash(f"{original}{index}") % 10000000).zfill(7)
                        variation[field] = f"{parts[0]}-{parts[1]}-{new_num}"

        # Update timestamps to current
        timestamp_fields = ["created_at", "updated_at", "modified_at", "timestamp"]
        current_time = datetime.now().isoformat()
        for field in timestamp_fields:
            if field in variation:
                variation[field] = current_time

        # Update UUIDs
        if "uuid" in variation or "id" in variation:
            key = "uuid" if "uuid" in variation else "id"
            variation[key] = str(uuid.uuid4())

        return variation

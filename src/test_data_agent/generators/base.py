"""Abstract base class for all data generators."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import AsyncIterator

from test_data_agent.proto import test_data_pb2


@dataclass
class GenerationResult:
    """Result from a generator."""

    data: list[dict]  # Generated records
    metadata: dict  # Metadata about generation (tokens, duration, etc.)

    def __post_init__(self):
        """Validate the result."""
        if not isinstance(self.data, list):
            raise ValueError("data must be a list")
        if not isinstance(self.metadata, dict):
            raise ValueError("metadata must be a dict")


class BaseGenerator(ABC):
    """Abstract base for all data generators."""

    @abstractmethod
    async def generate(
        self,
        request: test_data_pb2.GenerateRequest,
        context: dict | None = None,
    ) -> GenerationResult:
        """
        Generate records based on request.

        Args:
            request: Generate data request from gRPC
            context: Optional context (e.g., RAG examples for hybrid generation)

        Returns:
            GenerationResult with data and metadata
        """
        pass

    @abstractmethod
    async def generate_stream(
        self,
        request: test_data_pb2.GenerateRequest,
        batch_size: int = 50,
        context: dict | None = None,
    ) -> AsyncIterator[GenerationResult]:
        """
        Stream records in batches.

        Args:
            request: Generate data request from gRPC
            batch_size: Number of records per batch
            context: Optional context for generation

        Yields:
            GenerationResult for each batch
        """
        # Default implementation - subclasses can override
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

    @abstractmethod
    def supports(self, request: test_data_pb2.GenerateRequest) -> bool:
        """
        Check if this generator can handle the request.

        Args:
            request: Generate data request

        Returns:
            True if this generator supports the request
        """
        pass

    def _add_metadata_fields(self, records: list[dict]) -> list[dict]:
        """
        Add metadata fields to records (_index, _scenario).

        Args:
            records: List of generated records

        Returns:
            Records with metadata fields
        """
        for idx, record in enumerate(records):
            record["_index"] = idx
            if "_scenario" not in record:
                record["_scenario"] = "default"

        return records

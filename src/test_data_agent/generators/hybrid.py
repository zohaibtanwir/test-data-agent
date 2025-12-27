"""Hybrid generator combining RAG retrieval with LLM generation."""

import time

from test_data_agent.generators.base import BaseGenerator, GenerationResult
from test_data_agent.generators.rag import RAGGenerator
from test_data_agent.generators.llm import LLMGenerator
from test_data_agent.proto import test_data_pb2
from test_data_agent.utils.logging import get_logger

logger = get_logger(__name__)


class HybridGenerator(BaseGenerator):
    """Generator that combines RAG retrieval with LLM intelligence."""

    def __init__(
        self,
        rag_generator: RAGGenerator,
        llm_generator: LLMGenerator,
    ):
        """Initialize hybrid generator.

        Args:
            rag_generator: RAG generator for pattern retrieval
            llm_generator: LLM generator for intelligent generation
        """
        self.rag_generator = rag_generator
        self.llm_generator = llm_generator

    async def generate(
        self,
        request: test_data_pb2.GenerateRequest,
        context: dict | None = None,
    ) -> GenerationResult:
        """Generate data using RAG + LLM hybrid approach.

        Args:
            request: Generate data request
            context: Optional context (will be enhanced with RAG examples)

        Returns:
            GenerationResult with generated data
        """
        start_time = time.time()

        logger.info(
            "hybrid_generate_start",
            request_id=request.request_id,
            count=request.count,
            entity=request.entity,
        )

        # Step 1: Retrieve relevant patterns from RAG
        rag_result = await self.rag_generator.generate(request, context)

        rag_examples = []
        if rag_result.data:
            # Use RAG results as examples
            rag_examples = rag_result.data
            logger.info(
                "hybrid_rag_retrieval",
                request_id=request.request_id,
                examples_retrieved=len(rag_examples),
            )
        else:
            logger.warning(
                "hybrid_no_rag_examples",
                request_id=request.request_id,
                falling_back="llm_only",
            )

        # Step 2: Pass RAG examples to LLM for informed generation
        enhanced_context = context.copy() if context else {}
        enhanced_context["rag_examples"] = rag_examples

        # Use LLM to generate new data informed by RAG examples
        llm_result = await self.llm_generator.generate(request, context=enhanced_context)

        duration = time.time() - start_time

        logger.info(
            "hybrid_generate_success",
            request_id=request.request_id,
            records=len(llm_result.data),
            rag_examples_used=len(rag_examples),
            duration=duration,
        )

        # Combine metadata from both generators
        return GenerationResult(
            data=llm_result.data,
            metadata={
                "generation_path": "hybrid",
                "rag_examples_used": len(rag_examples),
                "rag_collection": rag_result.metadata.get("rag_collection", "unknown"),
                "llm_provider": llm_result.metadata.get("llm_provider", "unknown"),
                "llm_tokens_used": llm_result.metadata.get("tokens_used", 0),
                "generation_time_ms": duration * 1000,
                "coherence_score": llm_result.metadata.get("coherence_score", 0.0),
            },
        )

    async def generate_stream(
        self,
        request: test_data_pb2.GenerateRequest,
        batch_size: int = 50,
        context: dict | None = None,
    ):
        """Stream hybrid-generated records in batches.

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
        """Check if hybrid generator can handle this request.

        Args:
            request: Generate data request

        Returns:
            True if hybrid approach is best
        """
        # Use HYBRID when both RAG and LLM conditions are met

        has_rag_need = (
            request.learn_from_history or request.defect_triggering or request.production_like
        )

        has_llm_need = bool(request.context) or any(
            hint in [h.lower() for h in request.hints]
            for hint in ["realistic", "coherent", "intelligent"]
        )

        # Also use hybrid for complex scenarios with patterns
        complex_scenarios = len(request.scenarios) > 2

        return (has_rag_need and has_llm_need) or (complex_scenarios and has_rag_need)

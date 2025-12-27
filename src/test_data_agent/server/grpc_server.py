"""gRPC server implementation for Test Data Service."""

import json
from concurrent import futures
from typing import AsyncIterator

import grpc
from grpc_reflection.v1alpha import reflection

from test_data_agent.config import Settings
from test_data_agent.generators.traditional import TraditionalGenerator
from test_data_agent.generators.llm import LLMGenerator
from test_data_agent.generators.rag import RAGGenerator
from test_data_agent.generators.hybrid import HybridGenerator
from test_data_agent.clients.claude import ClaudeClient
from test_data_agent.clients.vllm import VLLMClient
from test_data_agent.clients.weaviate_client import WeaviateClient
from test_data_agent.prompts.builder import PromptBuilder
from test_data_agent.validators.constraint import ConstraintValidator
from test_data_agent.validators.coherence import CoherenceScorer
from test_data_agent.router.intelligence_router import IntelligenceRouter, GenerationPath
from test_data_agent.proto import test_data_pb2, test_data_pb2_grpc
from test_data_agent.schemas.registry import get_registry
from test_data_agent.utils.logging import bind_request_id, clear_request_context, get_logger
from test_data_agent.utils.metrics import MetricsCollector

logger = get_logger(__name__)
metrics = MetricsCollector()


class TestDataServiceServicer(test_data_pb2_grpc.TestDataServiceServicer):
    """Implementation of TestDataService gRPC service."""

    def __init__(self, settings: Settings):
        """
        Initialize the servicer.

        Args:
            settings: Application settings
        """
        self.settings = settings
        self.registry = get_registry()

        # Initialize generators
        self.traditional_generator = TraditionalGenerator()

        # Initialize LLM clients
        self.claude_client = ClaudeClient(settings)
        self.vllm_client = VLLMClient(settings) if settings.use_local_llm else None

        # Initialize supporting components
        self.prompt_builder = PromptBuilder()
        self.constraint_validator = ConstraintValidator()
        self.coherence_scorer = CoherenceScorer()

        # Initialize LLM generator
        self.llm_generator = LLMGenerator(
            claude_client=self.claude_client,
            vllm_client=self.vllm_client,
            prompt_builder=self.prompt_builder,
            constraint_validator=self.constraint_validator,
        )

        # Initialize Weaviate client for RAG
        self.weaviate_client = WeaviateClient(settings)

        # Initialize RAG generator
        self.rag_generator = RAGGenerator(
            weaviate_client=self.weaviate_client,
            top_k=settings.rag_top_k,
        )

        # Initialize Hybrid generator
        self.hybrid_generator = HybridGenerator(
            rag_generator=self.rag_generator,
            llm_generator=self.llm_generator,
        )

        # Initialize intelligence router
        self.router = IntelligenceRouter()

        logger.info(
            "test_data_servicer_initialized",
            grpc_port=settings.grpc_port,
            llm_enabled=True,
            vllm_enabled=self.vllm_client is not None,
            rag_enabled=True,
        )

    async def GenerateData(
        self,
        request: test_data_pb2.GenerateRequest,
        context: grpc.aio.ServicerContext,
    ) -> test_data_pb2.GenerateResponse:
        """
        Generate test data synchronously.

        Args:
            request: Generate data request
            context: gRPC context

        Returns:
            Generate data response
        """
        # Bind request ID for logging
        if request.request_id:
            bind_request_id(request.request_id)

        logger.info(
            "generate_data_request",
            request_id=request.request_id,
            domain=request.domain,
            entity=request.entity,
            count=request.count,
        )

        try:
            # Check record count limit
            if request.count > self.settings.max_sync_records:
                metrics.record_request(
                    path="traditional",
                    domain=request.domain,
                    entity=request.entity,
                    status="error",
                    duration=0,
                )
                return test_data_pb2.GenerateResponse(
                    request_id=request.request_id,
                    success=False,
                    data="",
                    record_count=0,
                    error=f"Count {request.count} exceeds max sync limit {self.settings.max_sync_records}. Use streaming instead.",
                )

            # Route request to appropriate generator
            routing_decision = self.router.route(request)
            logger.info(
                "routing_decision",
                request_id=request.request_id,
                path=routing_decision.path.value,
                reason=routing_decision.reason,
                confidence=routing_decision.confidence,
            )

            # Get schema dict for context
            schema_dict = {}
            if request.inline_schema:
                # Parse inline schema JSON
                try:
                    schema_dict = json.loads(request.inline_schema)
                    # Register temporarily if it has a name
                    if "name" in schema_dict:
                        self.registry.register_schema(schema_dict)
                    logger.info(
                        "inline_schema_loaded",
                        request_id=request.request_id,
                        schema_name=schema_dict.get("name", "anonymous"),
                    )
                except json.JSONDecodeError as e:
                    logger.error(
                        "inline_schema_parse_error",
                        request_id=request.request_id,
                        error=str(e),
                    )
            elif request.schema and request.schema.predefined_schema:
                found_schema = self.registry.get_schema(request.schema.predefined_schema)
                if found_schema:
                    schema_dict = found_schema
                else:
                    logger.warning(
                        "predefined_schema_not_found",
                        request_id=request.request_id,
                        schema_name=request.schema.predefined_schema,
                        msg="Will generate without predefined schema",
                    )
            elif request.entity:
                # Try to find schema by entity name
                found_schema = self.registry.get_schema(request.entity)
                if found_schema:
                    schema_dict = found_schema
                else:
                    logger.debug(
                        "entity_schema_not_found",
                        request_id=request.request_id,
                        entity=request.entity,
                        msg="Will generate without predefined schema",
                    )

            # Generate using selected path
            if routing_decision.path == GenerationPath.LLM:
                # LLM generation
                context = {"schema_dict": schema_dict}
                result = await self.llm_generator.generate(request, context=context)
            elif routing_decision.path == GenerationPath.TRADITIONAL:
                # Traditional generation
                result = await self.traditional_generator.generate(request)
            elif routing_decision.path == GenerationPath.RAG:
                # RAG generation - connect to Weaviate first
                try:
                    await self.weaviate_client.connect()
                    context = {"schema_dict": schema_dict}
                    result = await self.rag_generator.generate(request, context=context)
                    await self.weaviate_client.disconnect()

                    # Fall back to Traditional if RAG found no patterns
                    if not result.data:
                        logger.warning(
                            "rag_no_results_fallback",
                            request_id=request.request_id,
                            falling_back_to="traditional",
                        )
                        result = await self.traditional_generator.generate(request)
                except Exception as e:
                    logger.error("rag_error", error=str(e), request_id=request.request_id)
                    # Fall back to Traditional on error
                    result = await self.traditional_generator.generate(request)
                    await self.weaviate_client.disconnect()
            elif routing_decision.path == GenerationPath.HYBRID:
                # Hybrid generation (RAG + LLM)
                try:
                    await self.weaviate_client.connect()
                    context = {"schema_dict": schema_dict}
                    result = await self.hybrid_generator.generate(request, context=context)
                    await self.weaviate_client.disconnect()
                except Exception as e:
                    logger.error("hybrid_error", error=str(e), request_id=request.request_id)
                    # Fall back to LLM on error
                    context = {"schema_dict": schema_dict}
                    result = await self.llm_generator.generate(request, context=context)
                    await self.weaviate_client.disconnect()
            else:
                # Unknown path, use Traditional
                result = await self.traditional_generator.generate(request)

            # Calculate coherence score for all entities
            coherence_score = result.metadata.get("coherence_score", 0.0)
            if result.data:
                coherence_scores = [
                    self.coherence_scorer.score(record, request.entity) for record in result.data
                ]
                coherence_score = (
                    sum(coherence_scores) / len(coherence_scores) if coherence_scores else 0.0
                )
                logger.info(
                    "coherence_scored",
                    request_id=request.request_id,
                    entity=request.entity,
                    score=coherence_score,
                )

            # Convert to JSON
            data_json = json.dumps(result.data, indent=2)

            # Build metadata
            generation_path = result.metadata.get("generation_path", routing_decision.path.value)
            duration_ms = result.metadata.get("generation_time_ms", 0)

            metadata = test_data_pb2.GenerationMetadata(
                generation_path=generation_path,
                llm_tokens_used=result.metadata.get("llm_tokens_used", 0),
                generation_time_ms=duration_ms,
                coherence_score=coherence_score,
            )

            # Record metrics
            metrics.record_request(
                path=generation_path,
                domain=request.domain,
                entity=request.entity,
                status="success",
                duration=duration_ms / 1000,  # Convert ms to seconds
            )
            metrics.record_records_generated(
                domain=request.domain,
                entity=request.entity,
                count=len(result.data),
            )

            logger.info(
                "generate_data_success",
                request_id=request.request_id,
                record_count=len(result.data),
            )

            return test_data_pb2.GenerateResponse(
                request_id=request.request_id,
                success=True,
                data=data_json,
                record_count=len(result.data),
                metadata=metadata,
            )

        except Exception as e:
            # Record error metrics
            metrics.record_request(
                path="traditional",
                domain=request.domain,
                entity=request.entity,
                status="error",
                duration=0,
            )

            logger.error(
                "generate_data_error",
                request_id=request.request_id,
                error=str(e),
                exc_info=True,
            )
            return test_data_pb2.GenerateResponse(
                request_id=request.request_id,
                success=False,
                data="",
                record_count=0,
                error=str(e),
            )
        finally:
            clear_request_context()

    async def GenerateDataStream(
        self,
        request: test_data_pb2.GenerateRequest,
        context: grpc.aio.ServicerContext,
    ) -> AsyncIterator[test_data_pb2.DataChunk]:
        """
        Generate test data with streaming.

        Args:
            request: Generate data request
            context: gRPC context

        Yields:
            Data chunks
        """
        # Bind request ID for logging
        if request.request_id:
            bind_request_id(request.request_id)

        logger.info(
            "generate_data_stream_request",
            request_id=request.request_id,
            domain=request.domain,
            entity=request.entity,
            count=request.count,
        )

        try:
            # Route request to appropriate generator
            routing_decision = self.router.route(request)
            logger.info(
                "routing_decision_stream",
                request_id=request.request_id,
                path=routing_decision.path.value,
                reason=routing_decision.reason,
            )

            # Get schema dict for context
            schema_dict = {}
            if request.inline_schema:
                # Parse inline schema JSON
                try:
                    schema_dict = json.loads(request.inline_schema)
                    # Register temporarily if it has a name
                    if "name" in schema_dict:
                        self.registry.register_schema(schema_dict)
                    logger.info(
                        "inline_schema_loaded_stream",
                        request_id=request.request_id,
                        schema_name=schema_dict.get("name", "anonymous"),
                    )
                except json.JSONDecodeError as e:
                    logger.error(
                        "inline_schema_parse_error_stream",
                        request_id=request.request_id,
                        error=str(e),
                    )
            elif request.schema and request.schema.predefined_schema:
                found_schema = self.registry.get_schema(request.schema.predefined_schema)
                if found_schema:
                    schema_dict = found_schema
                else:
                    logger.warning(
                        "predefined_schema_not_found",
                        request_id=request.request_id,
                        schema_name=request.schema.predefined_schema,
                        msg="Will generate without predefined schema",
                    )
            elif request.entity:
                # Try to find schema by entity name
                found_schema = self.registry.get_schema(request.entity)
                if found_schema:
                    schema_dict = found_schema
                else:
                    logger.debug(
                        "entity_schema_not_found",
                        request_id=request.request_id,
                        entity=request.entity,
                        msg="Will generate without predefined schema",
                    )

            # Determine batch size (default or from settings)
            batch_size = getattr(self.settings, "default_batch_size", 50)

            # Generate using selected path
            chunk_index = 0
            total_records = 0

            if routing_decision.path == GenerationPath.LLM:
                # LLM generation stream
                gen_context = {"schema_dict": schema_dict}
                async for result in self.llm_generator.generate_stream(
                    request, batch_size=batch_size, context=gen_context
                ):
                    data_json = json.dumps(result.data)
                    total_records += len(result.data)

                    yield test_data_pb2.DataChunk(
                        request_id=request.request_id,
                        data=data_json,
                        chunk_index=chunk_index,
                        is_final=False,
                    )
                    chunk_index += 1

            elif routing_decision.path == GenerationPath.TRADITIONAL:
                # Traditional generation stream
                async for result in self.traditional_generator.generate_stream(
                    request, batch_size=batch_size
                ):
                    data_json = json.dumps(result.data)
                    total_records += len(result.data)

                    yield test_data_pb2.DataChunk(
                        request_id=request.request_id,
                        data=data_json,
                        chunk_index=chunk_index,
                        is_final=False,
                    )
                    chunk_index += 1

            elif routing_decision.path == GenerationPath.RAG:
                # RAG generation stream
                try:
                    await self.weaviate_client.connect()
                    gen_context = {"schema_dict": schema_dict}
                    async for result in self.rag_generator.generate_stream(
                        request, batch_size=batch_size, context=gen_context
                    ):
                        data_json = json.dumps(result.data)
                        total_records += len(result.data)

                        yield test_data_pb2.DataChunk(
                            request_id=request.request_id,
                            data=data_json,
                            chunk_index=chunk_index,
                            is_final=False,
                        )
                        chunk_index += 1
                    await self.weaviate_client.disconnect()
                except Exception as e:
                    logger.error("rag_stream_error", error=str(e), request_id=request.request_id)
                    await self.weaviate_client.disconnect()
                    # Fall back to traditional
                    async for result in self.traditional_generator.generate_stream(
                        request, batch_size=batch_size
                    ):
                        data_json = json.dumps(result.data)
                        total_records += len(result.data)

                        yield test_data_pb2.DataChunk(
                            request_id=request.request_id,
                            data=data_json,
                            chunk_index=chunk_index,
                            is_final=False,
                        )
                        chunk_index += 1

            elif routing_decision.path == GenerationPath.HYBRID:
                # Hybrid generation stream
                try:
                    await self.weaviate_client.connect()
                    gen_context = {"schema_dict": schema_dict}
                    async for result in self.hybrid_generator.generate_stream(
                        request, batch_size=batch_size, context=gen_context
                    ):
                        data_json = json.dumps(result.data)
                        total_records += len(result.data)

                        yield test_data_pb2.DataChunk(
                            request_id=request.request_id,
                            data=data_json,
                            chunk_index=chunk_index,
                            is_final=False,
                        )
                        chunk_index += 1
                    await self.weaviate_client.disconnect()
                except Exception as e:
                    logger.error("hybrid_stream_error", error=str(e), request_id=request.request_id)
                    await self.weaviate_client.disconnect()
                    # Fall back to LLM
                    gen_context = {"schema_dict": schema_dict}
                    async for result in self.llm_generator.generate_stream(
                        request, batch_size=batch_size, context=gen_context
                    ):
                        data_json = json.dumps(result.data)
                        total_records += len(result.data)

                        yield test_data_pb2.DataChunk(
                            request_id=request.request_id,
                            data=data_json,
                            chunk_index=chunk_index,
                            is_final=False,
                        )
                        chunk_index += 1

            # Send final chunk
            yield test_data_pb2.DataChunk(
                request_id=request.request_id,
                data="",
                chunk_index=chunk_index,
                is_final=True,
            )

            logger.info(
                "generate_data_stream_complete",
                request_id=request.request_id,
                total_chunks=chunk_index + 1,
                total_records=total_records,
            )

        except Exception as e:
            logger.error(
                "generate_data_stream_error",
                request_id=request.request_id,
                error=str(e),
                error_type=type(e).__name__,
            )
            # Yield error chunk
            yield test_data_pb2.DataChunk(
                request_id=request.request_id,
                data=json.dumps({"error": str(e)}),
                chunk_index=0,
                is_final=True,
            )
        finally:
            clear_request_context()

    async def GetSchemas(
        self,
        request: test_data_pb2.GetSchemasRequest,
        context: grpc.aio.ServicerContext,
    ) -> test_data_pb2.GetSchemasResponse:
        """
        Get available schemas.

        Args:
            request: Get schemas request
            context: gRPC context

        Returns:
            List of available schemas
        """
        logger.info("get_schemas_request", domain=request.domain if request.domain else "all")

        try:
            # Get schemas from registry
            schemas = self.registry.list_schemas(domain=request.domain if request.domain else None)

            # Convert to proto SchemaInfo
            schema_infos = []
            for schema in schemas:
                info = self.registry.get_schema_info(schema["name"])
                if info:
                    # Convert field dictionaries to SchemaFieldInfo protobuf objects
                    field_infos = []
                    for field in info["fields"]:
                        field_info = test_data_pb2.SchemaFieldInfo(
                            name=field["name"],
                            type=field["type"],
                            required=field["required"],
                            description=field["description"],
                            example=field["example"],
                        )
                        field_infos.append(field_info)

                    schema_info = test_data_pb2.SchemaInfo(
                        name=info["name"],
                        domain=info["domain"],
                        description=info["description"],
                        fields=field_infos,
                    )
                    schema_infos.append(schema_info)

            logger.info("get_schemas_success", count=len(schema_infos))

            return test_data_pb2.GetSchemasResponse(schemas=schema_infos)

        except Exception as e:
            logger.error("get_schemas_error", error=str(e), exc_info=True)
            return test_data_pb2.GetSchemasResponse(schemas=[])

    async def HealthCheck(
        self,
        request: test_data_pb2.HealthCheckRequest,
        context: grpc.aio.ServicerContext,
    ) -> test_data_pb2.HealthCheckResponse:
        """
        Health check endpoint.

        Args:
            request: Health check request
            context: gRPC context

        Returns:
            Health status
        """
        return test_data_pb2.HealthCheckResponse(
            status="healthy",
            components={
                "grpc_server": "healthy",
                "config": "healthy",
            },
        )


class GrpcServer:
    """gRPC server manager."""

    def __init__(self, settings: Settings):
        """
        Initialize gRPC server.

        Args:
            settings: Application settings
        """
        self.settings = settings
        self.server: grpc.aio.Server | None = None
        self.servicer = TestDataServiceServicer(settings)
        logger.info("grpc_server_created", port=settings.grpc_port)

    async def start(self) -> None:
        """Start the gRPC server."""
        self.server = grpc.aio.server(
            futures.ThreadPoolExecutor(max_workers=10),
            options=[
                ("grpc.max_send_message_length", 50 * 1024 * 1024),  # 50MB
                ("grpc.max_receive_message_length", 50 * 1024 * 1024),  # 50MB
            ],
        )

        test_data_pb2_grpc.add_TestDataServiceServicer_to_server(self.servicer, self.server)

        # Enable gRPC reflection for grpcurl and other tools
        service_names = (
            test_data_pb2.DESCRIPTOR.services_by_name["TestDataService"].full_name,
            reflection.SERVICE_NAME,
        )
        reflection.enable_server_reflection(service_names, self.server)

        listen_addr = f"[::]:{self.settings.grpc_port}"
        self.server.add_insecure_port(listen_addr)

        await self.server.start()
        logger.info("grpc_server_started", address=listen_addr)

        try:
            await self.server.wait_for_termination()
        except KeyboardInterrupt:
            logger.info("grpc_server_interrupted")
            await self.stop()

    async def stop(self, grace: float = 5.0) -> None:
        """
        Stop the gRPC server gracefully.

        Args:
            grace: Grace period in seconds for shutdown
        """
        if self.server:
            logger.info("grpc_server_stopping", grace_period=grace)
            await self.server.stop(grace)
            logger.info("grpc_server_stopped")

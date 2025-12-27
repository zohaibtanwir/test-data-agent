"""HTTP routes for UI integration."""

import json
from typing import Any, Optional
from fastapi import HTTPException
from pydantic import BaseModel
import grpc

from test_data_agent.proto import test_data_pb2, test_data_pb2_grpc
from test_data_agent.utils.logging import get_logger

logger = get_logger(__name__)


class GenerateRequest(BaseModel):
    """HTTP request model for data generation."""

    domain: str
    entity: str
    count: int = 10
    context: Optional[str] = None
    scenarios: Optional[list[dict[str, Any]]] = None
    hints: Optional[list[str]] = None
    outputFormat: Optional[str] = "JSON"
    options: Optional[dict[str, bool]] = None
    generationPath: Optional[str] = None
    inlineSchema: Optional[str] = None


class SchemaInfo(BaseModel):
    """Schema information model."""

    name: str
    description: str
    fields: list[dict[str, Any]]
    domain: Optional[str] = None


def add_http_routes(app, settings):
    """Add HTTP routes for UI integration."""

    @app.post("/generate")
    async def generate_data(request: GenerateRequest):
        """Generate test data via HTTP endpoint."""
        try:
            # Connect to gRPC server
            channel = grpc.insecure_channel(f"localhost:{settings.grpc_port}")
            stub = test_data_pb2_grpc.TestDataServiceStub(channel)

            # Build gRPC request
            grpc_request = test_data_pb2.GenerateRequest(
                request_id=f"http-{request.entity}-{request.count}",
                domain=request.domain,
                entity=request.entity,
                count=request.count,
            )

            if request.context:
                grpc_request.context = request.context

            if request.scenarios:
                for scenario in request.scenarios:
                    grpc_scenario = grpc_request.scenarios.add()
                    grpc_scenario.name = scenario.get("name", "")
                    grpc_scenario.description = scenario.get("description", "")
                    grpc_scenario.weight = scenario.get("weight", 1)

            if request.hints:
                grpc_request.hints.extend(request.hints)

            if request.inlineSchema:
                grpc_request.inline_schema = request.inlineSchema

            # Make gRPC call
            response = stub.GenerateData(grpc_request)

            # Parse the data field from JSON string to object
            data = json.loads(response.data) if response.data else []

            return {
                "success": response.success,
                "requestId": response.request_id,
                "data": data,
                "recordCount": response.record_count,
                "metadata": {
                    "generationPath": (
                        response.metadata.generation_path if response.metadata else None
                    ),
                    "llmTokensUsed": (
                        response.metadata.llm_tokens_used
                        if response.metadata and response.metadata.llm_tokens_used
                        else None
                    ),
                    "generationTimeMs": (
                        response.metadata.generation_time_ms
                        if response.metadata and response.metadata.generation_time_ms
                        else 0
                    ),
                    "coherenceScore": (
                        response.metadata.coherence_score if response.metadata else None
                    ),
                    "scenarioCounts": (
                        dict(response.metadata.scenario_counts) if response.metadata else {}
                    ),
                },
                "error": response.error if response.error else None,
            }

        except grpc.RpcError as e:
            logger.error("grpc_error_in_http", error=str(e))
            raise HTTPException(status_code=500, detail=str(e))
        except Exception as e:
            logger.error("http_generate_error", error=str(e))
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/schemas")
    async def list_schemas(domain: Optional[str] = None):
        """List available schemas."""
        try:
            # Connect to gRPC server
            channel = grpc.insecure_channel(f"localhost:{settings.grpc_port}")
            stub = test_data_pb2_grpc.TestDataServiceStub(channel)

            # Build gRPC request
            grpc_request = test_data_pb2.ListSchemasRequest()
            if domain:
                grpc_request.domain = domain

            # Make gRPC call
            response = stub.ListSchemas(grpc_request)

            schemas = []
            for schema in response.schemas:
                schemas.append(
                    {
                        "name": schema.name,
                        "description": schema.description,
                        "fields": [
                            {
                                "name": field.name,
                                "type": field.type,
                                "required": field.required,
                                "description": field.description,
                            }
                            for field in schema.fields
                        ],
                        "domain": schema.domain if schema.domain else None,
                    }
                )

            return {"schemas": schemas}

        except grpc.RpcError as e:
            logger.error("grpc_error_in_http_schemas", error=str(e))
            raise HTTPException(status_code=500, detail=str(e))
        except Exception as e:
            logger.error("http_schemas_error", error=str(e))
            raise HTTPException(status_code=500, detail=str(e))

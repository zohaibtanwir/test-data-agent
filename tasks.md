# Test Data Agent - Implementation Tasks

> **Usage:** Copy individual tasks or task groups into your IDE's AI chat (Claude Code, Cursor, Windsurf) to implement incrementally. Each task is self-contained with clear acceptance criteria.

---

## Phase 1: Foundation

### Task 1.1: Initialize Project Structure

```
Create the Python project with the following structure:

test-data-agent/
├── README.md
├── pyproject.toml
├── Dockerfile
├── docker-compose.yml
├── Makefile
├── .env.example
├── .gitignore
├── protos/
│   └── test_data.proto
├── src/
│   └── test_data_agent/
│       ├── __init__.py
│       └── main.py
├── tests/
│   ├── __init__.py
│   └── conftest.py
└── k8s/
    └── .gitkeep

Requirements for pyproject.toml:
- Project name: test-data-agent
- Python >= 3.11
- Dependencies: grpcio, grpcio-tools, fastapi, uvicorn, pydantic, pydantic-settings, structlog, prometheus-client
- Dev dependencies: pytest, pytest-asyncio, pytest-cov, black, ruff, mypy
- Build system: hatchling

Requirements for Makefile:
- proto: generate Python code from proto files
- run: run the service locally
- test: run pytest
- lint: run ruff and mypy
- format: run black
- docker-build: build Docker image
- docker-run: run Docker container

Requirements for .gitignore:
- Python defaults (__pycache__, *.pyc, .venv, dist, etc.)
- IDE files (.idea, .vscode)
- Environment files (.env)
- Generated proto files (*_pb2.py, *_pb2_grpc.py)

Acceptance Criteria:
- [ ] Project initializes with `pip install -e .`
- [ ] All directories exist
- [ ] Makefile commands are defined (can be stubs)
- [ ] .gitignore covers all patterns
```

---

### Task 1.2: Implement Configuration Management

```
Create src/test_data_agent/config.py with Pydantic Settings.

Configuration fields needed:

Service Settings:
- service_name: str = "test-data-agent"
- grpc_port: int = 9001
- http_port: int = 8081
- log_level: str = "INFO"
- environment: str = "development"

LLM - Claude:
- anthropic_api_key: str (required, from env)
- claude_model: str = "claude-sonnet-4-20250514"
- claude_max_tokens: int = 4096
- claude_temperature: float = 0.7

LLM - Local vLLM:
- vllm_base_url: str = "http://vllm:8000/v1"
- vllm_model: str = "meta-llama/Meta-Llama-3-8B-Instruct"
- use_local_llm: bool = False

RAG - Weaviate:
- weaviate_url: str = "http://weaviate:8080"
- weaviate_api_key: str | None = None
- rag_collection_patterns: str = "testdata_patterns"
- rag_collection_defects: str = "testdata_defects"
- rag_top_k: int = 5

Cache - Redis:
- redis_url: str = "redis://redis:6379/0"
- cache_ttl_seconds: int = 86400

Generation:
- max_sync_records: int = 1000
- default_batch_size: int = 50
- coherence_threshold: float = 0.85

Observability:
- prometheus_enabled: bool = True
- tracing_enabled: bool = True
- otlp_endpoint: str = "http://otel-collector:4317"

Also create .env.example with all variables.

Acceptance Criteria:
- [ ] Settings loads from environment variables
- [ ] Settings loads from .env file
- [ ] Required fields (anthropic_api_key) raise error if missing
- [ ] Default values work correctly
- [ ] Unit test for config loading passes
```

---

### Task 1.3: Implement Structured Logging

```
Create src/test_data_agent/utils/logging.py

Requirements:
- Use structlog for structured JSON logging
- Configure based on settings.log_level
- Include fields: timestamp, level, logger, event
- Add request_id processor for correlation
- Pretty print in development, JSON in production

Create a setup_logging() function that:
1. Configures structlog processors
2. Sets log level from config
3. Returns configured logger

Also create src/test_data_agent/utils/__init__.py

Usage example the code should support:
```python
from test_data_agent.utils.logging import setup_logging, get_logger

setup_logging()
logger = get_logger(__name__)
logger.info("server_started", port=9001, version="0.1.0")
logger.error("generation_failed", request_id="req-001", error="timeout")
```

Acceptance Criteria:
- [ ] Logs output as JSON in production
- [ ] Logs are pretty-printed in development
- [ ] Log level is configurable
- [ ] request_id can be bound to logger context
- [ ] Unit test verifies log output format
```

---

### Task 1.4: Create gRPC Proto Definition

```
Create protos/test_data.proto with the full service definition.

Service: TestDataService

RPCs:
1. GenerateData(GenerateRequest) returns (GenerateResponse) - unary
2. GenerateDataStream(GenerateRequest) returns (stream DataChunk) - server streaming
3. GetSchemas(GetSchemasRequest) returns (GetSchemasResponse) - unary
4. HealthCheck(HealthCheckRequest) returns (HealthCheckResponse) - unary

Messages needed:

GenerateRequest:
- request_id: string
- domain: string
- entity: string
- schema: Schema (message)
- constraints: Constraints (message)
- scenarios: repeated Scenario (message)
- context: string
- hints: repeated string
- output_format: OutputFormat (enum)
- count: int32
- use_cache: bool
- learn_from_history: bool
- defect_triggering: bool
- production_like: bool

Schema:
- fields: repeated Field
- predefined_schema: string

Field:
- name: string
- type: FieldType (enum)
- required: bool
- description: string
- nested_fields: repeated Field

FieldType enum: STRING, INTEGER, FLOAT, BOOLEAN, DATE, DATETIME, EMAIL, PHONE, ADDRESS, UUID, ENUM, OBJECT, ARRAY

Constraints:
- field_constraints: map<string, FieldConstraint>

FieldConstraint:
- min: optional double
- max: optional double
- enum_values: repeated string
- regex: optional string
- min_length: optional int32
- max_length: optional int32

Scenario:
- name: string
- count: int32
- overrides: map<string, string>
- description: string

OutputFormat enum: JSON, CSV, SQL

GenerateResponse:
- request_id: string
- success: bool
- data: string (JSON)
- record_count: int32
- metadata: GenerationMetadata
- error: string

GenerationMetadata:
- generation_path: string
- llm_tokens_used: int32
- generation_time_ms: float
- coherence_score: float
- scenario_counts: map<string, int32>

DataChunk:
- request_id: string
- data: string
- chunk_index: int32
- is_final: bool

GetSchemasRequest:
- domain: string (optional filter)

GetSchemasResponse:
- schemas: repeated SchemaInfo

SchemaInfo:
- name: string
- domain: string
- description: string
- fields: repeated string

HealthCheckRequest: empty
HealthCheckResponse:
- status: string
- components: map<string, string>

Update Makefile 'proto' target to generate Python code:
python -m grpc_tools.protoc -I./protos --python_out=./src/test_data_agent/proto --grpc_python_out=./src/test_data_agent/proto ./protos/test_data.proto

Create src/test_data_agent/proto/__init__.py

Acceptance Criteria:
- [ ] Proto file compiles without errors
- [ ] Generated *_pb2.py and *_pb2_grpc.py files work
- [ ] All messages serialize/deserialize correctly
- [ ] make proto succeeds
```

---

### Task 1.5: Implement gRPC Server Skeleton

```
Create src/test_data_agent/server/grpc_server.py

Implement TestDataServiceServicer with stub methods:
- GenerateData: return empty response with success=false, error="not implemented"
- GenerateDataStream: yield single chunk with error
- GetSchemas: return empty list
- HealthCheck: return status="healthy"

Create a GrpcServer class that:
- Takes Settings as constructor arg
- Creates grpc.aio.server()
- Adds TestDataServiceServicer
- Binds to configured port
- Has start() and stop() async methods

Also create src/test_data_agent/server/__init__.py

Usage:
```python
server = GrpcServer(settings)
await server.start()  # Blocks until shutdown
await server.stop()
```

Acceptance Criteria:
- [ ] Server starts on configured port
- [ ] HealthCheck RPC returns healthy status
- [ ] Other RPCs return not implemented error
- [ ] Server shuts down gracefully
- [ ] Unit test for health check passes
```

---

### Task 1.6: Implement Health HTTP Endpoint

```
Create src/test_data_agent/server/health.py

Use FastAPI to create health endpoints:

GET /health
- Returns: {"status": "healthy", "service": "test-data-agent", "version": "0.1.0"}

GET /health/live
- Kubernetes liveness probe
- Returns: {"status": "ok"}

GET /health/ready
- Kubernetes readiness probe
- Check gRPC server is running
- Returns: {"status": "ready"} or 503 if not ready

GET /metrics
- Prometheus metrics endpoint (placeholder for now)

Create HealthApp class that:
- Takes Settings as constructor arg
- Creates FastAPI app
- Runs on http_port from config
- Has start() and stop() async methods

Acceptance Criteria:
- [ ] /health returns service info
- [ ] /health/live returns 200
- [ ] /health/ready returns 200 when ready, 503 when not
- [ ] FastAPI runs on configured port
- [ ] Unit test for endpoints passes
```

---

### Task 1.7: Implement Main Entry Point

```
Create src/test_data_agent/main.py

Main entry point that:
1. Loads configuration
2. Sets up logging
3. Starts gRPC server (async)
4. Starts HTTP health server (async)
5. Handles SIGTERM/SIGINT for graceful shutdown
6. Runs both servers concurrently

Use asyncio for concurrent execution.

```python
# Expected usage:
# python -m test_data_agent.main
# or
# from test_data_agent.main import main; asyncio.run(main())
```

Log startup info:
- Service name
- gRPC port
- HTTP port
- Environment

Acceptance Criteria:
- [ ] Service starts with: python -m test_data_agent.main
- [ ] Both gRPC and HTTP servers run
- [ ] Ctrl+C triggers graceful shutdown
- [ ] Startup logs show configuration
- [ ] Docker container runs successfully
```

---

### Task 1.8: Create Dockerfile and Docker Compose

```
Create Dockerfile:
- Base: python:3.11-slim
- Install dependencies from pyproject.toml
- Copy source code
- Generate proto files
- Run as non-root user
- Expose ports 9001 (gRPC) and 8081 (HTTP)
- CMD: python -m test_data_agent.main

Create docker-compose.yml with services:
1. test-data-agent (the service)
   - Build from Dockerfile
   - Ports: 9001:9001, 8081:8081
   - Environment from .env
   - Depends on: redis, weaviate

2. redis
   - Image: redis:7-alpine
   - Port: 6379

3. weaviate
   - Image: semitechnologies/weaviate:latest
   - Port: 8080
   - Environment for modules

Update Makefile:
- docker-build: docker build -t test-data-agent .
- docker-run: docker-compose up

Acceptance Criteria:
- [ ] docker build succeeds
- [ ] docker-compose up starts all services
- [ ] Health endpoint accessible at localhost:8081/health
- [ ] gRPC health check works via grpcurl
- [ ] Container logs show startup
```

---

### Task 1.9: Write Phase 1 Tests

```
Create tests for Phase 1 components:

tests/unit/test_config.py:
- test_config_loads_defaults
- test_config_loads_from_env
- test_config_requires_api_key

tests/unit/test_logging.py:
- test_logger_outputs_json
- test_logger_binds_request_id

tests/unit/test_health.py:
- test_health_endpoint
- test_liveness_endpoint
- test_readiness_endpoint

tests/integration/test_grpc_server.py:
- test_health_check_rpc
- test_generate_data_not_implemented

Use pytest-asyncio for async tests.
Use httpx for FastAPI testing.
Use grpcio for gRPC client testing.

Create tests/conftest.py with fixtures:
- settings: test configuration
- grpc_channel: async channel to test server
- http_client: async httpx client

Acceptance Criteria:
- [ ] make test runs all tests
- [ ] All tests pass
- [ ] Coverage > 80% for Phase 1 code
- [ ] Tests run in CI (GitHub Actions stub)
```

---

## Phase 2: Traditional Generator

### Task 2.1: Create Base Generator Interface

```
Create src/test_data_agent/generators/base.py

Define abstract base class:

```python
from abc import ABC, abstractmethod
from typing import AsyncIterator
# Import proto messages

class GenerationResult:
    """Result from a generator."""
    data: list[dict]
    metadata: dict  # tokens_used, duration, etc.

class BaseGenerator(ABC):
    """Abstract base for all data generators."""
    
    @abstractmethod
    async def generate(
        self,
        request: GenerateRequest,
        context: dict | None = None
    ) -> GenerationResult:
        """Generate records based on request."""
        pass
    
    @abstractmethod
    async def generate_stream(
        self,
        request: GenerateRequest,
        batch_size: int = 50,
        context: dict | None = None
    ) -> AsyncIterator[GenerationResult]:
        """Stream records in batches."""
        pass
    
    @abstractmethod
    def supports(self, request: GenerateRequest) -> bool:
        """Check if this generator can handle the request."""
        pass
```

Also create src/test_data_agent/generators/__init__.py with exports.

Acceptance Criteria:
- [ ] BaseGenerator is abstract, cannot be instantiated
- [ ] Type hints are complete
- [ ] Docstrings explain each method
```

---

### Task 2.2: Implement Schema Registry

```
Create src/test_data_agent/schemas/registry.py

SchemaRegistry class that:
- Stores pre-defined entity schemas
- Loads schemas from entities/ directory
- Provides get_schema(name) method
- Provides list_schemas(domain=None) method
- Validates schemas on load

Create src/test_data_agent/schemas/entities/ with:

cart.py - Shopping cart schema:
- cart_id, customer_id, items (array), subtotal, tax, total, currency, timestamps
- Coherence rules: total = subtotal + tax

order.py - Order schema:
- order_id, customer_id, items, shipping_address, billing_address, payment, status, timestamps

payment.py - Payment schema:
- payment_id, order_id, method (enum), amount, currency, status, card_last_four, timestamps

user.py - User/customer schema:
- user_id, email, first_name, last_name, phone, addresses, loyalty_tier, timestamps

review.py - Product review schema:
- review_id, product_id, user_id, rating (1-5), title, body, verified_purchase, helpful_votes, timestamps

Each schema should be a dict with:
- name, domain, description
- fields (with type, required, constraints)
- coherence_rules (optional)

Create src/test_data_agent/schemas/__init__.py

Acceptance Criteria:
- [ ] SchemaRegistry.get_schema("cart") returns cart schema
- [ ] SchemaRegistry.list_schemas() returns all 5 schemas
- [ ] SchemaRegistry.list_schemas(domain="ecommerce") filters correctly
- [ ] Invalid schema raises ValidationError
- [ ] Unit tests for registry operations
```

---

### Task 2.3: Implement Constraint Validator

```
Create src/test_data_agent/validators/constraint.py

ConstraintValidator class that validates generated data against constraints:

Supported constraints:
- min/max for numbers
- min_length/max_length for strings
- enum_values for enums
- regex patterns
- required fields
- nested object validation
- array item validation

Methods:
- validate(data: dict, schema: dict, constraints: dict) -> ValidationResult
- validate_field(value: any, field_def: dict, constraint: dict) -> list[str]

ValidationResult:
- valid: bool
- errors: list[ValidationError]

ValidationError:
- field: str
- message: str
- value: any

Also create src/test_data_agent/validators/__init__.py

Acceptance Criteria:
- [ ] Validates min/max correctly
- [ ] Validates string length
- [ ] Validates enum membership
- [ ] Validates regex patterns
- [ ] Validates nested objects
- [ ] Returns all errors, not just first
- [ ] Unit tests cover all constraint types
```

---

### Task 2.4: Implement Traditional Generator

```
Create src/test_data_agent/generators/traditional.py

TraditionalGenerator extends BaseGenerator:

Uses Faker for generation with:
- Standard providers: name, email, phone, address, date, etc.
- Custom providers for:
  - SKU format: {BRAND}-{CAT}-{COLOR}-{SIZE}
  - Cart ID: CRT-{year}-{random:7}
  - Order ID: ORD-{year}-{random:7}
  - User ID: USR-{random:7}

Generation logic:
1. Parse schema to understand field types
2. For each field, select appropriate Faker method
3. Apply constraints (regenerate if invalid)
4. Handle nested objects recursively
5. Handle arrays with random length within constraints

Scenario handling:
- Distribute records across scenarios based on counts
- Apply scenario overrides to generated data
- Add _scenario and _index metadata fields

Methods:
- generate(): Generate all records at once
- generate_stream(): Yield batches
- supports(): Returns True for simple schemas without coherence needs

Acceptance Criteria:
- [ ] Generates valid data for all 5 entity schemas
- [ ] Respects all constraint types
- [ ] Distributes across scenarios correctly
- [ ] Adds _scenario and _index fields
- [ ] Streaming yields correct batch sizes
- [ ] Integration test generates 100 records
```

---

### Task 2.5: Wire Generator to gRPC Service

```
Update src/test_data_agent/server/grpc_server.py

Implement GenerateData RPC:
1. Log request received
2. Parse request into internal format
3. Get schema (from request or registry)
4. Call TraditionalGenerator.generate()
5. Validate output
6. Build GenerateResponse with:
   - success: true
   - data: JSON string
   - record_count
   - metadata (generation_path="traditional", duration)
7. Handle errors, return success=false with error message

Implement GetSchemas RPC:
1. Call SchemaRegistry.list_schemas(domain)
2. Build GetSchemasResponse

Update dependencies:
- Inject SchemaRegistry and TraditionalGenerator
- Use dependency injection pattern

Acceptance Criteria:
- [ ] GenerateData returns valid JSON data
- [ ] GetSchemas returns all registered schemas
- [ ] Errors are handled gracefully
- [ ] Logging shows request flow
- [ ] Integration test via gRPC client passes
```

---

### Task 2.6: Add Prometheus Metrics

```
Create src/test_data_agent/utils/metrics.py

Define metrics:
- testdata_requests_total: Counter with labels (path, domain, entity, status)
- testdata_generation_duration_seconds: Histogram with labels (path)
- testdata_records_generated: Counter with labels (domain, entity)
- testdata_validation_errors_total: Counter with labels (domain, entity)

Create MetricsCollector class:
- record_request(path, domain, entity, status, duration)
- record_records_generated(domain, entity, count)
- record_validation_error(domain, entity)

Update health.py:
- GET /metrics returns prometheus metrics

Instrument gRPC server:
- Record metrics for each request

Acceptance Criteria:
- [ ] /metrics returns Prometheus format
- [ ] Request counter increments
- [ ] Duration histogram records latency
- [ ] Labels are populated correctly
- [ ] Metrics persist across requests
```

---

### Task 2.7: Write Phase 2 Tests

```
Add tests for Phase 2:

tests/unit/test_schema_registry.py:
- test_get_schema
- test_list_schemas
- test_list_schemas_filtered
- test_invalid_schema

tests/unit/test_constraint_validator.py:
- test_validate_min_max
- test_validate_string_length
- test_validate_enum
- test_validate_regex
- test_validate_nested
- test_validate_array
- test_returns_all_errors

tests/unit/test_traditional_generator.py:
- test_generate_cart
- test_generate_order
- test_generate_payment
- test_generate_user
- test_generate_review
- test_respects_constraints
- test_scenario_distribution
- test_streaming_batches

tests/integration/test_generate_data.py:
- test_generate_via_grpc
- test_generate_with_scenarios
- test_generate_with_constraints
- test_get_schemas

Acceptance Criteria:
- [ ] All unit tests pass
- [ ] Integration tests pass with running server
- [ ] Coverage > 80% for Phase 2 code
```

---

## Phase 3: LLM Integration

### Task 3.1: Implement Claude Client

```
Create src/test_data_agent/clients/claude.py

ClaudeClient class:
- Constructor takes Settings
- Uses anthropic library
- Implements retry logic (3 retries, exponential backoff)
- Handles rate limits gracefully

Methods:
- async generate(system: str, user: str, max_tokens: int) -> ClaudeResponse
- async generate_json(system: str, user: str, max_tokens: int) -> dict

ClaudeResponse:
- content: str
- tokens_used: int (input + output)
- model: str
- stop_reason: str

Error handling:
- AuthenticationError: raise immediately
- RateLimitError: wait and retry
- APIError: retry with backoff
- Timeout: retry with backoff

Also create src/test_data_agent/clients/__init__.py

Acceptance Criteria:
- [ ] Successfully calls Claude API
- [ ] Retries on transient errors
- [ ] Returns token usage
- [ ] Parses JSON responses
- [ ] Unit test with mocked API
```

---

### Task 3.2: Implement vLLM Client (Fallback)

```
Create src/test_data_agent/clients/vllm.py

VLLMClient class:
- Constructor takes Settings
- Uses OpenAI-compatible API (vLLM serves this)
- Same interface as ClaudeClient

Methods:
- async generate(system: str, user: str, max_tokens: int) -> VLLMResponse
- async generate_json(system: str, user: str, max_tokens: int) -> dict

Configuration:
- base_url from settings.vllm_base_url
- model from settings.vllm_model

This is the fallback when:
- Claude is unavailable
- settings.use_local_llm is True
- Cost optimization is needed

Acceptance Criteria:
- [ ] Compatible interface with ClaudeClient
- [ ] Works with vLLM OpenAI-compatible endpoint
- [ ] Can be used as drop-in replacement
- [ ] Unit test with mocked API
```

---

### Task 3.3: Implement Prompt System

```
Create src/test_data_agent/prompts/system.py:
- SYSTEM_PROMPT constant with full system prompt from PRD

Create src/test_data_agent/prompts/templates.py:
- GENERAL_TEMPLATE
- RAG_TEMPLATE
- EDGE_CASE_TEMPLATE
- COHERENT_TEMPLATE
- TEXT_CONTENT_TEMPLATE

Create src/test_data_agent/prompts/builder.py:

PromptBuilder class:
- build_prompt(request, template_type, rag_context=None) -> tuple[str, str]
  - Returns (system_prompt, user_prompt)
- select_template(request) -> str
  - Logic to pick best template based on request
- format_schema(schema) -> str
  - Pretty format schema for prompt
- format_constraints(constraints) -> str
- format_scenarios(scenarios) -> str
- format_rag_examples(examples) -> str

Template selection logic:
- Has defect_triggering → EDGE_CASE_TEMPLATE
- Entity is cart/order and "coherent" in hints → COHERENT_TEMPLATE
- Entity is review/comment → TEXT_CONTENT_TEMPLATE
- Has RAG context → RAG_TEMPLATE
- Default → GENERAL_TEMPLATE

Also create src/test_data_agent/prompts/__init__.py

Acceptance Criteria:
- [ ] All templates defined
- [ ] PromptBuilder formats correctly
- [ ] Template selection logic works
- [ ] Variables are substituted
- [ ] Unit tests for each template
```

---

### Task 3.4: Implement LLM Generator

```
Create src/test_data_agent/generators/llm.py

LLMGenerator extends BaseGenerator:

Constructor:
- Takes ClaudeClient (primary) and VLLMClient (fallback)
- Takes PromptBuilder
- Takes ConstraintValidator

generate() method:
1. Build prompt using PromptBuilder
2. Call LLM (Claude, fallback to vLLM)
3. Parse JSON response
4. Validate against schema
5. If parse/validation fails, retry (max 2 times) with stricter prompt
6. Add metadata fields (_index, _scenario)
7. Return GenerationResult

supports() method:
- Returns True if:
  - context is provided
  - "realistic" or "coherent" in hints
  - Entity has text fields
  - Scenario descriptions are complex

JSON parsing:
- Handle markdown code blocks (```json)
- Handle trailing commas
- Validate is array of objects

Retry prompt modification:
- Add "IMPORTANT: Output ONLY valid JSON array, no other text"
- Include example of expected format

Acceptance Criteria:
- [ ] Generates coherent data via LLM
- [ ] Falls back to vLLM on Claude failure
- [ ] Parses JSON correctly
- [ ] Retries on parse failure
- [ ] Validates output against schema
- [ ] Integration test with mocked LLM
```

---

### Task 3.5: Implement Coherence Scorer

```
Create src/test_data_agent/validators/coherence.py

CoherenceScorer class:
- Scores how "coherent" generated data is
- Used for carts, orders, and related-item entities

Scoring rules for carts:
- Items should be from related categories (0-0.3)
- Quantities should be reasonable (0-0.2)
- Math should be correct: subtotal + tax = total (0-0.3)
- Dates should be chronological (0-0.2)

Methods:
- score(data: dict, schema: dict) -> float (0.0 to 1.0)
- score_cart(cart: dict) -> float
- score_order(order: dict) -> float

Category affinity rules (example):
- Fitness: running shoes, athletic socks, water bottle, fitness tracker
- Beauty: lipstick, mascara, foundation, brushes
- Home: bedding, pillows, blankets, candles

score() returns average of applicable rules.

Acceptance Criteria:
- [ ] Scores coherent cart > 0.8
- [ ] Scores random cart < 0.5
- [ ] Math validation works
- [ ] Date validation works
- [ ] Unit tests with known inputs
```

---

### Task 3.6: Implement Intelligence Router

```
Create src/test_data_agent/router/intelligence_router.py

GenerationPath enum: TRADITIONAL, LLM, RAG, HYBRID

RoutingDecision dataclass:
- path: GenerationPath
- reason: str
- confidence: float

IntelligenceRouter class:

route(request) -> RoutingDecision:

Logic:
1. Check for TRADITIONAL path (fast, cheap):
   - No context provided AND
   - No hints requiring intelligence AND
   - count > 500 (volume) OR
   - "fast" in hints OR
   - Entity is simple (user, no nested)
   
2. Check for RAG path:
   - learn_from_history = true OR
   - defect_triggering = true OR
   - production_like = true OR
   - "similar to" in hints
   
3. Check for LLM path:
   - context provided OR
   - "realistic" or "coherent" in hints OR
   - Entity has text fields OR
   - Entity is cart/order (needs coherence) OR
   - Scenario descriptions provided

4. Check for HYBRID (RAG + LLM):
   - Both RAG and LLM conditions met
   - Complex scenarios with historical patterns

Return decision with reason explaining why.

Also create src/test_data_agent/router/__init__.py

Acceptance Criteria:
- [ ] Routes simple requests to TRADITIONAL
- [ ] Routes context requests to LLM
- [ ] Routes history requests to RAG
- [ ] Routes complex to HYBRID
- [ ] Provides clear reason
- [ ] Unit tests for each path
```

---

### Task 3.7: Update gRPC Service for Multi-Path

```
Update src/test_data_agent/server/grpc_server.py

GenerateData now:
1. Use IntelligenceRouter to determine path
2. Call appropriate generator based on path:
   - TRADITIONAL → TraditionalGenerator
   - LLM → LLMGenerator
   - RAG → (stub for now, return error)
   - HYBRID → (stub for now, return error)
3. Include path in metadata
4. Log routing decision

Add to response metadata:
- generation_path
- llm_tokens_used (if LLM)
- coherence_score (if applicable)

Error handling:
- LLM timeout → fall back to Traditional
- LLM parse failure after retries → return error

Acceptance Criteria:
- [ ] Router selects correct path
- [ ] LLM path generates intelligent data
- [ ] Traditional fallback works
- [ ] Metadata includes path info
- [ ] Integration tests for both paths
```

---

### Task 3.8: Write Phase 3 Tests

```
Add tests for Phase 3:

tests/unit/test_claude_client.py:
- test_generate_success
- test_generate_retry_on_rate_limit
- test_generate_json_parse

tests/unit/test_prompt_builder.py:
- test_select_template_general
- test_select_template_coherent
- test_select_template_edge_case
- test_format_schema
- test_build_prompt

tests/unit/test_llm_generator.py:
- test_generate_with_context
- test_retry_on_parse_failure
- test_fallback_to_vllm

tests/unit/test_coherence_scorer.py:
- test_score_coherent_cart
- test_score_random_cart
- test_math_validation

tests/unit/test_intelligence_router.py:
- test_route_to_traditional
- test_route_to_llm
- test_route_to_rag
- test_route_to_hybrid

tests/integration/test_llm_generation.py:
- test_generate_coherent_cart (with mocked LLM)
- test_generate_realistic_reviews (with mocked LLM)

Acceptance Criteria:
- [ ] All tests pass with mocked external services
- [ ] Coverage > 80% for Phase 3 code
```

---

## Phase 4: RAG Integration

### Task 4.1: Implement Weaviate Client

```
Create src/test_data_agent/clients/weaviate.py

WeaviateClient class:
- Constructor takes Settings
- Uses weaviate-client v4

Methods:
- async connect() -> None
- async disconnect() -> None
- async search(collection: str, query: str, top_k: int) -> list[dict]
- async insert(collection: str, data: dict) -> str
- async batch_insert(collection: str, data: list[dict]) -> list[str]

Collections used:
- testdata_patterns: Successful test data examples
- testdata_defects: Data patterns that caused bugs
- testdata_prod_samples: Anonymized production patterns

Search returns:
- List of dicts with: id, data, score, metadata

Handle:
- Connection errors
- Search timeouts
- Empty results

Acceptance Criteria:
- [ ] Connects to Weaviate
- [ ] Searches with vector similarity
- [ ] Returns ranked results
- [ ] Handles errors gracefully
- [ ] Integration test with Weaviate container
```

---

### Task 4.2: Create RAG Collections Schema

```
Create src/test_data_agent/clients/weaviate_schema.py

Define Weaviate collection schemas:

TestDataPattern:
- domain: text
- entity: text
- scenario: text
- data: text (JSON string)
- quality_score: number
- usage_count: int
- created_at: date

DefectPattern:
- defect_id: text
- domain: text
- entity: text
- trigger_data: text (JSON string)
- defect_description: text
- severity: text (low, medium, high, critical)
- discovered_at: date

ProductionSample:
- domain: text
- entity: text
- anonymized_data: text (JSON string)
- distribution_stats: text (JSON string)
- sample_date: date

Create ensure_collections() function:
- Creates collections if not exist
- Uses text2vec-openai vectorizer

Add to startup:
- Call ensure_collections() on service start

Acceptance Criteria:
- [ ] Collections created on startup
- [ ] Schema matches definition
- [ ] Vectorizer configured correctly
- [ ] Idempotent (can run multiple times)
```

---

### Task 4.3: Implement RAG Generator

```
Create src/test_data_agent/generators/rag.py

RAGGenerator extends BaseGenerator:

generate() method:
1. Build search query from request context
2. Search relevant collection based on request:
   - defect_triggering → testdata_defects
   - production_like → testdata_prod_samples
   - default → testdata_patterns
3. Retrieve top_k examples
4. Return examples as generated data (with modifications)
5. Add metadata fields

supports() method:
- Returns True if:
  - learn_from_history = true
  - defect_triggering = true
  - production_like = true
  - Sufficient data in collections

Query building:
- Use domain + entity + context
- Weight by scenario if provided

Post-processing:
- Update timestamps to current
- Regenerate IDs
- Add _scenario and _index

Acceptance Criteria:
- [ ] Retrieves relevant patterns
- [ ] Returns properly formatted data
- [ ] Handles empty results
- [ ] Updates dynamic fields
- [ ] Integration test with seeded data
```

---

### Task 4.4: Implement Hybrid Generator

```
Create src/test_data_agent/generators/hybrid.py

HybridGenerator extends BaseGenerator:

Combines RAG retrieval with LLM generation:
1. Use RAG to retrieve relevant examples
2. Inject examples into LLM prompt (RAG_TEMPLATE)
3. LLM generates new data informed by examples
4. Validate and return

Constructor:
- Takes RAGGenerator
- Takes LLMGenerator
- Takes PromptBuilder

generate() method:
1. Call RAGGenerator to get examples
2. Format examples for prompt
3. Build prompt with RAG_TEMPLATE
4. Call LLMGenerator with RAG context
5. Return combined result

Metadata includes:
- generation_path: "hybrid"
- rag_examples_used: count
- llm_tokens_used: count

supports() method:
- Returns True if both RAG and LLM conditions met

Acceptance Criteria:
- [ ] Retrieves RAG context
- [ ] Passes context to LLM
- [ ] Generates informed data
- [ ] Metadata is complete
- [ ] Integration test with mocked services
```

---

### Task 4.5: Seed RAG Collections

```
Create src/test_data_agent/scripts/seed_rag.py

Script to seed RAG collections with initial data:

testdata_patterns (20 examples per entity):
- 5 cart examples (different shopping occasions)
- 5 order examples (different statuses)
- 5 payment examples (different methods)
- 5 review examples (different sentiments)

testdata_defects (10 examples):
- Timezone edge case (midnight UTC)
- Unicode in names (emoji, accents)
- Max length strings
- Zero amount payment
- Negative quantity (should be caught)
- SQL injection in text
- Missing required field
- Invalid enum value
- Decimal precision (0.001)
- Date in far future

Data should be realistic and high quality.

Usage:
python -m test_data_agent.scripts.seed_rag

Add to Makefile:
seed-rag: python -m test_data_agent.scripts.seed_rag

Acceptance Criteria:
- [ ] Seeds all collections
- [ ] Data is realistic
- [ ] Defect patterns are valid edge cases
- [ ] Idempotent (doesn't duplicate)
- [ ] Can run via make seed-rag
```

---

### Task 4.6: Complete Intelligence Router

```
Update src/test_data_agent/router/intelligence_router.py

Now with all 4 generators available, update routing:

Add check for RAG availability:
- Query collection counts
- If collection empty, don't route to RAG

Update route() to return all 4 paths correctly.

Add get_generators() method:
- Returns dict of path → generator instance

Update gRPC server:
- Use router.get_generators() 
- Call correct generator based on path
- Handle RAG/HYBRID paths

Acceptance Criteria:
- [ ] All 4 paths work end-to-end
- [ ] RAG falls back if empty
- [ ] Hybrid combines both
- [ ] Integration test for each path
```

---

### Task 4.7: Write Phase 4 Tests

```
Add tests for Phase 4:

tests/unit/test_weaviate_client.py:
- test_search
- test_insert
- test_batch_insert
- test_connection_error

tests/unit/test_rag_generator.py:
- test_generate_from_patterns
- test_generate_from_defects
- test_empty_collection

tests/unit/test_hybrid_generator.py:
- test_generate_with_rag_context
- test_context_injection

tests/integration/test_rag_flow.py:
- test_seed_and_retrieve
- test_full_hybrid_generation

Use testcontainers for Weaviate in integration tests.

Acceptance Criteria:
- [ ] All tests pass
- [ ] Integration tests use real Weaviate
- [ ] Coverage > 80% for Phase 4 code
```

---

## Phase 5: Production Readiness

### Task 5.1: Implement Redis Caching

```
Create src/test_data_agent/clients/redis.py

RedisClient class:
- Constructor takes Settings
- Uses redis.asyncio

Methods:
- async connect() -> None
- async disconnect() -> None
- async get(key: str) -> str | None
- async set(key: str, value: str, ttl: int) -> None
- async delete(key: str) -> None
- async get_from_pool(pool_name: str, count: int) -> list[dict]
- async add_to_pool(pool_name: str, data: list[dict]) -> None

Data pools:
- pool:addresses (pre-generated addresses)
- pool:phones (pre-generated phone numbers)
- pool:names (pre-generated names)
- pool:emails (pre-generated emails)

Pool implementation:
- Store as Redis list
- LPUSH to add, LRANGE to get
- TTL on pool keys

Update TraditionalGenerator:
- Check pool first for common fields
- Fall back to Faker if pool empty
- Optionally replenish pool

Acceptance Criteria:
- [ ] Caching reduces generation time
- [ ] Pools provide instant data
- [ ] TTL expires old data
- [ ] Integration test with Redis
```

---

### Task 5.2: Implement Streaming Generation

```
Update generators and gRPC for streaming:

Update BaseGenerator:
- generate_stream() yields batches

Update TraditionalGenerator.generate_stream():
- Yield batch_size records at a time
- Include chunk metadata

Update LLMGenerator.generate_stream():
- For large requests, make multiple LLM calls
- Each call generates batch_size records
- Yield as received

Update gRPC server:
- Implement GenerateDataStream RPC
- Yield DataChunk messages
- Include chunk_index and is_final

DataChunk:
- request_id
- data (JSON array string for this chunk)
- chunk_index (0, 1, 2, ...)
- is_final (true on last chunk)

Acceptance Criteria:
- [ ] Streaming works for large requests
- [ ] Client receives chunks incrementally
- [ ] Final chunk marked correctly
- [ ] Integration test with streaming client
```

---

### Task 5.3: Implement OpenTelemetry Tracing

```
Create src/test_data_agent/utils/tracing.py

Setup OpenTelemetry:
- Configure OTLP exporter
- Create tracer provider
- Add gRPC instrumentation
- Add HTTP instrumentation

Spans to create:
- generate_data (root span for request)
  - route_request (routing decision)
  - generate_traditional / generate_llm / generate_rag / generate_hybrid
    - llm_call (if LLM)
    - rag_search (if RAG)
  - validate_output
  - build_response

Add attributes:
- request_id
- domain
- entity
- generation_path
- record_count

Update main.py:
- Initialize tracing on startup
- Shutdown tracer on exit

Acceptance Criteria:
- [ ] Traces appear in collector
- [ ] Spans have correct parent-child relationships
- [ ] Attributes are populated
- [ ] Duration is accurate
```

---

### Task 5.4: Create Kubernetes Manifests

```
Create k8s/ directory with:

deployment.yaml:
- Deployment for test-data-agent
- 2 replicas
- Resource limits (500m CPU, 512Mi memory)
- Liveness probe: /health/live
- Readiness probe: /health/ready
- Environment from ConfigMap and Secret

service.yaml:
- ClusterIP service
- Port 9001 for gRPC
- Port 8081 for HTTP

configmap.yaml:
- Non-sensitive configuration
- Log level, ports, URLs

secrets.yaml:
- Template for secrets (API keys)
- Instructions for creating

serviceaccount.yaml:
- ServiceAccount for pod

hpa.yaml:
- HorizontalPodAutoscaler
- Min 2, max 10 replicas
- Target CPU 70%

Acceptance Criteria:
- [ ] kubectl apply -f k8s/ works
- [ ] Pods start and become ready
- [ ] Service routes traffic
- [ ] HPA scales correctly
```

---

### Task 5.5: Performance Testing

```
Create tests/performance/test_load.py

Use locust or custom async client:

Scenarios:
1. Traditional generation (simple)
   - 100 concurrent requests
   - 10 records each
   - Target: p99 < 200ms

2. LLM generation (complex)
   - 10 concurrent requests
   - 5 records each
   - Target: p99 < 5s

3. Streaming (large)
   - 5 concurrent requests
   - 1000 records each
   - Target: first chunk < 1s

4. Mixed workload
   - 80% traditional, 20% LLM
   - 50 concurrent requests
   - Target: p99 < 500ms

Create performance report:
- Latency percentiles (p50, p95, p99)
- Throughput (requests/sec)
- Error rate
- Resource usage

Add to Makefile:
perf-test: run performance tests

Acceptance Criteria:
- [ ] Performance tests run
- [ ] Targets are met
- [ ] Report generated
- [ ] No memory leaks
```

---

### Task 5.6: Documentation

```
Update README.md with:

Sections:
1. Overview
   - What the service does
   - Architecture diagram (text)

2. Quick Start
   - Prerequisites
   - docker-compose up
   - Test with grpcurl

3. Configuration
   - All environment variables
   - Example .env file

4. API Reference
   - gRPC methods
   - Request/response examples

5. Generation Paths
   - When each path is used
   - Examples for each

6. Development
   - Setup instructions
   - Running tests
   - Adding new schemas

7. Deployment
   - Kubernetes deployment
   - Monitoring setup

Create docs/ directory with:
- API.md - detailed API docs
- ARCHITECTURE.md - design decisions
- CONTRIBUTING.md - how to contribute

Acceptance Criteria:
- [ ] README is complete
- [ ] Examples work as documented
- [ ] New developer can onboard
```

---

### Task 5.7: Final Integration Tests

```
Create tests/e2e/test_full_flow.py

End-to-end tests covering:

1. test_traditional_cart_generation
   - Request simple cart
   - Verify Traditional path used
   - Validate output schema

2. test_llm_coherent_cart_generation
   - Request with "coherent" hint
   - Verify LLM path used
   - Check coherence score > 0.8

3. test_rag_defect_pattern_generation
   - Request with defect_triggering=true
   - Verify RAG path used
   - Check edge cases in output

4. test_hybrid_generation
   - Complex request with history
   - Verify Hybrid path used
   - Validate quality

5. test_streaming_large_request
   - Request 500 records
   - Verify streaming works
   - All chunks received

6. test_error_handling
   - Invalid schema
   - LLM timeout (mocked)
   - Verify graceful degradation

7. test_metrics_and_tracing
   - Make requests
   - Verify metrics incremented
   - Verify traces created

Run with: make e2e-test

Acceptance Criteria:
- [ ] All E2E tests pass
- [ ] Tests run in CI
- [ ] Coverage report generated
```

---

### Task 5.8: CI/CD Setup

```
Create .github/workflows/ci.yml:

Triggers:
- Push to main
- Pull requests

Jobs:

1. lint:
   - Run ruff
   - Run mypy
   - Run black --check

2. test:
   - Run unit tests
   - Run integration tests (with testcontainers)
   - Upload coverage report

3. build:
   - Build Docker image
   - Push to registry (on main only)

4. e2e (on main):
   - Deploy to test environment
   - Run E2E tests
   - Cleanup

Create .github/workflows/release.yml:
- Trigger on tag
- Build and push versioned image
- Create GitHub release

Acceptance Criteria:
- [ ] CI runs on every PR
- [ ] Tests must pass to merge
- [ ] Docker image built on main
- [ ] Release workflow works
```

---

## Task Checklist

### Phase 1: Foundation ✅ COMPLETED
- [x] Task 1.1: Initialize Project Structure
- [x] Task 1.2: Implement Configuration Management
- [x] Task 1.3: Implement Structured Logging
- [x] Task 1.4: Create gRPC Proto Definition
- [x] Task 1.5: Implement gRPC Server Skeleton
- [x] Task 1.6: Implement Health HTTP Endpoint
- [x] Task 1.7: Implement Main Entry Point
- [x] Task 1.8: Create Dockerfile and Docker Compose
- [x] Task 1.9: Write Phase 1 Tests

### Phase 2: Traditional Generator ✅ COMPLETED
- [x] Task 2.1: Create Base Generator Interface
- [x] Task 2.2: Implement Schema Registry
- [x] Task 2.3: Implement Constraint Validator
- [x] Task 2.4: Implement Traditional Generator
- [x] Task 2.5: Wire Generator to gRPC Service
- [x] Task 2.6: Add Prometheus Metrics
- [x] Task 2.7: Write Phase 2 Tests

### Phase 3: LLM Integration ✅ COMPLETED
- [x] Task 3.1: Implement Claude Client
- [x] Task 3.2: Implement vLLM Client (Fallback)
- [x] Task 3.3: Implement Prompt System
- [x] Task 3.4: Implement LLM Generator
- [x] Task 3.5: Implement Coherence Scorer
- [x] Task 3.6: Implement Intelligence Router
- [x] Task 3.7: Update gRPC Service for Multi-Path
- [x] Task 3.8: Write Phase 3 Tests

### Phase 4: RAG Integration ✅ COMPLETED
- [x] Task 4.1: Implement Weaviate Client
- [x] Task 4.2: Create RAG Collections Schema
- [x] Task 4.3: Implement RAG Generator
- [x] Task 4.4: Implement Hybrid Generator
- [x] Task 4.5: Seed RAG Collections
- [x] Task 4.6: Complete Intelligence Router
- [x] Task 4.7: Write Phase 4 Tests

### Phase 5: Production Readiness ✅ COMPLETED
- [x] Task 5.1: Implement Redis Caching
- [x] Task 5.2: Implement Streaming Generation
- [x] Task 5.3: Implement OpenTelemetry Tracing
- [x] Task 5.4: Create Kubernetes Manifests
- [x] Task 5.5: Performance Testing
- [x] Task 5.6: Documentation
- [x] Task 5.7: Final Integration Tests
- [x] Task 5.8: CI/CD Setup

---

## Usage Tips

### Starting a Task

Copy the task block into your IDE's AI chat:

```
I'm working on the Test Data Agent project. Here's my current task:

[Paste task block here]

The PRD.md file has the full context. Please implement this task.
```

### Continuing Work

```
Continue from Task 2.3. The previous tasks are complete. 
Here's the current project state: [describe or let AI check files]
```

### Debugging

```
Task 3.4 (LLM Generator) is failing tests. Here's the error:
[paste error]

The implementation is in src/test_data_agent/generators/llm.py
```

### Code Review

```
Review my implementation of Task 2.4 (Traditional Generator).
Check for:
- Compliance with PRD.md specifications
- Edge cases
- Test coverage
```

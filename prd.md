# Test Data Agent - Product Requirements Document

## Overview

The Test Data Agent is a Python microservice that generates intelligent test data for the QA Intelligence Platform. It serves all 7 Domain Agents via gRPC, using an Intelligence Router to select the optimal generation path: Traditional (Faker), LLM (Claude/Local), RAG (Vector DB patterns), or Hybrid (RAG+LLM).

**Repository:** `qa-platform/test-data-agent`
**Language:** Python 3.11+
**Framework:** gRPC + FastAPI (health endpoints)
**Primary Model:** Claude Sonnet 4 (`claude-sonnet-4-20250514`)
**Fallback Model:** Llama 3 8B via vLLM

---

## Project Structure

```
test-data-agent/
├── README.md
├── pyproject.toml
├── Dockerfile
├── docker-compose.yml
├── Makefile
├── .env.example
├── .gitignore
│
├── protos/
│   └── test_data.proto          # gRPC service definition
│
├── src/
│   └── test_data_agent/
│       ├── __init__.py
│       ├── main.py              # Entry point
│       ├── config.py            # Configuration management
│       │
│       ├── server/
│       │   ├── __init__.py
│       │   ├── grpc_server.py   # gRPC service implementation
│       │   └── health.py        # FastAPI health endpoints
│       │
│       ├── router/
│       │   ├── __init__.py
│       │   └── intelligence_router.py  # Routes requests to generators
│       │
│       ├── generators/
│       │   ├── __init__.py
│       │   ├── base.py          # Abstract base generator
│       │   ├── traditional.py   # Faker-based generation
│       │   ├── llm.py           # LLM-based generation
│       │   ├── rag.py           # RAG-based generation
│       │   └── hybrid.py        # RAG + LLM combined
│       │
│       ├── prompts/
│       │   ├── __init__.py
│       │   ├── system.py        # System prompt definitions
│       │   ├── templates.py     # User prompt templates
│       │   └── builder.py       # Dynamic prompt construction
│       │
│       ├── schemas/
│       │   ├── __init__.py
│       │   ├── registry.py      # Schema registry
│       │   └── entities/        # Pre-defined entity schemas
│       │       ├── __init__.py
│       │       ├── cart.py
│       │       ├── order.py
│       │       ├── payment.py
│       │       ├── user.py
│       │       └── review.py
│       │
│       ├── validators/
│       │   ├── __init__.py
│       │   ├── constraint.py    # Constraint validation
│       │   └── coherence.py     # Coherence scoring
│       │
│       ├── clients/
│       │   ├── __init__.py
│       │   ├── claude.py        # Anthropic API client
│       │   ├── vllm.py          # Local LLM client
│       │   ├── weaviate.py      # Vector DB client
│       │   └── redis.py         # Cache client
│       │
│       └── utils/
│           ├── __init__.py
│           ├── logging.py
│           ├── metrics.py       # Prometheus metrics
│           └── tracing.py       # OpenTelemetry
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── unit/
│   │   ├── test_router.py
│   │   ├── test_generators.py
│   │   └── test_validators.py
│   └── integration/
│       ├── test_grpc.py
│       └── test_e2e.py
│
└── k8s/
    ├── deployment.yaml
    ├── service.yaml
    ├── configmap.yaml
    └── secrets.yaml
```

---

## Tech Stack

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| Runtime | Python | 3.11+ | Core language |
| gRPC | grpcio, grpcio-tools | 1.60+ | Service communication |
| HTTP | FastAPI | 0.109+ | Health/metrics endpoints |
| LLM Client | anthropic | 0.40+ | Claude API |
| Local LLM | openai (vLLM compat) | 1.0+ | Llama 3 via vLLM |
| Vector DB | weaviate-client | 4.0+ | RAG retrieval |
| Cache | redis | 5.0+ | Data pool caching |
| Data Gen | faker | 22.0+ | Traditional generation |
| Validation | pydantic | 2.5+ | Schema validation |
| Config | pydantic-settings | 2.0+ | Environment config |
| Logging | structlog | 24.0+ | Structured logging |
| Metrics | prometheus-client | 0.19+ | Prometheus metrics |
| Tracing | opentelemetry-* | 1.22+ | Distributed tracing |
| Testing | pytest, pytest-asyncio | 8.0+ | Test framework |

---

## gRPC Service Definition

```protobuf
// protos/test_data.proto
syntax = "proto3";

package testdata.v1;

option python_package = "test_data_agent.proto";

service TestDataService {
  // Synchronous generation for small requests (<1000 records)
  rpc GenerateData(GenerateRequest) returns (GenerateResponse);
  
  // Streaming for large requests
  rpc GenerateDataStream(GenerateRequest) returns (stream DataChunk);
  
  // List available schemas
  rpc GetSchemas(GetSchemasRequest) returns (GetSchemasResponse);
  
  // Health check
  rpc HealthCheck(HealthCheckRequest) returns (HealthCheckResponse);
}

message GenerateRequest {
  string request_id = 1;                    // Unique ID for tracing
  string domain = 2;                        // ecommerce, supply_chain, loyalty, etc.
  string entity = 3;                        // cart, order, payment, user, review
  Schema schema = 4;                        // Field definitions (or use pre-defined)
  Constraints constraints = 5;              // Validation rules
  repeated Scenario scenarios = 6;          // Generation scenarios
  string context = 7;                       // Natural language context for LLM
  repeated string hints = 8;                // Routing hints: realistic, edge_case, defect_triggering
  OutputFormat output_format = 9;           // JSON, CSV, SQL
  int32 count = 10;                         // Total records to generate
  bool use_cache = 11;                      // Use cached data pools
  bool learn_from_history = 12;             // Use RAG patterns
  bool defect_triggering = 13;              // Generate bug-finding data
  bool production_like = 14;                // Mimic production distributions
}

message Schema {
  repeated Field fields = 1;
  string predefined_schema = 2;             // Use pre-defined: "cart", "order", etc.
}

message Field {
  string name = 1;
  FieldType type = 2;
  bool required = 3;
  string description = 4;                   // For LLM context
  repeated Field nested_fields = 5;         // For object/array types
}

enum FieldType {
  STRING = 0;
  INTEGER = 1;
  FLOAT = 2;
  BOOLEAN = 3;
  DATE = 4;
  DATETIME = 5;
  EMAIL = 6;
  PHONE = 7;
  ADDRESS = 8;
  UUID = 9;
  ENUM = 10;
  OBJECT = 11;
  ARRAY = 12;
}

message Constraints {
  map<string, FieldConstraint> field_constraints = 1;
}

message FieldConstraint {
  optional double min = 1;
  optional double max = 2;
  repeated string enum_values = 3;
  optional string regex = 4;
  optional int32 min_length = 5;
  optional int32 max_length = 6;
  optional string format = 7;               // date format, etc.
}

message Scenario {
  string name = 1;                          // happy_path, expired_token, etc.
  int32 count = 2;                          // Records for this scenario
  map<string, string> overrides = 3;        // Field value overrides
  string description = 4;                   // For LLM context
}

enum OutputFormat {
  JSON = 0;
  CSV = 1;
  SQL = 2;
}

message GenerateResponse {
  string request_id = 1;
  bool success = 2;
  string data = 3;                          // JSON string of generated data
  int32 record_count = 4;
  GenerationMetadata metadata = 5;
  string error = 6;
}

message GenerationMetadata {
  string generation_path = 1;               // traditional, llm, rag, hybrid
  int32 llm_tokens_used = 2;
  float generation_time_ms = 3;
  float coherence_score = 4;
  map<string, int32> scenario_counts = 5;
}

message DataChunk {
  string request_id = 1;
  string data = 2;                          // Partial JSON array
  int32 chunk_index = 3;
  bool is_final = 4;
}

message GetSchemasRequest {
  string domain = 1;                        // Filter by domain (optional)
}

message GetSchemasResponse {
  repeated SchemaInfo schemas = 1;
}

message SchemaInfo {
  string name = 1;
  string domain = 2;
  string description = 3;
  repeated string fields = 4;
}

message HealthCheckRequest {}

message HealthCheckResponse {
  string status = 1;                        // healthy, degraded, unhealthy
  map<string, string> components = 2;       // Component health status
}
```

---

## Configuration

```python
# src/test_data_agent/config.py
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    # Service
    service_name: str = "test-data-agent"
    grpc_port: int = 9001
    http_port: int = 8081
    log_level: str = "INFO"
    
    # LLM - Claude
    anthropic_api_key: str = Field(..., env="ANTHROPIC_API_KEY")
    claude_model: str = "claude-sonnet-4-20250514"
    claude_max_tokens: int = 4096
    claude_temperature: float = 0.7
    
    # LLM - Local (vLLM)
    vllm_base_url: str = "http://vllm:8000/v1"
    vllm_model: str = "meta-llama/Meta-Llama-3-8B-Instruct"
    use_local_llm: bool = False  # Fallback or primary
    
    # RAG - Weaviate
    weaviate_url: str = "http://weaviate:8080"
    weaviate_api_key: str | None = None
    rag_collection_patterns: str = "testdata_patterns"
    rag_collection_defects: str = "testdata_defects"
    rag_collection_prod: str = "testdata_prod_samples"
    rag_top_k: int = 5
    
    # Cache - Redis
    redis_url: str = "redis://redis:6379/0"
    cache_ttl_seconds: int = 86400  # 24 hours
    
    # Generation
    max_sync_records: int = 1000
    default_batch_size: int = 50
    coherence_threshold: float = 0.85
    
    # Observability
    prometheus_enabled: bool = True
    tracing_enabled: bool = True
    otlp_endpoint: str = "http://otel-collector:4317"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
```

---

## Core Components

### 1. Intelligence Router

The router analyzes each request and selects the optimal generation path.

```python
# src/test_data_agent/router/intelligence_router.py

from enum import Enum
from dataclasses import dataclass

class GenerationPath(Enum):
    TRADITIONAL = "traditional"
    LLM = "llm"
    RAG = "rag"
    HYBRID = "hybrid"  # RAG + LLM

@dataclass
class RoutingDecision:
    path: GenerationPath
    reason: str
    confidence: float

class IntelligenceRouter:
    """
    Routes generation requests to the optimal path based on:
    - Request complexity
    - Field types (text fields need LLM)
    - Coherence requirements
    - Historical pattern needs
    - Performance requirements
    """
    
    def route(self, request: GenerateRequest) -> RoutingDecision:
        """
        Decision logic:
        
        1. TRADITIONAL (fastest, cheapest):
           - Simple field types (email, phone, uuid)
           - No context provided
           - High volume (>500 records)
           - No coherence requirement
           - "fast" in hints
        
        2. LLM (intelligent):
           - Has text fields (description, review, comment)
           - Context provided
           - "realistic" or "coherent" in hints
           - Entity is cart/order (needs item coherence)
           - Scenario descriptions provided
        
        3. RAG (pattern-based):
           - learn_from_history = true
           - defect_triggering = true
           - production_like = true
           - "similar to" in hints
        
        4. HYBRID (best quality):
           - Needs both RAG context AND LLM generation
           - Complex scenarios with historical patterns
           - defect_triggering + realistic text
        """
        pass
```

### 2. Generators

Each generator implements a common interface:

```python
# src/test_data_agent/generators/base.py

from abc import ABC, abstractmethod
from typing import AsyncIterator

class BaseGenerator(ABC):
    """Abstract base for all generators."""
    
    @abstractmethod
    async def generate(
        self,
        request: GenerateRequest,
        context: dict | None = None  # RAG context for hybrid
    ) -> list[dict]:
        """Generate records based on request."""
        pass
    
    @abstractmethod
    async def generate_stream(
        self,
        request: GenerateRequest,
        context: dict | None = None
    ) -> AsyncIterator[list[dict]]:
        """Stream records in batches."""
        pass
```

**Traditional Generator:**
- Uses Faker for standard fields
- Custom generators for domain-specific formats
- Rule-based constraint enforcement
- Fastest path, no external API calls

**LLM Generator:**
- Constructs prompt from system + user template
- Calls Claude API (or vLLM fallback)
- Parses JSON response
- Validates against schema
- Retries on parse failures (max 2)

**RAG Generator:**
- Queries Weaviate for similar patterns
- Returns retrieved examples directly
- Used for "production-like" requests

**Hybrid Generator:**
- First retrieves RAG context
- Injects context into LLM prompt
- Best quality, highest cost

### 3. Prompt System

```python
# src/test_data_agent/prompts/system.py

SYSTEM_PROMPT = """You are a Test Data Generation Agent for Macy's retail systems.

YOUR ROLE:
Generate realistic, coherent test data that accurately simulates real-world retail scenarios. Your data will be used for automated testing of eCommerce, supply chain, loyalty, mobile, marketing, store operations, and enterprise systems.

CORE PRINCIPLES:
1. COHERENCE: Related fields must make sense together. A shopping cart should contain items a real customer would buy together (running shoes + athletic socks), not random products.
2. REALISM: Names, addresses, emails, and text should look authentic. Use realistic patterns, not 'test123' or 'John Doe'.
3. VALIDITY: All generated data must conform to the provided schema and constraints. Respect min/max, enum values, regex patterns, and data types.
4. DIVERSITY: Generate varied data within constraints. Don't repeat the same patterns across records.
5. EDGE CASES: When requested, include boundary values, special characters, and scenarios known to cause issues.

OUTPUT RULES:
- Always respond with valid JSON only. No markdown, no explanations, no preamble.
- Output must be a JSON array of objects matching the schema.
- Include a '_scenario' field in each record indicating which scenario it belongs to.
- Include a '_index' field with sequential numbering starting from 0.

DOMAIN KNOWLEDGE:
- Macy's sells apparel, accessories, home goods, beauty products, and jewelry
- Payment methods: Credit cards, PayPal, ApplePay, Google Pay, Macy's card, gift cards
- Loyalty program: Star Rewards with Bronze, Silver, Gold, Platinum tiers
- Shipping: Standard (5-7 days), Express (2-3 days), Same Day (select markets)
- Store pickup: BOPIS (Buy Online Pick up In Store)"""
```

```python
# src/test_data_agent/prompts/templates.py

# Template for general data generation
GENERAL_TEMPLATE = """Generate {count} test data records for the {domain} domain.

CONTEXT:
{context}

SCHEMA:
{schema}

CONSTRAINTS:
{constraints}

SCENARIOS:
{scenarios}

Generate exactly {count} records distributed across the scenarios as specified. Output valid JSON array only."""

# Template with RAG examples
RAG_TEMPLATE = """Generate {count} test data records for the {domain} domain.

CONTEXT:
{context}

REFERENCE EXAMPLES (from similar successful test data):
Study these examples to understand the expected patterns and quality:
{rag_examples}

SCHEMA:
{schema}

CONSTRAINTS:
{constraints}

Generate data that matches the quality and patterns shown in the examples while conforming to the schema. Output valid JSON array only."""

# Template for edge cases
EDGE_CASE_TEMPLATE = """Generate {count} EDGE CASE test data records designed to stress-test the system.

CONTEXT:
{context}

HISTORICAL DEFECT PATTERNS (from past bugs):
These data patterns have caused bugs before. Generate similar data to catch regressions:
{defect_patterns}

EDGE CASES TO INCLUDE:
- Boundary values (min, max, just above/below limits)
- Special characters (unicode, emojis, SQL injection patterns)
- Empty/null values where allowed
- Timezone edge cases (midnight, DST boundaries)
- Very long strings at max length
- Decimal precision edge cases

SCHEMA:
{schema}

Each record should target a specific edge case. Include '_edge_case_type' field describing what edge case it tests. Output valid JSON array only."""

# Template for coherent entities (carts, orders)
COHERENT_TEMPLATE = """Generate a COHERENT {entity_type} with logically related items.

CONTEXT:
{context}

COHERENCE REQUIREMENTS:
- Items must logically belong together (what a real customer would buy)
- Consider: shopping occasion, category affinity, complementary products
- Amounts must be mathematically consistent (subtotal + tax = total)
- Dates must be chronologically valid (created < modified < completed)

COHERENT SET EXAMPLES:
- Fitness: Running shoes + Athletic socks + Water bottle + Fitness tracker
- Date night: Dress + Heels + Clutch + Jewelry
- Home refresh: Bedding set + Pillows + Throw blanket + Candles
- Baby shower gift: Onesies + Blanket + Stuffed animal + Card

SCHEMA:
{schema}

Include '_shopping_occasion' field describing the coherent theme. Output valid JSON only."""

# Template for text content (reviews, comments)
TEXT_CONTENT_TEMPLATE = """Generate {count} realistic {content_type} entries.

CONTEXT:
{context}

TEXT QUALITY REQUIREMENTS:
- Write like a real customer, not a marketer or AI
- Include natural imperfections (casual grammar, abbreviations)
- Vary length and detail level across entries
- Reference specific product attributes when relevant
- Include emotional language where appropriate

SENTIMENT DISTRIBUTION:
{sentiment_distribution}

SCHEMA:
{schema}

Include '_sentiment' field (positive/negative/neutral). Output valid JSON array only."""
```

### 4. Schema Registry

Pre-defined schemas for common entities:

```python
# src/test_data_agent/schemas/entities/cart.py

CART_SCHEMA = {
    "name": "cart",
    "domain": "ecommerce",
    "description": "Shopping cart with items",
    "fields": {
        "cart_id": {"type": "string", "format": "CRT-{year}-{random:7}", "required": True},
        "customer_id": {"type": "string", "format": "USR-{random:7}", "required": True},
        "items": {
            "type": "array",
            "required": True,
            "items": {
                "type": "object",
                "fields": {
                    "sku": {"type": "string", "required": True},
                    "name": {"type": "string", "required": True},
                    "quantity": {"type": "integer", "min": 1, "max": 99, "required": True},
                    "price": {"type": "float", "min": 0.01, "required": True},
                    "category": {"type": "string", "required": False}
                }
            }
        },
        "subtotal": {"type": "float", "min": 0, "required": True},
        "tax": {"type": "float", "min": 0, "required": True},
        "total": {"type": "float", "min": 0, "required": True},
        "currency": {"type": "enum", "values": ["USD", "CAD"], "default": "USD"},
        "created_at": {"type": "datetime", "format": "iso8601", "required": True},
        "updated_at": {"type": "datetime", "format": "iso8601", "required": False}
    },
    "coherence_rules": [
        "total = subtotal + tax",
        "subtotal = sum(items.quantity * items.price)",
        "items should be thematically related"
    ]
}
```

---

## RAG Collections

### Weaviate Schema

```python
# Collection: testdata_patterns
{
    "class": "TestDataPattern",
    "vectorizer": "text2vec-openai",
    "properties": [
        {"name": "domain", "dataType": ["text"]},
        {"name": "entity", "dataType": ["text"]},
        {"name": "scenario", "dataType": ["text"]},
        {"name": "data", "dataType": ["text"]},  # JSON string
        {"name": "quality_score", "dataType": ["number"]},
        {"name": "usage_count", "dataType": ["int"]},
        {"name": "created_at", "dataType": ["date"]}
    ]
}

# Collection: testdata_defects
{
    "class": "DefectPattern",
    "vectorizer": "text2vec-openai",
    "properties": [
        {"name": "defect_id", "dataType": ["text"]},
        {"name": "domain", "dataType": ["text"]},
        {"name": "entity", "dataType": ["text"]},
        {"name": "trigger_data", "dataType": ["text"]},  # JSON string
        {"name": "defect_description", "dataType": ["text"]},
        {"name": "severity", "dataType": ["text"]},
        {"name": "discovered_at", "dataType": ["date"]}
    ]
}

# Collection: testdata_prod_samples  
{
    "class": "ProductionSample",
    "vectorizer": "text2vec-openai",
    "properties": [
        {"name": "domain", "dataType": ["text"]},
        {"name": "entity", "dataType": ["text"]},
        {"name": "anonymized_data", "dataType": ["text"]},  # JSON string
        {"name": "distribution_stats", "dataType": ["text"]},  # JSON string
        {"name": "sample_date", "dataType": ["date"]}
    ]
}
```

---

## API Examples

### Generate Coherent Cart

**Request:**
```json
{
  "request_id": "req-001",
  "domain": "ecommerce",
  "entity": "cart",
  "context": "Generate shopping carts for ApplePay checkout testing. Carts should have 3-5 items that a real customer would buy together.",
  "hints": ["realistic", "coherent"],
  "count": 10,
  "scenarios": [
    {"name": "happy_path", "count": 7, "description": "Normal checkout flow"},
    {"name": "high_value", "count": 2, "description": "Cart total > $500"},
    {"name": "single_item", "count": 1, "description": "Cart with only one item"}
  ],
  "output_format": "JSON"
}
```

**Response:**
```json
{
  "request_id": "req-001",
  "success": true,
  "data": "[{\"_index\": 0, \"_scenario\": \"happy_path\", \"_shopping_occasion\": \"marathon_training\", ...}]",
  "record_count": 10,
  "metadata": {
    "generation_path": "llm",
    "llm_tokens_used": 2847,
    "generation_time_ms": 3241.5,
    "coherence_score": 0.94,
    "scenario_counts": {"happy_path": 7, "high_value": 2, "single_item": 1}
  }
}
```

### Generate Edge Case Data

**Request:**
```json
{
  "request_id": "req-002",
  "domain": "ecommerce",
  "entity": "payment",
  "context": "Generate payment records that test edge cases in payment processing",
  "hints": ["edge_case"],
  "defect_triggering": true,
  "count": 20,
  "output_format": "JSON"
}
```

---

## Implementation Phases

### Phase 1: Foundation (Week 1-2)

**Tasks:**
1. Initialize Python project with pyproject.toml
2. Set up project structure as defined above
3. Implement config.py with pydantic-settings
4. Create proto file and generate Python code
5. Implement basic gRPC server (health check only)
6. Set up logging with structlog
7. Add Dockerfile and docker-compose.yml
8. Write unit tests for config loading

**Deliverable:** Running gRPC server with health check endpoint

### Phase 2: Traditional Generator (Week 2-3)

**Tasks:**
1. Implement BaseGenerator abstract class
2. Implement TraditionalGenerator with Faker
3. Create schema registry with 5 entities (cart, order, payment, user, review)
4. Implement constraint validation
5. Implement GenerateData RPC (traditional path only)
6. Add Prometheus metrics
7. Write unit tests for generator and validator

**Deliverable:** Working data generation via gRPC (Faker-based)

### Phase 3: LLM Integration (Week 3-4)

**Tasks:**
1. Implement Claude client with retry logic
2. Implement vLLM client as fallback
3. Create prompt system (system prompt, templates, builder)
4. Implement LLMGenerator
5. Add JSON parsing with validation
6. Implement coherence scoring
7. Update Intelligence Router (Traditional vs LLM)
8. Write integration tests with mocked LLM

**Deliverable:** LLM-powered generation for complex requests

### Phase 4: RAG Integration (Week 4-5)

**Tasks:**
1. Implement Weaviate client
2. Create RAG collections (patterns, defects, prod_samples)
3. Implement RAGGenerator
4. Implement HybridGenerator (RAG + LLM)
5. Complete Intelligence Router with all 4 paths
6. Add seed data for RAG collections
7. Write integration tests with Weaviate testcontainer

**Deliverable:** Full multi-path architecture

### Phase 5: Optimization & Production (Week 5-6)

**Tasks:**
1. Implement Redis caching for data pools
2. Add streaming support (GenerateDataStream)
3. Implement request batching for large requests
4. Add OpenTelemetry tracing
5. Create Kubernetes manifests
6. Performance testing and optimization
7. Documentation (README, API docs)
8. End-to-end integration tests

**Deliverable:** Production-ready service

---

## Testing Strategy

### Unit Tests
- Config loading
- Intelligence Router decision logic
- Each generator in isolation (mock external services)
- Constraint validation
- Prompt building
- JSON parsing

### Integration Tests
- gRPC server with test client
- LLM generator with mocked API responses
- RAG retrieval with Weaviate testcontainer
- Redis caching

### E2E Tests
- Full flow: request → router → generator → response
- All generation paths
- Streaming responses
- Error handling

### Performance Tests
- Latency per generation path
- Throughput under load
- Memory usage with large batches

---

## Observability

### Metrics (Prometheus)
- `testdata_requests_total{path, domain, status}`
- `testdata_generation_duration_seconds{path}`
- `testdata_llm_tokens_used{model}`
- `testdata_records_generated{domain, entity}`
- `testdata_cache_hits_total`
- `testdata_coherence_score{domain}`

### Logs (Structured)
- Request received (request_id, domain, entity, count)
- Routing decision (path, reason, confidence)
- Generation complete (duration, record_count)
- Errors with full context

### Traces (OpenTelemetry)
- Span per request
- Child spans for: routing, generation, validation
- LLM call duration
- RAG retrieval duration

---

## Error Handling

| Error | Code | Handling |
|-------|------|----------|
| Invalid schema | INVALID_ARGUMENT | Return validation errors |
| LLM timeout | DEADLINE_EXCEEDED | Fallback to local LLM, then traditional |
| LLM parse failure | INTERNAL | Retry up to 2 times with stricter prompt |
| RAG unavailable | UNAVAILABLE | Skip RAG, use LLM or traditional |
| Redis unavailable | UNAVAILABLE | Generate without cache |
| Count too high | INVALID_ARGUMENT | Return error, suggest streaming |

---

## Security

- No PII in generated data (synthetic only)
- API key stored in Kubernetes secrets
- gRPC TLS in production
- Rate limiting per client
- Request size limits (max 10K records)

---

## Dependencies

```toml
# pyproject.toml
[project]
name = "test-data-agent"
version = "0.1.0"
requires-python = ">=3.11"

dependencies = [
    "grpcio>=1.60.0",
    "grpcio-tools>=1.60.0",
    "fastapi>=0.109.0",
    "uvicorn>=0.27.0",
    "anthropic>=0.40.0",
    "openai>=1.0.0",
    "weaviate-client>=4.0.0",
    "redis>=5.0.0",
    "faker>=22.0.0",
    "pydantic>=2.5.0",
    "pydantic-settings>=2.0.0",
    "structlog>=24.0.0",
    "prometheus-client>=0.19.0",
    "opentelemetry-api>=1.22.0",
    "opentelemetry-sdk>=1.22.0",
    "opentelemetry-exporter-otlp>=1.22.0",
    "opentelemetry-instrumentation-grpc>=0.43b0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.23.0",
    "pytest-cov>=4.1.0",
    "testcontainers>=3.7.0",
    "black>=24.0.0",
    "ruff>=0.1.0",
    "mypy>=1.8.0",
]
```

---

## Next Steps

After creating the PRD, the implementation should proceed by:

1. **Create repository** with the defined structure
2. **Phase 1** tasks → get basic server running
3. **Phase 2** tasks → traditional generation working
4. **Phase 3** tasks → LLM integration
5. **Phase 4** tasks → RAG integration  
6. **Phase 5** tasks → production hardening

Each phase should have its own PR with tests passing before merge.

# Test Data Agent

**Intelligent test data generation microservice for the QA Intelligence Platform**

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-68%20passing-brightgreen.svg)]()
[![Coverage](https://img.shields.io/badge/coverage-41%25-yellow.svg)]()
[![Production Ready](https://img.shields.io/badge/status-production%20ready-success.svg)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## Overview

The Test Data Agent is a high-performance Python-based gRPC microservice that generates intelligent, context-aware test data using multiple AI-powered strategies. It combines traditional random generation, large language models (LLMs), retrieval-augmented generation (RAG), and hybrid approaches to produce realistic, coherent test data for QA automation.

### Key Features

- **4 Generation Paths**: Automatically routes to the optimal generation strategy
- **Intelligent Routing**: Context-aware selection based on request characteristics
- **Coherence Scoring**: Validates logical consistency of generated data
- **Pattern Learning**: Learns from historical data and defect patterns
- **High Performance**: From <5ms (Traditional) to ~20s (LLM) generation times
- **Redis Caching**: Data pools for instant access to common fields
- **Streaming Support**: Generate large datasets (500+) with chunked responses
- **Production Ready**: Kubernetes, auto-scaling, health checks, metrics, tracing, CI/CD

---

## Generation Strategies

| Strategy | Speed | Coherence | Use Case | When Used |
|----------|-------|-----------|----------|-----------|
| **Traditional** | <5ms | Low (0.2-0.4) | Bulk data, stress testing | High volume, no context needed |
| **LLM** | ~20s | High (0.7-0.9) | Realistic scenarios, demos | Context provided, coherence hints |
| **RAG** | ~20ms | Perfect (1.0) | Pattern reuse, compliance | `learn_from_history=true` |
| **Hybrid** | ~21s | Strong (0.7-0.8) | Best of both worlds | History + coherence needed |

---

## Quick Start

### Prerequisites

- **Python 3.11+**
- **Docker & Docker Compose**
- **Anthropic API Key** (for Claude LLM integration)
- **grpcurl** (for testing): `brew install grpcurl` (macOS) or [install guide](https://github.com/fullstorydev/grpcurl)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd test-data-agent
   ```

2. **Create environment configuration**
   ```bash
   cp .env.example .env
   ```

3. **Configure your API key** (edit `.env`):
   ```bash
   ANTHROPIC_API_KEY=sk-ant-your-api-key-here
   WEAVIATE_URL=http://localhost:8080
   ```

4. **Install dependencies**
   ```bash
   pip install -e .
   # or
   make install
   ```

5. **Generate proto files**
   ```bash
   make proto
   ```

### Running Locally

**Option 1: Run service directly**
```bash
python -m test_data_agent.main
```

**Option 2: Use Make**
```bash
make run
```

**Option 3: Docker Compose (with Weaviate & Redis)**
```bash
docker-compose up -d
```

### Verify Service is Running

```bash
# HTTP health check
curl http://localhost:8091/health

# gRPC health check
grpcurl -plaintext localhost:9091 testdata.v1.TestDataService/HealthCheck
```

**Expected output:**
```json
{
  "status": "healthy",
  "service": "test-data-agent",
  "version": "0.1.0"
}
```

---

## Usage Examples

### 1. Traditional Generation (Fast, Random)

**Use Case:** Bulk data generation, load testing, when coherence doesn't matter

```bash
grpcurl -plaintext -d '{
  "domain": "ecommerce",
  "entity": "cart",
  "count": 100
}' localhost:9091 testdata.v1.TestDataService/GenerateData
```

**Response:**
```json
{
  "success": true,
  "record_count": 100,
  "metadata": {
    "generation_path": "traditional",
    "generation_time_ms": 45.2,
    "coherence_score": 0.28
  }
}
```

---

### 2. LLM Generation (Intelligent, Realistic)

**Use Case:** Demo data, realistic scenarios, context-aware generation

```bash
grpcurl -plaintext -d '{
  "domain": "ecommerce",
  "entity": "cart",
  "count": 3,
  "hints": ["coherent", "realistic"],
  "context": "Generate shopping carts for fitness enthusiasts buying related workout gear"
}' localhost:9091 testdata.v1.TestDataService/GenerateData
```

**Response:**
```json
{
  "success": true,
  "data": "[{\"cart_id\": \"CRT-2024-A7K9M2P\", \"items\": [{\"name\": \"Nike Air Zoom Pegasus 40\", \"price\": 129.99}, {\"name\": \"Nike Dri-FIT Socks 3-Pack\", \"price\": 24.99}], \"total\": 154.98}]",
  "record_count": 3,
  "metadata": {
    "generation_path": "llm",
    "llm_tokens_used": 1247,
    "generation_time_ms": 18456.3,
    "coherence_score": 0.85
  }
}
```

**Notice:** Related items (running shoes + socks), high coherence score (0.85)

---

### 3. RAG Generation (Pattern-Based)

**Use Case:** Reproduce defects, compliance testing, production-like data

**First, seed RAG collections:**
```bash
# Start Weaviate
docker-compose up -d weaviate

# Seed patterns
WEAVIATE_URL=http://localhost:8080 python -m test_data_agent.scripts.seed_rag
```

**Generate from patterns:**
```bash
grpcurl -plaintext -d '{
  "domain": "ecommerce",
  "entity": "cart",
  "count": 5,
  "learn_from_history": true
}' localhost:9091 testdata.v1.TestDataService/GenerateData
```

**Response:**
```json
{
  "success": true,
  "record_count": 5,
  "metadata": {
    "generation_path": "rag",
    "generation_time_ms": 23.7,
    "coherence_score": 1.0
  }
}
```

**Notice:** Perfect coherence (1.0), very fast (23ms), matches historical patterns

---

### 4. Hybrid Generation (RAG + LLM)

**Use Case:** Best quality - combines historical patterns with creative variations

```bash
grpcurl -plaintext -d '{
  "domain": "ecommerce",
  "entity": "cart",
  "count": 3,
  "learn_from_history": true,
  "hints": ["coherent", "realistic"],
  "context": "Generate tech enthusiast shopping carts inspired by past successful patterns"
}' localhost:9091 testdata.v1.TestDataService/GenerateData
```

**Response:**
```json
{
  "success": true,
  "record_count": 3,
  "metadata": {
    "generation_path": "hybrid",
    "llm_tokens_used": 1523,
    "generation_time_ms": 21234.5,
    "coherence_score": 0.78
  }
}
```

**Notice:** Combines historical accuracy with creative LLM variations

---

### 5. Defect Pattern Generation (Edge Cases)

**Use Case:** Reproduce bugs, boundary testing, security testing

```bash
grpcurl -plaintext -d '{
  "domain": "ecommerce",
  "entity": "order",
  "count": 5,
  "defect_triggering": true
}' localhost:9091 testdata.v1.TestDataService/GenerateData
```

**Expected:** Data with edge cases like unicode characters, special chars, boundary values

---

### 6. Product Reviews (Text Generation)

```bash
grpcurl -plaintext -d '{
  "domain": "ecommerce",
  "entity": "review",
  "count": 5,
  "hints": ["realistic", "varied sentiment"],
  "context": "Generate product reviews for wireless headphones with mixed opinions"
}' localhost:9091 testdata.v1.TestDataService/GenerateData
```

**Expected:** Natural language reviews with ratings from 1-5, realistic feedback

---

## API Reference

### Available Entities

The service supports 6 predefined entity schemas:

| Entity | Domain | Fields | Description |
|--------|--------|--------|-------------|
| `cart` | ecommerce | cart_id, customer_id, items[], subtotal, tax, total | Shopping cart with line items |
| `order` | ecommerce | order_id, customer_id, items[], shipping_address, payment, status | Complete order |
| `payment` | ecommerce | payment_id, order_id, method, amount, status, card_last_four | Payment transaction |
| `product` | ecommerce | product_id, name, description, price, category, sku, stock | Product catalog item |
| `review` | ecommerce | review_id, product_id, user_id, rating, title, body, verified_purchase | Product review |
| `user` | ecommerce | user_id, email, name, phone, addresses[], loyalty_tier | Customer profile |

### List Available Schemas

```bash
grpcurl -plaintext -d '{}' localhost:9091 testdata.v1.TestDataService/GetSchemas
```

---

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ANTHROPIC_API_KEY` | *required* | Anthropic API key for Claude |
| `CLAUDE_MODEL` | `claude-sonnet-4-20250514` | Claude model to use |
| `CLAUDE_MAX_TOKENS` | `4096` | Max tokens per LLM request |
| `CLAUDE_TEMPERATURE` | `0.7` | LLM temperature (0.0-1.0) |
| `WEAVIATE_URL` | `http://weaviate:8080` | Weaviate vector DB URL |
| `REDIS_URL` | `redis://redis:6379/0` | Redis cache URL (Phase 5) |
| `GRPC_PORT` | `9091` | gRPC server port |
| `HTTP_PORT` | `8091` | HTTP health/metrics port |
| `LOG_LEVEL` | `INFO` | Logging level |
| `ENVIRONMENT` | `development` | Environment name |
| `MAX_SYNC_RECORDS` | `1000` | Max records for sync generation |
| `COHERENCE_THRESHOLD` | `0.85` | Minimum coherence score |

### Full Configuration Reference

See [.env.example](.env.example) for all available configuration options.

---

## Routing Logic

The Intelligence Router automatically selects the optimal generation path:

### Traditional Path

**Selected when:**
- No context provided
- No hints requiring intelligence
- High volume (count > 500)
- "fast" in hints

**Example:**
```bash
grpcurl -plaintext -d '{"entity": "user", "count": 1000}' \
  localhost:9091 testdata.v1.TestDataService/GenerateData
# → Routes to Traditional
```

### LLM Path

**Selected when:**
- Context provided
- "coherent" or "realistic" in hints
- Entity has text fields (review, comment)
- Entity requires coherence (cart, order)

**Example:**
```bash
grpcurl -plaintext -d '{"entity": "cart", "hints": ["coherent"]}' \
  localhost:9091 testdata.v1.TestDataService/GenerateData
# → Routes to LLM
```

### RAG Path

**Selected when:**
- `learn_from_history=true`
- `defect_triggering=true`
- `production_like=true`
- "similar to" in hints

**Example:**
```bash
grpcurl -plaintext -d '{"entity": "cart", "learn_from_history": true}' \
  localhost:9091 testdata.v1.TestDataService/GenerateData
# → Routes to RAG
```

### Hybrid Path

**Selected when:**
- Both RAG and LLM conditions met
- `learn_from_history=true` AND hints include "coherent"

**Example:**
```bash
grpcurl -plaintext -d '{"entity": "cart", "learn_from_history": true, "hints": ["coherent"]}' \
  localhost:9091 testdata.v1.TestDataService/GenerateData
# → Routes to Hybrid
```

---

## Development

### Running Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=src/test_data_agent --cov-report=html

# Specific test file
pytest tests/unit/test_intelligence_router.py -v

# Watch mode (requires pytest-watch)
ptw
```

**Current Status:** 68/68 tests passing ✅ (41% coverage, >80% on critical paths)

### Code Quality

```bash
# Format code
make format
# or
black src tests

# Lint
make lint
# or
ruff check src tests
mypy src

# Type checking
mypy src/test_data_agent
```

### Project Structure

```
test-data-agent/
├── src/test_data_agent/
│   ├── clients/          # External service clients (Claude, vLLM, Weaviate)
│   ├── generators/       # Data generation strategies
│   ├── prompts/          # LLM prompt templates
│   ├── proto/            # Generated gRPC code
│   ├── router/           # Intelligence routing logic
│   ├── schemas/          # Entity schema definitions
│   ├── scripts/          # Utility scripts (seed_rag.py)
│   ├── server/           # gRPC and HTTP servers
│   ├── utils/            # Logging, metrics, helpers
│   ├── validators/       # Constraint and coherence validation
│   ├── config.py         # Configuration management
│   └── main.py           # Application entry point
├── tests/
│   ├── unit/             # Unit tests
│   ├── integration/      # Integration tests
│   └── conftest.py       # Pytest fixtures
├── protos/               # Proto definitions
├── docker-compose.yml    # Docker services
├── Dockerfile            # Container image
├── Makefile              # Common tasks
└── pyproject.toml        # Python dependencies
```

---

## Deployment

### Docker Compose (Development)

```bash
# Start all services (agent + weaviate + redis)
docker-compose up -d

# View logs
docker-compose logs -f test-data-agent

# Stop services
docker-compose down
```

### Docker (Production)

```bash
# Build image
docker build -t test-data-agent:latest .

# Run container
docker run -d \
  -p 9091:9091 \
  -p 8091:8091 \
  -e ANTHROPIC_API_KEY=your-key \
  -e WEAVIATE_URL=http://weaviate:8080 \
  test-data-agent:latest
```

### Kubernetes (Production)

Complete Kubernetes deployment manifests are available in `k8s/` directory.

```bash
# Deploy to Kubernetes
kubectl apply -f k8s/

# Verify deployment
kubectl get pods -n test-data-agent
kubectl get svc -n test-data-agent

# Check logs
kubectl logs -n test-data-agent -l app=test-data-agent --tail=100

# Port forward for testing
kubectl port-forward -n test-data-agent svc/test-data-agent 9091:9091
kubectl port-forward -n test-data-agent svc/test-data-agent 8091:8091
```

**Features:**
- Auto-scaling (2-10 pods based on CPU/memory)
- Health probes (liveness, readiness, startup)
- Resource limits (256-512Mi memory, 250-500m CPU)
- ConfigMaps and Secrets management
- Prometheus metrics annotations

See [k8s/README.md](k8s/README.md) for detailed deployment guide.

---

## Monitoring & Observability

### Health Endpoints

```bash
# Basic health
curl http://localhost:8091/health

# Liveness probe (Kubernetes)
curl http://localhost:8091/health/live

# Readiness probe (Kubernetes)
curl http://localhost:8091/health/ready

# Prometheus metrics
curl http://localhost:8091/metrics
```

### Available Metrics

- `testdata_requests_total` - Total requests by path, domain, entity, status
- `testdata_generation_duration_seconds` - Generation time histogram
- `testdata_records_generated` - Total records generated
- `testdata_validation_errors_total` - Validation error count

### Logs

Structured JSON logging with contextual fields:

```bash
# View logs (when running locally)
tail -f /tmp/test_data_agent.log

# Filter for routing decisions
tail -100 /tmp/test_data_agent.log | grep routing_decision

# Filter for errors
tail -100 /tmp/test_data_agent.log | grep error
```

**Example log entry:**
```json
{
  "timestamp": "2024-01-15T14:23:45.678Z",
  "level": "info",
  "event": "routing_decision",
  "request_id": "req-12345",
  "path": "llm",
  "confidence": 0.85,
  "reason": "LLM: context provided, coherence needed"
}
```

### Distributed Tracing

OpenTelemetry tracing is integrated for request flow visualization:

```bash
# Enable tracing in .env
TRACING_ENABLED=true
OTLP_ENDPOINT=http://localhost:4317

# Traces are exported to OpenTelemetry Collector
# Compatible with Jaeger, Zipkin, and other backends
```

**Trace Spans:**
- Request routing decisions
- Generator execution time
- LLM API calls
- RAG pattern retrieval
- Validation steps

---

## Troubleshooting

### Service won't start

**Problem:** Port already in use
```
[Errno 48] address already in use
```

**Solution:** Change ports in `.env`
```bash
GRPC_PORT=9092
HTTP_PORT=8092
```

---

### LLM generation fails

**Problem:** `AuthenticationError: Invalid API key`

**Solution:** Check your Anthropic API key
```bash
# Verify .env file
cat .env | grep ANTHROPIC_API_KEY

# Test key validity
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01"
```

---

### RAG generation returns no results

**Problem:** Weaviate not running or collections not seeded

**Solution:**
```bash
# 1. Check Weaviate is running
curl http://localhost:8080/v1/.well-known/ready

# 2. If not running, start it
docker-compose up -d weaviate

# 3. Seed collections
WEAVIATE_URL=http://localhost:8080 python -m test_data_agent.scripts.seed_rag

# 4. Verify data was inserted
curl http://localhost:8080/v1/objects?class=TestDataPattern
```

---

### gRPC reflection not working

**Problem:** `server does not support the reflection API`

**Solution:** Ensure `grpcio-reflection` is installed
```bash
pip install grpcio-reflection
```

---

## Performance Benchmarks

Tested on MacBook Pro M1, 16GB RAM:

| Path | Records | Time | Throughput | Coherence |
|------|---------|------|------------|-----------|
| Traditional | 1,000 | 42ms | 23,809 rec/sec | 0.28 |
| Traditional | 10,000 | 387ms | 25,839 rec/sec | 0.31 |
| LLM | 1 | 8.2s | 0.12 rec/sec | 0.87 |
| LLM | 3 | 18.5s | 0.16 rec/sec | 0.82 |
| RAG | 10 | 28ms | 357 rec/sec | 1.0 |
| RAG | 100 | 134ms | 746 rec/sec | 1.0 |
| Hybrid | 3 | 21.2s | 0.14 rec/sec | 0.76 |

**Key Takeaways:**
- Traditional: Best for bulk data (25K+ records/sec)
- RAG: Great balance of speed + quality (700+ records/sec)
- LLM/Hybrid: Best quality, slower (0.1-0.2 records/sec)

---

## Project Status

### ✅ All Phases Complete (100% - 39/39 tasks)

**Phase 1: Foundation** ✅
- [x] gRPC server with reflection
- [x] Configuration management
- [x] Structured logging
- [x] Health endpoints
- [x] Docker & Docker Compose

**Phase 2: Traditional Generator** ✅
- [x] Faker-based generation
- [x] Schema registry (6 entities)
- [x] Constraint validation
- [x] Prometheus metrics

**Phase 3: LLM Integration** ✅
- [x] Claude API integration
- [x] vLLM fallback client
- [x] Prompt engineering system
- [x] Coherence scoring
- [x] Intelligence routing

**Phase 4: RAG Integration** ✅
- [x] Weaviate vector database
- [x] Pattern retrieval & storage
- [x] Hybrid generation (RAG + LLM)
- [x] RAG seeding scripts

**Phase 5: Production Readiness** ✅
- [x] Redis caching with data pools
- [x] Streaming generation (GenerateDataStream RPC)
- [x] OpenTelemetry distributed tracing
- [x] Kubernetes manifests (7 files)
- [x] Horizontal pod autoscaler
- [x] Performance testing framework
- [x] E2E integration tests (8 scenarios)
- [x] CI/CD pipeline (GitHub Actions)

**Status: PRODUCTION READY** 🚀

---

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

**Guidelines:**
- Follow PEP 8 style guide
- Add tests for new features
- Update documentation
- Run `make lint` and `make test` before submitting

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

- **Anthropic Claude** - LLM generation capabilities
- **Weaviate** - Vector database for RAG
- **Faker** - Traditional data generation
- **gRPC** - High-performance RPC framework

---

## Additional Features

### Streaming Generation

For large datasets, use the streaming RPC to receive data in chunks:

```bash
grpcurl -plaintext -d '{
  "domain": "ecommerce",
  "entity": "user",
  "count": 500
}' localhost:9091 testdata.v1.TestDataService/GenerateDataStream
```

**Benefits:**
- Handles 500+ records efficiently
- Client receives data incrementally
- Reduces memory footprint
- Better progress feedback

### Redis Caching

Redis caching with data pools provides instant access to pre-generated data:

```bash
# Configure Redis in .env
REDIS_URL=redis://localhost:6379/0
CACHE_TTL_SECONDS=86400

# Data pools available:
# - pool:addresses
# - pool:phones
# - pool:names
# - pool:emails
```

### Performance Testing

Run performance benchmarks:

```bash
python tests/performance/test_load.py
```

**Scenarios:**
- Traditional generation (100 concurrent clients)
- Streaming generation (500 records)

### CI/CD Pipeline

GitHub Actions workflows for automated testing and deployment:

```bash
# Continuous Integration (.github/workflows/ci.yml)
# - Linting (ruff, black, mypy)
# - Unit tests with coverage
# - Integration tests
# - Docker image build
# - Security scanning (Trivy)

# Release Automation (.github/workflows/release.yml)
# - Triggered on version tags (v*)
# - Builds and pushes Docker images
# - Creates GitHub releases
# - Generates changelogs
```

---

## Documentation

📚 **[DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md)** - Complete guide to all 17 documentation files

### Quick Links

**Getting Started:**
- **[README.md](README.md)** - This file (getting started, usage)
- **[TESTING_GUIDE.md](TESTING_GUIDE.md)** - Complete testing guide
- **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - Complete project overview

**LLM & RAG Testing:**
- **[LLM_RAG_TESTS.md](LLM_RAG_TESTS.md)** - 29 comprehensive AI test scenarios
- **[LLM_RAG_QUICK_REFERENCE.md](LLM_RAG_QUICK_REFERENCE.md)** - Quick command reference
- **[RAG_TESTING_QUICK_START.md](RAG_TESTING_QUICK_START.md)** - RAG setup & testing

**Custom Schema Development:**
- **[CUSTOM_SCHEMA_GUIDE.md](CUSTOM_SCHEMA_GUIDE.md)** - Complete custom schema guide (850+ lines)
- **[CUSTOM_SCHEMA_QUICK_START.md](CUSTOM_SCHEMA_QUICK_START.md)** - Quick schema creation

**Project Status:**
- **[IMPLEMENTATION_COMPLETE.md](IMPLEMENTATION_COMPLETE.md)** - Final status report
- **[tasks.md](tasks.md)** - Implementation tasks (39/39 complete)

**Deployment:**
- **[k8s/README.md](k8s/README.md)** - Kubernetes deployment guide

---

## Support

- **Documentation:** Complete guides in repository root and `k8s/` directory
- **Issues:** [GitHub Issues](https://github.com/your-org/test-data-agent/issues)
- **Discussions:** [GitHub Discussions](https://github.com/your-org/test-data-agent/discussions)

---

**Built with ❤️ for QA Intelligence Platform**

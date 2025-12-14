# Test Data Agent - Complete Testing Guide

This guide shows you how to run and test every feature of the Test Data Agent.

**For comprehensive LLM & RAG testing, see [LLM_RAG_TESTS.md](LLM_RAG_TESTS.md)** - 29 detailed tests for AI-powered generation paths.

---

## 🚀 Quick Start

### 1. Start the Service

```bash
# Option 1: Direct run (recommended for development)
python -m test_data_agent.main

# Option 2: Docker Compose (full stack with Redis + Weaviate)
docker-compose up -d

# Option 3: Using Make
make run
```

### 2. Verify Service is Running

```bash
# HTTP health check
curl http://localhost:8091/health

# gRPC health check
grpcurl -plaintext localhost:9091 testdata.v1.TestDataService/HealthCheck

# List available schemas
grpcurl -plaintext -d '{}' localhost:9091 testdata.v1.TestDataService/GetSchemas
```

---

## ✅ All 6 Entity Schemas

The service includes 6 predefined entities:

| Entity | Domain | Use Case | Example Fields |
|--------|--------|----------|----------------|
| **cart** | ecommerce | Shopping cart | cart_id, items[], total, tax |
| **order** | ecommerce | Order processing | order_id, shipping_address, status |
| **payment** | ecommerce | Payment transactions | payment_id, method, amount, card_last_four |
| **product** | ecommerce | Product catalog | product_id, name, price, sku, stock |
| **review** | ecommerce | Product reviews | review_id, rating, title, body |
| **user** | ecommerce | Customer profiles | user_id, email, name, addresses[] |

---

## 🧪 Testing Individual Entities

### Test Cart Generation

```bash
grpcurl -plaintext -d '{
  "request_id": "test-cart-1",
  "domain": "ecommerce",
  "entity": "cart",
  "count": 5
}' localhost:9091 testdata.v1.TestDataService/GenerateData
```

**Expected:** Traditional path, <10ms, random items

---

### Test Order Generation

```bash
grpcurl -plaintext -d '{
  "request_id": "test-order-1",
  "domain": "ecommerce",
  "entity": "order",
  "count": 5
}' localhost:9091 testdata.v1.TestDataService/GenerateData
```

**Expected:** Traditional path, complete order with shipping/billing addresses

---

### Test Payment Generation

```bash
grpcurl -plaintext -d '{
  "request_id": "test-payment-1",
  "domain": "ecommerce",
  "entity": "payment",
  "count": 5
}' localhost:9091 testdata.v1.TestDataService/GenerateData
```

**Expected:** Traditional path, payment transactions with card info

---

### Test Product Generation

```bash
grpcurl -plaintext -d '{
  "request_id": "test-product-1",
  "domain": "ecommerce",
  "entity": "product",
  "count": 5
}' localhost:9091 testdata.v1.TestDataService/GenerateData
```

**Expected:** Traditional path, product catalog items with SKU, price, stock

---

### Test Review Generation

```bash
grpcurl -plaintext -d '{
  "request_id": "test-review-1",
  "domain": "ecommerce",
  "entity": "review",
  "count": 5
}' localhost:9091 testdata.v1.TestDataService/GenerateData
```

**Expected:** LLM path (~20s), realistic natural language reviews with varied sentiments

**Note:** Reviews use the LLM path by default because they contain text fields that benefit from intelligent generation.

---

### Test User Generation

```bash
grpcurl -plaintext -d '{
  "request_id": "test-user-1",
  "domain": "ecommerce",
  "entity": "user",
  "count": 10
}' localhost:9091 testdata.v1.TestDataService/GenerateData
```

**Expected:** Traditional path, user profiles with addresses and contact info

---

## 🎯 Testing All 4 Generation Paths

### Path 1: Traditional (Fast, Random)

```bash
# High volume request
grpcurl -plaintext -d '{
  "request_id": "test-traditional",
  "domain": "ecommerce",
  "entity": "user",
  "count": 100
}' localhost:9091 testdata.v1.TestDataService/GenerateData
```

**Expected:**
- Path: `traditional`
- Time: <100ms
- Coherence: 0.2-0.4
- Use case: Bulk data, stress testing

---

### Path 2: LLM (Intelligent, Realistic)

```bash
# Request with context and hints
grpcurl -plaintext -d '{
  "request_id": "test-llm",
  "domain": "ecommerce",
  "entity": "cart",
  "count": 3,
  "hints": ["coherent", "realistic"],
  "context": "Generate shopping carts for fitness enthusiasts buying workout gear"
}' localhost:9091 testdata.v1.TestDataService/GenerateData
```

**Expected:**
- Path: `llm`
- Time: ~20 seconds
- Coherence: 0.7-0.9
- Related items (running shoes + fitness accessories)
- Requires: Valid `ANTHROPIC_API_KEY` in `.env`

---

### Path 3: RAG (Pattern-Based)

**Setup Required:**
```bash
# 1. Start Weaviate
docker-compose up -d weaviate

# 2. Wait for Weaviate to be ready
sleep 5

# 3. Seed patterns
WEAVIATE_URL=http://localhost:8080 python -m test_data_agent.scripts.seed_rag
```

**Test RAG:**
```bash
grpcurl -plaintext -d '{
  "request_id": "test-rag",
  "domain": "ecommerce",
  "entity": "cart",
  "count": 5,
  "learn_from_history": true
}' localhost:9091 testdata.v1.TestDataService/GenerateData
```

**Expected:**
- Path: `rag`
- Time: ~20-50ms
- Coherence: 1.0 (perfect - uses historical patterns)
- Uses patterns from Weaviate

---

### Path 4: Hybrid (RAG + LLM)

```bash
grpcurl -plaintext -d '{
  "request_id": "test-hybrid",
  "domain": "ecommerce",
  "entity": "cart",
  "count": 3,
  "learn_from_history": true,
  "hints": ["coherent", "realistic"],
  "context": "Generate tech enthusiast carts based on past patterns"
}' localhost:9091 testdata.v1.TestDataService/GenerateData
```

**Expected:**
- Path: `hybrid`
- Time: ~21 seconds (RAG + LLM)
- Coherence: 0.7-0.8
- Combines historical patterns with creative variations
- Requires: Weaviate + Claude API key

---

## 🌊 Testing Streaming Generation

For large datasets (100+ records), use streaming:

```bash
grpcurl -plaintext -d '{
  "request_id": "test-stream",
  "domain": "ecommerce",
  "entity": "user",
  "count": 500
}' localhost:9091 testdata.v1.TestDataService/GenerateDataStream
```

**Expected:**
- Multiple data chunks
- Each chunk has: `chunk_index`, `is_final`
- Final chunk: `is_final: true`, empty data
- Total records: 500

**View first few chunks only:**
```bash
grpcurl -plaintext -d '{"entity":"user","count":100}' \
  localhost:9091 testdata.v1.TestDataService/GenerateDataStream | head -50
```

---

## 📊 Testing Monitoring & Observability

### Prometheus Metrics

```bash
# View all metrics
curl http://localhost:8091/metrics

# Filter for test data metrics
curl http://localhost:8091/metrics | grep testdata

# Specific metrics
curl http://localhost:8091/metrics | grep testdata_requests_total
curl http://localhost:8091/metrics | grep testdata_generation_duration
curl http://localhost:8091/metrics | grep testdata_records_generated
```

---

### Health Probes

```bash
# Basic health
curl http://localhost:8091/health | jq

# Liveness probe (Kubernetes)
curl http://localhost:8091/health/live

# Readiness probe (Kubernetes)
curl http://localhost:8091/health/ready
```

---

### Logs

```bash
# View real-time logs (if running in foreground)
# Logs appear in terminal

# If running in background, check logs:
tail -f /tmp/test_data_agent.log

# Filter for routing decisions
tail -100 /tmp/test_data_agent.log | grep routing_decision

# Filter for errors
tail -100 /tmp/test_data_agent.log | grep error

# Pretty print JSON logs
tail -100 /tmp/test_data_agent.log | jq
```

---

## 🧪 Running Automated Tests

### Unit Tests

```bash
# All unit tests
pytest tests/unit/ -v

# Specific test file
pytest tests/unit/test_traditional_generator.py -v

# With coverage report
pytest tests/unit/ --cov=src/test_data_agent --cov-report=html

# View coverage
open htmlcov/index.html
```

**Current Status:** 68/68 tests passing ✅

---

### Integration Tests

```bash
# Requires service to be running
pytest tests/integration/ -v

# Run specific integration test
pytest tests/integration/test_grpc_server.py -v
```

---

### E2E Tests

```bash
# Requires service to be running
pytest tests/e2e/ -v -m e2e

# Tests include:
# - Traditional generation
# - LLM generation (if API key available)
# - Streaming
# - Concurrent requests
# - Error handling
# - Data quality validation
```

---

### Performance Tests

```bash
# Run performance benchmarks
python tests/performance/test_load.py

# Scenarios:
# 1. Traditional generation (100 concurrent clients)
# 2. Streaming (500 records)

# Expected results:
# - Traditional p99 < 200ms
# - Streaming first chunk < 1s
```

---

## 🎓 Advanced Testing

### Test Defect Patterns

```bash
grpcurl -plaintext -d '{
  "domain": "ecommerce",
  "entity": "order",
  "count": 5,
  "defect_triggering": true
}' localhost:9091 testdata.v1.TestDataService/GenerateData
```

**Expected:** Edge cases like unicode, special chars, boundary values

---

### Test With Constraints

```bash
grpcurl -plaintext -d '{
  "domain": "ecommerce",
  "entity": "product",
  "count": 10,
  "constraints": {
    "field_constraints": {
      "price": {
        "min": 10.0,
        "max": 100.0
      },
      "category": {
        "enum_values": ["Electronics", "Clothing"]
      }
    }
  }
}' localhost:9091 testdata.v1.TestDataService/GenerateData
```

**Expected:** All products priced between $10-$100, only Electronics or Clothing

---

### Test With Scenarios

```bash
grpcurl -plaintext -d '{
  "domain": "ecommerce",
  "entity": "cart",
  "count": 15,
  "scenarios": [
    {
      "name": "small_cart",
      "count": 5,
      "overrides": {"item_count": "1-2"}
    },
    {
      "name": "large_cart",
      "count": 10,
      "overrides": {"item_count": "5-10"}
    }
  ]
}' localhost:9091 testdata.v1.TestDataService/GenerateData
```

**Expected:** 5 carts with 1-2 items, 10 carts with 5-10 items

---

## 🔧 Troubleshooting Tests

### Service Won't Start

```bash
# Check if ports are in use
lsof -i :9091
lsof -i :8091

# Kill existing processes
pkill -f "python -m test_data_agent.main"

# Restart
python -m test_data_agent.main
```

---

### LLM Tests Fail

```bash
# Check API key is set
grep ANTHROPIC_API_KEY .env

# Test API key validity
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $(grep ANTHROPIC_API_KEY .env | cut -d= -f2)" \
  -H "anthropic-version: 2023-06-01"

# If no API key, tests will fall back to Traditional path
```

---

### RAG Tests Return Empty

```bash
# Check Weaviate is running
curl http://localhost:8080/v1/.well-known/ready

# Start Weaviate if needed
docker-compose up -d weaviate

# Seed collections
WEAVIATE_URL=http://localhost:8080 python -m test_data_agent.scripts.seed_rag

# Verify data
curl http://localhost:8080/v1/objects?class=TestDataPattern
```

---

### gRPC Connection Errors

```bash
# Verify gRPC port is open
nc -zv localhost 9091

# Test with grpcurl
grpcurl -plaintext localhost:9091 list

# Check service logs for errors
tail -50 /tmp/test_data_agent.log | grep error
```

---

## 📈 Performance Expectations

| Test Type | Expected Latency | Notes |
|-----------|------------------|-------|
| Traditional (10 records) | <10ms | Fast, random data |
| Traditional (1000 records) | <100ms | Bulk generation |
| LLM (3 records) | ~20s | Claude API latency |
| RAG (10 records) | <50ms | Weaviate lookup |
| Hybrid (3 records) | ~21s | RAG + LLM combined |
| Streaming (500 records) | First chunk <1s | Incremental delivery |
| Health check | <5ms | Instant response |

---

## 🎯 Quick Test Commands

### Test Everything At Once

```bash
# Run automated test script
/tmp/test_all_entities.sh

# Or create your own:
for entity in cart order payment product review user; do
  echo "Testing $entity..."
  grpcurl -plaintext -d "{\"entity\":\"$entity\",\"count\":3}" \
    localhost:9091 testdata.v1.TestDataService/GenerateData | \
    jq -r '.metadata.generation_path'
done
```

---

### Monitor While Testing

```bash
# Terminal 1: Watch metrics
watch -n 2 'curl -s http://localhost:8091/metrics | grep testdata_requests_total'

# Terminal 2: Watch logs
tail -f /tmp/test_data_agent.log | grep -E "routing_decision|generation_complete"

# Terminal 3: Run tests
grpcurl -plaintext -d '{"entity":"cart","count":10}' \
  localhost:9091 testdata.v1.TestDataService/GenerateData
```

---

## ✅ Test Checklist

Use this checklist to verify everything works:

- [ ] Service starts successfully
- [ ] Health endpoints respond
- [ ] All 6 entities generate data
- [ ] Metrics are exposed
- [ ] Logs show routing decisions
- [ ] Unit tests pass (68/68)
- [ ] Traditional path works (<10ms)
- [ ] LLM path works (~20s) - if API key available
- [ ] RAG path works (<50ms) - if Weaviate running
- [ ] Hybrid path works (~21s) - if both available
- [ ] Streaming works for large datasets
- [ ] gRPC reflection works

---

## 📞 Getting Help

If tests fail:

1. Check logs: `tail -100 /tmp/test_data_agent.log`
2. Verify health: `curl http://localhost:8091/health`
3. Test connectivity: `grpcurl -plaintext localhost:9091 list`
4. Check dependencies: Weaviate, Redis running if needed
5. Verify configuration: `cat .env`

---

**Last Updated:** December 13, 2025
**Service Version:** 0.1.0
**Test Coverage:** 68/68 tests passing ✅

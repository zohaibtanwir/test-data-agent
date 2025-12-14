# LLM & RAG Quick Reference Card

## Path Selection Logic

| Request Characteristics | Path Selected |
|------------------------|---------------|
| `hints: ["coherent"]` or `context` provided | **LLM** |
| `learn_from_history: true` | **RAG** |
| Both LLM + RAG triggers | **Hybrid** |
| None of the above | **Traditional** |
| Entity = "review" | **LLM** (automatic) |

---

## Copy-Paste Test Commands

### 1. LLM with Context (Fitness Theme)
```bash
grpcurl -plaintext -d '{
  "entity": "cart",
  "count": 3,
  "context": "Generate shopping carts for fitness enthusiasts",
  "hints": ["coherent", "realistic"]
}' localhost:9091 testdata.v1.TestDataService/GenerateData | jq
```
**Expected:** Path: `llm`, Time: ~20s, Fitness-related items

---

### 2. LLM Reviews (Natural Language)
```bash
grpcurl -plaintext -d '{
  "entity": "review",
  "count": 5,
  "context": "Generate diverse product reviews"
}' localhost:9091 testdata.v1.TestDataService/GenerateData | jq '.data | fromjson | .[] | {rating, title, body}'
```
**Expected:** Path: `llm`, Natural language reviews with sentiment

---

### 3. RAG Pattern Retrieval
```bash
grpcurl -plaintext -d '{
  "entity": "cart",
  "count": 5,
  "learn_from_history": true
}' localhost:9091 testdata.v1.TestDataService/GenerateData | jq
```
**Expected:** Path: `rag`, Time: ~30ms, Coherence: 1.0

**Setup Required:**
```bash
docker-compose up -d weaviate
sleep 5
WEAVIATE_URL=http://localhost:8080 python -m test_data_agent.scripts.seed_rag
```

---

### 4. RAG Defect Triggering
```bash
grpcurl -plaintext -d '{
  "entity": "order",
  "count": 5,
  "defect_triggering": true
}' localhost:9091 testdata.v1.TestDataService/GenerateData | jq
```
**Expected:** Path: `rag`, Edge cases (unicode, special chars, boundary values)

---

### 5. Hybrid (RAG + LLM)
```bash
grpcurl -plaintext -d '{
  "entity": "cart",
  "count": 3,
  "learn_from_history": true,
  "context": "Generate tech enthusiast carts",
  "hints": ["coherent"]
}' localhost:9091 testdata.v1.TestDataService/GenerateData | jq
```
**Expected:** Path: `hybrid`, Time: ~21s, Pattern-based + creative

---

### 6. LLM with Constraints
```bash
grpcurl -plaintext -d '{
  "entity": "cart",
  "count": 3,
  "context": "Budget shoppers",
  "constraints": {
    "field_constraints": {
      "total": {"min": 20.0, "max": 100.0}
    }
  },
  "hints": ["coherent"]
}' localhost:9091 testdata.v1.TestDataService/GenerateData | jq
```
**Expected:** All carts between $20-$100

---

### 7. Compare All Paths

**Traditional:**
```bash
grpcurl -plaintext -d '{"entity":"cart","count":10}' localhost:9091 testdata.v1.TestDataService/GenerateData | jq '{path: .metadata.generation_path, time: .metadata.generation_time_ms}'
```

**LLM:**
```bash
grpcurl -plaintext -d '{"entity":"cart","count":10,"hints":["coherent"]}' localhost:9091 testdata.v1.TestDataService/GenerateData | jq '{path: .metadata.generation_path, time: .metadata.generation_time_ms}'
```

**RAG:**
```bash
grpcurl -plaintext -d '{"entity":"cart","count":10,"learn_from_history":true}' localhost:9091 testdata.v1.TestDataService/GenerateData | jq '{path: .metadata.generation_path, time: .metadata.generation_time_ms}'
```

**Hybrid:**
```bash
grpcurl -plaintext -d '{"entity":"cart","count":10,"learn_from_history":true,"hints":["coherent"]}' localhost:9091 testdata.v1.TestDataService/GenerateData | jq '{path: .metadata.generation_path, time: .metadata.generation_time_ms}'
```

---

## Performance Expectations

| Path | Latency | Coherence | Best For |
|------|---------|-----------|----------|
| Traditional | <5ms | 0.2-0.4 | Bulk data (>500 records) |
| LLM | ~20s | 0.7-0.9 | Realistic scenarios, text |
| RAG | ~30ms | 1.0 | Historical patterns, defects |
| Hybrid | ~21s | 0.7-0.8 | Pattern + creativity |

---

## Monitoring

**View Path Metrics:**
```bash
curl -s http://localhost:8091/metrics | grep testdata_requests_total
```

**Watch Real-time:**
```bash
watch -n 2 'curl -s http://localhost:8091/metrics | grep testdata_requests_total'
```

**Check Routing Logs:**
```bash
tail -100 /tmp/test_data_agent.log | grep routing_decision | jq
```

---

## Quick Test Script

Run automated tests for all LLM & RAG paths:
```bash
bash /tmp/quick_llm_tests.sh
```

---

## Common Issues

### LLM Tests Fail
**Check API Key:**
```bash
grep ANTHROPIC_API_KEY .env
```

### RAG Tests Fail
**Check Weaviate:**
```bash
curl http://localhost:8080/v1/.well-known/ready
```

**Seed Patterns:**
```bash
WEAVIATE_URL=http://localhost:8080 python -m test_data_agent.scripts.seed_rag
```

---

## Full Documentation

- **Comprehensive Guide:** `LLM_RAG_TESTS.md` (29 tests)
- **General Testing:** `TESTING_GUIDE.md`
- **Quick Script:** `/tmp/quick_llm_tests.sh`
- **This Card:** `/tmp/llm_rag_quick_reference.md`

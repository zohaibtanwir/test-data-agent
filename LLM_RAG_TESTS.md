# LLM & RAG Testing Guide - Test Data Agent

**Comprehensive test commands for AI-powered generation paths**

Date: December 13, 2025
Service Version: 0.1.0

---

## Quick Reference

| Path | Speed | Coherence | Use Case | Requirements |
|------|-------|-----------|----------|--------------|
| **LLM** | ~20s | 0.7-0.9 | Realistic, context-aware data | `ANTHROPIC_API_KEY` |
| **RAG** | ~20-50ms | 1.0 | Historical patterns, defects | Weaviate + seeded data |
| **Hybrid** | ~21s | 0.7-0.8 | RAG context + LLM creativity | Both LLM + RAG |

---

# 🤖 LLM Path Tests (Claude AI)

## Setup

**Prerequisites:**
```bash
# 1. Ensure ANTHROPIC_API_KEY is set in .env
grep ANTHROPIC_API_KEY .env

# 2. Verify Claude client is initialized
curl http://localhost:8091/health | jq
```

---

## Test 1: Basic LLM Generation (Cart)

**Command:**
```bash
grpcurl -plaintext -d '{
  "request_id": "llm-test-1",
  "domain": "ecommerce",
  "entity": "cart",
  "count": 3,
  "hints": ["coherent", "realistic"]
}' localhost:9091 testdata.v1.TestDataService/GenerateData | jq
```

**Expected:**
- Path: `llm`
- Time: ~20 seconds
- Coherence: 0.7-0.9
- Items in cart are related/make sense together
- Total = subtotal + tax

**Example Output:**
```json
{
  "request_id": "llm-test-1",
  "success": true,
  "record_count": 3,
  "metadata": {
    "generation_path": "llm",
    "generation_time_ms": 20145.32,
    "coherence_score": 0.85
  }
}
```

---

## Test 2: LLM with Context (Fitness Theme)

**Command:**
```bash
grpcurl -plaintext -d '{
  "request_id": "llm-test-2",
  "domain": "ecommerce",
  "entity": "cart",
  "count": 5,
  "context": "Generate shopping carts for fitness enthusiasts buying workout gear",
  "hints": ["coherent", "realistic", "high-value"]
}' localhost:9091 testdata.v1.TestDataService/GenerateData | jq '.data | fromjson | .[0]'
```

**Expected:**
- Path: `llm`
- Items: Running shoes, fitness tracker, protein powder, yoga mat, etc.
- Related products grouped together
- Higher cart values

**Why It Works:**
- `context` field triggers LLM path
- Claude understands "fitness enthusiasts" theme
- Generates contextually appropriate items

---

## Test 3: LLM for Reviews (Natural Language)

**Command:**
```bash
grpcurl -plaintext -d '{
  "request_id": "llm-test-3",
  "domain": "ecommerce",
  "entity": "review",
  "count": 5,
  "context": "Generate diverse product reviews with varied sentiments"
}' localhost:9091 testdata.v1.TestDataService/GenerateData | jq '.data | fromjson | .[] | {rating, title, body}'
```

**Expected:**
- Path: `llm` (automatic for reviews)
- Natural language titles and bodies
- Rating matches sentiment (5 stars = positive review)
- Varied review lengths and styles

**Example Reviews:**
```json
{
  "rating": 5,
  "title": "Exceeded my expectations!",
  "body": "This product is fantastic. I've been using it for 3 weeks and it works perfectly. Highly recommend!"
}
{
  "rating": 2,
  "title": "Disappointed",
  "body": "Quality is not what I expected. The material feels cheap and it broke after just a few uses."
}
```

---

## Test 4: LLM with Luxury Theme (High-End Products)

**Command:**
```bash
grpcurl -plaintext -d '{
  "request_id": "llm-test-4",
  "domain": "ecommerce",
  "entity": "cart",
  "count": 3,
  "context": "Generate shopping carts for luxury shoppers buying premium items",
  "hints": ["coherent", "realistic", "premium"]
}' localhost:9091 testdata.v1.TestDataService/GenerateData | jq
```

**Expected:**
- High-value items (>$500)
- Premium brands mentioned
- Luxury categories (watches, designer clothing, electronics)
- Higher tax amounts

---

## Test 5: LLM for Orders with Specific Scenarios

**Command:**
```bash
grpcurl -plaintext -d '{
  "request_id": "llm-test-5",
  "domain": "ecommerce",
  "entity": "order",
  "count": 3,
  "context": "Generate orders for international customers with gift wrapping",
  "hints": ["coherent", "realistic"]
}' localhost:9091 testdata.v1.TestDataService/GenerateData | jq '.data | fromjson | .[0]'
```

**Expected:**
- International shipping addresses
- Gift messages or special instructions
- Coherent item combinations
- Appropriate shipping methods

---

## Test 6: LLM with Edge Cases (Small Count)

**Command:**
```bash
grpcurl -plaintext -d '{
  "request_id": "llm-test-6",
  "domain": "ecommerce",
  "entity": "cart",
  "count": 1,
  "context": "Generate a cart for a tech enthusiast buying gaming gear",
  "hints": ["coherent", "realistic"]
}' localhost:9091 testdata.v1.TestDataService/GenerateData | jq
```

**Expected:**
- Single cart with gaming-related items
- Coherent product combinations
- LLM path even for count=1

---

## Test 7: LLM for Multiple Entity Types

**Test Users with Context:**
```bash
grpcurl -plaintext -d '{
  "request_id": "llm-test-7a",
  "domain": "ecommerce",
  "entity": "user",
  "count": 3,
  "context": "Generate user profiles for premium loyalty members",
  "hints": ["realistic"]
}' localhost:9091 testdata.v1.TestDataService/GenerateData | jq
```

**Test Products with Context:**
```bash
grpcurl -plaintext -d '{
  "request_id": "llm-test-7b",
  "domain": "ecommerce",
  "entity": "product",
  "count": 5,
  "context": "Generate eco-friendly sustainable products",
  "hints": ["realistic"]
}' localhost:9091 testdata.v1.TestDataService/GenerateData | jq
```

**Expected:**
- Context-aware generation for each entity
- Realistic field values matching the theme

---

## Test 8: LLM with Constraints

**Command:**
```bash
grpcurl -plaintext -d '{
  "request_id": "llm-test-8",
  "domain": "ecommerce",
  "entity": "cart",
  "count": 3,
  "context": "Generate budget-conscious shopping carts",
  "constraints": {
    "field_constraints": {
      "total": {
        "min": 20.0,
        "max": 100.0
      }
    }
  },
  "hints": ["coherent", "realistic"]
}' localhost:9091 testdata.v1.TestDataService/GenerateData | jq
```

**Expected:**
- Path: `llm`
- All cart totals between $20-$100
- Budget-appropriate items
- Claude respects constraints

---

## Test 9: Streaming LLM Generation

**Command:**
```bash
grpcurl -plaintext -d '{
  "request_id": "llm-test-9",
  "domain": "ecommerce",
  "entity": "review",
  "count": 10,
  "context": "Generate product reviews for electronics"
}' localhost:9091 testdata.v1.TestDataService/GenerateDataStream | head -100
```

**Expected:**
- Streaming chunks of reviews
- Each chunk has `chunk_index` and `is_final`
- LLM-generated natural language

---

## Test 10: Verify LLM Path Selection

**Command:**
```bash
# This should use LLM (has hints)
grpcurl -plaintext -d '{
  "entity": "cart",
  "count": 3,
  "hints": ["coherent"]
}' localhost:9091 testdata.v1.TestDataService/GenerateData | jq '.metadata.generation_path'

# This should use Traditional (no hints, no context)
grpcurl -plaintext -d '{
  "entity": "cart",
  "count": 3
}' localhost:9091 testdata.v1.TestDataService/GenerateData | jq '.metadata.generation_path'
```

**Expected:**
- First: `"llm"`
- Second: `"traditional"`

---

# 🔍 RAG Path Tests (Pattern Retrieval)

## Setup

**Prerequisites:**
```bash
# 1. Start Weaviate
docker-compose up -d weaviate

# 2. Wait for Weaviate to be ready
sleep 5
curl http://localhost:8080/v1/.well-known/ready

# 3. Seed RAG collections with patterns
WEAVIATE_URL=http://localhost:8080 python -m test_data_agent.scripts.seed_rag

# 4. Verify patterns loaded
curl http://localhost:8080/v1/objects?class=TestDataPattern | jq '.objects | length'
```

**Expected:**
- Weaviate running on port 8080
- At least 30+ patterns seeded
- Collections: `TestDataPattern`, `TestDataDefect`, `TestDataProdSample`

---

## Test 11: Basic RAG Generation

**Command:**
```bash
grpcurl -plaintext -d '{
  "request_id": "rag-test-1",
  "domain": "ecommerce",
  "entity": "cart",
  "count": 5,
  "learn_from_history": true
}' localhost:9091 testdata.v1.TestDataService/GenerateData | jq
```

**Expected:**
- Path: `rag`
- Time: ~20-50ms (much faster than LLM!)
- Coherence: 1.0 (perfect - uses exact patterns)
- Data based on historical patterns from Weaviate

**How It Works:**
- `learn_from_history: true` triggers RAG path
- Retrieves similar patterns from Weaviate
- Modifies pattern data slightly for variation

---

## Test 12: RAG with Defect Triggering

**Command:**
```bash
grpcurl -plaintext -d '{
  "request_id": "rag-test-2",
  "domain": "ecommerce",
  "entity": "order",
  "count": 5,
  "defect_triggering": true
}' localhost:9091 testdata.v1.TestDataService/GenerateData | jq '.data | fromjson | .[0]'
```

**Expected:**
- Path: `rag`
- Edge case data:
  - Unicode characters in names/addresses
  - Special characters (', ", &, <, >)
  - Boundary values (very large/small numbers)
  - Empty optional fields
  - Maximum length strings

**Use Case:** Testing application robustness against edge cases

---

## Test 13: RAG Pattern Retrieval for Users

**Command:**
```bash
grpcurl -plaintext -d '{
  "request_id": "rag-test-3",
  "domain": "ecommerce",
  "entity": "user",
  "count": 10,
  "learn_from_history": true
}' localhost:9091 testdata.v1.TestDataService/GenerateData | jq
```

**Expected:**
- Path: `rag`
- Retrieves user patterns from Weaviate
- Consistent user profile structures
- Fast generation (~30ms)

---

## Test 14: RAG with Specific Domain

**Command:**
```bash
grpcurl -plaintext -d '{
  "request_id": "rag-test-4",
  "domain": "ecommerce",
  "entity": "payment",
  "count": 5,
  "learn_from_history": true
}' localhost:9091 testdata.v1.TestDataService/GenerateData | jq '.data | fromjson | .[] | {payment_id, method, amount, status}'
```

**Expected:**
- Payment patterns from production-like samples
- Realistic payment methods (credit_card, paypal, etc.)
- Appropriate amount ranges
- Valid status values

---

## Test 15: RAG Performance Test

**Command:**
```bash
# Generate 100 records using RAG
time grpcurl -plaintext -d '{
  "request_id": "rag-test-5",
  "domain": "ecommerce",
  "entity": "cart",
  "count": 100,
  "learn_from_history": true
}' localhost:9091 testdata.v1.TestDataService/GenerateData | jq '.metadata.generation_time_ms'
```

**Expected:**
- Time: <200ms for 100 records
- Much faster than Traditional for large counts
- Coherence maintained across all records

---

## Test 16: RAG Streaming

**Command:**
```bash
grpcurl -plaintext -d '{
  "request_id": "rag-test-6",
  "domain": "ecommerce",
  "entity": "product",
  "count": 50,
  "learn_from_history": true
}' localhost:9091 testdata.v1.TestDataService/GenerateDataStream | head -50
```

**Expected:**
- Streaming chunks with RAG-generated data
- Fast chunk delivery
- Pattern-based products

---

## Test 17: Verify RAG Pattern Match

**Command:**
```bash
# Generate with RAG
grpcurl -plaintext -d '{
  "entity": "cart",
  "count": 1,
  "learn_from_history": true
}' localhost:9091 testdata.v1.TestDataService/GenerateData > /tmp/rag_output.json

# Check coherence score
cat /tmp/rag_output.json | jq '.metadata.coherence_score'
```

**Expected:**
- Coherence score: 1.0 (perfect)
- Data matches historical pattern structure

---

# 🔄 Hybrid Path Tests (RAG + LLM)

## Test 18: Basic Hybrid Generation

**Command:**
```bash
grpcurl -plaintext -d '{
  "request_id": "hybrid-test-1",
  "domain": "ecommerce",
  "entity": "cart",
  "count": 3,
  "learn_from_history": true,
  "hints": ["coherent", "realistic"],
  "context": "Generate tech enthusiast shopping carts based on historical patterns"
}' localhost:9091 testdata.v1.TestDataService/GenerateData | jq
```

**Expected:**
- Path: `hybrid`
- Time: ~21 seconds (RAG retrieval + LLM generation)
- Coherence: 0.7-0.8
- Combines historical patterns with creative variations
- Context-aware AND pattern-based

**How It Works:**
1. RAG retrieves relevant patterns from Weaviate
2. Patterns sent to Claude as context
3. LLM generates new data inspired by patterns
4. Best of both worlds: speed of patterns + creativity of LLM

---

## Test 19: Hybrid with Defects + Context

**Command:**
```bash
grpcurl -plaintext -d '{
  "request_id": "hybrid-test-2",
  "domain": "ecommerce",
  "entity": "order",
  "count": 3,
  "learn_from_history": true,
  "defect_triggering": true,
  "context": "Generate edge case orders for stress testing",
  "hints": ["realistic"]
}' localhost:9091 testdata.v1.TestDataService/GenerateData | jq
```

**Expected:**
- Path: `hybrid`
- Edge cases based on historical defect patterns
- LLM-enhanced realistic variations
- Good for QA stress testing

---

## Test 20: Hybrid for Reviews

**Command:**
```bash
grpcurl -plaintext -d '{
  "request_id": "hybrid-test-3",
  "domain": "ecommerce",
  "entity": "review",
  "count": 5,
  "learn_from_history": true,
  "context": "Generate product reviews based on common review patterns"
}' localhost:9091 testdata.v1.TestDataService/GenerateData | jq '.data | fromjson | .[] | {rating, title}'
```

**Expected:**
- Natural language reviews
- Common review structures from patterns
- Creative variations from Claude

---

## Test 21: Hybrid with Constraints

**Command:**
```bash
grpcurl -plaintext -d '{
  "request_id": "hybrid-test-4",
  "domain": "ecommerce",
  "entity": "product",
  "count": 10,
  "learn_from_history": true,
  "context": "Generate electronics products",
  "constraints": {
    "field_constraints": {
      "price": {
        "min": 100.0,
        "max": 2000.0
      },
      "category": {
        "enum_values": ["Electronics", "Computers", "Gaming"]
      }
    }
  },
  "hints": ["realistic"]
}' localhost:9091 testdata.v1.TestDataService/GenerateData | jq
```

**Expected:**
- Pattern-based products
- LLM respects constraints
- Electronics category only
- Prices $100-$2000

---

# 📊 Comparison Tests

## Test 22: Compare All 4 Paths for Cart

**Traditional:**
```bash
grpcurl -plaintext -d '{
  "request_id": "compare-traditional",
  "entity": "cart",
  "count": 10
}' localhost:9091 testdata.v1.TestDataService/GenerateData | jq '{path: .metadata.generation_path, time: .metadata.generation_time_ms, coherence: .metadata.coherence_score}'
```

**LLM:**
```bash
grpcurl -plaintext -d '{
  "request_id": "compare-llm",
  "entity": "cart",
  "count": 10,
  "hints": ["coherent"]
}' localhost:9091 testdata.v1.TestDataService/GenerateData | jq '{path: .metadata.generation_path, time: .metadata.generation_time_ms, coherence: .metadata.coherence_score}'
```

**RAG:**
```bash
grpcurl -plaintext -d '{
  "request_id": "compare-rag",
  "entity": "cart",
  "count": 10,
  "learn_from_history": true
}' localhost:9091 testdata.v1.TestDataService/GenerateData | jq '{path: .metadata.generation_path, time: .metadata.generation_time_ms, coherence: .metadata.coherence_score}'
```

**Hybrid:**
```bash
grpcurl -plaintext -d '{
  "request_id": "compare-hybrid",
  "entity": "cart",
  "count": 10,
  "learn_from_history": true,
  "hints": ["coherent"]
}' localhost:9091 testdata.v1.TestDataService/GenerateData | jq '{path: .metadata.generation_path, time: .metadata.generation_time_ms, coherence: .metadata.coherence_score}'
```

**Expected Comparison:**
| Path | Time | Coherence | Use Case |
|------|------|-----------|----------|
| Traditional | ~5ms | 0.2-0.4 | Bulk data |
| LLM | ~20s | 0.7-0.9 | Realistic scenarios |
| RAG | ~30ms | 1.0 | Historical patterns |
| Hybrid | ~21s | 0.7-0.8 | Best of both |

---

# 🎯 Advanced Test Scenarios

## Test 23: Multi-Scenario with LLM

**Command:**
```bash
grpcurl -plaintext -d '{
  "request_id": "advanced-test-1",
  "domain": "ecommerce",
  "entity": "cart",
  "count": 15,
  "scenarios": [
    {
      "name": "budget_shoppers",
      "count": 5,
      "overrides": {"total": "20-50"}
    },
    {
      "name": "premium_shoppers",
      "count": 10,
      "overrides": {"total": "500-2000"}
    }
  ],
  "hints": ["coherent", "realistic"]
}' localhost:9091 testdata.v1.TestDataService/GenerateData | jq
```

**Expected:**
- 5 budget carts ($20-$50)
- 10 premium carts ($500-$2000)
- LLM-generated coherent items for each tier

---

## Test 24: RAG with Production Samples

**Command:**
```bash
grpcurl -plaintext -d '{
  "request_id": "advanced-test-2",
  "domain": "ecommerce",
  "entity": "user",
  "count": 20,
  "learn_from_history": true,
  "context": "production"
}' localhost:9091 testdata.v1.TestDataService/GenerateData | jq
```

**Expected:**
- Production-like user data
- Realistic email patterns
- Valid phone formats
- Proper address structures

---

## Test 25: Concurrent LLM Requests

**Command:**
```bash
# Terminal 1
grpcurl -plaintext -d '{"entity":"review","count":5,"hints":["realistic"]}' \
  localhost:9091 testdata.v1.TestDataService/GenerateData &

# Terminal 2
grpcurl -plaintext -d '{"entity":"review","count":5,"hints":["realistic"]}' \
  localhost:9091 testdata.v1.TestDataService/GenerateData &

# Terminal 3
grpcurl -plaintext -d '{"entity":"review","count":5,"hints":["realistic"]}' \
  localhost:9091 testdata.v1.TestDataService/GenerateData &

wait
```

**Expected:**
- All 3 requests complete successfully
- Concurrent Claude API calls
- Each takes ~20s
- No failures or timeouts

---

# 🔍 Monitoring & Verification

## Monitor LLM/RAG Path Usage

**Command:**
```bash
# Watch metrics in real-time
watch -n 2 'curl -s http://localhost:8091/metrics | grep testdata_requests_total'
```

**Expected Output:**
```
testdata_requests_total{path="traditional",status="success"} 45
testdata_requests_total{path="llm",status="success"} 12
testdata_requests_total{path="rag",status="success"} 8
testdata_requests_total{path="hybrid",status="success"} 3
```

---

## Check Service Logs for Routing Decisions

**Command:**
```bash
# View recent routing decisions
tail -100 /tmp/test_data_agent.log | grep routing_decision | jq
```

**Expected:**
```json
{
  "event": "routing_decision",
  "path": "llm",
  "reason": "hints_provided",
  "timestamp": "2025-12-13T08:00:00Z"
}
```

---

# 🚨 Error Scenarios

## Test 26: LLM Without API Key

**Command:**
```bash
# Temporarily unset API key
export ANTHROPIC_API_KEY=""

# Restart service
python -m test_data_agent.main

# Try LLM generation
grpcurl -plaintext -d '{
  "entity": "cart",
  "count": 3,
  "hints": ["coherent"]
}' localhost:9091 testdata.v1.TestDataService/GenerateData | jq
```

**Expected:**
- Fallback to Traditional path
- Warning in logs
- Still returns data (graceful degradation)

---

## Test 27: RAG Without Weaviate

**Command:**
```bash
# Stop Weaviate
docker-compose stop weaviate

# Try RAG generation
grpcurl -plaintext -d '{
  "entity": "cart",
  "count": 3,
  "learn_from_history": true
}' localhost:9091 testdata.v1.TestDataService/GenerateData | jq '.metadata.generation_path'
```

**Expected:**
- Fallback to Traditional path
- Error logged but request succeeds
- Graceful degradation

---

# 📈 Performance Benchmarks

## Test 28: LLM Throughput

**Command:**
```bash
# Generate 100 records with LLM
time grpcurl -plaintext -d '{
  "entity": "review",
  "count": 100,
  "hints": ["realistic"]
}' localhost:9091 testdata.v1.TestDataService/GenerateData | jq '.metadata.generation_time_ms'
```

**Expected:**
- Time: ~20-30 seconds
- Claude API rate limits may apply
- Consider streaming for large counts

---

## Test 29: RAG Throughput

**Command:**
```bash
# Generate 1000 records with RAG
time grpcurl -plaintext -d '{
  "entity": "cart",
  "count": 1000,
  "learn_from_history": true
}' localhost:9091 testdata.v1.TestDataService/GenerateData | jq '.metadata.generation_time_ms'
```

**Expected:**
- Time: <500ms for 1000 records
- Much faster than Traditional for large counts
- Weaviate retrieval scales well

---

# 🎓 Best Practices

## When to Use Each Path

### Use LLM When:
- ✅ Need realistic, natural language text
- ✅ Context-aware scenarios
- ✅ Coherent relationships between fields
- ✅ Creative variations required
- ❌ NOT for bulk generation (>100 records)

### Use RAG When:
- ✅ Need historical pattern consistency
- ✅ Fast generation with coherence
- ✅ Defect/edge case triggering
- ✅ Production-like data
- ❌ NOT without seeded patterns

### Use Hybrid When:
- ✅ Need both pattern consistency AND creativity
- ✅ Historical context with variations
- ✅ Best quality at acceptable speed
- ❌ NOT for time-sensitive requests

### Use Traditional When:
- ✅ Bulk data generation (>500 records)
- ✅ Speed is critical (<10ms)
- ✅ Random data is acceptable
- ❌ NOT when coherence matters

---

# 🛠 Troubleshooting

## LLM Tests Failing

**Check API Key:**
```bash
grep ANTHROPIC_API_KEY .env
echo $ANTHROPIC_API_KEY
```

**Test Claude API:**
```bash
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{
    "model": "claude-sonnet-4-20250514",
    "max_tokens": 100,
    "messages": [{"role": "user", "content": "Hello"}]
  }'
```

## RAG Tests Failing

**Check Weaviate:**
```bash
curl http://localhost:8080/v1/.well-known/ready
```

**Verify Patterns:**
```bash
curl http://localhost:8080/v1/objects?class=TestDataPattern | jq '.objects | length'
```

**Reseed if Needed:**
```bash
WEAVIATE_URL=http://localhost:8080 python -m test_data_agent.scripts.seed_rag
```

---

# 📋 Test Checklist

## LLM Path
- [ ] Basic LLM generation works
- [ ] Context-aware generation
- [ ] Reviews generate natural language
- [ ] Constraints are respected
- [ ] Coherence scores 0.7-0.9
- [ ] Streaming works with LLM
- [ ] Graceful fallback without API key

## RAG Path
- [ ] Weaviate connection works
- [ ] Patterns retrieved successfully
- [ ] Defect triggering produces edge cases
- [ ] Coherence score = 1.0
- [ ] Fast generation (<50ms)
- [ ] Streaming works with RAG
- [ ] Graceful fallback without Weaviate

## Hybrid Path
- [ ] Combines RAG + LLM correctly
- [ ] Uses pattern context in LLM prompts
- [ ] Takes ~21 seconds
- [ ] Coherence 0.7-0.8
- [ ] Works with all entities

---

**Last Updated:** December 13, 2025
**Service Version:** 0.1.0
**Total Tests:** 29

**Next Steps:**
1. Run through all tests systematically
2. Record actual performance metrics
3. Compare with expected results
4. Report any failures or discrepancies

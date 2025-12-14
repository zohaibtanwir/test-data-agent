# RAG Testing - Quick Start Guide

## ✅ Setup Complete

**Status:** RAG is READY to test!

- ✅ Weaviate running on port 8080
- ✅ Service running on ports 9091 (gRPC), 8091 (HTTP)
- ✅ 10 test data patterns seeded
- ✅ 10 defect patterns seeded
- ✅ 4 production samples seeded

---

## 🎯 Quick Test Verification

```bash
# Verified working - 9.59ms, coherence 1.0!
grpcurl -plaintext -d '{
  "entity": "cart",
  "count": 3,
  "learn_from_history": true
}' localhost:9091 testdata.v1.TestDataService/GenerateData | jq
```

**Result:** ✅ Path: `rag` | Time: `9.59ms` | Coherence: `1.0`

---

## 📋 RAG Test Commands

### Test 1: Basic RAG Cart Generation

```bash
grpcurl -plaintext -d '{
  "request_id": "rag-cart-1",
  "entity": "cart",
  "count": 5,
  "learn_from_history": true
}' localhost:9091 testdata.v1.TestDataService/GenerateData | jq
```

**Expected:**
- Path: `rag`
- Time: ~10-30ms (70x faster than LLM!)
- Coherence: 1.0 (perfect - uses exact historical patterns)

---

### Test 2: RAG Defect Triggering (Edge Cases)

```bash
grpcurl -plaintext -d '{
  "request_id": "rag-defect-1",
  "entity": "order",
  "count": 5,
  "defect_triggering": true
}' localhost:9091 testdata.v1.TestDataService/GenerateData | jq '.data | fromjson | .[0]'
```

**Expected:**
- Edge case data: unicode characters, special chars, boundary values
- Good for testing application robustness
- Super fast generation

---

### Test 3: RAG User Generation

```bash
grpcurl -plaintext -d '{
  "request_id": "rag-users-1",
  "entity": "user",
  "count": 10,
  "learn_from_history": true
}' localhost:9091 testdata.v1.TestDataService/GenerateData | jq
```

**Expected:**
- Pattern-based user profiles
- Consistent structure
- Fast generation

---

### Test 4: RAG Product Catalog

```bash
grpcurl -plaintext -d '{
  "request_id": "rag-products-1",
  "entity": "product",
  "count": 10,
  "learn_from_history": true
}' localhost:9091 testdata.v1.TestDataService/GenerateData | jq
```

---

### Test 5: RAG Large Dataset (Performance)

```bash
# Generate 100 records using RAG
grpcurl -plaintext -d '{
  "request_id": "rag-perf-1",
  "entity": "cart",
  "count": 100,
  "learn_from_history": true
}' localhost:9091 testdata.v1.TestDataService/GenerateData | jq '{path: .metadata.generation_path, time_ms: .metadata.generation_time_ms, records: .record_count}'
```

**Expected:**
- Time: <200ms for 100 records
- Much faster than Traditional for coherent data
- Perfect coherence across all records

---

## 🔄 Hybrid Path (RAG + LLM)

Combines RAG patterns with LLM creativity:

```bash
grpcurl -plaintext -d '{
  "request_id": "hybrid-test-1",
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
- Best of both worlds: pattern-based + creative

**Note:** This will take ~20 seconds due to Claude API call

---

## 🚀 Run All RAG Tests

```bash
bash /tmp/test_rag.sh
```

This runs 4 comprehensive RAG tests automatically.

---

## 📊 Performance Comparison

| Path | Speed | Coherence | Use Case |
|------|-------|-----------|----------|
| Traditional | <5ms | 0.2-0.4 | Bulk random data |
| **RAG** | **~10ms** | **1.0** | **Historical patterns, defects** |
| LLM | ~20s | 0.7-0.9 | Realistic text, context-aware |
| Hybrid | ~21s | 0.7-0.8 | Pattern + creativity |

**RAG Advantages:**
- ✅ 2000x faster than LLM
- ✅ Perfect coherence (1.0)
- ✅ Reproducible patterns
- ✅ Good for defect/edge case testing

---

## 🔍 Monitor RAG Usage

**View metrics:**
```bash
curl -s http://localhost:8091/metrics | grep testdata_requests_total
```

**Watch in real-time:**
```bash
watch -n 2 'curl -s http://localhost:8091/metrics | grep -E "rag|hybrid"'
```

**Check logs:**
```bash
tail -100 /tmp/test_data_agent.log | grep -E "rag|routing_decision" | jq
```

---

## 🗄️ Weaviate Status

**Check patterns loaded:**
```bash
# Test Data Patterns
curl -s 'http://localhost:8080/v1/objects?class=TestDataPattern' | jq '.objects | length'

# Defect Patterns
curl -s 'http://localhost:8080/v1/objects?class=DefectPattern' | jq '.objects | length'

# Production Samples
curl -s 'http://localhost:8080/v1/objects?class=ProductionSample' | jq '.objects | length'
```

**Expected:** 10, 10, 4

---

## 🎓 Key Differences: RAG vs Traditional vs LLM

### RAG (Pattern Retrieval)
```bash
{"learn_from_history": true}
```
- Retrieves historical patterns from Weaviate
- Modifies pattern data slightly for variation
- Perfect coherence (1.0)
- Super fast (~10ms)

### Traditional (Random)
```bash
# No special flags
{"entity": "cart", "count": 10}
```
- Uses Faker library for random data
- No coherence guarantee
- Very fast (<5ms)

### LLM (Intelligent)
```bash
{"hints": ["coherent"], "context": "..."}
```
- Claude AI generates realistic data
- High coherence (0.7-0.9)
- Slow (~20s)

---

## 🛠 Troubleshooting

**RAG tests return Traditional path?**
```bash
# Check Weaviate is running
curl http://localhost:8080/v1/.well-known/ready

# Verify patterns exist
curl -s 'http://localhost:8080/v1/objects?class=TestDataPattern' | jq '.objects | length'

# Re-seed if needed
WEAVIATE_URL=http://localhost:8080 python -m test_data_agent.scripts.seed_rag
```

**Service errors?**
```bash
# Check health
curl http://localhost:8091/health | jq

# View logs
tail -50 /tmp/test_data_agent.log
```

---

## 📚 Full Documentation

- **LLM_RAG_TESTS.md** - 29 comprehensive tests (Tests 11-21 for RAG)
- **TESTING_GUIDE.md** - General testing guide
- **Quick script:** `/tmp/test_rag.sh`

---

## ✅ Summary

**RAG is now configured and ready!**

- Path: ✅ Working (verified with test)
- Speed: ✅ 9.59ms (super fast!)
- Coherence: ✅ 1.0 (perfect!)
- Patterns: ✅ 10 test + 10 defect + 4 production

**Next Steps:**
1. Run: `bash /tmp/test_rag.sh` for automated tests
2. Try defect triggering for edge cases
3. Test hybrid path (RAG + LLM) for best quality
4. Compare performance with Traditional path

**Happy testing!** 🚀

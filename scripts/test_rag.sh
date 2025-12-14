#!/bin/bash

echo "========================================="
echo "RAG Path Testing"
echo "========================================="
echo ""

# Test 1: Basic RAG
echo "Test 1: RAG Cart Generation (Historical Patterns)"
echo "Expected: ~30ms, coherence 1.0"
echo "-----------------------------------------"
grpcurl -plaintext -d '{
  "request_id": "rag-test-1",
  "entity": "cart",
  "count": 5,
  "learn_from_history": true
}' localhost:9091 testdata.v1.TestDataService/GenerateData 2>&1 | jq -r 'if .success then "✅ SUCCESS - Path: \(.metadata.generation_path) | Time: \(.metadata.generation_time_ms)ms | Coherence: \(.metadata.coherence_score)" else "❌ FAILED - \(.error)" end'
echo ""

# Test 2: RAG Defects
echo "Test 2: RAG Defect Triggering (Edge Cases)"
echo "Expected: ~30ms, edge case data"
echo "-----------------------------------------"
grpcurl -plaintext -d '{
  "request_id": "rag-test-2",
  "entity": "order",
  "count": 3,
  "defect_triggering": true
}' localhost:9091 testdata.v1.TestDataService/GenerateData 2>&1 | jq -r 'if .success then "✅ SUCCESS - Path: \(.metadata.generation_path) | Time: \(.metadata.generation_time_ms)ms" else "❌ FAILED - \(.error)" end'
echo ""

# Test 3: RAG Users
echo "Test 3: RAG User Generation"
echo "Expected: ~30ms, pattern-based users"
echo "-----------------------------------------"
grpcurl -plaintext -d '{
  "request_id": "rag-test-3",
  "entity": "user",
  "count": 10,
  "learn_from_history": true
}' localhost:9091 testdata.v1.TestDataService/GenerateData 2>&1 | jq -r 'if .success then "✅ SUCCESS - Path: \(.metadata.generation_path) | Time: \(.metadata.generation_time_ms)ms" else "❌ FAILED - \(.error)" end'
echo ""

# Test 4: RAG Products
echo "Test 4: RAG Product Generation"
echo "Expected: ~30ms, pattern-based products"
echo "-----------------------------------------"
grpcurl -plaintext -d '{
  "request_id": "rag-test-4",
  "entity": "product",
  "count": 10,
  "learn_from_history": true
}' localhost:9091 testdata.v1.TestDataService/GenerateData 2>&1 | jq -r 'if .success then "✅ SUCCESS - Path: \(.metadata.generation_path) | Time: \(.metadata.generation_time_ms)ms" else "❌ FAILED - \(.error)" end'
echo ""

echo "========================================="
echo "RAG tests complete!"
echo "========================================="

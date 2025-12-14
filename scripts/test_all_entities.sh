#!/bin/bash

echo "Testing all 6 entity schemas..."
echo ""

# Test cart
echo "========================================="
echo "1. Testing CART"
echo "========================================="
grpcurl -plaintext -d '{"request_id":"test-cart","domain":"ecommerce","entity":"cart","count":3}' localhost:9091 testdata.v1.TestDataService/GenerateData 2>&1 | jq -r 'if .success then "✅ SUCCESS - Path: \(.metadata.generation_path) | Records: \(.record_count)" else "❌ FAILED - \(.error)" end'
echo ""

# Test order
echo "========================================="
echo "2. Testing ORDER"
echo "========================================="
grpcurl -plaintext -d '{"request_id":"test-order","domain":"ecommerce","entity":"order","count":3}' localhost:9091 testdata.v1.TestDataService/GenerateData 2>&1 | jq -r 'if .success then "✅ SUCCESS - Path: \(.metadata.generation_path) | Records: \(.record_count)" else "❌ FAILED - \(.error)" end'
echo ""

# Test payment
echo "========================================="
echo "3. Testing PAYMENT"
echo "========================================="
grpcurl -plaintext -d '{"request_id":"test-payment","domain":"ecommerce","entity":"payment","count":3}' localhost:9091 testdata.v1.TestDataService/GenerateData 2>&1 | jq -r 'if .success then "✅ SUCCESS - Path: \(.metadata.generation_path) | Records: \(.record_count)" else "❌ FAILED - \(.error)" end'
echo ""

# Test product
echo "========================================="
echo "4. Testing PRODUCT"
echo "========================================="
grpcurl -plaintext -d '{"request_id":"test-product","domain":"ecommerce","entity":"product","count":3}' localhost:9091 testdata.v1.TestDataService/GenerateData 2>&1 | jq -r 'if .success then "✅ SUCCESS - Path: \(.metadata.generation_path) | Records: \(.record_count)" else "❌ FAILED - \(.error)" end'
echo ""

# Test review
echo "========================================="
echo "5. Testing REVIEW"
echo "========================================="
grpcurl -plaintext -d '{"request_id":"test-review","domain":"ecommerce","entity":"review","count":3}' localhost:9091 testdata.v1.TestDataService/GenerateData 2>&1 | jq -r 'if .success then "✅ SUCCESS - Path: \(.metadata.generation_path) | Records: \(.record_count)" else "❌ FAILED - \(.error)" end'
echo ""

# Test user
echo "========================================="
echo "6. Testing USER"
echo "========================================="
grpcurl -plaintext -d '{"request_id":"test-user","domain":"ecommerce","entity":"user","count":3}' localhost:9091 testdata.v1.TestDataService/GenerateData 2>&1 | jq -r 'if .success then "✅ SUCCESS - Path: \(.metadata.generation_path) | Records: \(.record_count)" else "❌ FAILED - \(.error)" end'
echo ""

echo "========================================="
echo "All tests complete!"
echo "========================================="

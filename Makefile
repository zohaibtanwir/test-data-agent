.PHONY: help proto run test lint format docker-build docker-run clean install seed-rag perf-test e2e-test

help:
	@echo "Available targets:"
	@echo "  install       - Install dependencies"
	@echo "  proto         - Generate Python code from proto files"
	@echo "  run           - Run the service locally"
	@echo "  test          - Run pytest"
	@echo "  lint          - Run ruff and mypy"
	@echo "  format        - Run black formatter"
	@echo "  docker-build  - Build Docker image"
	@echo "  docker-run    - Run Docker container"
	@echo "  seed-rag      - Seed RAG collections with initial data"
	@echo "  perf-test     - Run performance tests"
	@echo "  e2e-test      - Run end-to-end tests"
	@echo "  clean         - Remove generated files"

install:
	pip install -e ".[dev]"

proto:
	mkdir -p src/test_data_agent/proto
	python -m grpc_tools.protoc \
		-I./protos \
		--python_out=./src/test_data_agent/proto \
		--grpc_python_out=./src/test_data_agent/proto \
		--pyi_out=./src/test_data_agent/proto \
		./protos/test_data.proto
	@echo "Proto files generated successfully"

run:
	python -m test_data_agent.main

test:
	pytest

lint:
	ruff check src/ tests/
	mypy src/

format:
	black src/ tests/

docker-build:
	docker build -t test-data-agent:latest .

docker-run:
	docker-compose up

seed-rag:
	python -m test_data_agent.scripts.seed_rag

perf-test:
	pytest tests/performance/ -v

e2e-test:
	pytest tests/e2e/ -v

clean:
	rm -rf build/ dist/ *.egg-info
	rm -rf src/test_data_agent/proto/*_pb2.py src/test_data_agent/proto/*_pb2_grpc.py src/test_data_agent/proto/*_pb2.pyi
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache htmlcov .coverage

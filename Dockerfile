# Test Data Agent Dockerfile
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY pyproject.toml ./
COPY README.md ./
COPY protos ./protos/
COPY src ./src/

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -e .

# Generate proto files
RUN python -m grpc_tools.protoc \
    -I./protos \
    --python_out=./src/test_data_agent/proto \
    --grpc_python_out=./src/test_data_agent/proto \
    --pyi_out=./src/test_data_agent/proto \
    ./protos/test_data.proto

# Fix proto imports
RUN sed -i 's/import test_data_pb2/from test_data_agent.proto import test_data_pb2/g' \
    ./src/test_data_agent/proto/test_data_pb2_grpc.py

# Create non-root user
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

USER appuser

# Expose ports
EXPOSE 9091 8091

# Health check - uses HTTP_PORT env var (default 8091)
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; import os; urllib.request.urlopen(f'http://localhost:{os.environ.get(\"HTTP_PORT\", \"8091\")}/health/live')" || exit 1

# Run the application
CMD ["python", "-m", "test_data_agent.main"]

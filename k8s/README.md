# Kubernetes Deployment

This directory contains Kubernetes manifests for deploying the Test Data Agent.

## Prerequisites

- Kubernetes cluster (1.24+)
- kubectl configured
- Docker image built and pushed to registry

## Quick Start

### 1. Create Namespace and ServiceAccount

```bash
kubectl apply -f namespace.yaml
kubectl apply -f serviceaccount.yaml
```

### 2. Create ConfigMap

```bash
kubectl apply -f configmap.yaml
```

### 3. Create Secrets

**Option A: Using kubectl (development)**

```bash
kubectl create secret generic test-data-agent-secrets \
  --from-literal=ANTHROPIC_API_KEY="your-api-key-here" \
  --namespace=test-data-agent
```

**Option B: Using secrets.yaml (replace placeholders first)**

```bash
# Edit secrets.yaml with real values
kubectl apply -f secrets.yaml
```

**Option C: Using .env file**

```bash
kubectl create secret generic test-data-agent-secrets \
  --from-env-file=../.env.production \
  --namespace=test-data-agent
```

### 4. Deploy Application

```bash
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
```

### 5. Enable Autoscaling

```bash
kubectl apply -f hpa.yaml
```

## Verify Deployment

```bash
# Check pods
kubectl get pods -n test-data-agent

# Check service
kubectl get svc -n test-data-agent

# Check logs
kubectl logs -n test-data-agent -l app=test-data-agent --tail=100

# Check health
kubectl port-forward -n test-data-agent svc/test-data-agent 8091:8091
curl http://localhost:8091/health
```

## Access the Service

### From within the cluster

```
grpc://test-data-agent.test-data-agent.svc.cluster.local:9091
http://test-data-agent.test-data-agent.svc.cluster.local:8091
```

### From outside the cluster (port-forward)

```bash
# gRPC
kubectl port-forward -n test-data-agent svc/test-data-agent 9091:9091

# HTTP
kubectl port-forward -n test-data-agent svc/test-data-agent 8091:8091
```

## Scaling

### Manual scaling

```bash
kubectl scale deployment test-data-agent --replicas=5 -n test-data-agent
```

### Autoscaling (HPA)

The HPA is configured to:
- Min replicas: 2
- Max replicas: 10
- Target CPU: 70%
- Target Memory: 80%

Monitor autoscaling:

```bash
kubectl get hpa -n test-data-agent --watch
```

## Monitoring

### Prometheus Metrics

The service exposes Prometheus metrics at:

```
http://test-data-agent:8091/metrics
```

Add to Prometheus scrape config:

```yaml
- job_name: 'test-data-agent'
  kubernetes_sd_configs:
  - role: pod
    namespaces:
      names:
      - test-data-agent
  relabel_configs:
  - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
    action: keep
    regex: true
  - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_path]
    action: replace
    target_label: __metrics_path__
    regex: (.+)
  - source_labels: [__address__, __meta_kubernetes_pod_annotation_prometheus_io_port]
    action: replace
    regex: ([^:]+)(?::\d+)?;(\d+)
    replacement: $1:$2
    target_label: __address__
```

### OpenTelemetry Traces

Traces are exported to the OTLP endpoint configured in ConfigMap:

```
http://otel-collector:4317
```

## Dependencies

The service depends on:

- **Redis** (required for caching)
- **Weaviate** (required for RAG)
- **OpenTelemetry Collector** (optional, for tracing)

Deploy dependencies in the same namespace or configure URLs in ConfigMap.

## Troubleshooting

### Pods not starting

```bash
kubectl describe pod -n test-data-agent <pod-name>
kubectl logs -n test-data-agent <pod-name>
```

### Service not accessible

```bash
kubectl get endpoints -n test-data-agent test-data-agent
kubectl describe svc -n test-data-agent test-data-agent
```

### Health check failing

```bash
kubectl port-forward -n test-data-agent <pod-name> 8091:8091
curl http://localhost:8091/health/live
curl http://localhost:8091/health/ready
```

### High resource usage

```bash
kubectl top pods -n test-data-agent
kubectl describe hpa -n test-data-agent test-data-agent
```

## Production Considerations

1. **Secrets Management**
   - Use external secrets operator or sealed secrets
   - Never commit actual secrets to Git

2. **Resource Limits**
   - Adjust based on actual usage
   - Monitor and tune over time

3. **High Availability**
   - Run minimum 2 replicas
   - Use pod anti-affinity for distribution

4. **Networking**
   - Consider using Ingress or Gateway for external access
   - Use NetworkPolicies to restrict traffic

5. **Monitoring**
   - Set up alerts for pod failures
   - Monitor gRPC and HTTP latency
   - Track autoscaling events

6. **Updates**
   - Use rolling updates (default)
   - Test in staging first
   - Have rollback plan ready

## Clean Up

```bash
kubectl delete -f .
kubectl delete namespace test-data-agent
```

# hep_programming Package

This package provides an MCP (Model Context Protocol) server for HEP programming hints.

## Structure

- `__init__.py` - Package initialization, exports the FastMCP app
- `server.py` - MCP server implementation with tools for accessing HEP programming hints

## Helm Deployment

The application can be deployed to Kubernetes using the Helm chart located in the `helm/hep-programming-hints/` directory.

### Installation

```bash
helm install hep-programming-hints ./helm/hep-programming-hints/
```

### Configuration

The following table lists the configurable parameters in `values.yaml`:

| Parameter | Description | Default |
|-----------|-------------|---------|
| `replicaCount` | Number of replicas to deploy | `1` |
| `image.repository` | Container image repository | `sslhep/hep-programming-hints` |
| `image.pullPolicy` | Image pull policy | `IfNotPresent` |
| `image.tag` | Container image tag | `dev` |
| `nameOverride` | Override the chart name | `""` |
| `fullnameOverride` | Override the full resource names | `""` |
| `podAnnotations` | Annotations to add to pods | `{}` |
| `podSecurityContext` | Security context for pods | `{}` |
| `securityContext` | Security context for containers | `{}` |
| `service.type` | Kubernetes service type | `ClusterIP` |
| `service.port` | Service port | `8080` |
| `ingress.enabled` | Enable ingress resource | `true` |
| `ingress.className` | Ingress class name | `""` |
| `ingress.annotations` | Ingress annotations | `{}` |
| `ingress.hosts` | Ingress host configuration | `[{host: hep-programming-hints.local, paths: [{path: /, pathType: Prefix}]}]` |
| `ingress.tls` | Ingress TLS configuration | `[]` |
| `resources` | CPU/Memory resource requests/limits | `{}` |
| `autoscaling.enabled` | Enable horizontal pod autoscaling | `false` |
| `autoscaling.minReplicas` | Minimum number of replicas | `1` |
| `autoscaling.maxReplicas` | Maximum number of replicas | `100` |
| `autoscaling.targetCPUUtilizationPercentage` | Target CPU utilization for autoscaling | `80` |
| `nodeSelector` | Node labels for pod assignment | `{}` |
| `tolerations` | Pod tolerations | `[]` |
| `affinity` | Pod affinity rules | `{}` |
| `secret.token` | Authentication token (stored as secret) | `""` |

### Example: Custom Installation

```bash
helm install hep-programming-hints ./helm/hep-programming-hints/ \
  --set image.tag=latest \
  --set replicaCount=3 \
  --set ingress.hosts[0].host=hints.example.com
```

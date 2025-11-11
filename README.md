# hep-programming-hints

An MCP (Model Context Protocol) server implementation that provides programming hints and guidance to help LLMs write code using IRIS-HEP tools for High Energy Physics analysis.

## Overview

This MCP server provides:
- Context and hints for various HEP libraries (awkward, hist, ServiceX, vector, xAOD, etc.)
- Custom agents for specialized tasks (e.g., plot generation)
- Example analysis scripts demonstrating best practices
- Helper utilities for xAOD analysis with func_adl

## What is MCP?

Model Context Protocol (MCP) is a standard for providing contextual information to Large Language Models. This server implements MCP to give LLMs access to domain-specific knowledge about High Energy Physics programming libraries and workflows.

## MCP Tools

The server provides the following tools:

1. **hep_coding_guidelines()** - Get general guidelines on using these hints to generate plots.

2. **get_hint(library: str)** - Get programming hints for a specific HEP library
   - Supports: awkward, hist, servicex, vector, xaod, and more
   
3. **list_available_hints()** - List all available hint files
   
4. **search_hints(keyword: str)** - Search for keywords across all hint files

## Auth
There is nothing sensitive about this server, but to avoid potential abuse, it is 
configured to require a bearer token password for access. The server expects this
token to be available in an environment variable called `TOKEN`


## Running the Server
This server is implemented using 
the [FastMCP framework](https://gofastmcp.com/getting-started/welcome). 

For local development and testing it can be run from bash as:
```bash
TOKEN="luckypass" uv run ./hep_programming/server.py
```
A Dockerfile is included for this server. When built, the docker image exposes port 8080
and expects the same TOKEN environment variable.

You can run the server with 
```bash
docker build -t hep-programming .
docker run -p 8080:8080 -e TOKEN="luckypass" hep-programming
```

## Using with MCP Clients

Add to your MCP client configuration (e.g., Claude Desktop):

```json
{
  "mcpServers": {
    "hep_programming": {
      "type": "http",
      "url": "http://localhost:8080/mcp",
      "headers": {
        "Authorization": "Bearer luckypass"
      }

    }
  }
}
```

Verify the configuration with 

```bash
% claude mcp list
Checking MCP server health...

hep_programming: http://localhost:8080/mcp (HTTP) - ✓ Connected
```

## MCP Server Features

### Hint Files

The server provides access to comprehensive hint files located in the `hints/` directory:
- `awkward-hints.md` - Working with awkward arrays
- `hist-hints.md` - Creating histograms
- `servicex-hints.md` - Using ServiceX for data delivery
- `vector-hints.md` - Physics vector operations
- `xaod-hints.md` - xAOD analysis with func_adl
- And more...

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

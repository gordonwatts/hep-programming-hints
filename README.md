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

## Prerequisites

- Python 3.10 or higher
- [uv](https://github.com/astral-sh/uv) package manager (recommended)
- An MCP-compatible client (e.g., Claude Desktop, Claude Code, or other MCP clients)
- Docker (optional, for containerized deployment)

## Installation

### Option 1: Docker (Recommended for Production)

The easiest way to run the MCP server is using Docker:

1. Build the Docker image:
   ```bash
   docker build -t hep-programming-hints .
   ```

2. Run the container with your authentication token:
   ```bash
   docker run -d \
     -p 8080:8080 \
     -e TOKEN="your-secret-token-here" \
     --name hep-hints-server \
     hep-programming-hints
   ```

3. Verify the server is running:
   ```bash
   curl http://localhost:8080/health
   ```

**Note:** The `TOKEN` environment variable is required for server authentication. Generate a secure token and keep it secret.

### Option 2: Local Installation

#### MCP Server Setup

The MCP server itself only requires fastMCP and does not need the HEP analysis libraries installed.

#### Using uv (recommended)

1. Install uv if you haven't already:
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. Clone the repository:
   ```bash
   git clone <repository-url>
   cd hep-programming-hints
   ```

3. Create a virtual environment and install the MCP server:
   ```bash
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   uv pip install -e .
   ```

#### Using pip

Alternatively, you can use standard pip:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e .
```

### Analysis Environment Setup (Optional)

To run the example analysis scripts (`jet_pt_plot.py`), you'll need a separate environment with the HEP analysis libraries. The `config.json` file specifies these dependencies:

```bash
# Create a separate environment for analysis
uv venv hep_venv
source hep_venv/bin/activate

# Install HEP analysis libraries
uv pip install servicex func-adl-servicex-xaodr25 hist awkward vector \
    matplotlib mplhep servicex-analysis-utils jinja2 numpy uproot \
    dask dask-awkward
```

Or use the existing `hep_venv` directory if already configured.

## Running the MCP Server

### Using Docker

See the Docker installation section above for running the server in a container.

### Using MCP Client Configuration

The MCP server is configured via the `config.json` file. To use it with an MCP client:

1. Reference this project in your MCP client configuration
2. The server will provide access to:
   - Hint files for HEP libraries
   - Custom agents (e.g., `generate-plot`)
   - Configuration for the Python environment with required analysis dependencies

### Example: Using with Claude Desktop

Add to your Claude Desktop MCP configuration:
```json
{
  "mcpServers": {
    "hep-hints": {
      "command": "uv",
      "args": ["--directory", "/path/to/hep-programming-hints", "run", "fastmcp", "run", "config.json"],
      "env": {}
    }
  }
}
```

Or if using a standard Python installation:
```json
{
  "mcpServers": {
    "hep-hints": {
      "command": "/path/to/hep-programming-hints/.venv/bin/fastmcp",
      "args": ["run", "/path/to/hep-programming-hints/config.json"],
      "env": {}
    }
  }
}
```

### Running Standalone Server

To run the server directly with HTTP transport:

```bash
# Set the TOKEN environment variable
export TOKEN="your-secret-token-here"

# Run the server
python -m hep_programming.server
```

The server will start on `http://127.0.0.1:8080`.

## Running Example Scripts

The example scripts require the HEP analysis environment (see Analysis Environment Setup above):

```bash
source hep_venv/bin/activate
python jet_pt_plot.py
```

This will:
- Fetch jet data from ServiceX using func_adl queries
- Create a histogram of jet pT using the hist library
- Generate a plot saved as `jet_pt.png`

## MCP Server Features

### Hint Files

The server provides access to comprehensive hint files located in the `hints/` directory:
- `awkward-hints.md` - Working with awkward arrays
- `hist-hints.md` - Creating histograms
- `servicex-hints.md` - Using ServiceX for data delivery
- `vector-hints.md` - Physics vector operations
- `xaod-hints.md` - xAOD analysis with func_adl
- And more...

### Custom Agents

The `generate-plot` agent helps create physics plots from ATLAS data with proper styling and best practices.

### Python Environment Configuration

The `config.json` specifies the analysis environment requirements:
- servicex - Data delivery service
- func-adl-servicex-xaodr25 - func_adl backend for xAOD
- awkward - Jagged array operations
- hist - Histogram creation
- vector - Lorentz vector operations
- matplotlib & mplhep - Plotting
- And more...

These libraries are **not** required for the MCP server itself, only for running the actual analysis code.

## Docker Configuration

### Environment Variables

- `TOKEN` (required): Authentication token for accessing the MCP server

### Ports

- `8080`: HTTP server port

### Building Custom Images

You can customize the Dockerfile to:
- Use different Python versions (change the base image)
- Add additional dependencies
- Modify server configuration

Example with custom token during build:
```bash
docker build --build-arg DEFAULT_TOKEN=your-token -t hep-programming-hints .
```

### Docker Compose

For easier deployment, you can use Docker Compose:

```yaml
version: '3.8'

services:
  hep-hints:
    build: .
    ports:
      - "8080:8080"
    environment:
      - TOKEN=${TOKEN}
    restart: unless-stopped
```

Run with:
```bash
TOKEN=your-secret-token docker-compose up -d
```

## Project Structure

```
.
├── hints/              # Markdown hint files for various libraries
├── prompts/            # Prompt templates for custom agents
├── hep_programming/    # MCP server implementation
│   ├── __init__.py
│   ├── server.py       # Main server code
│   └── README.md
├── Dockerfile          # Docker configuration
├── config.json         # MCP server configuration
├── pyproject.toml      # MCP server dependencies (fastMCP only)
├── jet_pt_plot.py      # Example analysis script
├── xaod_hints.py       # Helper utilities for xAOD analysis
└── hep_venv/           # Optional: Separate analysis environment
```

## Development

To install development dependencies for the MCP server:

```bash
uv pip install -e ".[dev]"
```

## Verification

### Verify MCP Server Installation

```bash
fastmcp --version
```

### Verify Docker Deployment

```bash
# Check if container is running
docker ps | grep hep-hints

# Check logs
docker logs hep-hints-server

# Test health endpoint
curl http://localhost:8080/health
```

### Verify Analysis Environment (if installed)

```bash
source hep_venv/bin/activate

# Check ServiceX CLI
servicex codegen list

# Test Python imports
python -c "import awkward, matplotlib.pyplot, numpy, servicex, func_adl_servicex_xaodr25; print('All core dependencies imported successfully')"
```

## Security Notes

- **Always use a strong, randomly generated TOKEN** for production deployments
- Never commit tokens to version control
- Consider using Docker secrets or environment variable management tools for production
- The server runs on HTTP by default; for production use, consider adding TLS/HTTPS via a reverse proxy

## Contributing

Contributions are welcome! When adding new hint files or updating dependencies:
1. Add hint files to the `hints/` directory
2. Update `config.json` to reference new hints
3. Update `pyproject.toml` only for MCP server dependencies
4. Analysis library requirements should be documented in `config.json`
5. Use `uv` to manage dependencies
6. Test Docker builds with `docker build -t hep-programming-hints .`

## License

BSD 3-Clause License

# hep_programming Package

This package provides an MCP (Model Context Protocol) server for HEP programming hints.

## Structure

- `__init__.py` - Package initialization, exports the FastMCP app
- `server.py` - MCP server implementation with tools for accessing HEP programming hints

## MCP Tools

The server provides the following tools:

1. **get_hint(library: str)** - Get programming hints for a specific HEP library
   - Supports: awkward, hist, servicex, vector, xaod, and more
   
2. **list_available_hints()** - List all available hint files

3. **get_plan(task_type: str)** - Get planning guides for specific tasks
   - Supports: plot, awkward, hist, servicex
   
4. **search_hints(keyword: str)** - Search for keywords across all hint files

## Running the Server

```bash
# Using the installed script
hep-programming-server

# Or directly with Python
python -m hep_programming.server

# Or programmatically
from hep_programming import app
app.run()
```

## Using with MCP Clients

Add to your MCP client configuration (e.g., Claude Desktop):

```json
{
  "mcpServers": {
    "hep-hints": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/hep-programming-hints",
        "run",
        "hep-programming-server"
      ]
    }
  }
}
```

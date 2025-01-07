# MCP Server for Milvus

A Model Context Protocol (MCP) server that provides access to Milvus vector database functionality.

## Installation

```bash
pip install uv  # If you don't have uv installed
pip install -e .  # Install in development mode
```

## Usage with Claude Desktop

1. Install Claude Desktop from https://claude.ai/download
2. Open your Claude Desktop configuration:
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`

3. Add the following configuration:
```json
{
  "mcpServers": {
    "milvus": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/mcp-server-milvus/src/mcp_server_milvus",
        "run",
        "server.py",
        "--milvus-uri",
        "http://localhost:19530"
      ]
    }
  }
}
```

4. Restart Claude Desktop

## Available Tools

The server provides the following tools:
- `milvus-text-search`: Search for documents using full text search
- `milvus-list-collections`: List all collections in the database
- `milvus-collection-info`: Get detailed information about a collection
- `milvus-query`: Query collection using filter expressions
- `milvus-count`: Count entities in a collection

## Environment Variables

- `MILVUS_URI`: Milvus server URI (can be set instead of --milvus-uri)
- `MILVUS_TOKEN`: Optional authentication token
- `MILVUS_DB`: Database name (defaults to "default")

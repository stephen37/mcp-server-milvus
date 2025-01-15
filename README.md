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
      "command": "/PATH/TO/uv",
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
  - Parameters:
    - `collection_name`: Name of collection to search
    - `query_text`: Text to search for
    - `limit`: Maximum results (default: 5)
    - `output_fields`: Fields to include in results
    - `drop_ratio`: Proportion of low-frequency terms to ignore (0.0-1.0)

- `milvus-list-collections`: List all collections in the database

- `milvus-collection-info`: Get detailed information about a collection
  - Parameters:
    - `collection_name`: Name of the collection

- `milvus-query`: Query collection using filter expressions
  - Parameters:
    - `collection_name`: Name of collection to query
    - `filter_expr`: Filter expression (e.g. 'age > 20')
    - `output_fields`: Fields to include in results
    - `limit`: Maximum results (default: 10)

- `milvus-count`: Count entities in a collection
  - Parameters:
    - `collection_name`: Name of the collection
    - `filter_expr`: Optional filter expression

## Environment Variables

- `MILVUS_URI`: Milvus server URI (can be set instead of --milvus-uri)
- `MILVUS_TOKEN`: Optional authentication token
- `MILVUS_DB`: Database name (defaults to "default")

## Development

To run the server directly:

```bash
uv run server.py --milvus-uri http://localhost:19530
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

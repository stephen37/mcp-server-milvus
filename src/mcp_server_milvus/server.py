from typing import Optional, List
from pymilvus import MilvusClient
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.types as types
import click
import asyncio
import mcp

class MilvusConnector:
    def __init__(
        self,
        uri: str,
        token: Optional[str] = None,
        db_name: Optional[str] = "default"
    ):
        self.client = MilvusClient(
            uri=uri,
            token=token,
            db_name=db_name
        )

    async def list_collections(self) -> List[str]:
        """List all collections in the database."""
        try:
            return self.client.list_collections()
        except Exception as e:
            raise ValueError(f"Failed to list collections: {str(e)}")

    async def get_collection_info(self, collection_name: str) -> dict:
        """Get detailed information about a collection."""
        try:
            return self.client.describe_collection(collection_name)
        except Exception as e:
            raise ValueError(f"Failed to get collection info: {str(e)}")

    async def search_collection(
        self,
        collection_name: str,
        query_text: str,
        limit: int = 5,
        output_fields: Optional[List[str]] = None,
        drop_ratio: float = 0.2
    ) -> List[dict]:
        """
        Perform full text search on a collection.
        
        Args:
            collection_name: Name of collection to search
            query_text: Text to search for
            limit: Maximum number of results
            output_fields: Fields to return in results
            drop_ratio: Proportion of low-frequency terms to ignore (0.0-1.0)
        """
        try:
            search_params = {
                'params': {'drop_ratio_search': drop_ratio}
            }

            results = self.client.search(
                collection_name=collection_name,
                data=[query_text],
                anns_field='sparse',
                limit=limit,
                output_fields=output_fields,
                search_params=search_params
            )
            return results
        except Exception as e:
            raise ValueError(f"Search failed: {str(e)}")

    async def query_collection(
        self,
        collection_name: str,
        filter_expr: str,
        output_fields: Optional[List[str]] = None,
        limit: int = 10
    ) -> List[dict]:
        """Query collection using filter expressions."""
        try:
            return self.client.query(
                collection_name=collection_name,
                filter=filter_expr,
                output_fields=output_fields,
                limit=limit
            )
        except Exception as e:
            raise ValueError(f"Query failed: {str(e)}")

    async def count_entities(self, collection_name: str, filter_expr: Optional[str] = None) -> int:
        """Count entities in a collection, optionally filtered."""
        try:
            return self.client.count(collection_name, filter=filter_expr)
        except Exception as e:
            raise ValueError(f"Count failed: {str(e)}")

def serve(
    milvus_uri: str,
    milvus_token: Optional[str] = None,
    db_name: Optional[str] = "default"
) -> Server:
    """
    Create and configure the MCP server with Milvus tools.
    
    Args:
        milvus_uri: URI for Milvus server
        milvus_token: Optional auth token
        db_name: Database name to use
    """
    server = Server("milvus")
    milvus = MilvusConnector(milvus_uri, milvus_token, db_name)

    @server.list_tools()
    async def list_tools() -> List[types.Tool]:
        return [
            types.Tool(
                name="milvus-text-search",
                description="Search for documents using full text search in a Milvus collection",
                inputSchema={
                    "type": "object", 
                    "properties": {
                        "collection_name": {
                            "type": "string",
                            "description": "Name of the collection to search"
                        },
                        "query_text": {
                            "type": "string",
                            "description": "Text to search for"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of results to return",
                            "default": 5
                        },
                        "output_fields": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Fields to include in results",
                            "default": None
                        },
                        "drop_ratio": {
                            "type": "number",
                            "description": "Proportion of low-frequency terms to ignore (0.0-1.0)",
                            "default": 0.2
                        }
                    },
                    "required": ["collection_name", "query_text"]
                }
            ),
            types.Tool(
                name="milvus-list-collections",
                description="List all collections in the database",
                inputSchema={
                    "type": "object",
                    "properties": {}
                }
            ),
            types.Tool(
                name="milvus-collection-info",
                description="Get detailed information about a collection",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "collection_name": {
                            "type": "string",
                            "description": "Name of the collection"
                        }
                    },
                    "required": ["collection_name"]
                }
            ),
            types.Tool(
                name="milvus-query",
                description="Query collection using filter expressions",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "collection_name": {
                            "type": "string",
                            "description": "Name of the collection to query"
                        },
                        "filter_expr": {
                            "type": "string",
                            "description": "Filter expression (e.g. 'age > 20')"
                        },
                        "output_fields": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Fields to include in results"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of results",
                            "default": 10
                        }
                    },
                    "required": ["collection_name", "filter_expr"]
                }
            ),
            types.Tool(
                name="milvus-count",
                description="Count entities in a collection",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "collection_name": {
                            "type": "string",
                            "description": "Name of the collection"
                        },
                        "filter_expr": {
                            "type": "string",
                            "description": "Optional filter expression"
                        }
                    },
                    "required": ["collection_name"]
                }
            )
        ]

    @server.call_tool()
    async def call_tool(
        name: str,
        arguments: dict
    ) -> List[types.TextContent | types.ImageContent | types.EmbeddedResource]:
        if name == "milvus-text-search":
            collection_name = arguments["collection_name"]
            query_text = arguments["query_text"]
            limit = arguments.get("limit", 5)
            output_fields = arguments.get("output_fields")
            drop_ratio = arguments.get("drop_ratio", 0.2)

            results = await milvus.search_collection(
                collection_name=collection_name,
                query_text=query_text,
                limit=limit,
                output_fields=output_fields,
                drop_ratio=drop_ratio
            )

            content = [
                types.TextContent(
                    type="text",
                    text=f"Search results for '{query_text}' in collection '{collection_name}':"
                )
            ]
            
            for result in results:
                content.append(
                    types.TextContent(
                        type="text",
                        text=f"<r>{str(result)}<r>"
                    )
                )
            
            return content

        elif name == "milvus-list-collections":
            collections = await milvus.list_collections()
            return [
                types.TextContent(
                    type="text",
                    text=f"Collections in database:\n{', '.join(collections)}"
                )
            ]

        elif name == "milvus-collection-info":
            collection_name = arguments["collection_name"]
            info = await milvus.get_collection_info(collection_name)
            return [
                types.TextContent(
                    type="text",
                    text=f"Collection info for '{collection_name}':\n{str(info)}"
                )
            ]

        elif name == "milvus-query":
            collection_name = arguments["collection_name"]
            filter_expr = arguments["filter_expr"]
            output_fields = arguments.get("output_fields")
            limit = arguments.get("limit", 10)

            results = await milvus.query_collection(
                collection_name=collection_name,
                filter_expr=filter_expr,
                output_fields=output_fields,
                limit=limit
            )

            content = [
                types.TextContent(
                    type="text",
                    text=f"Query results for '{filter_expr}' in collection '{collection_name}':"
                )
            ]
            
            for result in results:
                content.append(
                    types.TextContent(
                        type="text",
                        text=f"<r>{str(result)}<r>"
                    )
                )
            
            return content

        elif name == "milvus-count":
            collection_name = arguments["collection_name"]
            filter_expr = arguments.get("filter_expr")
            count = await milvus.count_entities(collection_name, filter_expr)
            msg = f"Count for collection '{collection_name}'"
            if filter_expr:
                msg += f" with filter '{filter_expr}'"
            msg += f": {count}"
            return [types.TextContent(type="text", text=msg)]

    return server

@click.command()
@click.option(
    "--milvus-uri",
    envvar="MILVUS_URI",
    required=True,
    help="Milvus server URI"
)
@click.option(
    "--milvus-token",
    envvar="MILVUS_TOKEN",
    required=False,
    help="Milvus authentication token"
)
@click.option(
    "--db-name",
    envvar="MILVUS_DB",
    default="default",
    help="Milvus database name"
)
def main(
    milvus_uri: str,
    milvus_token: Optional[str],
    db_name: str
):
    async def _run():
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            server = serve(
                milvus_uri,
                milvus_token,
                db_name
            )
            await server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="milvus",
                    server_version="0.1.0",
                    capabilities=server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    ),
                ),
            )

    asyncio.run(_run())

if __name__ == "__main__":
    main()
from fastmcp import FastMCP
from typing import Dict, Any, List, Optional
import os
import dotenv
import datetime
import tools as arango_tools
from tools.db_connection import db, mcp as base_mcp

dotenv.load_dotenv()

mcp = FastMCP(name="arango-knowledge-base", port=22000, host="0.0.0.0")

mcp.add_tool(arango_tools.add_temporal_metadata)
mcp.add_tool(arango_tools.arango_query)
mcp.add_tool(arango_tools.arango_insert)
mcp.add_tool(arango_tools.arango_update)
mcp.add_tool(arango_tools.arango_remove)
mcp.add_tool(arango_tools.arango_get_document)
mcp.add_tool(arango_tools.arango_truncate_collection)
mcp.add_tool(arango_tools.arango_list_collections)
mcp.add_tool(arango_tools.arango_create_collection)
mcp.add_tool(arango_tools.arango_create_edge)
mcp.add_tool(arango_tools.arango_create_sequential_relationship)
mcp.add_tool(arango_tools.arango_query_edges)
mcp.add_tool(arango_tools.arango_traverse_graph)
mcp.add_tool(arango_tools.arango_temporal_traverse)
mcp.add_tool(arango_tools.arango_time_series_analysis)
mcp.add_tool(arango_tools.arango_query_by_time_range)
mcp.add_tool(arango_tools.arango_query_valid_at)
mcp.add_tool(arango_tools.arango_set_validity_period)
mcp.add_tool(arango_tools.arango_create_index)
mcp.add_tool(arango_tools.arango_list_indexes)
mcp.add_tool(arango_tools.arango_create_temporal_indexes)
mcp.add_tool(arango_tools.arango_backup)
mcp.add_tool(arango_tools.arango_get_metadata)

# Image/Asset management tools
# Setting FASTMCP_ALLOW_ARBITRARY_TYPES=1 environment variable will be needed
mcp.add_tool(arango_tools.arango_upload_image)
mcp.add_tool(arango_tools.arango_get_image)
mcp.add_tool(arango_tools.arango_list_images)
mcp.add_tool(arango_tools.arango_delete_image)
mcp.add_tool(arango_tools.arango_update_image_metadata)

if __name__ == "__main__":
    import asyncio
    asyncio.run(mcp.run(transport='sse', host="0.0.0.0"))
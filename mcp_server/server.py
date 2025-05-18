from fastmcp import FastMCP
from typing import Dict, Any, List, Optional
import os
from arango import ArangoClient
import dotenv
import datetime
import tools as arango_tools

dotenv.load_dotenv()

# Get environment variables or use defaults
ARANGO_URL = os.environ.get("ARANGO_URL")
ARANGO_DB = os.environ.get("ARANGO_DB")
ARANGO_USERNAME = os.environ.get("ARANGO_USERNAME")
ARANGO_PASSWORD = os.environ.get("ARANGO_PASSWORD")

mcp = FastMCP("ArangoDB Server 🔗", port=22000)

# Initialize ArangoDB client
client = ArangoClient(hosts=ARANGO_URL)
db = client.db(ARANGO_DB, username=ARANGO_USERNAME, password=ARANGO_PASSWORD)

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

# Image/Asset management tools
# Setting FASTMCP_ALLOW_ARBITRARY_TYPES=1 environment variable will be needed
mcp.add_tool(arango_tools.arango_upload_image)
mcp.add_tool(arango_tools.arango_get_image)
mcp.add_tool(arango_tools.arango_list_images)
mcp.add_tool(arango_tools.arango_delete_image)
mcp.add_tool(arango_tools.arango_update_image_metadata)

if __name__ == "__main__":
    mcp.run()
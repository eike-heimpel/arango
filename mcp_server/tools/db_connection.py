from arango import ArangoClient
import os
import dotenv
import datetime
from typing import Dict, Any
from fastmcp import FastMCP

dotenv.load_dotenv()

# Initialize FastMCP
mcp = FastMCP(name="arango-knowledge-base")

# Get environment variables or use defaults
ARANGO_URL = os.environ.get("ARANGO_URL", "http://arangodb:8529")
ARANGO_DB = os.environ.get("ARANGO_DB", "knowledge_db").lower() 
ARANGO_USERNAME = os.environ.get("ARANGO_USERNAME") 
ARANGO_PASSWORD = os.environ.get("ARANGO_PASSWORD")

# Initialize ArangoDB client
client = ArangoClient(hosts=ARANGO_URL)
db = client.db(ARANGO_DB, username=ARANGO_USERNAME, password=ARANGO_PASSWORD)

@mcp.tool()
def add_temporal_metadata(document: Dict[str, Any], is_update: bool = False) -> Dict[str, Any]:
    """Add temporal metadata fields to a document.
    
    This utility function adds created_at, updated_at, valid_from, and valid_until fields
    to documents for temporal data management.
    
    Args:
        document: The document to add metadata to
        is_update: Whether this is an update operation
        
    Returns:
        The document with added temporal metadata
    """
    now = datetime.datetime.utcnow().isoformat()
    
    if not is_update:
        document["created_at"] = now
        document["updated_at"] = now
        
        if "valid_from" not in document:
            document["valid_from"] = now
        if "valid_until" not in document:
            document["valid_until"] = None
    else:
        document["updated_at"] = now
    
    return document 
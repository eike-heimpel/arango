import os
import json
from typing import Dict, Any, List, Optional
from .db_connection import db, client, ARANGO_URL, ARANGO_DB, ARANGO_USERNAME, mcp

@mcp.tool()
def arango_backup(output_dir: str, collection: Optional[str] = None, doc_limit: int = 1000) -> Dict[str, Any]:
    """Back up ArangoDB collections to JSON files.
    
    Args:
        output_dir: Directory to store the backup files
        collection: Optional specific collection to back up (backs up all collections if not specified)
        doc_limit: Maximum number of documents to back up per collection
        
    Returns:
        Dictionary with backup summary information
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    collections_to_backup = [collection] if collection else [c['name'] for c in db.collections() if not c['name'].startswith('_')]
    results = {}
    
    for coll_name in collections_to_backup:
        try:
            query = f"FOR doc IN {coll_name} LIMIT {doc_limit} RETURN doc"
            cursor = db.aql.execute(query)
            docs = [doc for doc in cursor]
            
            file_path = os.path.join(output_dir, f"{coll_name}.json")
            with open(file_path, 'w') as f:
                json.dump(docs, f, indent=2)
                
            results[coll_name] = {
                "status": "success",
                "doc_count": len(docs),
                "file_path": file_path
            }
        except Exception as e:
            results[coll_name] = {
                "status": "error",
                "error": str(e)
            }
    
    return {
        "backup_summary": results,
        "collections_backed_up": len(results),
        "output_directory": output_dir
    } 

@mcp.tool()
def arango_get_metadata(random_string: str) -> Dict[str, Any]:
    """Retrieve metadata about the ArangoDB server connection and database
    
    Returns information about the ArangoDB server, database, and collections to provide
    context about the current environment.
    
    Returns:
        Dictionary with server information, database details, and collection list
    """
    # Get ArangoDB version information
    version_info = {"version": "Unknown", "server": "Unknown"}
    
    # Get database info
    system_db = client.db("_system", username=ARANGO_USERNAME, password=os.environ.get("ARANGO_PASSWORD", ""))
    db_info = {}
    
    try:
        if system_db.has_database(ARANGO_DB):
            db_info = {
                "name": ARANGO_DB,
                "exists": True
            }
    except:
        db_info = {
            "name": ARANGO_DB,
            "exists": "Unknown"
        }
    
    # Get collection information
    collections = []
    try:
        collections = [
            {"name": c["name"], "type": c["type"]} 
            for c in db.collections() 
            if not c["name"].startswith("_")
        ]
    except:
        pass
    
    return {
        "server": {
            "url": ARANGO_URL,
            "version": version_info.get("version", "Unknown"),
            "server": version_info.get("server", "Unknown"),
        },
        "database": db_info,
        "collections": {
            "count": len(collections),
            "items": collections
        }
    }
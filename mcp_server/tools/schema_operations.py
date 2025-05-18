from typing import Dict, Any, List
from .db_connection import db, mcp

@mcp.tool()
def arango_create_index(collection: str, fields: List[str], index_type: str = "persistent", unique: bool = False) -> Dict[str, Any]:
    """Create an index on a collection.
    
    Args:
        collection: The name of the collection
        fields: List of fields to include in the index
        index_type: Type of index ('persistent', 'geo', 'fulltext', etc.)
        unique: Whether the index values must be unique
        
    Returns:
        Dictionary with the index creation metadata
    """
    coll = db.collection(collection)
    
    index_data = {
        'type': index_type,
        'fields': fields,
        'unique': unique
    }
    
    if index_type == "geo":
        index_data = {'type': 'geo', 'fields': fields}
    elif index_type == "fulltext":
        index_data = {'type': 'fulltext', 'fields': fields}
    
    return coll.add_index(index_data)

@mcp.tool()
def arango_list_indexes(collection: str) -> List[Dict[str, Any]]:
    """List all indexes in a collection.
    
    Args:
        collection: The name of the collection
        
    Returns:
        List of index definitions
    """
    coll = db.collection(collection)
    return coll.indexes()


@mcp.tool()
def arango_create_temporal_indexes(collection: str) -> Dict[str, Any]:
    """Create standard indexes for temporal data management.
    
    Args:
        collection: The name of the collection
        
    Returns:
        Dictionary with the index creation results
    """
    coll = db.collection(collection)
    results = {}
    
    results["created_at"] = coll.add_index({
        'type': 'persistent', 
        'fields': ['created_at']
    })
    
    results["updated_at"] = coll.add_index({
        'type': 'persistent', 
        'fields': ['updated_at']
    })
    
    results["validity_period"] = coll.add_index({
        'type': 'persistent', 
        'fields': ['valid_from', 'valid_until']
    })
    
    return results 
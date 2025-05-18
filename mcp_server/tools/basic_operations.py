from typing import Dict, Any, List, Optional
from .db_connection import db, add_temporal_metadata, mcp

@mcp.tool()
def arango_query(query: str, bind_vars: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """Execute an AQL query against the ArangoDB database.
    
    Args:
        query: The AQL query string to execute
        bind_vars: Optional dictionary of bind variables for the query
        
    Returns:
        List of documents that match the query
    """
    cursor = db.aql.execute(query, bind_vars=bind_vars or {})
    return [doc for doc in cursor]

@mcp.tool()
def arango_insert(collection: str, document: Dict[str, Any]) -> Dict[str, Any]:
    """Insert a new document into the specified collection.
    
    Args:
        collection: The name of the collection
        document: The document to insert
        
    Returns:
        Dictionary with the document metadata (_id, _key, etc.)
    """
    coll = db.collection(collection)
    document = add_temporal_metadata(document)
    return coll.insert(document)

@mcp.tool()
def arango_update(collection: str, document_key: str, update: Dict[str, Any]) -> Dict[str, Any]:
    """Update an existing document in the specified collection.
    
    Args:
        collection: The name of the collection
        document_key: The key of the document to update
        update: The updates to apply to the document
        
    Returns:
        Dictionary with the update metadata
    """
    coll = db.collection(collection)
    update = add_temporal_metadata(update, is_update=True)
    return coll.update(document_key, update)

@mcp.tool()
def arango_remove(collection: str, document_key: str) -> Dict[str, Any]:
    """Remove a document from the specified collection.
    
    Args:
        collection: The name of the collection
        document_key: The key of the document to remove
        
    Returns:
        Dictionary with the deletion metadata
    """
    coll = db.collection(collection)
    return coll.delete(document_key)

@mcp.tool()
def arango_get_document(collection: str, document_key: str) -> Dict[str, Any]:
    """Retrieve a document by its key from the specified collection.
    
    Args:
        collection: The name of the collection
        document_key: The key of the document to retrieve
        
    Returns:
        The document data if found
    """
    coll = db.collection(collection)
    return coll.get(document_key)

@mcp.tool()
def arango_truncate_collection(collection: str) -> Dict[str, Any]:
    """Remove all documents from a collection while keeping the collection itself.
    
    Args:
        collection: The name of the collection to truncate
        
    Returns:
        Dictionary indicating the operation status
    """
    coll = db.collection(collection)
    coll.truncate()
    return {"collection": collection, "status": "truncated"}

@mcp.tool()
def arango_list_collections() -> List[Dict[str, Any]]:
    """List all collections in the database.
    
    Returns:
        List of collections with their metadata
    """
    return db.collections()

@mcp.tool()
def arango_create_collection(name: str, collection_type: str = "document") -> Dict[str, Any]:
    """Create a new collection in the database.
    
    Args:
        name: The name of the collection to create
        collection_type: The type of collection ("document" or "edge")
        
    Returns:
        Dictionary with the collection creation status
    """
    edge = collection_type.lower() == "edge"
    collection = db.create_collection(name, edge=edge)
    return {
        "name": collection.name,
        "type": "edge" if edge else "document",
        "status": "created"
    } 
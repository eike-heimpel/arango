from typing import Dict, Any, List, Optional
from .db_connection import db, add_temporal_metadata

def arango_query(query: str, bind_vars: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    cursor = db.aql.execute(query, bind_vars=bind_vars or {})
    return [doc for doc in cursor]

def arango_insert(collection: str, document: Dict[str, Any]) -> Dict[str, Any]:
    coll = db.collection(collection)
    document = add_temporal_metadata(document)
    return coll.insert(document)

def arango_update(collection: str, document_key: str, update: Dict[str, Any]) -> Dict[str, Any]:
    coll = db.collection(collection)
    update = add_temporal_metadata(update, is_update=True)
    return coll.update(document_key, update)

def arango_remove(collection: str, document_key: str) -> Dict[str, Any]:
    coll = db.collection(collection)
    return coll.delete(document_key)

def arango_get_document(collection: str, document_key: str) -> Dict[str, Any]:
    coll = db.collection(collection)
    return coll.get(document_key)

def arango_truncate_collection(collection: str) -> Dict[str, Any]:
    coll = db.collection(collection)
    coll.truncate()
    return {"collection": collection, "status": "truncated"}

def arango_list_collections() -> List[Dict[str, Any]]:
    return db.collections()

def arango_create_collection(name: str, collection_type: str = "document", wait_for_sync: bool = False) -> Dict[str, Any]:
    edge = collection_type.lower() == "edge"
    collection = db.create_collection(name, edge=edge, wait_for_sync=wait_for_sync)
    return {
        "name": collection.name,
        "type": "edge" if edge else "document",
        "status": "created"
    } 
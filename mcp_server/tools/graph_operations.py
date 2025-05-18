from typing import Dict, Any, List, Optional
from .db_connection import db, add_temporal_metadata

def arango_create_edge(edge_collection: str, from_id: str, to_id: str, attributes: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    edge_coll = db.collection(edge_collection)
    edge_doc = attributes or {}
    edge_doc["_from"] = from_id
    edge_doc["_to"] = to_id
    edge_doc = add_temporal_metadata(edge_doc)
    return edge_coll.insert(edge_doc)

def arango_create_sequential_relationship(edge_collection: str, items: List[str], 
                                       relationship_type: str = "NEXT", 
                                       attributes: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    if len(items) < 2:
        return {"error": "Need at least 2 items to create a sequence"}
    
    results = []
    for i in range(len(items) - 1):
        edge_doc = attributes.copy() if attributes else {}
        edge_doc["_from"] = items[i]
        edge_doc["_to"] = items[i + 1]
        edge_doc["relationship_type"] = relationship_type
        edge_doc["sequence_index"] = i
        edge_doc = add_temporal_metadata(edge_doc)
        result = db.collection(edge_collection).insert(edge_doc)
        results.append(result)
    return results

def arango_query_edges(edge_collection: str, from_id: Optional[str] = None, 
                      to_id: Optional[str] = None, direction: str = "outbound") -> List[Dict[str, Any]]:
    query_parts = [f"FOR edge IN {edge_collection}"]
    bind_vars = {}
    
    filters = []
    if from_id:
        filters.append("edge._from == @from_id")
        bind_vars["from_id"] = from_id
    
    if to_id:
        filters.append("edge._to == @to_id")
        bind_vars["to_id"] = to_id
    
    if filters:
        query_parts.append("FILTER " + " AND ".join(filters))
    
    query_parts.append("RETURN edge")
    query = " ".join(query_parts)
    cursor = db.aql.execute(query, bind_vars=bind_vars)
    return [doc for doc in cursor]

def arango_traverse_graph(start_vertex: str, edge_collection: str, min_depth: int = 1, 
                         max_depth: int = 1, direction: str = "outbound") -> List[Dict[str, Any]]:
    query = f"""
    FOR v, e, p IN {min_depth}..{max_depth} {direction} @start_vertex {edge_collection}
        RETURN {{
            "vertex": v,
            "edge": e,
            "path": p.vertices
        }}
    """
    cursor = db.aql.execute(query, bind_vars={"start_vertex": start_vertex})
    return [doc for doc in cursor]

def arango_temporal_traverse(start_vertex: str, edge_collection: str, timestamp: str,
                           min_depth: int = 1, max_depth: int = 1, 
                           direction: str = "outbound") -> List[Dict[str, Any]]:
    query = f"""
    FOR v, e, p IN {min_depth}..{max_depth} {direction} @start_vertex {edge_collection}
        FILTER e.valid_from <= @timestamp
        FILTER e.valid_until == null OR e.valid_until >= @timestamp
        FILTER v.valid_from <= @timestamp
        FILTER v.valid_until == null OR v.valid_until >= @timestamp
        RETURN {{
            "vertex": v,
            "edge": e,
            "path": p.vertices
        }}
    """
    cursor = db.aql.execute(query, bind_vars={
        "start_vertex": start_vertex,
        "timestamp": timestamp
    })
    return [doc for doc in cursor] 
from typing import Dict, Any, List, Optional
from .db_connection import db, add_temporal_metadata, mcp

@mcp.tool()
def arango_create_edge(edge_collection: str, from_id: str, to_id: str, attributes: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Create an edge between two documents in a graph.
    
    Args:
        edge_collection: The name of the edge collection
        from_id: The ID of the source document
        to_id: The ID of the target document
        attributes: Optional additional attributes for the edge
        
    Returns:
        Dictionary with the edge metadata (_id, _key, etc.)
    """
    edge_coll = db.collection(edge_collection)
    edge_doc = attributes or {}
    edge_doc["_from"] = from_id
    edge_doc["_to"] = to_id
    edge_doc = add_temporal_metadata(edge_doc)
    return edge_coll.insert(edge_doc)

@mcp.tool()
def arango_create_sequential_relationship(edge_collection: str, items: List[str], 
                                       relationship_type: str = "NEXT", 
                                       attributes: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """Create a sequence of edges connecting items in order.
    
    Args:
        edge_collection: The name of the edge collection
        items: List of document IDs to connect in sequence
        relationship_type: The type of relationship to create
        attributes: Optional additional attributes for the edges
        
    Returns:
        List of edge creation results
    """
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

@mcp.tool()
def arango_query_edges(edge_collection: str, from_id: Optional[str] = None, 
                      to_id: Optional[str] = None, direction: str = "outbound") -> List[Dict[str, Any]]:
    """Query edges in an edge collection with optional filtering.
    
    Args:
        edge_collection: The name of the edge collection
        from_id: Optional ID of the source document to filter by
        to_id: Optional ID of the target document to filter by
        direction: Direction of traversal ('outbound', 'inbound', or 'any')
        
    Returns:
        List of edges matching the query criteria
    """
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

@mcp.tool()
def arango_traverse_graph(start_vertex: str, edge_collection: str, min_depth: int = 1, 
                         max_depth: int = 1, direction: str = "outbound") -> List[Dict[str, Any]]:
    """Traverse a graph starting from a vertex.
    
    Args:
        start_vertex: The ID of the starting vertex
        edge_collection: The name of the edge collection to traverse
        min_depth: Minimum traversal depth
        max_depth: Maximum traversal depth
        direction: Direction of traversal ('outbound', 'inbound', or 'any')
        
    Returns:
        List of traversal results including vertices, edges, and paths
    """
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

@mcp.tool()
def arango_temporal_traverse(start_vertex: str, edge_collection: str, timestamp: str,
                           min_depth: int = 1, max_depth: int = 1, 
                           direction: str = "outbound") -> List[Dict[str, Any]]:
    """Traverse a graph considering the temporal validity of vertices and edges.
    
    Args:
        start_vertex: The ID of the starting vertex
        edge_collection: The name of the edge collection to traverse
        timestamp: The timestamp for which edges and vertices should be valid
        min_depth: Minimum traversal depth
        max_depth: Maximum traversal depth 
        direction: Direction of traversal ('outbound', 'inbound', or 'any')
        
    Returns:
        List of temporally valid traversal results including vertices, edges, and paths
    """
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
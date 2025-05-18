from typing import Dict, Any, List, Optional
import datetime
from .db_connection import db, mcp

@mcp.tool()
def arango_time_series_analysis(collection: str, time_field: str = "created_at", 
                              interval: str = "day", grouping_field: Optional[str] = None) -> List[Dict[str, Any]]:
    """Perform time series analysis on documents in a collection.
    
    Args:
        collection: The name of the collection to analyze
        time_field: The document field containing the timestamp
        interval: Time interval for grouping ('hour', 'day', 'week', 'month', 'year')
        grouping_field: Optional field to further group results by
        
    Returns:
        List of time series data points grouped by the selected interval
    """
    date_function = {
        "hour": "DATE_HOUR",
        "day": "DATE_DAY", 
        "week": "DATE_WEEK",
        "month": "DATE_MONTH",
        "year": "DATE_YEAR"
    }.get(interval.lower(), "DATE_DAY")
    
    if grouping_field:
        query = f"""
        FOR doc IN {collection}
            COLLECT time_unit = {date_function}(doc.{time_field}), 
                    group_key = doc.{grouping_field}
            SORT time_unit
            RETURN {{
                "time_unit": time_unit,
                "group_key": group_key,
                "count": COUNT(1)
            }}
        """
    else:
        query = f"""
        FOR doc IN {collection}
            COLLECT time_unit = {date_function}(doc.{time_field})
            SORT time_unit
            RETURN {{
                "time_unit": time_unit,
                "count": COUNT(1)
            }}
        """
    
    cursor = db.aql.execute(query)
    return [doc for doc in cursor]

@mcp.tool()
def arango_query_by_time_range(collection: str, start_time: str, end_time: str, 
                             field: str = "created_at") -> List[Dict[str, Any]]:
    """Query documents within a specific time range.
    
    Args:
        collection: The name of the collection to query
        start_time: The start time of the range (ISO format)
        end_time: The end time of the range (ISO format)
        field: The document field containing the timestamp
        
    Returns:
        List of documents that fall within the specified time range
    """
    query = f"""
    FOR doc IN {collection}
        FILTER doc.{field} >= @start_time AND doc.{field} <= @end_time
        RETURN doc
    """
    cursor = db.aql.execute(query, bind_vars={"start_time": start_time, "end_time": end_time})
    return [doc for doc in cursor]

@mcp.tool()
def arango_query_valid_at(collection: str, timestamp: str) -> List[Dict[str, Any]]:
    """Query documents that were valid at a specific point in time.
    
    Args:
        collection: The name of the collection to query
        timestamp: The timestamp (ISO format) for which to check validity
        
    Returns:
        List of documents that were valid at the specified timestamp
    """
    query = f"""
    FOR doc IN {collection}
        FILTER doc.valid_from <= @timestamp
        FILTER doc.valid_until == null OR doc.valid_until >= @timestamp
        RETURN doc
    """
    cursor = db.aql.execute(query, bind_vars={"timestamp": timestamp})
    return [doc for doc in cursor]

@mcp.tool()
def arango_set_validity_period(collection: str, document_key: str, 
                             valid_from: Optional[str] = None, 
                             valid_until: Optional[str] = None) -> Dict[str, Any]:
    """Set or update the validity period for a document.
    
    Args:
        collection: The name of the collection
        document_key: The key of the document to update
        valid_from: The start of the validity period (ISO format)
        valid_until: The end of the validity period (ISO format)
        
    Returns:
        Dictionary with the update metadata
    """
    coll = db.collection(collection)
    update = {"updated_at": datetime.datetime.utcnow().isoformat()}
    
    if valid_from is not None:
        update["valid_from"] = valid_from
    
    if valid_until is not None:
        update["valid_until"] = valid_until
    
    result = coll.update(document_key, update)
    return result 
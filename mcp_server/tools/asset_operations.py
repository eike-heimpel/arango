from typing import Dict, Any, List, Optional, Union
import base64
import uuid
from datetime import datetime
from fastmcp import Image
from pydantic import ConfigDict
from .db_connection import db, add_temporal_metadata

# Define the collection name for assets
ASSETS_COLLECTION = "assets"

# Wrapper class for Image to make it work with Pydantic validation
class ImgData:
    def __init__(self, data, format=None):
        self.data = data
        self.format = format
    
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, v):
        if isinstance(v, Image):
            return v
        return cls(v.data, v.format)
    
    def __get_pydantic_core_schema__(self, _source_type, _handler):
        return {"type": "any"}

def _ensure_assets_collection():
    """Ensure the assets collection exists, creating it if necessary."""
    collections = [c["name"] for c in db.collections()]
    if ASSETS_COLLECTION not in collections:
        db.create_collection(ASSETS_COLLECTION)
        # Create an index on asset_type for faster querying
        db.collection(ASSETS_COLLECTION).add_hash_index(["asset_type"], unique=False)
        print(f"Created '{ASSETS_COLLECTION}' collection")

def arango_upload_image(image_data: bytes, format: str = "png", name: Optional[str] = None, 
                        tags: Optional[List[str]] = None, 
                        description: Optional[str] = None) -> Dict[str, Any]:
    """Upload an image to ArangoDB.
    
    Args:
        image_data: The raw image data as bytes
        format: The image format (e.g., 'png', 'jpeg', etc.)
        name: Optional name for the image
        tags: Optional list of tags to categorize the image
        description: Optional description of the image
        
    Returns:
        Dict with the result of the operation, including the document key
    """
    _ensure_assets_collection()
    
    # Create an Image object
    image = Image(data=image_data, format=format)
    
    # Generate a unique ID if name is not provided
    if not name:
        name = f"image_{uuid.uuid4().hex[:8]}"
    
    # Create the asset document
    asset_doc = {
        "name": name,
        "asset_type": "image",
        "mime_type": f"image/{image.format.lower()}" if image.format else "image/unknown",
        "size_bytes": len(image.data),
        "tags": tags or [],
        "description": description or "",
        "image_data": base64.b64encode(image.data).decode('utf-8'),
        "uploaded_at": datetime.utcnow().isoformat()
    }
    
    # Add temporal metadata and insert
    asset_doc = add_temporal_metadata(asset_doc)
    result = db.collection(ASSETS_COLLECTION).insert(asset_doc)
    
    # Return a clean result without the image data to avoid large responses
    return {
        "key": result["_key"],
        "id": result["_id"],
        "name": name,
        "asset_type": "image",
        "size_bytes": len(image.data),
        "mime_type": asset_doc["mime_type"],
        "status": "uploaded"
    }

def arango_get_image(key: str) -> Dict[str, Any]:
    """Retrieve an image from ArangoDB by its key.
    
    Args:
        key: The document key of the image to retrieve
        
    Returns:
        Dict containing the image data and metadata
    """
    _ensure_assets_collection()
    
    # Get the document
    doc = db.collection(ASSETS_COLLECTION).get(key)
    if not doc:
        raise ValueError(f"Image with key {key} not found")
    
    if doc.get("asset_type") != "image":
        raise ValueError(f"Document with key {key} is not an image")
    
    # Decode the image data
    image_data = base64.b64decode(doc["image_data"])
    
    # Get format from mime_type
    format = "png"  # Default format
    if "mime_type" in doc and "/" in doc["mime_type"]:
        format = doc["mime_type"].split("/")[1]
    
    # Return the image and metadata
    return {
        "key": doc["_key"],
        "name": doc["name"],
        "asset_type": "image",
        "mime_type": doc.get("mime_type", f"image/{format}"),
        "image_data": image_data,
        "format": format,
        "size_bytes": len(image_data),
        "tags": doc.get("tags", []),
        "description": doc.get("description", "")
    }

def arango_list_images(tag: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
    """List images stored in ArangoDB, optionally filtered by tag.
    
    Args:
        tag: Optional tag to filter images
        limit: Maximum number of images to return (default: 100)
        
    Returns:
        List of image metadata dictionaries
    """
    _ensure_assets_collection()
    
    # Build the query
    query = "FOR doc IN assets FILTER doc.asset_type == 'image'"
    
    # Add tag filter if provided
    if tag:
        query += f" FILTER '{tag}' IN doc.tags"
    
    # Complete the query
    query += f" LIMIT {limit} RETURN {{ _key: doc._key, _id: doc._id, name: doc.name, mime_type: doc.mime_type, size_bytes: doc.size_bytes, tags: doc.tags, description: doc.description, uploaded_at: doc.uploaded_at }}"
    
    # Execute the query
    cursor = db.aql.execute(query)
    return [doc for doc in cursor]

def arango_delete_image(key: str) -> Dict[str, Any]:
    """Delete an image from ArangoDB by its key.
    
    Args:
        key: The document key of the image to delete
        
    Returns:
        Dict with the result of the operation
    """
    _ensure_assets_collection()
    
    # Check if the document exists and is an image
    doc = db.collection(ASSETS_COLLECTION).get(key)
    if not doc:
        raise ValueError(f"Image with key {key} not found")
    
    if doc.get("asset_type") != "image":
        raise ValueError(f"Document with key {key} is not an image")
    
    # Delete the document
    result = db.collection(ASSETS_COLLECTION).delete(key)
    return {
        "key": key,
        "status": "deleted"
    }

def arango_update_image_metadata(key: str, 
                               name: Optional[str] = None, 
                               tags: Optional[List[str]] = None, 
                               description: Optional[str] = None) -> Dict[str, Any]:
    """Update metadata for an existing image.
    
    Args:
        key: The document key of the image to update
        name: New name for the image
        tags: New tags for the image
        description: New description for the image
        
    Returns:
        Dict with the result of the operation
    """
    _ensure_assets_collection()
    
    # Check if the document exists and is an image
    doc = db.collection(ASSETS_COLLECTION).get(key)
    if not doc:
        raise ValueError(f"Image with key {key} not found")
    
    if doc.get("asset_type") != "image":
        raise ValueError(f"Document with key {key} is not an image")
    
    # Build update document
    update = {}
    if name is not None:
        update["name"] = name
    if tags is not None:
        update["tags"] = tags
    if description is not None:
        update["description"] = description
    
    # Add updated_at timestamp
    update["updated_at"] = datetime.utcnow().isoformat()
    
    # Add temporal metadata
    update = add_temporal_metadata(update, is_update=True)
    
    # Update the document
    result = db.collection(ASSETS_COLLECTION).update(key, update)
    
    return {
        "key": key,
        "status": "updated",
        "updates": list(update.keys())
    } 
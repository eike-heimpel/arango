import os
import json
from typing import Dict, Any, List, Optional
from .db_connection import db

def arango_backup(output_dir: str, collection: Optional[str] = None, doc_limit: int = 1000) -> Dict[str, Any]:
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
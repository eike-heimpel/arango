from arango import ArangoClient
import os
import dotenv
import datetime
from typing import Dict, Any

dotenv.load_dotenv()

# Get environment variables or use defaults
ARANGO_URL = os.environ.get("ARANGO_URL", "http://localhost:8529")
ARANGO_DB = os.environ.get("ARANGO_DB", "_system")
ARANGO_USERNAME = os.environ.get("ARANGO_USERNAME", "root")
ARANGO_PASSWORD = os.environ.get("ARANGO_PASSWORD", "")

# Initialize ArangoDB client
client = ArangoClient(hosts=ARANGO_URL)
db = client.db(ARANGO_DB, username=ARANGO_USERNAME, password=ARANGO_PASSWORD)

def add_temporal_metadata(document: Dict[str, Any], is_update: bool = False) -> Dict[str, Any]:
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
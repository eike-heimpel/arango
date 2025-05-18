import os
import requests
from dotenv import load_dotenv
from arango import ArangoClient

# Load environment variables
load_dotenv()

# Get environment variables
ARANGO_URL = os.getenv('ARANGO_URL', 'http://localhost:8529')
ARANGO_DB = os.getenv('ARANGO_DB', 'knowledge_db').lower()  # Force lowercase
ARANGO_USERNAME = os.getenv('ARANGO_USERNAME', 'root')
ARANGO_PASSWORD = os.getenv('ARANGO_PASSWORD', '')

print(f"Testing connection to ArangoDB...")
print(f"URL: {ARANGO_URL}")
print(f"Database: {ARANGO_DB}")
print(f"Username: {ARANGO_USERNAME}")

# First, try a direct API call to check basic connectivity
try:
    # Test basic connectivity with /_api/version
    response = requests.get(
        f"{ARANGO_URL}/_api/version",
        auth=(ARANGO_USERNAME, ARANGO_PASSWORD)
    )
    print("\n1. Direct API Test:")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Direct API call failed: {str(e)}")

# Try with the ArangoDB client
try:
    print("\nArangoDB Client Test:")
    # Initialize the client
    client = ArangoClient(hosts=ARANGO_URL)
    
    # Connect directly to the target database
    db = client.db(ARANGO_DB, username=ARANGO_USERNAME, password=ARANGO_PASSWORD)
    print(f"Successfully connected to database: {ARANGO_DB}")
    
    # Try to access a specific collection
    try:
        # Try to create a test collection
        if not db.has_collection('test_collection'):
            collection = db.create_collection('test_collection')
            print("Created test collection successfully")
        else:
            collection = db.collection('test_collection')
            print("Accessed existing test collection successfully")
        
        # Try to insert a document
        doc = {'_key': 'test1', 'value': 'test'}
        result = collection.insert(doc)
        print(f"Inserted document successfully: {result}")
        
        # Try to read the document back
        doc = collection.get('test1')
        print(f"Retrieved document successfully: {doc}")
        
        # Clean up
        collection.delete(doc)
        print("Deleted test document successfully")
        
    except Exception as e:
        print(f"Collection operation failed: {str(e)}")
    
except Exception as e:
    print(f"ArangoDB client connection failed: {str(e)}") 
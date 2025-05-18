# ArangoDB MCP Server

A Model Context Protocol (MCP) server for interacting with ArangoDB databases. This server provides tools for executing AQL queries, managing documents and collections, creating indexes, and backing up data.

## Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

## Environment Variables

The server uses the following environment variables:

- `ARANGO_URL`: ArangoDB server URL (default: "http://localhost:8529")
- `ARANGO_DB`: Database name (default: "_system")
- `ARANGO_USERNAME`: Database username (default: "root")
- `ARANGO_PASSWORD`: Database password (default: "")

## Running the Server

```bash
python server.py
```

## Available Tools

### Query and Document Management

- **arango_query**: Execute AQL queries with optional bind variables
- **arango_get_document**: Retrieve a specific document by its key
- **arango_insert**: Insert a document into a collection
- **arango_update**: Update an existing document
- **arango_remove**: Remove a document from a collection

### Collection Management

- **arango_list_collections**: List all collections in the database
- **arango_create_collection**: Create a new document or edge collection
- **arango_truncate_collection**: Remove all documents from a collection

### Index Management

- **arango_create_index**: Create an index on a collection (hash, skiplist, persistent, geo, or fulltext)
- **arango_list_indexes**: List all indexes on a collection

### Data Backup

- **arango_backup**: Backup collections to JSON files

## Example Usage

```python
# Execute an AQL query
arango_query(
    query="FOR doc IN users FILTER doc.age > @minAge RETURN doc", 
    bind_vars={"minAge": 30}
)

# Create a new collection
arango_create_collection(
    name="products", 
    collection_type="document", 
    wait_for_sync=False
)

# Insert a document
arango_insert(
    collection="users", 
    document={"name": "John", "email": "john@example.com"}
)

# Backup data
arango_backup(
    output_dir="./backup", 
    collection="users", 
    doc_limit=1000
)
```

## Integration with MCP Clients

To use this server with an MCP client like Claude Desktop, add the following to your client configuration:

```json
{
  "mcpServers": {
    "arangodb": {
      "command": "python",
      "args": ["/path/to/server.py"],
      "env": {
        "ARANGO_URL": "http://localhost:8529",
        "ARANGO_DB": "myDatabase",
        "ARANGO_USERNAME": "username",
        "ARANGO_PASSWORD": "password"
      }
    }
  }
}
``` 
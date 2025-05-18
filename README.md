# ArangoDB MCP Server

A containerized setup running ArangoDB with a custom Memory Control Protocol (MCP) server.

## Quick Start

1. Set up environment variables:
```bash
# Create .env file with required variables
ARANGO_ROOT_PASSWORD=your_root_password
ARANGO_USERNAME=root
ARANGO_URL=http://arangodb:8529
ARANGO_DB=your_database_name
ARANGO_PASSWORD=your_password
```

2. Start the services:
```bash
docker compose up -d
```

## Components

- **ArangoDB (port 8529)**: Graph database server
- **MCP Server (port 22000)**: Custom Memory Control Protocol server

## Data Persistence

The setup includes persistent volumes for ArangoDB:
- Database data: `arangodb_data`
- Applications: `arangodb_apps`

## Development

The project uses Docker Compose for local development and deployment. Services automatically restart unless stopped manually.

## Access

- ArangoDB UI: http://localhost:8529
- MCP Server: http://localhost:22000 
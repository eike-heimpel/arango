#!/bin/bash

# Load environment variables from .env file
if [ -f .env ]; then
    echo "Loading environment variables from .env file"
    export $(grep -v '^#' .env | xargs)
else
    echo "No .env file found. Please create one based on .env.example"
    exit 1
fi

# Configuration
# Use environment variables with defaults as fallback
REMOTE_HOST="${REMOTE_HOST:-localhost}"
REMOTE_USER="${REMOTE_USER:-user}"
REMOTE_DIR="${REMOTE_DIR:-/tmp/llm-privacy-layer}"
SOURCE_DIR="$(pwd)"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Starting deployment to homeserver...${NC}"
echo "Source: $SOURCE_DIR"
echo "Destination: $REMOTE_USER@$REMOTE_HOST:$REMOTE_DIR"

# Make sure remote directory exists
ssh $REMOTE_USER@$REMOTE_HOST "mkdir -p $REMOTE_DIR"

if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to create remote directory. Exiting.${NC}"
    exit 1
fi

# Use rsync to copy files - with improved selection
# -a: archive mode (preserves permissions, etc.)
# -v: verbose
# -z: compress during transfer
# --delete: delete files on destination that don't exist on source
# --exclude: don't copy these directories/files
rsync -avz --delete \
    --include="mail_archiving/***" \
    --include="mail_fetcher.py" \
    --include="Dockerfile" \
    --include="docker-compose.yml" \
    --include="requirements.txt" \
    --include="setup.py" \
    --include="Makefile" \
    --include=".env.example" \
    --include=".env" \
    --exclude=".git/" \
    --exclude=".github/" \
    --exclude=".gitignore" \
    --exclude=".cursorignore" \
    --exclude=".dockerignore" \
    --exclude="venv/" \
    --exclude="__pycache__/" \
    --exclude="*.pyc" \
    --exclude=".DS_Store" \
    --exclude=".env.local" \
    --exclude="test*" \
    --exclude="tests/" \
    --exclude="docker-compose.test.yml" \
    --exclude="requirements-dev.txt" \
    --exclude="README.md" \
    --exclude="send_to_homeserver.sh" \
    "$SOURCE_DIR/" "$REMOTE_USER@$REMOTE_HOST:$REMOTE_DIR/"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}Deployment successful!${NC}"
    echo -e "${GREEN}Files synchronized to $REMOTE_USER@$REMOTE_HOST:$REMOTE_DIR${NC}"
else
    echo -e "${RED}Deployment failed.${NC}"
    exit 1
fi

# Display remote directory contents
echo -e "${YELLOW}Remote directory contents:${NC}"
ssh $REMOTE_USER@$REMOTE_HOST "ls -la $REMOTE_DIR"

# Show what files were transferred (summary)
echo -e "${YELLOW}Transferred files summary:${NC}"
find "$SOURCE_DIR" -type f \
    -not -path "*/\.*" \
    -not -path "*/venv/*" \
    -not -path "*/__pycache__/*" \
    -not -path "*/tests/*" \
    -not -name "test_*" \
    -not -name "*.pyc" \
    -not -name "docker-compose.test.yml" \
    -not -name "requirements-dev.txt" \
    -not -name "README.md" \
    -not -name "send_to_homeserver.sh" \
    -o -name ".env" \
    -o -name ".env.example" \
    | sort

exit 0 
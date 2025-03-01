#!/bin/bash

# Simple script to run The Last Centaur using Docker without docker-compose

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== The Last Centaur - Docker Setup (Simple) ===${NC}"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
  echo -e "${RED}Error: Docker is not running. Please start Docker and try again.${NC}"
  exit 1
fi

# Check for OpenAI API key
if [ -z "$OPENAI_API_KEY" ]; then
  echo -e "${YELLOW}Warning: OPENAI_API_KEY environment variable is not set.${NC}"
  echo -e "${YELLOW}LLM enhancement will be disabled. Set it with:${NC}"
  echo -e "${YELLOW}export OPENAI_API_KEY=your_api_key_here${NC}"
  read -p "Do you want to continue without LLM enhancement? (y/n) " -n 1 -r
  echo
  if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 1
  fi
fi

# Clean up any existing containers
echo -e "${YELLOW}Cleaning up any existing containers...${NC}"
docker stop thelastcentaur-frontend thelastcentaur-backend thelastcentaur-postgres 2>/dev/null || true
docker rm thelastcentaur-frontend thelastcentaur-backend thelastcentaur-postgres 2>/dev/null || true
docker network rm thelastcentaur-network 2>/dev/null || true

# Create a Docker network
echo -e "${GREEN}Creating Docker network...${NC}"
docker network create thelastcentaur-network || true

# Start PostgreSQL
echo -e "${GREEN}Starting PostgreSQL...${NC}"
docker run -d \
  --name thelastcentaur-postgres \
  --network thelastcentaur-network \
  -e POSTGRES_USER=crstjames \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=thelastcentaur \
  -p 5432:5432 \
  postgres:14

# Wait for PostgreSQL to be ready
echo -e "${GREEN}Waiting for PostgreSQL to be ready...${NC}"
sleep 10

# Build and start the backend
echo -e "${GREEN}Building and starting backend...${NC}"
docker build -t thelastcentaur-backend -f Dockerfile.backend .
docker run -d \
  --name thelastcentaur-backend \
  --network thelastcentaur-network \
  -e POSTGRES_SERVER=thelastcentaur-postgres \
  -e POSTGRES_USER=crstjames \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=thelastcentaur \
  -e OPENAI_API_KEY="${OPENAI_API_KEY}" \
  -e ANTHROPIC_API_KEY="${ANTHROPIC_API_KEY}" \
  -e CORS_ORIGINS="http://localhost:3002,http://127.0.0.1:3002" \
  -p 8000:8000 \
  -v "$(pwd):/app" \
  thelastcentaur-backend

# Build and start the frontend
echo -e "${GREEN}Building and starting frontend...${NC}"
docker build -t thelastcentaur-frontend -f Dockerfile.frontend .
docker run -d \
  --name thelastcentaur-frontend \
  --network thelastcentaur-network \
  -e NEXT_PUBLIC_API_URL=http://localhost:8000 \
  -e NEXT_PUBLIC_WS_URL=ws://localhost:8000 \
  -p 3002:3002 \
  -v "$(pwd)/frontend:/app" \
  --add-host=host.docker.internal:host-gateway \
  thelastcentaur-frontend

echo -e "${GREEN}Services are running!${NC}"
echo -e "${GREEN}Frontend: http://localhost:3002${NC}"
echo -e "${GREEN}Backend API: http://localhost:8000${NC}"
echo -e "${GREEN}PostgreSQL: localhost:5432${NC}"

echo -e "\n${YELLOW}To view logs:${NC}"
echo "docker logs thelastcentaur-backend"
echo "docker logs thelastcentaur-frontend"

echo -e "\n${YELLOW}To stop services:${NC}"
echo "./stop-docker.sh" 
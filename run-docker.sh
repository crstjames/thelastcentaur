#!/bin/bash

# Script to run The Last Centaur using Docker

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== The Last Centaur - Docker Setup ===${NC}"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
  echo -e "${RED}Error: Docker is not running. Please start Docker and try again.${NC}"
  exit 1
fi

# Check if docker compose is available
if ! docker compose version > /dev/null 2>&1; then
  echo -e "${RED}Error: 'docker compose' command not found. Please make sure Docker Desktop is installed and up to date.${NC}"
  exit 1
fi

# Load environment variables from .env file if it exists
if [ -f .env ]; then
  echo -e "${GREEN}Loading environment variables from .env file...${NC}"
  export $(grep -v '^#' .env | xargs)
  echo -e "${GREEN}OpenAI API Key: ${OPENAI_API_KEY:0:3}...${OPENAI_API_KEY: -4}${NC}"
else
  echo -e "${YELLOW}Warning: .env file not found.${NC}"
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

# Create or update .env file for Docker
echo -e "${GREEN}Ensuring .env file is up to date...${NC}"
echo "OPENAI_API_KEY=${OPENAI_API_KEY}" > .env.docker
echo "ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}" >> .env.docker

# Build and start the containers
echo -e "${GREEN}Building and starting containers...${NC}"
docker compose --env-file .env.docker up --build -d

# Wait for services to be ready
echo -e "${GREEN}Waiting for services to be ready...${NC}"
sleep 5

# Check if services are running
if docker compose ps | grep -q "Up"; then
  echo -e "${GREEN}Services are running!${NC}"
  echo -e "${GREEN}Frontend: http://localhost:3002${NC}"
  echo -e "${GREEN}Backend API: http://localhost:8000${NC}"
  echo -e "${GREEN}PostgreSQL: localhost:5432${NC}"
  
  echo -e "\n${YELLOW}To view logs:${NC}"
  echo "docker compose logs -f"
  
  echo -e "\n${YELLOW}To stop services:${NC}"
  echo "docker compose down"
else
  echo -e "${RED}Error: Services failed to start properly.${NC}"
  echo -e "${YELLOW}Checking logs:${NC}"
  docker compose logs
  exit 1
fi 
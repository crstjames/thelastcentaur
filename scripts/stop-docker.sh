#!/bin/bash

# Script to stop and clean up Docker containers for The Last Centaur

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== The Last Centaur - Docker Cleanup ===${NC}"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
  echo -e "${RED}Error: Docker is not running. Please start Docker and try again.${NC}"
  exit 1
fi

# Try docker compose first
if docker compose version > /dev/null 2>&1; then
  echo -e "${YELLOW}Stopping containers with docker compose...${NC}"
  docker compose down
else
  # Fall back to direct docker commands
  echo -e "${YELLOW}Stopping containers with direct docker commands...${NC}"
  
  # Stop containers
  echo -e "${YELLOW}Stopping containers...${NC}"
  docker stop thelastcentaur-frontend thelastcentaur-backend thelastcentaur-postgres 2>/dev/null || true
  
  # Remove containers
  echo -e "${YELLOW}Removing containers...${NC}"
  docker rm thelastcentaur-frontend thelastcentaur-backend thelastcentaur-postgres 2>/dev/null || true
  
  # Remove network
  echo -e "${YELLOW}Removing network...${NC}"
  docker network rm thelastcentaur-network 2>/dev/null || true
fi

echo -e "${GREEN}Cleanup complete!${NC}" 
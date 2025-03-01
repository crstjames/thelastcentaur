#!/bin/bash

# Script to check if Docker containers for The Last Centaur are running properly

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== The Last Centaur - Docker Status Check ===${NC}"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
  echo -e "${RED}Error: Docker is not running. Please start Docker and try again.${NC}"
  exit 1
fi

# Check PostgreSQL container
echo -e "${YELLOW}Checking PostgreSQL container...${NC}"
if docker ps | grep -q "thelastcentaur-postgres"; then
  echo -e "${GREEN}✅ PostgreSQL container is running${NC}"
  
  # Check if PostgreSQL is accepting connections
  if docker exec thelastcentaur-postgres pg_isready -U crstjames -d thelastcentaur > /dev/null 2>&1; then
    echo -e "${GREEN}✅ PostgreSQL is accepting connections${NC}"
  else
    echo -e "${RED}❌ PostgreSQL is not accepting connections${NC}"
  fi
else
  echo -e "${RED}❌ PostgreSQL container is not running${NC}"
fi

# Check Backend container
echo -e "\n${YELLOW}Checking Backend container...${NC}"
if docker ps | grep -q "thelastcentaur-backend"; then
  echo -e "${GREEN}✅ Backend container is running${NC}"
  
  # Check if Backend API is accessible
  if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Backend API is accessible${NC}"
  else
    echo -e "${RED}❌ Backend API is not accessible${NC}"
  fi
else
  echo -e "${RED}❌ Backend container is not running${NC}"
fi

# Check Frontend container
echo -e "\n${YELLOW}Checking Frontend container...${NC}"
if docker ps | grep -q "thelastcentaur-frontend"; then
  echo -e "${GREEN}✅ Frontend container is running${NC}"
  
  # Check if Frontend is accessible
  if curl -s http://localhost:3002 > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Frontend is accessible${NC}"
  else
    echo -e "${RED}❌ Frontend is not accessible${NC}"
  fi
else
  echo -e "${RED}❌ Frontend container is not running${NC}"
fi

# Show container logs if there are issues
echo -e "\n${YELLOW}Container logs (last 10 lines):${NC}"
echo -e "${YELLOW}PostgreSQL:${NC}"
docker logs --tail 10 thelastcentaur-postgres 2>/dev/null || echo "No logs available"

echo -e "\n${YELLOW}Backend:${NC}"
docker logs --tail 10 thelastcentaur-backend 2>/dev/null || echo "No logs available"

echo -e "\n${YELLOW}Frontend:${NC}"
docker logs --tail 10 thelastcentaur-frontend 2>/dev/null || echo "No logs available"

echo -e "\n${GREEN}Status check complete!${NC}" 
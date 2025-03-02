#!/bin/bash

# Docker Manager for The Last Centaur
# A simple wrapper around the existing Docker scripts

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
  echo -e "${RED}Error: Docker is not running. Please start Docker and try again.${NC}"
  exit 1
fi

# Display menu
echo -e "${BLUE}=== The Last Centaur - Docker Manager ===${NC}"
echo -e "${YELLOW}Please select an option:${NC}"
echo -e "${GREEN}1. Start Docker containers${NC}"
echo -e "${RED}2. Stop Docker containers${NC}"
echo -e "${YELLOW}3. Restart Docker containers${NC}"
echo -e "${BLUE}4. Check Docker container status${NC}"
echo -e "${GREEN}5. View Docker logs${NC}"
echo -e "${RED}0. Exit${NC}"

# Get user input
read -p "Enter your choice [0-5]: " choice

case $choice in
  1)
    echo -e "${GREEN}Starting Docker containers...${NC}"
    bash ./run-docker.sh
    ;;
  2)
    echo -e "${RED}Stopping Docker containers...${NC}"
    bash ./stop-docker.sh
    ;;
  3)
    echo -e "${YELLOW}Restarting Docker containers...${NC}"
    bash ./stop-docker.sh
    echo -e "${YELLOW}Waiting for containers to stop completely...${NC}"
    sleep 5
    bash ./run-docker.sh
    ;;
  4)
    echo -e "${BLUE}Checking Docker container status...${NC}"
    bash ./check-docker.sh
    ;;
  5)
    echo -e "${GREEN}Viewing Docker logs...${NC}"
    echo -e "${YELLOW}Which container logs do you want to view?${NC}"
    echo -e "1. All containers"
    echo -e "2. Backend"
    echo -e "3. Frontend"
    echo -e "4. PostgreSQL"
    read -p "Enter your choice [1-4]: " log_choice
    
    case $log_choice in
      1)
        docker compose logs -f
        ;;
      2)
        docker logs -f thelastcentaur-backend
        ;;
      3)
        docker logs -f thelastcentaur-frontend
        ;;
      4)
        docker logs -f thelastcentaur-postgres
        ;;
      *)
        echo -e "${RED}Invalid choice. Exiting.${NC}"
        exit 1
        ;;
    esac
    ;;
  0)
    echo -e "${BLUE}Exiting Docker Manager.${NC}"
    exit 0
    ;;
  *)
    echo -e "${RED}Invalid choice. Exiting.${NC}"
    exit 1
    ;;
esac

echo -e "${GREEN}Operation completed!${NC}" 
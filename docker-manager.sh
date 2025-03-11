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

# Process choice
case $choice in
  1)
    # Start Docker containers
    echo -e "${GREEN}Starting Docker containers...${NC}"
    ./scripts/run-docker.sh
    ;;
  2)
    # Stop Docker containers
    echo -e "${RED}Stopping Docker containers...${NC}"
    ./scripts/stop-docker.sh
    ;;
  3)
    # Restart Docker containers
    echo -e "${YELLOW}Restarting Docker containers...${NC}"
    ./scripts/restart-services.sh
    ;;
  4)
    # Check Docker container status
    echo -e "${BLUE}Checking Docker container status...${NC}"
    echo
    docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    echo
    ;;
  5)
    # View Docker logs
    echo -e "${GREEN}Which container's logs would you like to view?${NC}"
    echo -e "${YELLOW}1. Backend${NC}"
    echo -e "${YELLOW}2. Frontend${NC}"
    echo -e "${YELLOW}3. Database${NC}"
    echo -e "${RED}0. Back to main menu${NC}"
    
    read -p "Enter your choice [0-3]: " log_choice
    
    case $log_choice in
      1)
        echo -e "${GREEN}Viewing backend logs (press Ctrl+C to exit)...${NC}"
        docker logs -f thelastcentaur-backend
        ;;
      2)
        echo -e "${GREEN}Viewing frontend logs (press Ctrl+C to exit)...${NC}"
        docker logs -f thelastcentaur-frontend
        ;;
      3)
        echo -e "${GREEN}Viewing database logs (press Ctrl+C to exit)...${NC}"
        docker logs -f thelastcentaur-postgres
        ;;
      0)
        echo -e "${RED}Returning to main menu...${NC}"
        exec $0
        ;;
      *)
        echo -e "${RED}Invalid option. Returning to main menu...${NC}"
        exec $0
        ;;
    esac
    ;;
  0)
    # Exit
    echo -e "${RED}Exiting...${NC}"
    exit 0
    ;;
  *)
    # Invalid option
    echo -e "${RED}Invalid option. Please try again.${NC}"
    exec $0
    ;;
esac 
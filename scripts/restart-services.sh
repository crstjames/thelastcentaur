#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Restarting The Last Centaur services with CORS fixes...${NC}"

# Stop existing services
echo -e "${YELLOW}Stopping existing services...${NC}"
docker compose down

# Create a backup of the main.py file
echo -e "${YELLOW}Creating backup of main.py...${NC}"
cp src/main.py src/main.py.bak

# Apply CORS fixes if they're not already applied
if ! grep -q "CORS origins configured" src/main.py; then
    echo -e "${YELLOW}Applying CORS fixes to main.py...${NC}"
    sed -i.bak '/# Configure CORS/,/allow_headers=\["*"\]/c\
# Configure CORS\
origins = []\
# Add localhost origins by default\
for port in ["3000", "3001", "3002", "3003", "5173", "5174"]:\
    origins.extend([f"http://localhost:{port}", f"http://127.0.0.1:{port}"])\
\
# Add origins from settings.CORS_ORIGINS environment variable if it exists\
import os\
cors_origins_env = os.getenv("CORS_ORIGINS", "")\
if cors_origins_env:\
    origins.extend([origin.strip() for origin in cors_origins_env.split(",") if origin.strip()])\
\
print(f"CORS origins configured: {origins}")\
\
app.add_middleware(\
    CORSMiddleware,\
    allow_origins=origins,\
    allow_credentials=True,\
    allow_methods=["*"],\
    allow_headers=["*"],\
    expose_headers=["*"],\
)' src/main.py
fi

# Start services
echo -e "${YELLOW}Starting services...${NC}"
docker compose up -d

# Wait for services to be ready
echo -e "${YELLOW}Waiting for services to be ready...${NC}"
sleep 5

# Test the API
echo -e "${YELLOW}Testing API connectivity...${NC}"
curl -s http://localhost:8000/api/v1/health > /dev/null
if [ $? -eq 0 ]; then
    echo -e "${GREEN}API is reachable!${NC}"
else
    echo -e "${RED}API is not reachable. Check logs with 'docker logs thelastcentaur-backend'${NC}"
fi

# Test the frontend
echo -e "${YELLOW}Testing frontend connectivity...${NC}"
curl -s http://localhost:3002 > /dev/null
if [ $? -eq 0 ]; then
    echo -e "${GREEN}Frontend is reachable!${NC}"
else
    echo -e "${RED}Frontend is not reachable. Check logs with 'docker logs thelastcentaur-frontend'${NC}"
fi

echo -e "${GREEN}Services restarted! The coordinate-based movement system is now active.${NC}"
echo -e "${YELLOW}Run the following commands to test:${NC}"
echo -e "  1. Play game directly: ${GREEN}python play_coordinate_game.py${NC}"
echo -e "  2. Test API connectivity: ${GREEN}python test_api_connectivity.py${NC}"
echo -e "  3. Test API game interaction: ${GREEN}python test_game_api.py${NC}"
echo -e "  4. Run Playwright tests: ${GREEN}cd frontend && npm run test:e2e${NC}"
echo -e "\nEnjoy playing The Last Centaur with coordinate-based movement!" 
#!/bin/bash
# Deployment script for The Last Centaur

set -e  # Exit on error

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Error: .env file not found. Please create one based on .env.example"
    exit 1
fi

# Load environment variables
source .env

# Pull latest changes
echo "Pulling latest changes from repository..."
git pull

# Build and start the containers
echo "Building and starting containers..."
docker-compose -f docker-compose.yml build
docker-compose -f docker-compose.yml up -d

# Run database migrations
echo "Running database migrations..."
docker-compose -f docker-compose.yml exec app alembic upgrade head

# Clean up unused images
echo "Cleaning up unused Docker images..."
docker image prune -f

echo "Deployment completed successfully!"
echo "Your application is running at: http://$DOMAIN" 
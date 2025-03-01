# Docker Setup for The Last Centaur

This document provides instructions for running The Last Centaur using Docker.

## Prerequisites

- Docker installed and running
- Docker Compose (optional, but recommended)
- OpenAI API key (for LLM enhancement)

## API Key Setup

The LLM enhancement feature requires an OpenAI API key. Set it as an environment variable before running the Docker scripts:

```bash
export OPENAI_API_KEY=your_api_key_here
```

Without this key, the game will still run, but you won't get the rich, immersive LLM-enhanced descriptions.

## Quick Start

### Option 1: Using Docker Compose (Recommended)

If you have Docker Compose installed, you can use the following command:

```bash
./run-docker.sh
```

This script will:

1. Check if Docker is running
2. Check if the OpenAI API key is set
3. Create a `.env` file if it doesn't exist
4. Build and start all containers
5. Check if services are running properly

### Option 2: Using Direct Docker Commands

If you don't have Docker Compose, you can use the following command:

```bash
./run-docker-simple.sh
```

This script will:

1. Check if Docker is running
2. Check if the OpenAI API key is set
3. Create a Docker network
4. Start PostgreSQL
5. Build and start the backend
6. Build and start the frontend

## Checking Container Status

To check if all containers are running properly:

```bash
./check-docker.sh
```

This script will:

1. Check if all containers are running
2. Check if services are accessible
3. Show container logs if there are issues

## Stopping Containers

To stop and remove all containers:

```bash
./stop-docker.sh
```

## Manual Commands

If you prefer to run commands manually:

### Start Containers

```bash
# Using Docker Compose
docker compose up -d

# Using direct Docker commands
docker network create thelastcentaur-network
docker run -d --name thelastcentaur-postgres --network thelastcentaur-network -e POSTGRES_USER=crstjames -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=thelastcentaur -p 5432:5432 postgres:14
docker build -t thelastcentaur-backend -f Dockerfile.backend .
docker run -d --name thelastcentaur-backend --network thelastcentaur-network -e POSTGRES_SERVER=thelastcentaur-postgres -e POSTGRES_USER=crstjames -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=thelastcentaur -e OPENAI_API_KEY=${OPENAI_API_KEY} -e ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY} -p 8000:8000 -v "$(pwd):/app" thelastcentaur-backend
docker build -t thelastcentaur-frontend -f Dockerfile.frontend .
docker run -d --name thelastcentaur-frontend --network thelastcentaur-network -e NEXT_PUBLIC_API_URL=http://localhost:8000 -e NEXT_PUBLIC_WS_URL=ws://localhost:8000 -p 3002:3002 -v "$(pwd)/frontend:/app" --add-host=host.docker.internal:host-gateway thelastcentaur-frontend
```

### Stop Containers

```bash
# Using Docker Compose
docker compose down

# Using direct Docker commands
docker stop thelastcentaur-frontend thelastcentaur-backend thelastcentaur-postgres
docker rm thelastcentaur-frontend thelastcentaur-backend thelastcentaur-postgres
docker network rm thelastcentaur-network
```

## Accessing Services

- Frontend: http://localhost:3002
- Backend API: http://localhost:8000
- PostgreSQL: localhost:5432

## Troubleshooting

### LLM Enhancement Not Working

If you're not getting rich, immersive descriptions:

1. Check if the OpenAI API key is set correctly:

   ```bash
   echo $OPENAI_API_KEY
   ```

2. Check the backend logs for any API key errors:

   ```bash
   docker logs thelastcentaur-backend
   ```

3. Make sure the API key is being passed to the container:
   ```bash
   docker exec thelastcentaur-backend env | grep OPENAI
   ```

### Port Conflicts

If you encounter port conflicts, make sure no other services are using ports 8000, 3002, or 5432.

### Container Logs

To view container logs:

```bash
docker logs thelastcentaur-backend
docker logs thelastcentaur-frontend
docker logs thelastcentaur-postgres
```

### Network Issues

If containers can't communicate with each other, check if they're on the same network:

```bash
docker network inspect thelastcentaur-network
```

### Database Connection Issues

If the backend can't connect to the database, check if PostgreSQL is running and accepting connections:

```bash
docker exec thelastcentaur-postgres pg_isready -U crstjames -d thelastcentaur
```

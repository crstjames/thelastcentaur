# The Last Centaur - Port Configuration

This document outlines the port configuration for The Last Centaur project to ensure consistent development and deployment.

## Port Overview

| Service             | Default Port | Current Port  | Environment Variable | Configuration File                            |
| ------------------- | ------------ | ------------- | -------------------- | --------------------------------------------- |
| Backend API         | 8000         | 8000 (Docker) | N/A                  | `src/main.py`, `docker-compose.yml`           |
| Frontend Dev Server | 3002         | 3002 (Docker) | N/A                  | `frontend/package.json`, `docker-compose.yml` |
| PostgreSQL          | 5432         | 5432 (Docker) | N/A                  | `docker-compose.yml`                          |

## Backend Configuration

The backend FastAPI server runs on port 8000 by default. This is configured in `src/main.py`.

If port 8000 is already in use, the application will automatically find an available port in the range 8000-8100. However, when running in Docker, the port is fixed to 8000.

## Frontend Configuration

The frontend Next.js development server runs on port 3002. This is specified when starting the development server:

```bash
cd frontend && npm run dev -- -p 3002
```

When running in Docker, the port is fixed to 3002.

## Docker Configuration

The project includes Docker configuration for easy setup and consistent environments:

```bash
# Start all services
docker-compose up

# Start in detached mode
docker-compose up -d

# Stop all services
docker-compose down

# Rebuild containers
docker-compose build
```

The Docker setup ensures that:

- Backend API is accessible at http://localhost:8000
- Frontend is accessible at http://localhost:3002
- PostgreSQL is accessible at localhost:5432

## API Communication

The frontend communicates with the backend through the API configuration in `frontend/app/services/api.ts`:

```typescript
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const API_V1_PREFIX = "/api/v1";
const WS_URL = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000";
```

When running in Docker, these environment variables are set in the docker-compose.yml file.

### Important Notes

1. **Environment Variables**: In production, use the environment variables `NEXT_PUBLIC_API_URL` and `NEXT_PUBLIC_WS_URL` to configure the API endpoints.

2. **Port Synchronization**: Always ensure that the port in `API_BASE_URL` and `WS_URL` matches the port where the backend server is running.

3. **Port Conflicts**: If you encounter port conflicts:
   - For local development: The backend will automatically find an available port, and you can specify a different port for the frontend
   - For Docker: Make sure the ports 8000, 3002, and 5432 are available on your host machine

## Troubleshooting

If you encounter issues with API communication:

1. Verify the backend server is running and note which port it's using (check the console output)
2. Check that `API_BASE_URL` in `frontend/app/services/api.ts` matches the backend port
3. Ensure there are no CORS issues by checking the browser console
4. Confirm that authentication tokens are being properly passed in API requests

### Docker-specific Troubleshooting

1. **Port conflicts**: If you see errors like "port is already allocated", make sure no other services are using ports 8000, 3002, or 5432
2. **Database connection issues**: Check if the PostgreSQL container is healthy with `docker-compose ps`
3. **API connection issues**: Ensure the backend container is running and the frontend is configured to use the correct URL

## WebSocket Connection

WebSocket connections use the `WS_URL` configuration which should point to the same server as the REST API but with the `ws://` protocol.

```typescript
socket = new WebSocket(`${WS_URL}/ws/game/${gameId}?token=${token}`);
```

Always ensure that the WebSocket URL uses the same port as the backend API server.

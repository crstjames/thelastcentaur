# Docker Deployment for The Last Centaur

This directory contains Docker configuration files for deploying The Last Centaur application.

## Directory Contents

- `Dockerfile` - Backend API service configuration
- `Dockerfile.frontend` - Frontend web service configuration
- `docker-compose.yml` - Production deployment configuration
- `docker-compose.dev.yml` - Development environment configuration
- `nginx.conf` - Nginx configuration for the frontend
- `.env.example` - Example environment variables
- `deploy.sh` - Deployment script

## Development Setup

To run the application in development mode with hot reloading:

1. Copy the example environment file:

   ```bash
   cp docker/.env.example docker/.env
   ```

2. Edit the `.env` file with your API keys and configuration.

3. Start the development environment:

   ```bash
   cd docker
   docker-compose -f docker-compose.dev.yml up
   ```

4. Access the application:
   - Backend API: http://localhost:8000
   - Frontend: http://localhost:3000

## Production Deployment

### Prerequisites

- Docker and Docker Compose installed on your server
- Git access to the repository
- Domain name (optional, but recommended)

### Deployment Steps

1. Clone the repository on your server:

   ```bash
   git clone https://github.com/yourusername/thelastcentaur.git
   cd thelastcentaur
   ```

2. Copy and configure the environment file:

   ```bash
   cp docker/.env.example docker/.env
   nano docker/.env  # Edit with your production settings
   ```

3. Run the deployment script:

   ```bash
   cd docker
   ./deploy.sh
   ```

4. Access your application at the configured domain or server IP.

### Manual Deployment

If you prefer to deploy manually:

1. Build the Docker images:

   ```bash
   cd docker
   docker-compose -f docker-compose.yml build
   ```

2. Start the services:

   ```bash
   docker-compose -f docker-compose.yml up -d
   ```

3. Run database migrations:
   ```bash
   docker-compose -f docker-compose.yml exec app alembic upgrade head
   ```

## Configuration Options

### Environment Variables

- `POSTGRES_USER` - PostgreSQL username
- `POSTGRES_PASSWORD` - PostgreSQL password
- `POSTGRES_SERVER` - PostgreSQL server hostname
- `POSTGRES_DB` - PostgreSQL database name
- `SECRET_KEY` - Secret key for JWT tokens and encryption
- `ENVIRONMENT` - Application environment (development/production)
- `OPENAI_API_KEY` - OpenAI API key for LLM interface
- `ANTHROPIC_API_KEY` - Anthropic API key for LLM interface
- `DOMAIN` - Your domain name for production deployment

## Troubleshooting

### Common Issues

1. **Database connection errors**:

   - Check that the PostgreSQL container is running: `docker ps`
   - Verify database credentials in the `.env` file

2. **API key issues**:

   - Ensure your OpenAI and Anthropic API keys are correctly set in the `.env` file

3. **Port conflicts**:
   - If ports 80 or 8000 are already in use, modify the port mappings in `docker-compose.yml`

### Logs

To view logs for troubleshooting:

```bash
# View logs for all services
docker-compose -f docker-compose.yml logs

# View logs for a specific service
docker-compose -f docker-compose.yml logs app
docker-compose -f docker-compose.yml logs web
```

## Updating the Application

To update to the latest version:

```bash
cd docker
./deploy.sh
```

This will pull the latest changes, rebuild the containers, and run any necessary migrations.

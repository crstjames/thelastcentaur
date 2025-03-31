import uvicorn
import socket
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncpg
import os
import traceback

from src.core.config import settings
from src.api.routes import api_router
from src.db.session import engine, get_db
from src.db.base import Base
from src.game.websocket import handle_game_websocket

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Try to create the database if it doesn't exist
    try:
        # Connect to the default postgres database
        conn = await asyncpg.connect(
            user=settings.POSTGRES_USER,
            password=settings.POSTGRES_PASSWORD,
            host=settings.POSTGRES_SERVER,
            database="postgres"  # Connect to default database first
        )
        
        # Check if our database exists
        result = await conn.fetchrow(
            "SELECT 1 FROM pg_database WHERE datname = $1",
            settings.POSTGRES_DB
        )
        
        # If database doesn't exist, create it
        if not result:
            print(f"Database '{settings.POSTGRES_DB}' does not exist. Creating...")
            # We need to be careful with SQL injection here, but since this is a constant from settings, it's safe
            await conn.execute(f"CREATE DATABASE {settings.POSTGRES_DB}")
            print(f"Database '{settings.POSTGRES_DB}' created successfully.")
        
        await conn.close()
    except Exception as e:
        print(f"Warning: Could not check/create database: {e}")
        print("Continuing startup process...")
    
    try:
        # Create database tables
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("Database tables created successfully.")
    except Exception as e:
        print(f"Error creating database tables: {e}")
        print("Application may not function correctly without database tables.")
    
    yield
    
    # Close database connections on shutdown
    try:
        await engine.dispose()
    except Exception as e:
        print(f"Error disposing database engine: {e}")

app = FastAPI(
    title="The Last Centaur API",
    description="API for The Last Centaur game",
    version="0.1.0",
    lifespan=lifespan,
    debug=True,  # Enable debug mode
)

# Configure CORS
origins = []
# Add localhost origins by default
for port in ["3000", "3001", "3002", "3003", "3005", "5173", "5174"]:
    origins.extend([f"http://localhost:{port}", f"http://127.0.0.1:{port}"])

# Add origins from settings.CORS_ORIGINS environment variable if it exists
cors_origins_env = os.getenv("CORS_ORIGINS", "")
if cors_origins_env:
    origins.extend([origin.strip() for origin in cors_origins_env.split(",") if origin.strip()])

print(f"CORS origins configured: {origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Exception handler for debug output
@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    print(f"ERROR in request {request.url.path}: {exc}")
    print(traceback.format_exc())
    return {"detail": str(exc), "traceback": traceback.format_exc()}

# Include routers
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    return {
        "message": "Welcome to The Last Centaur API",
        "version": "2.0.0",
        "status": "online"
    }

@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}

@app.websocket("/ws/game/{game_id}")
async def websocket_endpoint(websocket: WebSocket, game_id: str):
    """WebSocket endpoint for game connections."""
    await handle_game_websocket(websocket, game_id)

def find_available_port(start_port=8000, max_port=8100):
    """Find an available port starting from start_port up to max_port."""
    for port in range(start_port, max_port + 1):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            result = sock.connect_ex(('localhost', port))
            if result != 0:  # Port is available
                return port
    raise RuntimeError(f"Could not find an available port in range {start_port}-{max_port}")

if __name__ == "__main__":
    try:
        # Try the default port first
        port = 8000
        try:
            # Check if the default port is available
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                result = sock.connect_ex(('localhost', port))
                if result == 0:  # Port is in use
                    # Find an available port
                    port = find_available_port()
                    print(f"Port 8000 is in use. Using port {port} instead.")
        except Exception as e:
            print(f"Error checking port availability: {e}")
            # Fall back to finding an available port
            port = find_available_port()
            
        # Run the application
        uvicorn.run(
            "src.main:app",
            host="0.0.0.0",
            port=port,
            reload=True,
        )
    except Exception as e:
        print(f"Failed to start the application: {e}") 
from fastapi import APIRouter

from src.auth.router import router as auth_router
from src.game.router import router as game_router
# Uncomment the admin routes import now that we've fixed the issues
from src.game.admin_routes import router as admin_router

api_router = APIRouter()

# Include auth routes
api_router.include_router(
    auth_router,
    prefix="/auth",
    tags=["auth"]
)

# Include game routes
api_router.include_router(
    game_router,
    prefix="/game",
    tags=["game"]
)

# Uncomment the admin routes inclusion now that we've fixed the issues
# Include admin routes
api_router.include_router(
    admin_router,
    prefix="/admin",
    tags=["admin"]
) 
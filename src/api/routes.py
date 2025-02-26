from fastapi import APIRouter

from src.auth.router import router as auth_router
from src.game.router import router as game_router

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
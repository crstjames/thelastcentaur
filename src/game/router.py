from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, WebSocket
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
import uuid
from datetime import datetime

from src.auth.deps import get_current_user
from src.db.session import get_db
from src.db.models import User, GameInstance, Tile, TileHistory
from src.game.schemas import (
    GameInstanceCreate, 
    GameInstanceUpdate, 
    GameInstanceResponse,
    GameCommandRequest,
    GameCommandResponse,
    MapResponse,
    TileResponse,
    GameStatus
)
from src.game.state_manager import GameStateManager

router = APIRouter()
game_state_manager = GameStateManager()

@router.post("", response_model=GameInstanceResponse)
async def create_game_instance(
    game_data: GameInstanceCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new game instance."""
    # Initialize game_state with status and description since description column doesn't exist
    game_state = {
        "status": GameStatus.ACTIVE.value,
        "description": game_data.description
    }
    
    # Only use fields we know exist in the database
    game_instance = GameInstance(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        name=game_data.name,
        is_active=True,
        current_position={"x": 0, "y": 0},
        game_state=game_state,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    db.add(game_instance)
    await db.commit()
    await db.refresh(game_instance)
    
    # Initialize the game world
    await game_state_manager.initialize_game_instance(game_instance.id, db)
    
    return game_instance

@router.get("", response_model=List[GameInstanceResponse])
async def list_game_instances(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all game instances for the current user."""
    result = await db.execute(
        select(GameInstance).where(GameInstance.user_id == current_user.id)
    )
    game_instances = result.scalars().all()
    return game_instances

@router.get("/{game_id}", response_model=GameInstanceResponse)
async def get_game_instance(
    game_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific game instance."""
    result = await db.execute(
        select(GameInstance).where(
            GameInstance.id == game_id,
            GameInstance.user_id == current_user.id
        )
    )
    game_instance = result.scalars().first()
    
    if not game_instance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game instance not found"
        )
    
    return game_instance

@router.put("/{game_id}", response_model=GameInstanceResponse)
async def update_game_instance(
    game_id: str,
    game_data: GameInstanceUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a game instance."""
    result = await db.execute(
        select(GameInstance).where(
            GameInstance.id == game_id,
            GameInstance.user_id == current_user.id
        )
    )
    game_instance = result.scalars().first()
    
    if not game_instance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game instance not found"
        )
    
    update_data = game_data.dict(exclude_unset=True)
    
    # Handle status updates by storing in both is_active and game_state
    if "status" in update_data:
        status_value = update_data.pop("status")
        # Update is_active for backward compatibility
        update_data["is_active"] = (status_value == GameStatus.ACTIVE)
        
        # Update game_state with status
        game_state = dict(game_instance.game_state) if game_instance.game_state else {}
        game_state["status"] = status_value.value if isinstance(status_value, GameStatus) else status_value
        update_data["game_state"] = game_state
    
    for key, value in update_data.items():
        setattr(game_instance, key, value)
    
    game_instance.updated_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(game_instance)
    
    return game_instance

@router.delete("/{game_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_game_instance(
    game_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a game instance."""
    result = await db.execute(
        select(GameInstance).where(
            GameInstance.id == game_id,
            GameInstance.user_id == current_user.id
        )
    )
    game_instance = result.scalars().first()
    
    if not game_instance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game instance not found"
        )
    
    # First get all tiles for this game
    tile_result = await db.execute(
        select(Tile.id).where(Tile.game_instance_id == game_id)
    )
    tile_ids = [tile_id for tile_id, in tile_result]
    
    # Delete related tile history records
    if tile_ids:
        await db.execute(
            delete(TileHistory).where(TileHistory.tile_id.in_(tile_ids))
        )
    
    # Delete related tiles
    await db.execute(
        delete(Tile).where(Tile.game_instance_id == game_id)
    )
    
    # Finally delete the game instance
    await db.delete(game_instance)
    await db.commit()
    
    return None

@router.post("/{game_id}/command", response_model=GameCommandResponse)
async def execute_command(
    game_id: str,
    command_data: GameCommandRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Execute a command on a game instance."""
    result = await db.execute(
        select(GameInstance).where(
            GameInstance.id == game_id,
            GameInstance.user_id == current_user.id
        )
    )
    game_instance = result.scalars().first()
    
    if not game_instance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game instance not found"
        )
    
    # Load the game state if not already loaded
    await game_state_manager.load_game_instance(game_id, db)
    
    # Execute the command
    command_result = await game_state_manager.execute_command(
        game_id, 
        command_data.command
    )
    
    # Create response
    response = GameCommandResponse(
        command=command_data.command,
        response=command_result,
        game_id=game_id,
        timestamp=datetime.utcnow()
    )
    
    return response

@router.get("/{game_id}/map", response_model=MapResponse)
async def get_game_map(
    game_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get the current game map."""
    result = await db.execute(
        select(GameInstance).where(
            GameInstance.id == game_id,
            GameInstance.user_id == current_user.id
        )
    )
    game_instance = result.scalars().first()
    
    if not game_instance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game instance not found"
        )
    
    # Load the game state if not already loaded
    await game_state_manager.load_game_instance(game_id, db)
    
    # Get the map
    map_data = await game_state_manager.get_map(game_id)
    
    return map_data 
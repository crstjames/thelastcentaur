from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
import uuid
from datetime import datetime
import os

from src.auth.deps import get_current_user
from src.db.session import get_db
from src.db.models import User, GameInstance, Tile
from src.game.schemas import (
    GameInstanceCreate, 
    GameInstanceUpdate, 
    GameInstanceResponse,
    GameCommandRequest,
    GameCommandResponse,
    MapResponse,
    TileResponse
)
from src.game.state_manager import GameStateManager
from src.core.config import settings

router = APIRouter()
game_state_manager = GameStateManager()

@router.post("", response_model=GameInstanceResponse)
async def create_game_instance(
    game_data: GameInstanceCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new game instance."""
    game_instance = GameInstance(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        name=game_data.name,
        status="ACTIVE",
        max_players=game_data.max_players,
        current_players=1,
        description=game_data.description,
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
    
    # Import LLMInterface here to avoid circular imports
    from src.game.llm_interface import LLMInterface
    
    # Get OpenAI API key from environment
    openai_api_key = os.environ.get("OPENAI_API_KEY")
    if not openai_api_key:
        # Log warning and return basic response if no API key
        print("WARNING: No OpenAI API key found. LLM enhancement disabled.")
        
        # Load the game state if not already loaded
        await game_state_manager.load_game_instance(game_id, db)
        
        # Execute the command directly
        command_result = await game_state_manager.execute_command(
            game_id, 
            command_data.command
        )
        
        # Create response without enhancement
        response = GameCommandResponse(
            command=command_data.command,
            response=command_result,
            game_id=game_id,
            timestamp=datetime.utcnow()
        )
        
        return response
    
    # Create LLM interface instance
    llm_interface = LLMInterface(api_base_url="", api_port=8000)
    
    try:
        # Load the game state if not already loaded
        await game_state_manager.load_game_instance(game_id, db)
        
        # Get current game state for context
        game_state = await game_state_manager.get_game_state(game_id)
        
        # First, interpret the natural language command
        user_input = command_data.command
        game_command = await llm_interface._interpret_command(user_input, game_state)
        
        # Execute the command
        command_result = await game_state_manager.execute_command(
            game_id, 
            game_command
        )
        
        # Enhance the response with LLM
        enhanced_response = await llm_interface._enhance_response(
            command_result, 
            user_input, 
            game_command
        )
        
        # Create response
        response = GameCommandResponse(
            command=command_data.command,
            response=enhanced_response,  # Use the enhanced response
            game_id=game_id,
            timestamp=datetime.utcnow()
        )
        
        return response
    except Exception as e:
        # Log the error but provide a fallback response
        print(f"Error processing command: {str(e)}")
        
        # Execute the command directly as fallback
        command_result = await game_state_manager.execute_command(
            game_id, 
            command_data.command
        )
        
        # Create response with original result
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
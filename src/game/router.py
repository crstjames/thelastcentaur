from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, Request, File, UploadFile, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse, StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
import uuid
from datetime import datetime
import os
import traceback
import random

from src.auth.deps import get_current_user
from src.db.session import get_db
from src.db.models import User, GameInstance, Tile, TileHistory, GameStatus
from src.core.config import settings
from src.core.models import Direction, TerrainType, StoryArea
from src.game.schemas import (
    GameInstanceCreate, 
    GameInstanceUpdate, 
    GameInstanceResponse,
    GameCommandRequest,
    GameCommandResponse,
    MapResponse,
    TileResponse,
    CommandData
)
from src.game.state_manager import GameStateManager
from src.engine.core.command_parser import CommandParser, CommandType
from src.game.command_service import CommandService
from src.game.llm_interface import LLMInterface
from src.engine.core.player import Player
from src.engine.core.map_system import MapManager

router = APIRouter(
    prefix="/game",
    tags=["game"],
    responses={404: {"description": "Not found"}},
)
game_state_manager = GameStateManager()

# Instead of creating a global CommandParser, we'll create one for each game instance
# Remove the global command_parser
# command_parser = CommandParser(game_state_manager)

# Update the command service getter to create a CommandParser on demand
async def get_command_service(game_id: str, db: AsyncSession = Depends(get_db)) -> CommandService:
    """Get a command service instance for a specific game."""
    # Load the game instance
    await game_state_manager.load_game_instance(game_id, db)
    
    # Get the player for this game instance
    if game_id in game_state_manager._loaded_instances:
        player = game_state_manager._loaded_instances[game_id]["player"]
        # Create a command parser for this specific player
        command_parser = CommandParser(player)
        return CommandService(command_parser, db)
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game instance not found"
        )

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
    print(f"ROUTER-DEBUG: API endpoint: execute_command called for game_id: {game_id}")
    
    result = await db.execute(
        select(GameInstance).where(
            GameInstance.id == game_id,
            GameInstance.user_id == current_user.id
        )
    )
    game_instance = result.scalars().first()
    
    if not game_instance:
        print(f"ROUTER-DEBUG: Game instance not found for game_id: {game_id}, user_id: {current_user.id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game instance not found"
        )
    
    # Always load the game instance first, regardless of LLM usage
    print(f"ROUTER-DEBUG: Loading game instance for game_id: {game_id}")
    loaded_instance = await game_state_manager.load_game_instance(game_id, db)
    
    if not loaded_instance:
        print(f"ROUTER-DEBUG: Failed to load game instance for game_id: {game_id}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to load game instance"
        )
    
    # Check if we should bypass LLM processing
    if not command_data.use_llm or not os.environ.get("OPENAI_API_KEY"):
        if not os.environ.get("OPENAI_API_KEY") and command_data.use_llm:
            # Log warning if LLM was requested but API key is missing
            print("ROUTER-DEBUG: No OpenAI API key found. LLM enhancement disabled.")
        
        print(f"ROUTER-DEBUG: Executing command: {command_data.command}")
        # IMPORTANT: Before executing the command directly, try to interpret it using LLM if possible
        try:
            # Get current game state for context
            game_state = await game_state_manager.get_game_state(game_id)
            print(f"ROUTER-DEBUG: Current game state: {game_state}")
            
            # Try to interpret the command
            if os.environ.get("OPENAI_API_KEY"):
                print(f"ROUTER-DEBUG: Using LLM to interpret command: {command_data.command}")
                interpreted_command = await LLMInterface(api_base_url="http://localhost:8000")._interpret_command(command_data.command, game_state)
                print(f"ROUTER-DEBUG: LLM interpreted command: {interpreted_command}")
                # Use interpreted command instead
                command_to_execute = interpreted_command
            else:
                # No API key, use original command
                print(f"ROUTER-DEBUG: No API key available, using original command")
                command_to_execute = command_data.command
                
        except Exception as e:
            print(f"ROUTER-DEBUG: ERROR using LLM to interpret command: {str(e)}")
            traceback.print_exc()  # Add full traceback for debugging
            # Fall back to original command if interpretation fails
            command_to_execute = command_data.command
            
        # Execute the command with our command_service
        try:
            print(f"ROUTER-DEBUG: Executing command: {command_to_execute}")
            # Get command service specific to this game
            command_service = await get_command_service(game_id, db)
            result = await command_service.process_command(command_to_execute, game_id, db)
            print(f"ROUTER-DEBUG: Command result: {result}")
            
            # Track command in history
            await game_state_manager.add_command_to_history(
                game_id=game_id,
                command=command_data.command,
                result=result,
                db=db
            )
            
            # Return the result
            return {
                "command": command_data.command,
                "response": result,
                "game_id": game_id,
                "timestamp": datetime.now()
            }
            
        except Exception as e:
            print(f"ROUTER-DEBUG: Error processing command: {str(e)}")
            traceback.print_exc()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error processing command: {str(e)}"
            )
    
    # If we're here, we should use the LLM to process the command
    print(f"ROUTER-DEBUG: Using LLM for command processing: {command_data.command}")
    
    try:
        # Use LLMInterface which was already imported earlier
        # Create an LLM interface instance with the required api_base_url parameter
        llm_interface = LLMInterface(api_base_url="http://localhost:8000")
        
        # Process the command with the LLM
        print(f"ROUTER-DEBUG: Processing command with LLM: {command_data.command}")
        # Get current game state for context
        game_state = await game_state_manager.get_game_state(game_id)
        
        # Use the _interpret_command method to process the command
        interpreted_command = await llm_interface._interpret_command(command_data.command, game_state)
        print(f"ROUTER-DEBUG: LLM interpreted command: {interpreted_command}")
        
        # Proceed with the interpreted command
        command_to_execute = interpreted_command or command_data.command
        
        # Execute the command with our command_service
        try:
            print(f"ROUTER-DEBUG: Executing command: {command_to_execute}")
            # Get command service specific to this game
            command_service = await get_command_service(game_id, db)
            result = await command_service.process_command(command_to_execute, game_id, db)
            print(f"ROUTER-DEBUG: Command result: {result}")
            
            # Track command in history
            await game_state_manager.add_command_to_history(
                game_id=game_id,
                command=command_data.command,
                result=result,
                db=db
            )
            
            # Return the result
            return {
                "command": command_data.command,
                "response": result,
                "game_id": game_id,
                "timestamp": datetime.now()
            }
            
        except Exception as e:
            print(f"ROUTER-DEBUG: Error processing command: {str(e)}")
            traceback.print_exc()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error processing command: {str(e)}"
            )
    except Exception as e:
        print(f"ROUTER-DEBUG: Error using LLM to process command: {str(e)}")
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error using LLM to process command: {str(e)}"
        )

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

@router.post("/command/{game_id}")
async def process_command(
    game_id: str,
    command_data: CommandData,
    db: AsyncSession = Depends(get_db)
):
    """Process a game command for a specific game instance."""
    print(f"\n\n==== ROUTER-DEBUG: Received command request for game_id: {game_id}, command: {command_data.command} ====\n\n")
    
    result = await db.execute(
        select(GameInstance).where(
            GameInstance.id == game_id,
            GameInstance.user_id == command_data.user_id
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
    
    # Process the command
    print(f"ROUTER-DEBUG: Processing command: {command_data.command}")
    result = await game_state_manager.process_command(game_id, command_data.command, db)
    print(f"ROUTER-DEBUG: Command processing result: {result}")
    
    # Track command in history
    await game_state_manager.add_command_to_history(
        game_id=game_id,
        command=command_data.command,
        result=result,
        db=db
    )
    
    return {"result": result} 
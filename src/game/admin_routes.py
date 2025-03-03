"""
Admin-only routes for The Last Centaur.

These routes are for testing and debugging purposes only and should not be exposed in production.
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.deps import get_current_user
from src.db.session import get_db
from src.db.models import GameInstance, User
from src.game.llm_interface import LLMInterface
from src.engine.core.map_system import GAME_MAP
from src.engine.core.enemies import ENEMIES

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(tags=["admin"], prefix="/admin")

# Use the same OAuth2 scheme as the main API
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Only allow admin routes in development or test
ENVIRONMENT = os.environ.get("ENVIRONMENT", "dev").lower()
ADMIN_ENABLED = ENVIRONMENT in ("dev", "test")

# Check if caller is allowed to use admin routes
async def verify_admin_access(token: str = Depends(oauth2_scheme)):
    """
    Verify that the caller is allowed to use admin routes.
    
    Admin routes are only available in development or test environments.
    """
    if not ADMIN_ENABLED:
        logger.warning(f"Admin routes accessed in {ENVIRONMENT} environment")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin routes are disabled in this environment"
        )
    
    # Get current user from token
    user = await get_current_user(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    return user

@router.post("/game/{game_id}/inventory/add", response_model=Dict[str, Any])
async def add_item_to_inventory(
    game_id: str,
    item: Dict[str, str] = Body(...),
    user: Dict[str, Any] = Depends(verify_admin_access),
    db: AsyncSession = Depends(get_db)
):
    """
    Admin route to add an item to the player's inventory.
    
    Args:
        game_id: The game ID
        item: Dictionary with "item" key containing the item name
        
    Returns:
        Success message
    """
    # Check if game exists and belongs to user
    result = await db.execute(
        select(GameInstance).where(
            GameInstance.id == game_id,
            GameInstance.user_id == user["id"]
        )
    )
    game_instance = result.scalar_one_or_none()
    
    if not game_instance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found"
        )
    
    # Get the item name
    item_name = item.get("item")
    if not item_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Item name is required"
        )
    
    logger.info(f"Adding item {item_name} to inventory for game {game_id}")
    
    # Get current inventory
    inventory = []
    if game_instance.game_state and "inventory" in game_instance.game_state:
        inventory = game_instance.game_state["inventory"]
    
    # Add item to inventory if not already present
    if item_name not in inventory:
        inventory.append(item_name)
        
        # Update game state
        if game_instance.game_state and "inventory" in game_instance.game_state:
            game_instance.game_state["inventory"] = inventory
            
        # Save game instance
        await db.commit()
        
        return {"success": True, "message": f"Item {item_name} added to inventory", "inventory": inventory}
    else:
        return {"success": True, "message": f"Item {item_name} already in inventory", "inventory": inventory}

@router.post("/game/{game_id}/teleport", response_model=Dict[str, Any])
async def teleport_to_area(
    game_id: str,
    area: Dict[str, str] = Body(...),
    user: Dict[str, Any] = Depends(verify_admin_access),
    db: AsyncSession = Depends(get_db)
):
    """
    Admin route to teleport the player to a specific area.
    
    Args:
        game_id: The game ID
        area: Dictionary with "area" key containing the area name
        
    Returns:
        Success message
    """
    # Check if game exists and belongs to user
    result = await db.execute(
        select(GameInstance).where(
            GameInstance.id == game_id,
            GameInstance.user_id == user["id"]
        )
    )
    game_instance = result.scalar_one_or_none()
    
    if not game_instance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found"
        )
    
    # Get the area name
    area_name = area.get("area")
    if not area_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Area name is required"
        )
    
    logger.info(f"Teleporting to area {area_name} for game {game_id}")
    
    # Create LLM interface
    llm_interface = LLMInterface()
    
    # Execute debug teleport command
    try:
        command_result = await llm_interface._execute_direct_command(
            f"debug teleport {area_name}", 
            game_id, 
            user["access_token"]
        )
        
        return {
            "success": True, 
            "message": f"Teleported to {area_name}", 
            "command_result": command_result
        }
    except Exception as e:
        logger.error(f"Error teleporting to {area_name}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error teleporting to {area_name}: {str(e)}"
        )

@router.post("/game/{game_id}/defeat_enemy", response_model=Dict[str, Any])
async def defeat_enemy(
    game_id: str,
    enemy: Dict[str, str] = Body(...),
    user: Dict[str, Any] = Depends(verify_admin_access),
    db: AsyncSession = Depends(get_db)
):
    """
    Admin route to defeat an enemy instantly.
    
    Args:
        game_id: The game ID
        enemy: Dictionary with "enemy" key containing the enemy name
        
    Returns:
        Success message
    """
    # Check if game exists and belongs to user
    result = await db.execute(
        select(GameInstance).where(
            GameInstance.id == game_id,
            GameInstance.user_id == user["id"]
        )
    )
    game_instance = result.scalar_one_or_none()
    
    if not game_instance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found"
        )
    
    # Get the enemy name
    enemy_name = enemy.get("enemy")
    if not enemy_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Enemy name is required"
        )
    
    logger.info(f"Defeating enemy {enemy_name} for game {game_id}")
    
    # Create LLM interface
    llm_interface = LLMInterface()
    
    # Execute debug defeat enemy command
    try:
        command_result = await llm_interface._execute_direct_command(
            f"debug defeat {enemy_name}", 
            game_id, 
            user["access_token"]
        )
        
        return {
            "success": True, 
            "message": f"Defeated {enemy_name}", 
            "command_result": command_result
        }
    except Exception as e:
        logger.error(f"Error defeating {enemy_name}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error defeating {enemy_name}: {str(e)}"
        )

@router.get("/game/{game_id}", response_model=Dict[str, Any])
async def get_game_state(
    game_id: str,
    user: Dict[str, Any] = Depends(verify_admin_access),
    db: AsyncSession = Depends(get_db)
):
    """
    Get the current state of a game instance.
    """
    result = await db.execute(
        select(GameInstance).where(
            GameInstance.id == game_id,
            GameInstance.user_id == user["id"]
        )
    )
    game_instance = result.scalar_one_or_none()
    
    if not game_instance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game instance not found"
        )
    
    return {
        "id": game_instance.id,
        "name": game_instance.name,
        "status": game_instance.status,
        "current_position": game_instance.current_position,
        "game_state": game_instance.game_state
    }

class AdminCommandRequest(BaseModel):
    """Request model for admin commands"""
    command: str

@router.post("/debug/command", response_model=Dict[str, Any])
async def execute_debug_command(
    request: AdminCommandRequest,
    user: Dict[str, Any] = Depends(verify_admin_access),
    db: AsyncSession = Depends(get_db)
):
    """
    Execute a debug command for testing purposes.
    Only available in development mode.
    """
    if not user.get("is_superuser", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to use debug commands"
        )
    
    try:
        result = await db.execute(
            select(GameInstance).where(
                GameInstance.id == request.game_id,
                GameInstance.user_id == user["id"]
            )
        )
        game_instance = result.scalar_one_or_none()
        
        if not game_instance:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Game instance not found"
            )
        
        # Process debug command
        command_parts = request.command.split()
        command_type = command_parts[0] if command_parts else ""
        
        response = {"message": "Debug command executed", "result": None}
        
        if command_type == "debug_add_item":
            if len(command_parts) < 2:
                response["result"] = "Error: Item name required"
            else:
                item_name = command_parts[1]
                if "inventory" not in game_instance.game_state:
                    game_instance.game_state["inventory"] = []
                
                game_instance.game_state["inventory"].append(item_name)
                await db.commit()
                response["result"] = f"Added {item_name} to inventory"
        
        elif command_type == "debug_teleport":
            if len(command_parts) < 3:
                response["result"] = "Error: Coordinates required (x y)"
            else:
                try:
                    x = int(command_parts[1])
                    y = int(command_parts[2])
                    game_instance.game_state["player_position"] = [x, y]
                    game_instance.current_position = {"x": x, "y": y}
                    await db.commit()
                    response["result"] = f"Teleported to ({x}, {y})"
                except ValueError:
                    response["result"] = "Error: Invalid coordinates"
        
        else:
            response["result"] = f"Unknown debug command: {command_type}"
        
        return response
    
    except Exception as e:
        logger.error(f"Error executing debug command: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error executing debug command: {str(e)}"
        )

@router.post("/game/{game_id}/force_item", response_model=Dict[str, Any])
async def force_add_item(
    game_id: str,
    item_data: Dict[str, str] = Body(...),
    user: Dict[str, Any] = Depends(verify_admin_access),
    db: AsyncSession = Depends(get_db)
):
    """
    Admin route to force-add an item to the player's inventory.
    
    Args:
        game_id: The game ID
        item_data: Dictionary with "item_name" key containing the item name
        
    Returns:
        Success message
    """
    # Check if game exists and belongs to user
    result = await db.execute(
        select(GameInstance).where(
            GameInstance.id == game_id,
            GameInstance.user_id == user["id"]
        )
    )
    game_instance = result.scalar_one_or_none()
    
    if not game_instance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found"
        )
    
    # Get the item name
    item_name = item_data.get("item_name")
    if not item_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Item name is required"
        )
    
    logger.info(f"Force-adding item {item_name} to inventory for game {game_id}")
    
    # Get current inventory
    inventory = []
    if game_instance.game_state and "inventory" in game_instance.game_state:
        inventory = game_instance.game_state["inventory"]
    
    # Add item to inventory if not already present
    if item_name not in inventory:
        inventory.append(item_name)
        
        # Update game state
        if game_instance.game_state and "inventory" in game_instance.game_state:
            game_instance.game_state["inventory"] = inventory
            
        # Save game instance
        await db.commit()
        
        return {"success": True, "message": f"Item {item_name} added to inventory", "inventory": inventory}
    else:
        return {"success": True, "message": f"Item {item_name} already in inventory", "inventory": inventory}

@router.get("/debug_game_state/{game_id}")
async def debug_game_state(
    game_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Debug endpoint to check the game state"""
    # Get the game instance
    result = await db.execute(
        select(GameInstance).where(
            GameInstance.id == game_id,
            GameInstance.user_id == current_user.id
        )
    )
    game_instance = result.scalars().first()
    
    if not game_instance:
        raise HTTPException(status_code=404, detail="Game not found")
    
    # Get current tile enemies
    position = game_instance.current_position
    position_str = f"{position[0]},{position[1]}"
    
    # Create response
    response = {
        "game_id": game_id,
        "position": position,
        "tile_exists_in_map": position_str in GAME_MAP,
        "enemies_in_tile": []
    }
    
    if position_str in GAME_MAP:
        tile = GAME_MAP[position_str]
        response["enemies_in_tile"] = tile.enemies
        response["tile_description"] = tile.get_description()
        
        # Check if phantom_assassin is in ENEMIES
        response["phantom_in_enemies"] = "phantom_assassin" in ENEMIES
        response["enemies_keys"] = list(ENEMIES.keys())
        
    return response 
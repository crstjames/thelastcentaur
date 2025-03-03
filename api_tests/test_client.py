"""
TestGameClient for The Last Centaur API Tests.

This module provides a client for testing The Last Centaur game through its API,
with robust error handling and detailed logging.
"""

import os
import sys
import json
import logging
import asyncio
import httpx
from typing import Dict, List, Optional, Union, Any
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("thelastcentaur_api_tests")

class TestGameClient:
    """Client for making API calls to The Last Centaur game."""
    
    def __init__(self, api_base_url: str = "http://localhost:8000", log_responses: bool = True):
        """
        Initialize the TestGameClient.
        
        Args:
            api_base_url: Base URL for the game API
            log_responses: Whether to log API responses (default: True)
        """
        self.api_base_url = api_base_url
        self.access_token = None
        self.game_id = None
        self.user_id = None
        self.session = httpx.AsyncClient(timeout=30.0)  # Longer timeout for stability
        self.log_responses = log_responses
        self.command_history = []
        
    async def login(self, username: str = "test_player") -> str:
        """
        Create a user and log in to obtain access token.
        
        Args:
            username: Username for the test player
            
        Returns:
            Access token string
        
        Raises:
            httpx.HTTPStatusError: If the API request fails
        """
        logger.info(f"Attempting login with username: {username}")
        try:
            # First try to register the user
            try:
                register_response = await self.session.post(
                    f"{self.api_base_url}/api/v1/auth/register",
                    json={
                        "username": username,
                        "email": f"{username}@example.com",
                        "password": "password123"
                    }
                )
                register_response.raise_for_status()
                user_data = register_response.json()
                self.user_id = user_data["id"]
                logger.info(f"User {username} registered successfully with ID: {self.user_id}")
            except httpx.HTTPStatusError as e:
                # If user already exists, that's fine
                if e.response.status_code != 400:
                    raise
                logger.info(f"User {username} already exists")
                
                # If we couldn't register, try to get the user ID by creating a game
                # This is a workaround to get the user ID
                self.access_token = await self._login_only(username)
                
                # Add the token to future requests
                self.session.headers.update({"Authorization": f"Bearer {self.access_token}"})
                
                # Create a temporary game to get the user ID
                try:
                    game_response = await self.session.post(
                        f"{self.api_base_url}/api/v1/game",
                        json={"name": f"temp_game_{username}"}
                    )
                    game_response.raise_for_status()
                    game_data = game_response.json()
                    self.user_id = game_data["id"]
                    logger.info(f"Retrieved user ID from game creation: {self.user_id}")
                    
                    # Delete the temporary game
                    temp_game_id = game_data["id"]
                    await self.session.delete(f"{self.api_base_url}/api/v1/game/{temp_game_id}")
                    logger.info(f"Deleted temporary game: {temp_game_id}")
                except Exception as e:
                    logger.error(f"Failed to get user ID from game creation: {e}")
                    # If we can't get the user ID, generate a random one
                    import uuid
                    self.user_id = str(uuid.uuid4())
                    logger.warning(f"Using generated user ID: {self.user_id}")
                
                return self.access_token
            
            # If we registered successfully, login
            self.access_token = await self._login_only(username)
            return self.access_token
            
        except httpx.HTTPStatusError as e:
            status_code = e.response.status_code
            error_detail = e.response.text
            logger.error(f"Login failed with status {status_code}: {error_detail}")
            raise
        except Exception as e:
            logger.error(f"Login failed with unexpected error: {e}")
            raise
    
    async def _login_only(self, username: str) -> str:
        """
        Login only without registration.
        
        Args:
            username: Username for the test player
            
        Returns:
            Access token string
        """
        response = await self.session.post(
            f"{self.api_base_url}/api/v1/auth/login",
            data={"username": username, "password": "password123"}
        )
        response.raise_for_status()
        
        data = response.json()
        access_token = data["access_token"]
        
        # Add the token to future requests
        self.session.headers.update({"Authorization": f"Bearer {access_token}"})
        
        logger.info(f"Login successful for {username}")
        return access_token
    
    async def create_game(self) -> str:
        """
        Create a new game instance.
        
        Returns:
            Game ID string
            
        Raises:
            httpx.HTTPStatusError: If the API request fails
        """
        logger.info("Creating new game instance")
        try:
            response = await self.session.post(
                f"{self.api_base_url}/api/v1/game",
                json={
                    "name": f"Test Game {int(time.time())}",
                    "description": "Test game for API testing"
                }
            )
            response.raise_for_status()
            
            data = response.json()
            self.game_id = data["id"]
            logger.info(f"Game created with ID: {self.game_id}")
            return self.game_id
        except httpx.HTTPStatusError as e:
            logger.error(f"Game creation failed with status {e.response.status_code}: {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Game creation failed with unexpected error: {str(e)}")
            raise
    
    async def send_command(self, command: str, retry_count: int = 3, retry_delay: float = 1.0) -> str:
        """
        Send a command to the game.
        
        Args:
            command: Command string to send
            retry_count: Number of retries on failure
            retry_delay: Delay between retries in seconds
            
        Returns:
            Response string from the game
            
        Raises:
            httpx.HTTPStatusError: If the API request fails after retries
            ValueError: If no game ID is available
        """
        if not self.game_id:
            raise ValueError("No game ID available. Call create_game() first.")
            
        self.command_history.append(command)
        logger.info(f"Sending command: {command}")
        
        attempt = 0
        last_error = None
        
        while attempt < retry_count:
            try:
                response = await self.session.post(
                    f"{self.api_base_url}/api/v1/game/{self.game_id}/command",
                    json={"command": command}
                )
                response.raise_for_status()
                data = response.json()
                game_response = data["response"]
                
                if self.log_responses:
                    logger.info(f"Response received: '{game_response}'")
                    
                return game_response
            except httpx.HTTPStatusError as e:
                last_error = e
                logger.warning(f"Command '{command}' failed (attempt {attempt}/{retry_count}) "
                               f"with status {e.response.status_code}: {e.response.text}")
                
                if attempt < retry_count:
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 1.5  # Exponential backoff
            except Exception as e:
                last_error = e
                logger.warning(f"Command '{command}' failed (attempt {attempt}/{retry_count}) "
                               f"with unexpected error: {str(e)}")
                
                if attempt < retry_count:
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 1.5  # Exponential backoff
                    
        # All retries failed
        logger.error(f"Command '{command}' failed after {retry_count} attempts")
        if last_error:
            raise last_error
        else:
            raise RuntimeError(f"Command '{command}' failed after {retry_count} attempts with no specific error")
    
    async def get_game_state(self) -> Dict[str, Any]:
        """
        Get the current game state.
        
        Returns:
            Game state dictionary
            
        Raises:
            httpx.HTTPStatusError: If the API request fails
            ValueError: If no game ID is available
        """
        if not self.game_id:
            raise ValueError("No game ID available. Call create_game() first.")
            
        logger.info("Getting game state")
        try:
            response = await self.session.get(
                f"{self.api_base_url}/api/v1/game/{self.game_id}"
            )
            response.raise_for_status()
            game_state = response.json()
            
            if self.log_responses:
                logger.info(f"Game state retrieved with keys: {list(game_state.keys())}")
                
            return game_state
        except httpx.HTTPStatusError as e:
            logger.error(f"Game state retrieval failed with status {e.response.status_code}: {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Game state retrieval failed with unexpected error: {str(e)}")
            raise
            
    async def admin_force_item(self, item_name: str) -> Dict[str, Any]:
        """
        Admin command to force add an item to the player's inventory.
        
        Args:
            item_name: Name of the item to add
            
        Returns:
            Response data
            
        Raises:
            httpx.HTTPStatusError: If the API request fails
            ValueError: If no game ID is available
        """
        if not self.game_id:
            raise ValueError("No game ID available. Call create_game() first.")
            
        logger.info(f"Admin: Force adding item '{item_name}' to inventory")
        try:
            response = await self.session.post(
                f"{self.api_base_url}/api/v1/admin/game/{self.game_id}/force_item",
                json={"item_name": item_name}
            )
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Item '{item_name}' added to inventory")
            return data
        except httpx.HTTPStatusError as e:
            logger.error(f"Admin force item failed with status {e.response.status_code}: {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Admin force item failed with unexpected error: {str(e)}")
            raise
            
    async def admin_teleport(self, area_name: str) -> Dict[str, Any]:
        """
        Admin command to teleport the player to a specific area.
        
        Args:
            area_name: Name of the area to teleport to
            
        Returns:
            Response data
            
        Raises:
            httpx.HTTPStatusError: If the API request fails
            ValueError: If no game ID is available
        """
        if not self.game_id:
            raise ValueError("No game ID available. Call create_game() first.")
            
        logger.info(f"Admin: Teleporting to area '{area_name}'")
        try:
            response = await self.session.post(
                f"{self.api_base_url}/api/v1/admin/game/{self.game_id}/teleport",
                json={"area_name": area_name}
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            # If admin endpoint fails, try a debug command
            logger.warning(f"Admin endpoint failed, trying debug command for teleport to '{area_name}'")
            try:
                debug_response = await self.send_command(f"debug teleport {area_name}")
                return {"success": True, "response": debug_response}
            except Exception as debug_err:
                logger.error(f"Both admin endpoint and debug command failed for teleport to '{area_name}'")
                raise e  # Raise the original error
        except Exception as e:
            logger.error(f"Admin teleport failed with unexpected error: {str(e)}")
            raise
            
    def get_command_history(self) -> List[str]:
        """Get the history of commands sent to the game."""
        return self.command_history
    
    def clear_command_history(self) -> None:
        """Clear the command history."""
        self.command_history = []
        
    async def cleanup(self) -> None:
        """Close the session and clean up resources."""
        logger.info("Cleaning up resources")
        await self.session.aclose()
        logger.info("Session closed")

# Helper functions for common test patterns

async def ensure_item_acquired(client: TestGameClient, item_name: str, 
                              commands_to_try: List[str], 
                              max_attempts: int = 3) -> bool:
    """
    Try multiple commands to acquire an item until successful.
    
    Args:
        client: TestGameClient instance
        item_name: Name of the item to acquire
        commands_to_try: List of commands to try
        max_attempts: Maximum number of attempts per command
        
    Returns:
        True if item was acquired, False otherwise
    """
    # First check if we already have the item
    inventory_response = await client.send_command("inventory")
    if item_name in inventory_response:
        logger.info(f"Item '{item_name}' already in inventory")
        return True
    
    # Try each command in sequence
    for command in commands_to_try:
        logger.info(f"Attempting to acquire '{item_name}' with command: '{command}'")
        
        for attempt in range(max_attempts):
            response = await client.send_command(command)
            
            # Check if the item was acquired directly
            acquisition_phrases = [
                f"You take the {item_name}", 
                f"added {item_name} to your inventory",
                f"You've added {item_name} to your inventory",
                f"You gather some {item_name}"
            ]
            if any(phrase in response for phrase in acquisition_phrases):
                logger.info(f"Successfully acquired '{item_name}' with command: '{command}'")
                return True
            
            # Check inventory after command
            inventory_response = await client.send_command("inventory")
            if item_name in inventory_response:
                logger.info(f"Item '{item_name}' found in inventory after command: '{command}'")
                return True
                
            # If we haven't succeeded and have more attempts, look around before trying again
            if attempt < max_attempts - 1:
                await client.send_command("look")
    
    # If we get here, we failed to acquire the item naturally
    logger.warning(f"Failed to acquire '{item_name}' through normal commands")
    return False

async def ensure_enemy_defeated(client: TestGameClient, enemy_name: str) -> bool:
    """
    Ensure that an enemy is defeated.
    
    Args:
        client: TestGameClient instance
        enemy_name: Name of the enemy to defeat
        
    Returns:
        True if enemy was defeated or is not present, False otherwise
    """
    look_response = await client.send_command("look")
    
    # Check if the enemy is present
    if enemy_name not in look_response:
        logger.info(f"Enemy '{enemy_name}' not found in current location")
        return True  # Enemy is not present, so consider it defeated
    
    # Try to defeat the enemy
    logger.info(f"Attempting to defeat enemy: '{enemy_name}'")
    
    # First try the defeat command (for testing)
    try:
        defeat_response = await client.send_command(f"defeat {enemy_name}")
        if "defeated" in defeat_response.lower() or "you defeated" in defeat_response.lower():
            logger.info(f"Successfully defeated '{enemy_name}' with defeat command")
            return True
    except Exception as e:
        logger.warning(f"Defeat command failed for '{enemy_name}': {str(e)}")
    
    # If defeat command didn't work, try to attack
    try:
        attack_response = await client.send_command(f"attack {enemy_name}")
        # In a real implementation, we'd need to handle multi-turn combat here
        # For now, just check if the enemy is still present after attacking
        look_after_response = await client.send_command("look")
        if enemy_name not in look_after_response:
            logger.info(f"Successfully defeated '{enemy_name}' through combat")
            return True
    except Exception as e:
        logger.warning(f"Attack command failed for '{enemy_name}': {str(e)}")
    
    logger.warning(f"Failed to defeat '{enemy_name}'")
    return False

async def verify_current_area(client: TestGameClient, area_name: str) -> bool:
    """
    Verify that the player is currently in the specified area.
    
    Args:
        client: TestGameClient instance
        area_name: Name of the area to check for
        
    Returns:
        True if in the specified area, False otherwise
    """
    try:
        game_state = await client.get_game_state()
        
        # Check different possible structures for current area
        current_area = None
        
        if "game_state" in game_state and "current_area" in game_state["game_state"]:
            current_area = game_state["game_state"]["current_area"]
        elif "current_area" in game_state:
            current_area = game_state["current_area"]
        elif "game_state" in game_state and "current_tile" in game_state["game_state"] and "area" in game_state["game_state"]["current_tile"]:
            current_area = game_state["game_state"]["current_tile"]["area"]
        
        if current_area:
            # Normalize area names for comparison
            normalized_current = current_area.lower().replace("_", " ")
            normalized_target = area_name.lower().replace("_", " ")
            
            if normalized_target in normalized_current:
                logger.info(f"Verified current area is '{area_name}'")
                return True
        
        # If we can't verify from the game state, try looking for area name in description
        look_response = await client.send_command("look")
        area_keywords = area_name.lower().replace("_", " ").split()
        
        # Check if enough keywords match in the description
        matches = sum(1 for keyword in area_keywords if keyword in look_response.lower())
        if matches >= len(area_keywords) / 2:  # At least half the keywords match
            logger.info(f"Verified current area is likely '{area_name}' based on description")
            return True
            
        logger.warning(f"Failed to verify current area is '{area_name}'")
        return False
    except Exception as e:
        logger.error(f"Error verifying current area: {str(e)}")
        return False

async def verify_inventory_contains(client: TestGameClient, items: List[str]) -> List[str]:
    """
    Verify that the player's inventory contains the specified items.
    
    Args:
        client: TestGameClient instance
        items: List of item names to check for
        
    Returns:
        List of items that are missing from the inventory
    """
    try:
        inventory_response = await client.send_command("inventory")
        
        missing_items = []
        for item in items:
            if item not in inventory_response:
                missing_items.append(item)
                logger.warning(f"Item '{item}' not found in inventory")
            else:
                logger.info(f"Verified item '{item}' is in inventory")
                
        return missing_items
    except Exception as e:
        logger.error(f"Error verifying inventory: {str(e)}")
        return items  # Assume all items are missing if an error occurs 
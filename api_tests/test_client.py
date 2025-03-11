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
        # Use a shorter timeout for testing
        self.session = httpx.AsyncClient(timeout=10.0)  
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
                    await self.session.delete(f"{self.api_base_url}/api/v1/game/game/{temp_game_id}")
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
    
    async def create_game(self, game_name: Optional[str] = None, description: Optional[str] = None) -> str:
        """
        Create a new game instance.
        
        Args:
            game_name: Optional name for the game
            description: Optional description for the game
            
        Returns:
            Game ID string
            
        Raises:
            httpx.HTTPStatusError: If the API request fails
        """
        logger.info("Creating new game instance")
        try:
            # Update the endpoint to match the backend structure
            response = await self.session.post(
                f"{self.api_base_url}/api/v1/game/game",
                json={
                    "name": game_name or f"Test Game {int(time.time())}",
                    "description": description or "Test game for API testing"
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
                # Update the endpoint to match the backend structure
                response = await self.session.post(
                    f"{self.api_base_url}/api/v1/game/game/{self.game_id}/command",
                    json={"command": command, "use_llm": True}
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
            # Update the endpoint to match the backend structure
            response = await self.session.get(
                f"{self.api_base_url}/api/v1/game/game/{self.game_id}"
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
        
    async def cleanup(self):
        """Clean up resources after tests."""
        logger.info("Cleaning up test resources")
        
        if self.game_id:
            logger.info(f"Deleting game instance: {self.game_id}")
            try:
                temp_game_id = self.game_id
                self.game_id = None
                # Update the endpoint to match the backend structure
                await self.session.delete(f"{self.api_base_url}/api/v1/game/game/{temp_game_id}")
                logger.info(f"Game instance {temp_game_id} deleted")
            except Exception as e:
                logger.warning(f"Failed to delete game instance: {str(e)}")
        
        await self.session.aclose()
        logger.info("HTTP session closed")

    async def ensure_location(self, area_name: str) -> bool:
        """Ensure the player is in the specified area."""
        # Check if we're already in the right area
        is_in_area = await verify_current_area(self, area_name)
        if is_in_area:
            return True
        
        # If not, try to move there (in a real implementation, this would be more complex)
        logging.warning(f"Not in {area_name}, trying to force move")
        return await self.force_move_to_area(area_name)

    async def force_move_to_area(self, area_name: str) -> bool:
        """
        Force move to a specific area using teleport or debug command.
        
        Args:
            area_name: Name of the area to move to
            
        Returns:
            True if successfully moved to the area, False otherwise
        """
        # Try admin teleport first if available
        try:
            await self.admin_teleport(area_name)
            return await verify_current_area(self, area_name)
        except Exception as e:
            logger.warning(f"Admin teleport failed: {e}")
        
        # Fallback to debug command
        try:
            command = f"debug_set_position {area_name}"
            response = await self.send_command(command)
            logger.info(f"Debug teleport response: {response}")
            return await verify_current_area(self, area_name)
        except Exception as e:
            logger.error(f"Debug teleport failed: {e}")
            return False
            
    async def get_current_location(self) -> Dict[str, str]:
        """
        Get the current location details using the debug_location command.
        
        Returns:
            Dictionary with location details (position, area, etc.)
        """
        try:
            response = await self.send_command("debug_location")
            
            # Parse the response
            location_info = {}
            
            # Process each line of the response
            for line in response.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    location_info[key.strip()] = value.strip()
                    
            logger.info(f"Got current location: {location_info}")
            return location_info
        except Exception as e:
            logger.error(f"Failed to get current location: {e}")
            return {"error": str(e)}
    
    async def get_player_position(self) -> Dict[str, Any]:
        """
        Get the player's position directly from the game state.
        
        Returns:
            Dictionary with position information
        """
        try:
            # Get the game state from the API
            game_state = await self.get_game_state()
            
            # Create a position info dictionary
            position_info = {}
            
            # Extract position from game state
            if 'game_state' in game_state and 'position' in game_state['game_state']:
                position = game_state['game_state']['position']
                position_info['position'] = position
                position_info['x'] = position[0] if isinstance(position, (list, tuple)) else None
                position_info['y'] = position[1] if isinstance(position, (list, tuple)) else None
            
            # Extract current area if available
            if 'game_state' in game_state and 'current_area' in game_state['game_state']:
                position_info['current_area'] = game_state['game_state']['current_area']
            
            # Log the extracted position info
            logger.info(f"Player position: {position_info}")
            return position_info
        except Exception as e:
            logger.error(f"Error getting player position: {str(e)}")
            return {"error": str(e)}

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
    # First try using the get_player_position method
    try:
        position_info = await client.get_player_position()
        
        # Check if we have current_area in position info
        if 'current_area' in position_info:
            current_area = position_info['current_area']
            # Normalize area names for comparison
            normalized_current = current_area.replace(' ', '_').upper() if current_area else ''
            normalized_target = area_name.replace(' ', '_').upper()
            
            if normalized_current == normalized_target:
                logger.info(f"Verified current area is {area_name} using position info")
                return True
                
        # Check if position matches a named area
        if 'position' in position_info:
            # Get position coordinates
            x, y = position_info.get('x'), position_info.get('y')
            if x is not None and y is not None:
                # Log the position for debugging
                logger.info(f"Player is at position ({x}, {y})")
                
                # Check if position corresponds to the target area
                # This requires mapping positions to named areas
                area_positions = {
                    "AWAKENING_WOODS": (0, 0),
                    "WARRIORS_CAMP": (1, 0),
                    "TRIALS_PATH": (0, 1),
                    "MOUNTAIN_BASE": (1, 1),
                    "TRAINING_GROUNDS": (2, 0),
                    # Add more area mappings as needed
                }
                
                # Check if position matches the target area
                if area_name in area_positions and area_positions[area_name] == (x, y):
                    logger.info(f"Verified current area is {area_name} by matching position ({x}, {y})")
                    return True
    except Exception as e:
        logger.warning(f"Error using position info: {e}")
    
    # If direct position check failed, fall back to look command verification
    try:
        look_result = await client.send_command("look")
        # Check for area keywords in the description
        words = area_name.replace('_', ' ').lower().split()
        normalized_result = look_result.lower()
        
        # Check for common keywords per area
        area_keywords = {
            "AWAKENING_WOODS": ["forest", "clearing", "ancient forest"],
            "WARRIORS_CAMP": ["warrior", "camp", "training"],
            "TRAINING_GROUNDS": ["training", "ground", "arena", "practice"],
            "SHADOW_DOMAIN": ["shadow", "domain", "darkness"],
            "MYSTIC_MOUNTAINS": ["mystic", "mountain", "peak"],
            # Add more keywords for other areas
        }
        
        if area_name in area_keywords:
            for keyword in area_keywords[area_name]:
                if keyword.lower() in normalized_result:
                    logger.info(f"Verified current area is {area_name} by matching keyword '{keyword}'")
                    return True
    except Exception as e:
        logger.warning(f"Error checking area via look command: {str(e)}")
    
    logger.warning(f"Failed to verify current area is '{area_name}'")
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

async def navigate_to_area(client: TestGameClient, target_area: str, max_attempts: int = 20) -> bool:
    """
    Navigate to a target area using directional commands.
    
    Args:
        client: TestGameClient instance
        target_area: The area to navigate to
        max_attempts: Maximum number of movement attempts
        
    Returns:
        True if navigation was successful, False otherwise
    """
    logger.info(f"Attempting to navigate to {target_area}")
    
    # First check if we're already in the target area
    if await verify_current_area(client, target_area):
        logger.info(f"Already in target area {target_area}")
        return True
    
    # Map of area coordinates based on NAMED_AREAS
    area_coordinates = {
        "AWAKENING_WOODS": (0, 0),   # Starting area
        "WARRIORS_CAMP": (1, 0),     # East of starting area
        "TRIALS_PATH": (0, 1),       # North of starting area
        "MOUNTAIN_BASE": (1, 1),     # Northeast of starting area
        "TRAINING_GROUNDS": (2, 0),  # East of Warrior's Camp
        "SHADOW_DOMAIN": (0, 2),     # North of Trials Path
        "SHADOW_TRAINING": (0, 3),   # North of Shadow Domain
        "MYSTIC_MOUNTAINS": (1, 2),  # Northeast of Trials Path
        "CRYSTAL_POND": (2, 2),      # East of Mystic Mountains
        "HONOR_SHRINE": (3, 0),      # East of Training Grounds
        "FORGOTTEN_TEMPLE": (0, 4),  # North of Shadow Training
        "MEDITATION_CIRCLE": (3, 2), # East of Crystal Pond
        "ENCHANTED_VALLEY": (1, 3),  # North of Mystic Mountains
        "CRYSTAL_CAVES": (1, 4),     # North of Enchanted Valley
        "FORGOTTEN_GROVE": (2, 4),   # Northeast of Crystal Caves
        "CROSSROADS": (5, 5),        # Central connecting area
        "GUARDIAN_OVERLOOK": (8, 8), # Pre-boss area
        "ANCIENT_SANCTUARY": (9, 9)  # Final boss area
    }
    
    # Get current position
    current_area = None
    for area, is_current in [(area, await verify_current_area(client, area)) for area in area_coordinates.keys()]:
        if is_current:
            current_area = area
            break
    
    if not current_area:
        logger.warning("Could not determine current area")
        return False
    
    current_pos = area_coordinates.get(current_area)
    target_pos = area_coordinates.get(target_area)
    
    if not current_pos or not target_pos:
        logger.warning(f"Could not find coordinates for current area {current_area} or target area {target_area}")
        return False
    
    logger.info(f"Current position: {current_pos}, Target position: {target_pos}")
    
    # Attempt to navigate to the target area
    attempts = 0
    while attempts < max_attempts:
        # Check if we've reached the target area
        if await verify_current_area(client, target_area):
            logger.info(f"Successfully navigated to {target_area}")
            return True
        
        # Get current position again (it might have changed)
        for area, is_current in [(area, await verify_current_area(client, area)) for area in area_coordinates.keys()]:
            if is_current:
                current_area = area
                current_pos = area_coordinates.get(current_area)
                break
        
        # Determine direction to move
        x_diff = target_pos[0] - current_pos[0]
        y_diff = target_pos[1] - current_pos[1]
        
        direction = None
        if x_diff > 0:
            direction = "east"
        elif x_diff < 0:
            direction = "west"
        elif y_diff > 0:
            direction = "north"
        elif y_diff < 0:
            direction = "south"
        
        if not direction:
            logger.warning("No valid direction to move")
            return False
        
        # Try to move in the determined direction
        logger.info(f"Attempting to move {direction}")
        response = await client.send_command(f"move {direction}")
        
        # Check for obstacles or failures
        if "can't go that way" in response.lower() or "blocked" in response.lower():
            logger.warning(f"Movement blocked in direction {direction}: {response}")
            
            # Try other directions
            for alt_direction in ["north", "east", "south", "west"]:
                if alt_direction != direction:
                    logger.info(f"Trying alternative direction: {alt_direction}")
                    alt_response = await client.send_command(f"move {alt_direction}")
                    if "can't go that way" not in alt_response.lower() and "blocked" not in alt_response.lower():
                        logger.info(f"Successfully moved in alternative direction {alt_direction}")
                        break
        
        attempts += 1
        # Wait briefly between commands
        await asyncio.sleep(0.5)
    
    logger.warning(f"Failed to navigate to {target_area} after {max_attempts} attempts")
    return False 
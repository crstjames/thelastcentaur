"""
Environmental items handler for The Last Centaur.

This module provides functionality to detect and handle environmental items
that are not explicitly listed in the game state but would naturally be present
based on the terrain type and description.
"""

import logging
from typing import Dict, List, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define environmental items by terrain type
ENVIRONMENTAL_ITEMS = {
    "forest": ["leaves", "twigs", "bark", "berries", "moss", "flowers", "herbs"],
    "mountain": ["rocks", "stones", "pebbles", "dirt", "snow", "ice"],
    "river": ["water", "reeds", "clay", "mud", "sand"],
    "beach": ["sand", "shells", "seaweed", "driftwood"],
    "cave": ["rocks", "stones", "crystals", "dust", "dirt"],
    "clearing": ["grass", "flowers", "weeds", "dirt", "soil"],
    "ruins": ["dust", "debris", "fragments", "stones", "rubble"],
    "woods": ["leaves", "twigs", "bark", "berries", "moss", "flowers", "herbs"]  # Add woods as synonym for forest
}

# Keywords that might appear in descriptions
TERRAIN_KEYWORDS = {
    "forest": ["forest", "woods", "trees", "woodland", "grove", "thicket"],
    "mountain": ["mountain", "hill", "peak", "cliff", "rocky", "highlands"],
    "river": ["river", "stream", "brook", "creek", "water", "flowing"],
    "beach": ["beach", "shore", "coast", "sand", "ocean", "sea"],
    "cave": ["cave", "cavern", "grotto", "tunnel", "underground"],
    "clearing": ["clearing", "meadow", "field", "glade", "open space"],
    "ruins": ["ruins", "ancient", "crumbling", "abandoned", "old structure"]
}

def is_environmental_item(item_name: str, terrain_type: str = "", description: str = "") -> bool:
    """
    Check if an item is an environmental item based on terrain type and description.
    
    Args:
        item_name: The name of the item to check
        terrain_type: The terrain type of the current location
        description: The description of the current location
        
    Returns:
        True if the item is an environmental item, False otherwise
    """
    # Log the inputs for debugging
    logger.info(f"Checking if {item_name} is environmental. Terrain: '{terrain_type}', Description: '{description}'")
    
    # Convert terrain_type to lowercase for case-insensitive matching
    terrain_type_lower = terrain_type.lower() if terrain_type else ""
    description_lower = description.lower() if description else ""
    
    # Special case for common forest/woods items
    forest_keywords = ["forest", "woods", "trees", "woodland", "grove", "thicket", "ancient woods", "branches", "canopy", "foliage"]
    forest_items = ["leaves", "twigs", "bark", "berries", "moss", "flowers", "herbs"]
    
    # If the item is a forest item, check for forest keywords in the description
    if item_name in forest_items:
        # Check if any forest keyword is in the terrain type or description
        if terrain_type_lower == "forest" or "forest" in terrain_type_lower:
            logger.info(f"Item {item_name} is environmental based on forest terrain type")
            return True
            
        if any(keyword in description_lower for keyword in forest_keywords):
            logger.info(f"Item {item_name} is environmental based on forest keywords in description: {[kw for kw in forest_keywords if kw in description_lower]}")
            return True
        
        # Special case for "ancient woods" which appears in the game
        if "ancient" in description_lower and ("woods" in description_lower or "wood" in description_lower):
            logger.info(f"Item {item_name} is environmental based on 'ancient woods' in description")
            return True
    
    # Check based on explicit terrain type
    for terrain_key, items in ENVIRONMENTAL_ITEMS.items():
        if terrain_key in terrain_type_lower and item_name in items:
            logger.info(f"Item {item_name} is environmental based on terrain type {terrain_type}")
            return True
        
    # Check based on description keywords
    for terrain, keywords in TERRAIN_KEYWORDS.items():
        if any(keyword in description_lower for keyword in keywords):
            if item_name in ENVIRONMENTAL_ITEMS.get(terrain, []):
                logger.info(f"Item {item_name} is environmental based on description keywords for {terrain}")
                return True
    
    # If we have a description that mentions the ground or floor with leaves
    if item_name == "leaves" and any(ground_word in description_lower for ground_word in ["ground", "floor"]) and "leaves" in description_lower:
        logger.info(f"Item {item_name} is environmental based on ground with leaves in description")
        return True
                
    logger.info(f"Item {item_name} is NOT an environmental item in this context")
    return False

async def update_inventory_with_item(client, game_id: str, access_token: str, item_name: str, api_base_url: str) -> Dict[str, Any]:
    """
    Update the player's inventory with an environmental item.
    
    Args:
        client: The HTTP client to use for API calls
        game_id: The game instance ID
        access_token: The user's access token
        item_name: The name of the item to add to inventory
        api_base_url: The base URL for the API
        
    Returns:
        A dictionary with the result of the operation
    """
    try:
        # First get the full game state
        game_state_response = await client.get(
            f"{api_base_url}/game/{game_id}",
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=10.0
        )
        
        if game_state_response.status_code != 200:
            logger.warning(f"Failed to get game state: {game_state_response.status_code} - {game_state_response.text}")
            return {
                "success": False,
                "message": f"You gather some {item_name} from the surroundings.",
                "error": f"Failed to get game state: {game_state_response.status_code}"
            }
            
        full_game_data = game_state_response.json()
        logger.info(f"Game state structure keys: {list(full_game_data.keys())}")
        
        # Find the inventory in the game state
        inventory = None
        
        # Check different possible structures
        if "game_state" in full_game_data and "inventory" in full_game_data["game_state"]:
            # Structure: {"game_state": {"inventory": [...]}}
            inventory = full_game_data["game_state"]["inventory"]
            logger.info(f"Found inventory in game_state: {inventory}")
        elif "inventory" in full_game_data:
            # Structure: {"inventory": [...]}
            inventory = full_game_data["inventory"]
            logger.info(f"Found inventory directly in response: {inventory}")
        
        # If we still can't find the inventory, try a different approach
        if inventory is None:
            # Try to get the inventory through a direct command
            inventory_response = await client.post(
                f"{api_base_url}/game/{game_id}/command",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {access_token}"
                },
                json={"command": "inventory"},
                timeout=10.0
            )
            
            if inventory_response.status_code == 200:
                inventory_text = inventory_response.json().get("response", "")
                logger.info(f"Got inventory response: {inventory_text}")
                
                # Parse the inventory from the text response
                # This is a fallback and might not be perfect
                if inventory_text:
                    # Simple parsing: assume format like "Inventory: item1, item2, item3"
                    if ":" in inventory_text:
                        items_part = inventory_text.split(":", 1)[1].strip()
                        if items_part:
                            inventory = [item.strip() for item in items_part.split(",")]
                            logger.info(f"Parsed inventory from command: {inventory}")
                        else:
                            inventory = []  # Empty inventory
                    else:
                        inventory = []  # Couldn't parse, assume empty
            
        if inventory is None:
            logger.warning(f"Could not find inventory in game state: {list(full_game_data.keys())}")
            return {
                "success": False,
                "message": f"You gather some {item_name} from the surroundings.",
                "error": "Could not find inventory in game state"
            }
            
        # Check if the player already has this item
        if item_name in inventory:
            return {
                "success": True,
                "message": f"You already have some {item_name} in your inventory.",
                "inventory": inventory
            }
            
        # Check if the inventory is full (arbitrary limit of 20 items)
        if len(inventory) >= 20:
            return {
                "success": False,
                "message": f"You gather some {item_name} from the surroundings, but your inventory is full.",
                "inventory": inventory
            }
            
        # Add the item to inventory
        inventory.append(item_name)
        logger.info(f"Added {item_name} to inventory: {inventory}")
        
        # Update the game state with the new inventory
        if "game_state" in full_game_data and "inventory" in full_game_data["game_state"]:
            full_game_data["game_state"]["inventory"] = inventory
        elif "inventory" in full_game_data:
            full_game_data["inventory"] = inventory
        else:
            # If we can't find where to update the inventory in the game state,
            # try a direct approach by dropping and taking the item
            logger.info(f"Using alternative approach to add {item_name} to inventory")
            
            # First try to create the item in the current location
            create_response = await client.post(
                f"{api_base_url}/game/{game_id}/command",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {access_token}"
                },
                json={"command": f"create {item_name}"},
                timeout=10.0
            )
            
            # Then try to take it
            take_response = await client.post(
                f"{api_base_url}/game/{game_id}/command",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {access_token}"
                },
                json={"command": f"take {item_name}"},
                timeout=10.0
            )
            
            if take_response.status_code == 200:
                return {
                    "success": True,
                    "message": f"You gather some {item_name} from the surroundings and add them to your inventory.",
                    "inventory": inventory
                }
            else:
                logger.warning(f"Failed to take {item_name} using alternative approach: {take_response.status_code}")
        
        # Send the complete updated game state
        update_response = await client.put(
            f"{api_base_url}/game/{game_id}",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {access_token}"
            },
            json=full_game_data,
            timeout=10.0
        )
        
        if update_response.status_code == 200:
            logger.info(f"Successfully added {item_name} to inventory")
            return {
                "success": True,
                "message": f"You gather some {item_name} from the surroundings and add them to your inventory.",
                "inventory": inventory
            }
        else:
            logger.warning(f"Failed to update inventory with {item_name}: {update_response.status_code} - {update_response.text}")
            return {
                "success": False,
                "message": f"You gather some {item_name} from the surroundings.",
                "error": f"Failed to update inventory: {update_response.status_code}"
            }
    except Exception as e:
        logger.error(f"Error updating inventory with {item_name}: {e}")
        return {
            "success": False,
            "message": f"You gather some {item_name} from the surroundings.",
            "error": str(e)
        } 
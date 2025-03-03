#!/usr/bin/env python3
"""
Script to check if the Phantom Assassin is correctly placed in the game map.
"""

from src.engine.core.map_system import GAME_MAP, MapSystem
from src.engine.core.models import Enemy
from src.engine.core.world_design import WORLD_ENEMIES

def check_position(position, area_name):
    """Check if the Phantom Assassin exists in the given position."""
    print(f"\n=== Checking position {position} ({area_name}) ===")
    
    # Find the node at this position
    target_node = None
    for area, node in GAME_MAP.items():
        if node.position == position:
            target_node = node
            area_name = area
            break
    
    if not target_node:
        print(f"ERROR: No node found at position {position}")
        return False
    
    print(f"Found node at position {position}: {area_name}")
    
    # Check enemies
    if not hasattr(target_node, 'enemies') or not target_node.enemies:
        print(f"ERROR: No enemies found in the node at position {position}")
        return False
    
    # Print all enemies
    print(f"Enemies at position {position}:")
    for enemy in target_node.enemies:
        if isinstance(enemy, Enemy):
            print(f"  - {enemy.name}: {enemy.description}")
        elif isinstance(enemy, dict):
            print(f"  - {enemy.get('name', 'Unknown')}: {enemy.get('description', 'No description')}")
        elif isinstance(enemy, str):
            print(f"  - {enemy} (ID only)")
        else:
            print(f"  - Unknown enemy type: {type(enemy)}")
    
    # Check specifically for Phantom Assassin
    phantom_exists = False
    for enemy in target_node.enemies:
        if isinstance(enemy, Enemy) and enemy.name.lower() == "phantom assassin":
            phantom_exists = True
            break
        elif isinstance(enemy, dict) and enemy.get("name", "").lower() == "phantom assassin":
            phantom_exists = True
            break
        elif isinstance(enemy, str) and enemy == "phantom_assassin":
            phantom_exists = True
            break
    
    if phantom_exists:
        print(f"SUCCESS: Phantom Assassin found at position {position}")
        return True
    else:
        print(f"ERROR: Phantom Assassin NOT found at position {position}")
        return False

def main():
    """Check if the Phantom Assassin exists in the correct positions."""
    # Initialize the MapSystem to trigger our fix
    map_system = MapSystem()
    
    # Check both positions
    positions = [
        ((7, 6), "position from WORLD_ENEMIES"),
        ((5, 5), "Forgotten Grove")
    ]
    
    success = True
    for position, desc in positions:
        if not check_position(position, desc):
            success = False
    
    # Print overall result
    if success:
        print("\nSUCCESS: Phantom Assassin is correctly placed in all expected locations!")
    else:
        print("\nWARNING: Phantom Assassin is missing from one or more expected locations.")
        
    # Print information about the Phantom Assassin in WORLD_ENEMIES
    print("\n=== PHANTOM ASSASSIN INFO ===")
    phantom_data = next((e for e in WORLD_ENEMIES if e["id"] == "phantom_assassin"), None)
    if phantom_data:
        print(f"ID: {phantom_data['id']}")
        print(f"Name: {phantom_data['name']}")
        print(f"Description: {phantom_data['description']}")
        print(f"Position: {phantom_data.get('position', 'Not specified')}")
        print(f"Drops: {phantom_data.get('drops', [])}")
        print(f"Requirements: {phantom_data.get('requirements', [])}")
    else:
        print("Phantom Assassin not found in WORLD_ENEMIES")

if __name__ == "__main__":
    main() 
#!/usr/bin/env python3
"""
Script to print information about all nodes in the GAME_MAP.
"""

from src.engine.core.map_system import GAME_MAP
from src.engine.core.models import Enemy
from src.engine.core.world_design import WORLD_ENEMIES

def main():
    """Print information about all nodes in the GAME_MAP."""
    print("=== GAME_MAP NODES ===")
    
    # Print all nodes
    for area, node in GAME_MAP.items():
        print(f"\nArea: {area}")
        print(f"  Position: {node.position}")
        print(f"  Terrain: {node.terrain_type}")
        print(f"  Description: {node.base_description}")
        
        # Print enemies
        if hasattr(node, 'enemies') and node.enemies:
            print(f"  Enemies:")
            for enemy in node.enemies:
                if isinstance(enemy, Enemy):
                    print(f"    - {enemy.name}: {enemy.description}")
                elif isinstance(enemy, dict):
                    print(f"    - {enemy.get('name', 'Unknown')}: {enemy.get('description', 'No description')}")
                elif isinstance(enemy, str):
                    print(f"    - {enemy} (ID only)")
                else:
                    print(f"    - Unknown enemy type: {type(enemy)}")
        else:
            print("  Enemies: None")
    
    # Print position to node mapping
    print("\n=== POSITIONS ===")
    position_map = {}
    for area, node in GAME_MAP.items():
        position_map[node.position] = area
    
    for position, area in sorted(position_map.items()):
        print(f"Position {position}: {area}")
    
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
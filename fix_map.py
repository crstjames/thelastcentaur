#!/usr/bin/env python3
"""
Script to fix the map in The Last Centaur game.
"""

from src.engine.core.map_system import GAME_MAP
from src.engine.core.enemies import ENEMIES

def main():
    """Add the phantom assassin to the map at position (0,3)."""
    # Get the node at position (0,3)
    node = GAME_MAP.get('0,3')
    
    if not node:
        print("Node not found at position (0,3)")
        return
    
    # Add the phantom assassin to the enemies list
    node.enemies = ['phantom_assassin']
    
    print(f"Updated enemies at (0,3): {node.enemies}")

if __name__ == "__main__":
    main() 
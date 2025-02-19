"""
Map visualization utilities for The Last Centaur.

This module provides tools to visualize the game map and its connections,
useful for both development and potentially in-game map features.
"""

from typing import Dict, List, Set, Tuple
from .map_system import GAME_MAP, AreaNode, AreaConnection
from .models import StoryArea, Direction

def create_ascii_map() -> str:
    """
    Create an ASCII representation of the game map.
    Shows areas, connections, and requirements.
    """
    # Initialize 10x10 grid with empty spaces
    grid = [[' ' for _ in range(10)] for _ in range(10)]
    
    # Add areas to grid
    for area, node in GAME_MAP.items():
        x, y = node.position
        # Flip y coordinate since we want (0,0) at bottom
        y = 9 - y
        grid[y][x] = 'O'
    
    # Add connections
    for area, node in GAME_MAP.items():
        x, y = node.position
        y = 9 - y  # Flip y coordinate
        
        for conn in node.connections:
            dest = GAME_MAP[conn.to_area]
            dest_x, dest_y = dest.position
            dest_y = 9 - dest_y  # Flip y coordinate
            
            # Draw connection line based on direction
            if conn.direction == Direction.NORTH:
                for i in range(y - 1, dest_y, -1):
                    grid[i][x] = '|'
            elif conn.direction == Direction.SOUTH:
                for i in range(y + 1, dest_y):
                    grid[i][x] = '|'
            elif conn.direction == Direction.EAST:
                for i in range(x + 1, dest_x):
                    grid[y][i] = '-'
            elif conn.direction == Direction.WEST:
                for i in range(x - 1, dest_x, -1):
                    grid[y][i] = '-'
    
    # Convert grid to string
    map_str = ""
    for row in grid:
        map_str += ''.join(row) + '\n'
    
    # Add legend
    map_str += "\nLegend:\n"
    map_str += "O : Area\n"
    map_str += "| : North/South connection\n"
    map_str += "- : East/West connection\n"
    
    return map_str

def get_area_info(area: StoryArea) -> str:
    """Get detailed information about an area."""
    node = GAME_MAP[area]
    info = [
        f"Area: {area.value}",
        f"Position: {node.position}",
        f"Terrain: {node.terrain_type.value}",
        f"Description: {node.base_description}",
        "\nConnections:"
    ]
    
    for conn in node.connections:
        req_str = ", ".join(conn.requirements) if conn.requirements else "None"
        info.append(f"- To {conn.to_area.value} ({conn.direction.value})")
        info.append(f"  Requirements: {req_str}")
        info.append(f"  Description: {conn.description}")
    
    info.extend([
        "\nRequirements:",
        ", ".join(node.requirements) if node.requirements else "None",
        "\nEnemies:",
        ", ".join(node.enemies),
        "\nItems:",
        ", ".join(node.items)
    ])
    
    return "\n".join(info)

def get_path_info(path_type: str) -> str:
    """Get information about a specific path through the game."""
    path_areas = {
        "warrior": [
            StoryArea.AWAKENING_WOODS,
            StoryArea.TRIALS_PATH,
            StoryArea.ANCIENT_RUINS,
            StoryArea.ENCHANTED_VALLEY,
            StoryArea.SHADOW_DOMAIN
        ],
        "mystic": [
            StoryArea.AWAKENING_WOODS,
            StoryArea.TRIALS_PATH,
            StoryArea.MYSTIC_MOUNTAINS,
            StoryArea.CRYSTAL_CAVES,
            StoryArea.SHADOW_DOMAIN
        ],
        "stealth": [
            StoryArea.AWAKENING_WOODS,
            StoryArea.TRIALS_PATH,
            StoryArea.FORGOTTEN_GROVE,
            StoryArea.SHADOW_DOMAIN
        ]
    }
    
    if path_type not in path_areas:
        return f"Unknown path: {path_type}"
    
    info = [f"\n{path_type.title()} Path:"]
    areas = path_areas[path_type]
    
    for i, area in enumerate(areas):
        node = GAME_MAP[area]
        info.append(f"\n{i+1}. {area.value}")
        info.append(f"   Location: {node.position}")
        if i < len(areas) - 1:
            next_area = areas[i + 1]
            conn = next((c for c in node.connections if c.to_area == next_area), None)
            if conn:
                req_str = ", ".join(conn.requirements) if conn.requirements else "None"
                info.append(f"   → Requirements to proceed: {req_str}")
    
    return "\n".join(info)

def print_all_paths() -> str:
    """Print information about all possible paths through the game."""
    return "\n\n".join([
        get_path_info("warrior"),
        get_path_info("mystic"),
        get_path_info("stealth")
    ]) 
#!/usr/bin/env python3
"""
Script to fix the Phantom Assassin issue in The Last Centaur game.
This script adds the Phantom Assassin enemy to the map data.
"""

import requests
import json

def main():
    """Add the Phantom Assassin to the map data via the admin API."""
    # Get the game ID
    response = requests.get(
        "http://localhost:8000/api/v1/game",
        headers={"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyNWU3Y2NjNy1hOWFlLTRiNGQtOTQ5Ni01MjIyYmU2M2FjNzYiLCJleHAiOjE3MDk0MzA0MzR9.Nh8Xt_1O-dXZG9lFHDZFr9SsIQPQqpnIKvlGMETJGQE"}
    )
    
    if response.status_code != 200:
        print(f"Error getting games: {response.status_code} - {response.text}")
        return
    
    games = response.json()
    if not games:
        print("No games found")
        return
    
    game_id = games[0]["id"]
    print(f"Using game ID: {game_id}")
    
    # Add the phantom_assassin to the player's current location
    response = requests.post(
        f"http://localhost:8000/api/v1/admin/debug/command",
        headers={"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyNWU3Y2NjNy1hOWFlLTRiNGQtOTQ5Ni01MjIyYmU2M2FjNzYiLCJleHAiOjE3MDk0MzA0MzR9.Nh8Xt_1O-dXZG9lFHDZFr9SsIQPQqpnIKvlGMETJGQE"},
        json={"command": "debug add_enemy phantom_assassin"}
    )
    
    if response.status_code != 200:
        print(f"Error adding enemy: {response.status_code} - {response.text}")
        return
    
    print(f"Successfully added phantom_assassin to the game: {response.json()}")

if __name__ == "__main__":
    main() 
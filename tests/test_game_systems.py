"""
Test suite for The Last Centaur's core game systems.

Tests the following systems:
- Time progression
- Achievement tracking
- Title unlocking
- Leaderboard functionality
"""

import pytest
from datetime import datetime
from src.engine.core.models import Direction, StoryArea, PathType
from src.engine.core.player import Player
from src.engine.core.map_system import MapSystem
from src.engine.core.command_parser import CommandParser
from src.engine.core.game_systems import LeaderboardEntry

def test_time_system():
    """Test the game's time progression system."""
    # Initialize game systems
    map_system = MapSystem()
    player = Player(map_system, player_id="test_player", player_name="Test Player")
    command_parser = CommandParser(player)
    
    def execute(command: str) -> str:
        cmd = command_parser.parse_command(command)
        assert cmd is not None, f"Command '{command}' could not be parsed"
        result = command_parser.execute_command(cmd)
        print(f"\n> {command}")
        print(result)
        return result
    
    # Game should start at 8:00 AM on Day 1
    result = execute("status")
    assert "Day 1, 08:00" in result
    
    # Defeat the Wolf Pack blocking the path
    result = execute("look")  # Check what's in the area
    if "Wolf Pack" in result:
        result = execute("defeat Wolf Pack")
        assert "Victory" in result
    
    # Moving should advance time by 5 minutes
    result = execute("n")
    assert "Moved north" in result
    result = execute("status")
    assert "Day 1, 08:35" in result  # 30 mins for combat + 5 mins for movement
    
    # Combat should advance time by 30 minutes
    result = execute("attack wolf_pack")
    result = execute("status")
    assert "Day 1, 09:05" in result
    
    # Resting should advance time based on stamina recovered
    result = execute("rest")
    result = execute("status")
    assert "Day 1, 09:25" in result  # 20 minutes for rest
    
    # Test day progression
    # Set time to 23:55 through multiple actions
    for _ in range(31):  # Use meditation to advance time faster (30 minutes each)
        execute("meditate")
    
    result = execute("status")
    assert "Day 2" in result  # Should have progressed to next day

def test_achievement_system():
    """Test the achievement tracking system."""
    map_system = MapSystem()
    player = Player(map_system, player_id="test_player", player_name="Test Player")
    command_parser = CommandParser(player)
    
    def execute(command: str) -> str:
        cmd = command_parser.parse_command(command)
        assert cmd is not None
        result = command_parser.execute_command(cmd)
        print(f"\n> {command}")
        print(result)
        return result
    
    # Clear any existing achievements
    player.achievement_system.unlocked_achievements.clear()
    for achievement in player.achievement_system.achievements.values():
        achievement.unlocked = False
    
    # Check initial achievements
    result = execute("achievements")
    assert "Achievements (0/50)" in result  # Assuming 50 total achievements
    
    # Test exploration achievement
    execute("n")  # Move to new area
    result = execute("achievements")
    assert "First Steps" in result  # Achievement for first exploration
    
    # Test combat achievement
    execute("attack wolf_pack")
    execute("defeat wolf_pack")
    result = execute("achievements")
    assert "First Blood" in result  # Achievement for first combat victory
    
    # Test hidden achievement
    for _ in range(10):
        execute("rest")  # Try to rest multiple times with enemies present
    result = execute("achievements")
    assert "Just Five More Minutes..." in result  # Hidden achievement unlocked

def test_title_system():
    """Test the title unlocking and selection system."""
    map_system = MapSystem()
    player = Player(map_system, player_id="test_player", player_name="Test Player")
    command_parser = CommandParser(player)
    
    def execute(command: str) -> str:
        cmd = command_parser.parse_command(command)
        assert cmd is not None
        result = command_parser.execute_command(cmd)
        print(f"\n> {command}")
        print(result)
        return result
    
    # Check initial titles
    result = execute("titles")
    assert "No titles unlocked yet" in result
    
    # Complete speed run conditions
    player.time_system.time.days = 1  # Set time to Day 1
    player.time_system.time.hours = 12  # Set time to noon
    result = player.complete_game("warrior")  # Complete game in under 2 days
    
    # Check for The Swift title
    result = execute("titles")
    assert "The Swift" in result
    
    # Test title selection
    result = execute("select title the_swift")
    assert "Title equipped: The Swift" in result
    
    # Verify title appears in status
    result = execute("status")
    assert "The Swift" in result

def test_time_based_events():
    """Test events and mechanics that depend on game time."""
    map_system = MapSystem()
    player = Player(map_system, player_id="test_player", player_name="Test Player")
    command_parser = CommandParser(player)
    
    def execute(command: str) -> str:
        cmd = command_parser.parse_command(command)
        assert cmd is not None
        result = command_parser.execute_command(cmd)
        print(f"\n> {command}")
        print(result)
        return result
    
    # Check morning description
    result = execute("look")
    assert "morning sun" in result
    
    # Defeat all enemies in the area before meditation
    result = execute("look")
    if "Wolf Pack" in result:
        result = execute("defeat Wolf Pack")
        assert "Victory" in result
    
    # Advance time to night (8:00 PM = 720 minutes from 8:00 AM)
    result = execute("meditate 720")  # Meditate for 12 hours to reach night
    assert "night" in result.lower()
    
    # Check night description
    result = execute("look")
    assert "The land lies under a blanket of stars" in result
    
    # Verify certain enemies only appear at night
    result = execute("look")
    assert "Shadow Stalker" in result  # Night-only enemy

def test_leaderboard_system():
    """Test the leaderboard tracking and display."""
    # Create multiple players for testing
    map_system = MapSystem()
    players = [
        Player(map_system, f"player_{i}", f"Player {i}")
        for i in range(1, 4)
    ]
    
    # Clear the leaderboard before starting
    players[0].leaderboard_system.clear()
    
    # Simulate game completions
    # Player 1: Fast warrior path with 1 achievement
    players[0].time_system.time.days = 1
    players[0].time_system.time.hours = 12
    players[0].time_system.time.minutes = 35
    players[0].achievement_system.unlock_achievement("first_steps")
    result = players[0].complete_game("warrior")
    assert "Congratulations, Player 1" in result
    assert "Day 1, 12:35" in result
    
    # Player 2: Achievement-focused mystic path with 10 achievements
    players[1].time_system.time.days = 2
    players[1].time_system.time.hours = 15
    players[1].time_system.time.minutes = 45
    # Create and add a new leaderboard entry with more achievements
    entry = LeaderboardEntry(
        player_id=players[1].state.player_id,
        player_name=players[1].state.player_name,
        completion_time=players[1].time_system.time.get_formatted_time(),
        achievements=10,  # Set a higher achievement count
        path_type="mystic",
        date=datetime.now()
    )
    players[1].leaderboard_system.add_entry(entry)
    
    # Player 3: Stealth path with 2 achievements
    players[2].time_system.time.days = 1
    players[2].time_system.time.hours = 18
    players[2].time_system.time.minutes = 20
    players[2].achievement_system.unlock_achievement("first_steps")
    players[2].achievement_system.unlock_achievement("first_blood")
    result = players[2].complete_game("stealth")
    assert "Congratulations, Player 3" in result
    
    # Test leaderboard display
    # Overall rankings
    result = players[0].get_leaderboard()
    assert "Overall Rankings" in result
    assert "1. Player 1" in result  # Should be fastest
    
    # Path-specific rankings
    result = players[0].get_leaderboard("warrior")
    assert "Warrior Path Rankings" in result
    assert "1. Player 1" in result
    
    # Test mystic path rankings
    result = players[1].get_leaderboard("mystic")  # Use player 2's instance
    assert "Mystic Path Rankings" in result
    assert "1. Player 2" in result
    
    # Achievement rankings
    result = players[0].get_leaderboard("achievements")
    print("\nAchievement Rankings:")
    print(result)  # Print the result for debugging
    assert "Most Achievements" in result
    assert "1. Player 2" in result  # Should have most achievements (10)
    
    # Test personal records
    result = players[0].get_personal_records()
    assert "Personal Records" in result
    assert "Warrior Path: Day 1, 12:35" in result
    
    # Test global stats
    stats = players[0].leaderboard_system.get_global_stats()
    assert stats["total_entries"] == 3
    assert stats["total_players"] == 3
    assert stats["path_distribution"]["warrior"] == 1
    assert stats["path_distribution"]["mystic"] == 1
    assert stats["path_distribution"]["stealth"] == 1
    
    # Test path records
    warrior_records = players[0].leaderboard_system.get_path_records("warrior")
    assert "Player 1" in warrior_records["fastest_time"]
    
    mystic_records = players[0].leaderboard_system.get_path_records("mystic")
    assert "Player 2" in mystic_records["most_achievements"] 
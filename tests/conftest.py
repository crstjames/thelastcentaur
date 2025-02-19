"""
Pytest configuration and fixtures for The Last Centaur tests.
"""

import pytest
from src.engine.core.player import Player
from src.engine.core.map_system import MapSystem
from src.engine.core.command_parser import CommandParser

@pytest.fixture
def map_system():
    """Create a fresh map system for each test."""
    return MapSystem()

@pytest.fixture
def player(map_system):
    """Create a fresh player instance for each test."""
    return Player(map_system)

@pytest.fixture
def command_parser(player):
    """Create a command parser instance for each test."""
    return CommandParser(player)

@pytest.fixture
def execute_command(command_parser):
    """Helper fixture to execute commands and return results."""
    def _execute(command: str) -> str:
        cmd = command_parser.parse_command(command)
        assert cmd is not None, f"Command '{command}' could not be parsed"
        result = command_parser.execute_command(cmd)
        print(f"\n> {command}")
        print(result)
        return result
    return _execute 
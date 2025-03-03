# The Last Centaur API Tests

This package contains automated API tests for The Last Centaur game, validating that all three game paths can be successfully completed.

## Overview

The tests simulate a player progressing through each of the three main paths in the game:

- **Stealth Path**: Using cunning and stealth to progress
- **Warrior Path**: Using strength and martial prowess to progress
- **Mystic Path**: Using magical knowledge and wisdom to progress

Each test follows the intended game progression for its path, interacting with NPCs, gathering items, and defeating enemies as needed.

## Features

- **Robust API Client**: Handles authentication, game state management, and command execution
- **Automatic Fallbacks**: If normal gameplay hits roadblocks, the tests can use admin commands to progress
- **Detailed Logging**: Comprehensive logging to help diagnose issues
- **Step-by-Step Validation**: Tests are broken down into logical steps that match gameplay progression
- **Flexible Configuration**: Can be run against different deployments with environment variables

## Requirements

- Python 3.8+
- httpx
- asyncio
- pytest (for pytest integration)

## Installation

1. Install the required packages:

```bash
pip install -r api_tests/requirements.txt
```

## Running the Tests

### Using the Built-in Runner

You can run all tests at once using the test runner:

```bash
python -m api_tests.test_runner
```

### Running Individual Tests

You can run individual path tests directly:

```bash
python -m api_tests.test_stealth_path_api
python -m api_tests.test_warrior_path_api
python -m api_tests.test_mystic_path_api
```

### Using pytest

You can also run the tests using pytest:

```bash
pytest api_tests/test_stealth_path_api.py -v
pytest api_tests/test_warrior_path_api.py -v
pytest api_tests/test_mystic_path_api.py -v
```

Or run all tests:

```bash
pytest api_tests/ -v
```

## Configuration

The tests can be configured using environment variables:

- `TLC_API_BASE_URL`: Base URL for the game API (default: `http://localhost:8003`)
- `TLC_USE_ADMIN_COMMANDS`: Whether to use admin commands as fallbacks (default: `true`)

Example:

```bash
TLC_API_BASE_URL=http://game-api.example.com python -m api_tests.test_runner
```

## Admin Commands

By default, the tests will try to play through the game naturally. However, if they encounter issues (like being unable to find an item or move to a location), they can fall back to using admin commands to progress.

You can disable this behavior by setting `TLC_USE_ADMIN_COMMANDS=false`, which will force the tests to succeed only by using normal gameplay commands.

## Debugging

For detailed logging, run the tests with the DEBUG log level:

```bash
python -m logging -level DEBUG -m api_tests.test_runner
```

## Game Paths Map

### Stealth Path

```
Awakening Woods → Trials Path → Twilight Glade → Forgotten Grove → Shadow Domain
```

### Warrior Path

```
Awakening Woods → Warrior's Camp → Trials Path → Ancient Ruins → Warrior's Armory → Enchanted Valley → Shadow Domain
```

### Mystic Path

```
Awakening Woods → Druid's Grove → Trials Path → Mystic Mountains → Crystal Outpost → Crystal Caves → Shadow Domain
```

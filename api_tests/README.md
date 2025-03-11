# The Last Centaur - API Integration Tests

This directory contains integration tests for The Last Centaur that test the game through its API interface.

## Overview

These tests focus on verifying the game's behavior through the public API endpoints, simulating how real users and clients would interact with the game. They test the full system integration from API endpoint all the way through to game logic and database.

## Test Client

The `TestGameClient` class in `test_client.py` provides a convenient interface for interacting with the game API during tests. It handles:

- User registration and login
- Game instance creation and management
- Command sending and response handling
- Verification helpers for common test scenarios

## Test Categories

- **Path Tests**: Tests that verify completion of the game through various paths (warrior, mystic, stealth)
- **Movement Tests**: Tests for the movement system
- **Command Tests**: Tests for various game commands
- **Debug Tests**: Tests for debugging functionality

## Running the Tests

To run all the API tests:

```bash
python -m api_tests.test_runner
```

Or run individual tests:

```bash
python -m api_tests.test_warrior_path
```

## Relationship to Unit Tests

These tests verify the game's behavior from the outside, through its API. For more focused unit tests that directly test internal engine components, see the `tests/` directory in the project root.

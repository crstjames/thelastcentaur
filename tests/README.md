# The Last Centaur - Unit Tests

This directory contains unit tests for The Last Centaur game engine components.

## Overview

These tests focus on directly testing the internal engine components by calling their methods directly, rather than testing through the API interface. This allows for more precise testing of individual game systems.

## Test Categories

- **Core Tests**: Test basic game functionality (movement, inventory, etc.)
- **Engine Tests**: Test the game engine components
- **Path Tests**: Test different game paths (warrior, mystic, stealth)
- **System Tests**: Test specific game systems (combat, discovery, etc.)

## Running the Tests

To run the tests, use pytest from the project root:

```bash
pytest tests/
```

Or run a specific test:

```bash
pytest tests/test_warrior_path.py
```

## Test Organization

- `conftest.py`: Contains fixtures and setup for tests
- `test_*.py`: Individual test files
- Subdirectories contain more specialized tests

## Relationship to API Tests

The tests in this directory are unit tests that directly test engine components. For integration tests that test the game through its API interface, see the `api_tests/` directory.

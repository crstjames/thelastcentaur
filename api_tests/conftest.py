"""
Pytest configuration for The Last Centaur API Tests.

This module provides fixtures and configuration for running the tests with pytest.
"""

import os
import sys
import pytest
import logging
import asyncio
from typing import Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("pytest_runner")

# Allow setting the API base URL from an environment variable
@pytest.fixture
def api_base_url() -> str:
    """Get the API base URL from environment variable or use default."""
    return os.environ.get("TLC_API_BASE_URL", "http://localhost:8003")

# Allow enabling/disabling admin commands from an environment variable
@pytest.fixture
def use_admin_commands() -> bool:
    """Get whether to use admin commands from environment variable or use default."""
    return os.environ.get("TLC_USE_ADMIN_COMMANDS", "true").lower() in ("true", "1", "yes")

# Fixture for creating a consistent test ID
@pytest.fixture
def test_id(request) -> str:
    """Generate a test ID based on the test name."""
    test_name = request.node.name
    # Remove common pytest prefixes/suffixes and clean up
    test_name = test_name.replace("test_", "").replace("_api", "").replace("_test", "")
    return f"pytest_{test_name}_{os.getpid()}"

# Mark all tests as asyncio tests
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "asyncio: mark test as an asyncio coroutine")

# Make all tests run with asyncio
@pytest.fixture(autouse=True)
def event_loop():
    """Create a new event loop for each test."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close() 
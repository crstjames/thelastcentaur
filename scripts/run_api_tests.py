#!/usr/bin/env python3
"""
API Test Runner for The Last Centaur.

This script runs the API tests that verify the game works through the API without LLM dependencies.
"""

import os
import sys
import argparse
import subprocess
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("api_test_runner")

def main():
    """Run the specified API tests."""
    parser = argparse.ArgumentParser(description="Run API tests")
    parser.add_argument(
        "--test", 
        choices=["movement", "combat", "puzzle", "simple", "navigation", "paths", "db", "all"],
        default="simple",
        help="Which API test to run: movement, combat, puzzle, navigation, simple (mocked), paths, db (real database), or all tests"
    )
    
    args = parser.parse_args()
    
    # Build pytest command
    pytest_cmd = ["python", "-m", "pytest", "-xvs"]
    
    # Determine which test file to run
    if args.test == "all":
        # Run all API tests
        pytest_cmd.append("tests/test_api_simple.py")
        pytest_cmd.append("tests/test_api_movement.py")
        pytest_cmd.append("tests/test_api_combat_system.py")
        pytest_cmd.append("tests/test_api_puzzle_system.py")
        pytest_cmd.append("tests/test_api_navigation.py")
        pytest_cmd.append("tests/test_api_path_progression.py")
        pytest_cmd.append("tests/test_api_db_integration.py")
    elif args.test == "movement":
        # Run movement API tests
        pytest_cmd.append("tests/test_api_movement.py")
    elif args.test == "combat":
        # Run combat API tests
        pytest_cmd.append("tests/test_api_combat_system.py")
    elif args.test == "puzzle":
        # Run puzzle API tests
        pytest_cmd.append("tests/test_api_puzzle_system.py")
    elif args.test == "navigation":
        # Run enhanced navigation API tests
        pytest_cmd.append("tests/test_api_navigation.py")
    elif args.test == "simple":
        # Run simplified API tests
        pytest_cmd.append("tests/test_api_simple.py")
    elif args.test == "paths":
        # Run path progression tests
        pytest_cmd.append("tests/test_api_path_progression.py")
    elif args.test == "db":
        # Run database integration tests
        pytest_cmd.append("tests/test_api_db_integration.py")
    
    logger.info(f"Running API tests with command: {' '.join(pytest_cmd)}")
    
    try:
        # Run the pytest command
        result = subprocess.run(pytest_cmd, check=False)
        
        # Check the result
        if result.returncode == 0:
            logger.info("API tests completed successfully")
        else:
            logger.error(f"API tests failed with exit code {result.returncode}")
            sys.exit(result.returncode)
    except Exception as e:
        logger.error(f"Error running API tests: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 
#!/usr/bin/env python3
"""
Test runner for The Last Centaur game.

This script runs the specified tests or all tests if none are specified.
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
logger = logging.getLogger("test_runner")

def main():
    """Run the specified tests."""
    parser = argparse.ArgumentParser(description="Run game tests")
    parser.add_argument(
        "--path", 
        choices=["warrior", "mystic", "stealth", "all", "movement"],
        default="all",
        help="Which path to test"
    )
    parser.add_argument(
        "--test", 
        help="Specific test to run (e.g., 'test_cardinal_directions')"
    )
    
    args = parser.parse_args()
    
    # Build pytest command
    pytest_cmd = ["python", "-m", "pytest", "-xvs"]
    
    # Determine which test file to run
    if args.path == "all":
        # Run all test files
        pytest_cmd.append("api_tests/")
    elif args.path == "warrior":
        # Run warrior path test
        pytest_cmd.append("api_tests/test_game_paths.py::TestWarriorPath")
    elif args.path == "mystic":
        # Run mystic path test
        pytest_cmd.append("api_tests/test_game_paths.py::TestMysticPath")
    elif args.path == "stealth":
        # Run stealth path test
        pytest_cmd.append("api_tests/test_game_paths.py::TestStealthPath")
    elif args.path == "movement":
        # Run movement tests
        pytest_cmd.append("api_tests/test_movement.py")
        
    # Add specific test if provided
    if args.test:
        # Append the specific test to the path
        if "::" not in pytest_cmd[-1]:
            pytest_cmd[-1] = f"{pytest_cmd[-1]}::{args.test}"
        else:
            # If we already have a class specified, append the test
            pytest_cmd[-1] = f"{pytest_cmd[-1]}::{args.test}"
    
    logger.info(f"Running tests with command: {' '.join(pytest_cmd)}")
    
    try:
        # Run the pytest command
        result = subprocess.run(pytest_cmd, check=False)
        
        # Check the result
        if result.returncode == 0:
            logger.info("Tests completed successfully")
        else:
            logger.error(f"Tests failed with exit code {result.returncode}")
            sys.exit(result.returncode)
    except Exception as e:
        logger.error(f"Error running tests: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 
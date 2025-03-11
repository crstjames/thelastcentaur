#!/usr/bin/env python3
"""
Core Engine Test Runner for The Last Centaur.

This script runs the core engine tests without API or LLM dependencies.
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
logger = logging.getLogger("core_test_runner")

def main():
    """Run the specified core engine tests."""
    parser = argparse.ArgumentParser(description="Run core engine tests")
    parser.add_argument(
        "--test", 
        choices=["warrior", "mystic", "stealth", "all", "movement", "board", "items", "combat", "puzzle"],
        default="all",
        help="Which test to run: warrior path, mystic path, stealth path, movement, board exploration, item interaction, combat, puzzle system, or all tests"
    )
    
    args = parser.parse_args()
    
    # Build pytest command
    pytest_cmd = ["python", "-m", "pytest", "-xvs"]
    
    # Determine which test file to run
    if args.test == "all":
        # Run all core engine tests
        pytest_cmd.append("tests/test_warrior_path.py")
        pytest_cmd.append("tests/test_mystic_path.py")
        pytest_cmd.append("tests/test_stealth_path.py")
        pytest_cmd.append("tests/test_movement.py")
        pytest_cmd.append("tests/test_board_exploration.py")
        pytest_cmd.append("tests/test_combat_system.py")
        pytest_cmd.append("tests/test_puzzle_system.py")
    elif args.test == "warrior":
        # Run warrior path test
        pytest_cmd.append("tests/test_warrior_path.py")
    elif args.test == "mystic":
        # Run mystic path test
        pytest_cmd.append("tests/test_mystic_path.py")
    elif args.test == "stealth":
        # Run stealth path test
        pytest_cmd.append("tests/test_stealth_path.py")
    elif args.test == "movement":
        # Run movement tests
        pytest_cmd.append("tests/test_movement.py")
    elif args.test == "board":
        # Run board exploration tests
        pytest_cmd.append("tests/test_board_exploration.py")
    elif args.test == "items":
        # Run item interaction tests (from board exploration)
        pytest_cmd.append("tests/test_board_exploration.py::TestCompleteBoardExploration::test_pickup_items")
    elif args.test == "combat":
        # Run combat tests
        pytest_cmd.append("tests/test_combat_system.py")
    elif args.test == "puzzle":
        # Run puzzle system tests
        pytest_cmd.append("tests/test_puzzle_system.py")
    
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
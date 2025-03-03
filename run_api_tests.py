#!/usr/bin/env python3
"""
Run all API tests for The Last Centaur.

This script is a convenience wrapper around api_tests.test_runner.
"""

import os
import sys
import asyncio

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Run the tests
if __name__ == "__main__":
    try:
        # Import and run the test runner
        from api_tests.test_runner import main
        main()
    except ImportError as e:
        print(f"Error importing test runner: {e}")
        print("Make sure you've installed the required packages:")
        print("pip install -r api_tests/requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"Error running tests: {e}")
        sys.exit(1) 
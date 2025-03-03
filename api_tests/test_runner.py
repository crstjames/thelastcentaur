"""
Test runner for The Last Centaur API Tests.

This module provides a runner for executing API tests asynchronously with
proper error handling and reporting.
"""

import os
import sys
import asyncio
import logging
import inspect
import traceback
import time
from typing import Dict, List, Callable, Awaitable, Optional, Any, Tuple

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("thelastcentaur_test_runner")

class TestRunner:
    """Runner for API tests that handles async execution."""
    
    def __init__(self, stop_on_failure: bool = False):
        """
        Initialize the test runner.
        
        Args:
            stop_on_failure: Whether to stop running tests after a failure
        """
        self.stop_on_failure = stop_on_failure
        self.test_results = {}
        
    async def run_test(self, test_func: Callable[[], Awaitable[None]], test_name: Optional[str] = None) -> Tuple[bool, str]:
        """
        Run a single test function asynchronously.
        
        Args:
            test_func: Async test function to execute
            test_name: Name of the test (defaults to function name)
            
        Returns:
            Tuple of (success, error_message)
        """
        if test_name is None:
            test_name = test_func.__name__
        
        logger.info(f"Running test: {test_name}")
        start_time = time.time()
        
        try:
            await test_func()
            duration = time.time() - start_time
            logger.info(f"Test {test_name} passed in {duration:.2f} seconds")
            return True, ""
        except Exception as e:
            duration = time.time() - start_time
            error_message = f"{str(e)}\n{traceback.format_exc()}"
            logger.error(f"Test {test_name} failed after {duration:.2f} seconds: {error_message}")
            return False, error_message
            
    async def run_tests(self, tests: Dict[str, Callable[[], Awaitable[None]]]) -> Dict[str, Dict[str, Any]]:
        """
        Run multiple tests and collect results.
        
        Args:
            tests: Dictionary mapping test names to test functions
            
        Returns:
            Dictionary mapping test names to result dictionaries
        """
        results = {}
        
        for test_name, test_func in tests.items():
            logger.info(f"Starting test: {test_name}")
            start_time = time.time()
            success, error_message = await self.run_test(test_func, test_name)
            duration = time.time() - start_time
            
            results[test_name] = {
                "success": success,
                "duration": duration,
                "error_message": error_message
            }
            
            if not success and self.stop_on_failure:
                logger.warning("Stopping tests due to failure and stop_on_failure=True")
                break
                
        self.test_results = results
        return results
        
    def print_results(self) -> None:
        """Print a summary of test results."""
        if not self.test_results:
            logger.warning("No test results to print")
            return
            
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result["success"])
        failed_tests = total_tests - passed_tests
        
        print("\n" + "=" * 80)
        print(f"TEST RESULTS: {passed_tests}/{total_tests} PASSED ({failed_tests} FAILED)")
        print("-" * 80)
        
        for test_name, result in self.test_results.items():
            status = "PASS" if result["success"] else "FAIL"
            duration = result["duration"]
            print(f"{status}: {test_name} ({duration:.2f}s)")
            
            if not result["success"]:
                first_error_line = result['error_message'].split('\n')[0]
                print(f"  Error: {first_error_line}")
                
        print("=" * 80)
        
def main() -> None:
    """Main entry point for running tests."""
    from api_tests.test_stealth_path_api import test_stealth_path_api
    from api_tests.test_warrior_path_api import test_warrior_path_api
    from api_tests.test_mystic_path_api import test_mystic_path_api
    
    tests = {
        "Stealth Path": test_stealth_path_api,
        "Warrior Path": test_warrior_path_api,
        "Mystic Path": test_mystic_path_api
    }
    
    runner = TestRunner(stop_on_failure=False)
    
    async def run():
        await runner.run_tests(tests)
        runner.print_results()
        
    asyncio.run(run())
    
    # Exit with error code if any tests failed
    if any(not result["success"] for result in runner.test_results.values()):
        sys.exit(1)

if __name__ == "__main__":
    main() 
"""
Base Path Test for The Last Centaur API Tests.

This module provides a base class for path-specific tests that includes
common functionality and utilities.
"""

import os
import sys
import asyncio
import logging
import json
from typing import Dict, List, Optional, Union, Any, Callable, Awaitable

from api_tests.test_client import TestGameClient, ensure_item_acquired, ensure_enemy_defeated
from api_tests.test_client import verify_current_area, verify_inventory_contains

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("thelastcentaur_path_tests")

class BasePathTest:
    """Base class for path-specific tests."""
    
    def __init__(self, 
                path_name: str,
                required_items: List[str],
                api_base_url: str = "http://localhost:8000",
                username_prefix: str = "test",
                max_retries: int = 3,
                use_admin_commands: bool = True):
        """
        Initialize the base path test.
        
        Args:
            path_name: Name of the path being tested (stealth, warrior, mystic)
            required_items: List of items required to complete the path
            api_base_url: Base URL for the game API
            username_prefix: Prefix for the test username
            max_retries: Maximum number of retries for failed operations
            use_admin_commands: Whether to use admin commands as fallbacks
        """
        self.path_name = path_name
        self.required_items = required_items
        self.api_base_url = api_base_url
        self.username = f"{username_prefix}_{path_name}_path"
        self.max_retries = max_retries
        self.use_admin_commands = use_admin_commands
        
        # Initialize state
        self.client = None
        self.steps_completed = set()
        self.command_retries = {}
        
    async def setup(self) -> None:
        """Set up the test by creating a client, logging in, and starting a game."""
        logger.info(f"Setting up {self.path_name} path test")
        
        self.client = TestGameClient(api_base_url=self.api_base_url)
        await self.client.login(self.username)
        await self.client.create_game()
        
        logger.info(f"Setup complete for {self.path_name} path test")
        
    async def teardown(self) -> None:
        """Clean up resources after the test."""
        logger.info(f"Tearing down {self.path_name} path test")
        
        if self.client:
            await self.client.cleanup()
            
        logger.info(f"Teardown complete for {self.path_name} path test")
        
    async def execute_command(self, 
                            command: str, 
                            expected_text: Optional[str] = None,
                            max_retries: Optional[int] = None,
                            ignore_failure: bool = False,
                            case_sensitive: bool = True) -> str:
        """
        Execute a command and check for expected text in the response.
        
        Args:
            command: The command to execute
            expected_text: Text that should be in the response
            max_retries: Maximum number of retries (defaults to self.max_retries)
            ignore_failure: Whether to ignore failure if expected_text is not found
            case_sensitive: Whether to use case-sensitive matching for expected_text
            
        Returns:
            The response from the command
            
        Raises:
            AssertionError: If expected_text is not found in the response and ignore_failure is False
        """
        if max_retries is None:
            max_retries = self.max_retries
            
        # Track retries for this command
        if command not in self.command_retries:
            self.command_retries[command] = 0
        else:
            self.command_retries[command] += 1
            
        current_retry = self.command_retries[command]
        
        # Log with retry count if applicable
        if current_retry > 0:
            logger.info(f"Executing command (retry {current_retry}/{max_retries}): '{command}'")
        else:
            logger.info(f"Executing command: '{command}'")
        
        response = await self.client.send_command(command)
        
        # Check for expected text if specified
        if expected_text:
            # Prepare text for comparison based on case sensitivity
            response_to_check = response
            expected_to_check = expected_text
            
            if not case_sensitive:
                response_to_check = response.lower()
                expected_to_check = expected_text.lower()
                
            if expected_to_check not in response_to_check:
                if current_retry < max_retries:
                    # Try looking around first and then retry
                    logger.warning(f"Expected text '{expected_text}' not found in response to '{command}', looking around and retrying")
                    await self.client.send_command("look")
                    return await self.execute_command(command, expected_text, max_retries, ignore_failure, case_sensitive)
                elif not ignore_failure:
                    logger.error(f"Expected text '{expected_text}' not found in response to '{command}' after {max_retries} retries")
                    logger.error(f"Actual response: {response}")
                    raise AssertionError(f"Expected text '{expected_text}' not found in response to '{command}'")
                else:
                    logger.warning(f"Expected text '{expected_text}' not found in response to '{command}', but ignoring failure")
                
        return response
        
    async def ensure_location(self, area_name: str) -> bool:
        """
        Ensure that the player is in the specified area.
        
        Args:
            area_name: Name of the area
            
        Returns:
            True if in the specified area (or teleported there), False otherwise
        """
        # First try to verify current location
        in_area = await verify_current_area(self.client, area_name)
        
        if in_area:
            logger.info(f"Already in area: {area_name}")
            return True
            
        # If not in the area and admin commands are enabled, try teleporting
        if self.use_admin_commands:
            logger.info(f"Not in area {area_name}, attempting to teleport")
            try:
                await self.client.admin_teleport(area_name)
                
                # Verify teleport success
                in_area_after_teleport = await verify_current_area(self.client, area_name)
                if in_area_after_teleport:
                    logger.info(f"Successfully teleported to {area_name}")
                    return True
                else:
                    logger.warning(f"Teleport to {area_name} seemed to succeed but verification failed")
            except Exception as e:
                logger.error(f"Failed to teleport to {area_name}: {str(e)}")
                
        logger.warning(f"Failed to ensure location in {area_name}")
        return False
        
    async def ensure_item(self, item_name: str, commands_to_try: List[str]) -> bool:
        """
        Ensure that the player has the specified item.
        
        Args:
            item_name: Name of the item
            commands_to_try: List of commands to try to acquire the item
            
        Returns:
            True if the item was acquired (or already had), False otherwise
        """
        # Check inventory first
        inventory_response = await self.client.send_command("inventory")
        if item_name in inventory_response:
            logger.info(f"Already have item: {item_name}")
            return True
            
        # Try to acquire the item naturally
        item_acquired = await ensure_item_acquired(self.client, item_name, commands_to_try)
        
        if item_acquired:
            logger.info(f"Successfully acquired item: {item_name}")
            return True
            
        # If natural acquisition failed and admin commands are enabled, force add the item
        if self.use_admin_commands:
            logger.warning(f"Failed to acquire {item_name} naturally, using admin command")
            try:
                await self.client.admin_force_item(item_name)
                
                # Verify item was added
                inventory_after = await self.client.send_command("inventory")
                if item_name in inventory_after:
                    logger.info(f"Successfully force-added item: {item_name}")
                    return True
                else:
                    logger.warning(f"Force-add of {item_name} seemed to succeed but verification failed")
            except Exception as e:
                logger.error(f"Failed to force-add item {item_name}: {str(e)}")
                
        logger.warning(f"Failed to ensure item: {item_name}")
        return False
        
    async def verify_completion(self) -> bool:
        """
        Verify that the path has been completed successfully.
        
        Returns:
            True if all required items are in inventory and in final area, False otherwise
        """
        logger.info(f"Verifying completion of {self.path_name} path")
        
        # Check if we have all required items
        missing_items = await verify_inventory_contains(self.client, self.required_items)
        
        if missing_items:
            logger.warning(f"Missing required items: {missing_items}")
            return False
            
        # Check if we're in the final area (Shadow Domain)
        in_final_area = await verify_current_area(self.client, "SHADOW_DOMAIN")
        
        if not in_final_area:
            logger.warning("Not in final area (Shadow Domain)")
            return False
            
        logger.info(f"{self.path_name} path completed successfully")
        return True
        
    async def run_test(self) -> None:
        """
        Run the path test.
        
        This method should be overridden by subclasses to implement path-specific logic.
        """
        raise NotImplementedError("Subclasses must override run_test method")
        
    async def try_step(self, step_name: str, step_func: Callable[[], Awaitable[None]]) -> bool:
        """
        Try to execute a test step and mark it as completed if successful.
        
        Args:
            step_name: Name of the step
            step_func: Async function to execute for the step
            
        Returns:
            True if the step succeeded, False otherwise
        """
        if step_name in self.steps_completed:
            logger.info(f"Step '{step_name}' already completed, skipping")
            return True
            
        logger.info(f"Executing step: {step_name}")
        try:
            await step_func()
            self.steps_completed.add(step_name)
            logger.info(f"Step '{step_name}' completed successfully")
            return True
        except Exception as e:
            logger.error(f"Step '{step_name}' failed: {str(e)}")
            return False
            
    async def __call__(self) -> None:
        """Make the test runnable by calling the instance."""
        try:
            await self.setup()
            await self.run_test()
            # Verify completion even if run_test passes (belt and suspenders)
            completion_verified = await self.verify_completion()
            if not completion_verified:
                raise AssertionError(f"{self.path_name} path completion verification failed")
        finally:
            await self.teardown() 
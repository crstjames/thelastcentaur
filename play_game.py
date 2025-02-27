#!/usr/bin/env python3
"""
The Last Centaur - Natural Language Game Interface

This script starts the natural language interface for The Last Centaur game.
It allows players to interact with the game using natural language and
receive rich, immersive responses.

Usage:
    python play_game.py [--port PORT]

Options:
    --port PORT    Port for the game API (default: 8000)
"""

import os
import sys
import asyncio
import argparse
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Check for required environment variables
required_env_vars = ["OPENAI_API_KEY"]
missing_vars = [var for var in required_env_vars if not os.getenv(var)]

if missing_vars:
    print(f"Error: Missing required environment variables: {', '.join(missing_vars)}")
    print("Please set these variables in your .env file or environment.")
    sys.exit(1)

# Import the CLI interface
try:
    from src.game.llm_cli import main
except ImportError as e:
    print(f"Error importing game modules: {e}")
    print("Make sure you're running this script from the project root directory.")
    sys.exit(1)

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="The Last Centaur - Natural Language CLI")
    parser.add_argument("--port", type=int, default=8000, help="Port for the game API (default: 8000)")
    args = parser.parse_args()
    
    # Run the CLI with the specified port
    asyncio.run(main(args.port)) 
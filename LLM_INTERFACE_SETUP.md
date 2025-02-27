# Setting Up the LLM Interface for The Last Centaur

This document provides step-by-step instructions for setting up and using the LLM-powered natural language interface for The Last Centaur game.

## What We've Built

We've created a natural language interface for The Last Centaur that allows players to:

1. Interact with the game using everyday language instead of specific commands
2. Receive rich, immersive responses that enhance the game's narrative
3. Maintain context-aware conversations for a more coherent experience

The implementation consists of:

- `src/game/llm_interface.py`: Core class that handles natural language understanding and response enhancement
- `src/game/llm_cli.py`: Command-line interface for playing the game with natural language
- `play_game.py`: Executable script to start the LLM interface
- `examples/llm_interface_example.py`: Example script demonstrating programmatic use of the interface
- `tests/test_llm_interface.py`: Test suite for the LLM interface

## Prerequisites

Before using the LLM interface, you need:

1. The Last Centaur game server installed and configured
2. API keys for OpenAI and Anthropic
3. Python 3.9+ with required dependencies installed

## Setup Instructions

1. **Install Dependencies**

   Make sure all required packages are installed:

   ```bash
   pip install -r requirements.txt
   ```

2. **Configure API Keys**

   Add your API keys to the `.env` file:

   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ANTHROPIC_API_KEY=your_anthropic_api_key_here
   ```

3. **Start the Game Server**

   In one terminal, start The Last Centaur game server:

   ```bash
   python -m src.main
   ```

4. **Start the LLM Interface**

   In another terminal, run the LLM interface:

   ```bash
   python play_game.py
   ```

## Using the LLM Interface

Once both the game server and LLM interface are running:

1. **Register or Login**

   - If you're a new user, select option 2 to register
   - If you already have an account, select option 1 to login

2. **Create or Load a Game**

   - If you have existing games, you can choose to load one
   - Otherwise, create a new game with a name and description

3. **Play with Natural Language**
   - Type commands in natural language (e.g., "I want to go north" instead of just "north")
   - Receive rich, immersive responses that enhance the game experience
   - Use the context of your conversation to make more natural interactions

## Example Commands

Here are some examples of natural language commands you can use:

| Natural Language Input                 | Equivalent Game Command |
| -------------------------------------- | ----------------------- |
| "I want to go north"                   | north                   |
| "Look around carefully"                | look                    |
| "Pick up the sword"                    | take sword              |
| "Check what I'm carrying"              | inventory               |
| "Attack the wolf with my sword"        | attack wolf             |
| "Talk to the merchant about his wares" | talk merchant           |
| "Draw my sword and prepare for battle" | examine sword           |
| "Mark this location on my map"         | map                     |

## Programmatic Usage

If you want to integrate the LLM interface into your own application, you can use the `LLMInterface` class directly. See `examples/llm_interface_example.py` for a demonstration of how to:

1. Connect to the game API
2. Login and create a game instance
3. Process natural language commands
4. Enhance game responses

## Troubleshooting

- **API Key Issues**: Make sure your API keys are correctly set in the `.env` file
- **Connection Errors**: Ensure the game server is running on the expected port
- **Import Errors**: Run the scripts from the project root directory
- **Rate Limiting**: If you encounter rate limiting from the LLM providers, consider implementing caching or reducing the frequency of requests

## Next Steps

- **Custom Prompts**: Modify the system prompts in `src/game/llm_interface.py` to change how commands are interpreted or responses are enhanced
- **Web Interface**: Integrate the LLM interface with a web frontend for a more accessible experience
- **Voice Input/Output**: Add speech-to-text and text-to-speech capabilities for a fully voice-controlled game
- **Response Caching**: Implement caching for common responses to reduce API usage and improve performance

# The Last Centaur - LLM Interface

This extension adds a natural language interface to The Last Centaur game, allowing players to interact with the game using everyday language and receive rich, immersive responses.

## Features

- **Natural Language Understanding**: Interpret player commands expressed in natural language
- **Rich Fantasy Descriptions**: Enhance game responses with vivid, detailed fantasy descriptions
- **Context-Aware Assistance**: Maintain conversation history for more coherent interactions
- **Simple CLI Interface**: Easy-to-use command-line interface for playing the game

## Prerequisites

- Python 3.9+
- The Last Centaur game server running
- OpenAI API key
- Anthropic API key

## Installation

1. Make sure all dependencies are installed:

   ```
   pip install -r requirements.txt
   ```

2. Set up your environment variables in a `.env` file:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ANTHROPIC_API_KEY=your_anthropic_api_key_here
   ```

## Usage

1. Start The Last Centaur game server:

   ```
   python -m src.main
   ```

2. In a separate terminal, run the LLM interface:

   ```
   python play_game.py
   ```

3. Follow the prompts to:
   - Register a new user or log in with existing credentials
   - Create a new game or load an existing one
   - Start playing using natural language commands

## Example Commands

The LLM interface allows you to use natural language instead of specific game commands. For example:

| Natural Language Input | Game Command  |
| ---------------------- | ------------- |
| "I want to go north"   | north         |
| "Look around"          | look          |
| "Pick up the sword"    | take sword    |
| "Check my inventory"   | inventory     |
| "Attack the wolf"      | attack wolf   |
| "Talk to the merchant" | talk merchant |

## Architecture

The LLM interface consists of two main components:

1. **LLMInterface** (`src/game/llm_interface.py`): Core class that handles:

   - Natural language understanding
   - Game API communication
   - Response enhancement

2. **GameCLI** (`src/game/llm_cli.py`): Command-line interface that provides:
   - User authentication
   - Game management
   - Interactive gameplay loop

## Customization

You can customize the LLM behavior by modifying the system prompts in `src/game/llm_interface.py`:

- `command_system_prompt`: Controls how natural language is interpreted
- `response_system_prompt`: Controls how game responses are enhanced

## Troubleshooting

- **API Key Issues**: Ensure your API keys are correctly set in the `.env` file
- **Connection Errors**: Make sure the game server is running on the expected port
- **Import Errors**: Run the script from the project root directory

## License

This project is licensed under the same terms as The Last Centaur game.

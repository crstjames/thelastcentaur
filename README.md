# The Last Centaur

A text-based RPG that combines classic role-playing elements with modern accessibility, allowing players to experience an epic story through web browsers and chat interfaces.

![Version](https://img.shields.io/badge/version-0.1.0-blue)
![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## Overview

The Last Centaur is an immersive text-based RPG where you play as Centaur Prime, the last of your kind, seeking to reclaim your destiny. Navigate through a rich world filled with ancient magic, forgotten lore, and challenging choices.

### Key Features

- Three distinct paths to victory:
  - 🗡️ **Warrior Path**: Master combat and ancient weapons
  - 🔮 **Mystic Path**: Harness magical powers and forgotten knowledge
  - 🌑 **Stealth Path**: Master the arts of shadows and deception
- Rich, dynamic world with:
  - Detailed environment descriptions
  - Interactive NPCs with unique stories
  - Complex item and resource systems
  - Weather and environmental effects
- Multiple interface options:
  - Web browser interface
  - Chat platform integration
  - Command-line interface
  - **NEW: Natural Language Interface** powered by LLMs

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/thelastcentaur.git
cd thelastcentaur
```

2. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Set up PostgreSQL:

```bash
# Install PostgreSQL if you haven't already
# On macOS: brew install postgresql
# On Ubuntu: sudo apt install postgresql

# Start PostgreSQL service
# On macOS: brew services start postgresql
# On Ubuntu: sudo service postgresql start

# Create a PostgreSQL user (if needed)
# createuser -P -s postgres
```

5. Set up environment variables:

```bash
cp .env.example .env
# Edit .env with your configuration
```

The application will automatically create the database and tables on startup if they don't exist.

## Quick Start

1. Start the game server:

```bash
python -m src.main
```

2. Start the frontend development server:

```bash
cd frontend && npm run dev -- -p 3002
```

3. Open your web browser and navigate to:

```
http://localhost:3002
```

> **Important**: For details on port configuration and troubleshooting connection issues, see [PORT_CONFIGURATION.md](PORT_CONFIGURATION.md).

### Using the Natural Language Interface

For a more immersive experience, you can use the LLM-powered natural language interface:

1. Make sure you have set up your API keys in the `.env` file:

```
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

2. In a separate terminal, run the LLM interface:

```bash
python play_game.py
```

3. Follow the prompts to register/login and start playing using natural language!

For more details on the LLM interface, see [README_LLM_INTERFACE.md](README_LLM_INTERFACE.md).

## Testing the Game API

For development and testing purposes, you can interact with the game directly through the API. Follow these steps to test the core functionality:

### 1. Register a New User

```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "email": "test@example.com", "password": "password123"}'
```

**Note:** If you encounter a "Username already registered" error, try a different username.

### 2. Login to Get an Access Token

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -F "username=testuser" \
  -F "password=password123"
```

This will return an access token in the format:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Important:** Save this token for use in subsequent requests. The token will be valid for 24 hours.

### 3. Create a Game Instance

```bash
curl -X POST "http://localhost:8000/api/v1/game" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{"name": "My Adventure", "max_players": 1, "description": "A test game instance"}'
```

This will return a game instance ID that you'll need for further commands.

### 4. View the Game Map

```bash
curl -X GET "http://localhost:8000/api/v1/game/YOUR_GAME_ID/map" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 5. Look Around

```bash
curl -X POST "http://localhost:8000/api/v1/game/YOUR_GAME_ID/command" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{"command": "look"}'
```

### 6. Try Movement Commands

```bash
# Move north
curl -X POST "http://localhost:8000/api/v1/game/YOUR_GAME_ID/command" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{"command": "north"}'

# Other directions: south, east, west
```

### 7. Other Commands to Try

```bash
# Check inventory
curl -X POST "http://localhost:8000/api/v1/game/YOUR_GAME_ID/command" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{"command": "inventory"}'

# Attack an enemy
curl -X POST "http://localhost:8000/api/v1/game/YOUR_GAME_ID/command" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{"command": "attack wolf"}'
```

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

4. Set up environment variables:

```bash
cp .env.example .env
# Edit .env with your configuration
```

## Quick Start

1. Start the game server:

```bash
python -m src.main
```

2. Open your web browser and navigate to:

```
http://localhost:8000
```

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

### Known Issues

- **Authentication Persistence**: This issue has been fixed by implementing a persistent secret key that is stored in `auth_secret.json`. If you encounter authentication issues after a server restart, make sure this file exists and has not been corrupted.
- **Port Conflicts**: If you see "Address already in use" errors, check for existing processes using port 8000 with `lsof -i :8000` and terminate them if needed.

## Game Commands

### Basic Movement

- `n`, `s`, `e`, `w` - Move in cardinal directions
- `look` - Examine your surroundings
- `inventory` or `i` - Check your inventory
- `map` or `m` - View discovered areas

### Interaction

- `take/get [item]` - Pick up items
- `drop [item]` - Drop items
- `talk [npc]` - Interact with NPCs
- `gather [resource]` - Collect resources

### Combat

- `attack [target]` - Attack an enemy
- `defend` - Take defensive stance
- `dodge` - Prepare to dodge
- `special` - Use special ability

### Environment

- `mark [desc]` - Leave a mark
- `draw [desc]` - Draw something
- `write [text]` - Write a message
- `alter [desc]` - Change the environment

## Development

### Project Structure

```
thelastcentaur/
├── src/
│   ├── engine/
│   │   ├── core/
│   │   │   ├── models.py      # Core game models
│   │   │   ├── map_system.py  # World and map logic
│   │   │   ├── player.py      # Player mechanics
│   │   │   └── ...
│   │   ├── api/              # FastAPI endpoints
│   │   └── interfaces/       # UI implementations
│   └── main.py
├── tests/                    # Test suite
├── docs/                     # Documentation
└── requirements.txt
```

### Running Tests

```bash
pytest
pytest --cov=src tests/      # With coverage
```

### Code Style

We follow PEP 8 guidelines with some modifications:

```bash
black src/
isort src/
flake8 src/
```

## Contributing

1. Fork the repository
2. Create your feature branch:

```bash
git checkout -b feature/amazing-feature
```

3. Commit your changes:

```bash
git commit -m 'Add amazing feature'
```

4. Push to the branch:

```bash
git push origin feature/amazing-feature
```

5. Open a Pull Request

## Technical Details

### Core Systems

- FastAPI for web interface
- SQLAlchemy for data persistence
- Pydantic for data validation
- Pytest for testing

### Game Engine Features

- Event-driven architecture
- State management system
- Environmental effects system
- Dynamic NPC interactions

## Troubleshooting

### Common Issues

1. **Game won't start**

   - Check if all dependencies are installed
   - Verify environment variables
   - Check port availability

2. **Can't move between areas**

   - Verify you have required items
   - Check for blocking enemies
   - Ensure sufficient stamina

3. **Commands not working**
   - Check command syntax
   - Verify current game state
   - Check for environmental effects

### Getting Help

- Open an issue on GitHub
- Check the [Wiki](https://github.com/yourusername/thelastcentaur/wiki)
- Join our [Discord](https://discord.gg/thelastcentaur)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Inspired by classic text adventures
- Built with modern Python best practices
- Community contributions welcome

---

_"Not all who wander through the ancient woods are lost; some are finding their destiny."_ - The Hermit Druid

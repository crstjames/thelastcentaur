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

### Option 1: Local Installation

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

### Option 2: Docker Installation (Recommended)

If you prefer to use Docker, we provide several scripts to make Docker management easy:

1. Make sure Docker is installed and running on your system.

2. Use our Docker manager script for a convenient interface:

```bash
./docker-manager.sh
```

This interactive script provides options to:

- Start Docker containers
- Stop Docker containers
- Restart Docker containers
- Check Docker container status
- View Docker logs

For more detailed Docker setup instructions, see [docs/DOCKER.md](docs/DOCKER.md).

## Quick Start

After installation, you can play the game in several ways:

1. **Web Interface**: Run `python play_game.py` to start the game in your web browser.
2. **Command Line Interface**: Run `python play_game.py --cli` to play in the terminal.
3. **API Mode**: Start the API server with `uvicorn src.main:app --reload` and interact via HTTP requests.

## Documentation

For more detailed information about the project, check out these resources:

- [Documentation Index](docs/index.md)
- [API Reference](docs/api-reference.md) - Complete API endpoint documentation
- [Contributing Guide](CONTRIBUTING.md) - Guidelines for contributing to the project
- [Code Review Template](docs/code-review-template.md) - Template for code reviews
- [Docker Setup](docs/DOCKER.md)
- [Port Configuration](docs/PORT_CONFIGURATION.md)
- [LLM Interface Setup](docs/LLM_INTERFACE_SETUP.md)
- [Unit Tests](tests/README.md)
- [API Tests](api_tests/README.md)
- [Game Data](data/README.md)
- [Utility Scripts](scripts/README.md)
- [Configuration Files](config/README.md)

## Project Structure

The Last Centaur follows a structured organization:

- **src/**: Core source code
  - **core/**: Core game models and utilities
  - **engine/**: Game engine components
  - **api/**: FastAPI endpoints
- **tests/**: Unit tests for direct component testing
- **api_tests/**: Integration tests through the API
- **data/**: Game world data files (CSV and JSON)
- **docs/**: Project documentation
- **scripts/**: Utility scripts for development and operations
- **config/**: Configuration files for testing and development
- **frontend/**: Web interface components
- **docker/**: Docker-related configuration files
- **migrations/**: Database migration scripts

## Game Systems

The Last Centaur's engine includes several interacting systems:

1. **Movement System**: Navigate through the world using cardinal directions
2. **Combat System**: Engage in tactical combat with enemies
3. **Discovery System**: Uncover secrets and hidden paths
4. **Inventory System**: Collect, use, and manage items
5. **Quest System**: Receive and complete missions
6. **LLM Interface**: Communicate using natural language

## Development

For development work, it is recommended to use a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt -r requirements-dev.txt
```

Running the tests:

```bash
# Unit tests
python scripts/run_tests.sh

# API integration tests
python scripts/run_api_tests.py

# Game path tests
python scripts/run_game_tests.py --path warrior
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

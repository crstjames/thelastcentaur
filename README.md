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

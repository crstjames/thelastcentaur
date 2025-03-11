# The Last Centaur - Data Files

This directory contains data files used by The Last Centaur game engine.

## Map Data Files

The following CSV files define the game world:

### map_data.csv

Contains the basic tile information for each position in the game world, including:

- Position coordinates
- Terrain type
- Area designation
- Description

### map_areas.csv

Contains information about different areas in the game world, including:

- Area identifiers
- Area names
- Area descriptions
- Area-specific properties

### map_enemies.csv

Contains information about enemies placed throughout the game world, including:

- Enemy positions
- Enemy types
- Enemy stats
- Loot tables

### map_items.csv

Contains information about items placed throughout the game world, including:

- Item positions
- Item types
- Item properties
- Requirements for acquisition

### map_data.json

A JSON representation of the game world map, including:

- Area names
- Position coordinates
- Terrain types
- Descriptions
- Requirements for access
- Area flags and properties

## Usage

These data files are loaded by the game engine at startup to create the game world. They should not be modified directly unless you know what you're doing, as changes can affect game balance and progression.

If you need to add new content to the game, it's recommended to use the in-game tools or developer utilities rather than editing these files manually.

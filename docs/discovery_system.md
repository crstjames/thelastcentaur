# Discovery System for The Last Centaur

## Overview

The Discovery System enhances the immersive experience in "The Last Centaur" by allowing players to interact with the environment in natural, free-form ways. Rather than relying solely on predefined commands, players can describe what they want to do in natural language, and the system will interpret their intentions and respond accordingly.

This system enables:

1. **Natural Language Interactions**: Players can interact with the environment using descriptive language rather than rigid commands.
2. **Hidden Discoveries**: Special items and effects can be found by exploring the environment in creative ways.
3. **Environmental Changes**: Player actions can permanently alter the environment, with those changes persisting throughout the game.
4. **Roleplay Actions**: Players can express themselves through actions like dancing, singing, or any other creative behavior.

## Key Features

### Natural Language Processing

The system parses player input to identify the type of interaction they're attempting:

- **Examine**: "look at the tree", "inspect the ruins", "study the markings"
- **Touch**: "touch the crystal", "feel the bark", "run my hand along the wall"
- **Gather**: "pick up the berries", "collect some sand", "gather herbs"
- **Break**: "break the branch", "smash the rock", "crack open the shell"
- **Move**: "push the boulder", "lift the log", "turn over the stone"
- **Climb**: "climb the tree", "scale the cliff", "ascend the ruins"
- **Dig**: "dig in the sand", "excavate the soil", "burrow into the ground"
- **Listen**: "listen to the wind", "hear the sounds of the forest"
- **Smell**: "smell the flowers", "sniff the air"
- **Taste**: "taste the berries", "lick the crystal" (potentially risky!)

If none of these patterns match, the system treats the input as a roleplay action.

### Hidden Discoveries

Throughout the game world, there are hidden discoveries that can be found by interacting with the environment in specific ways. These discoveries:

- Are terrain-specific (forest, mountain, desert, ruins, etc.)
- May require specific weather conditions or time of day
- Need particular interaction types (examine, touch, gather, etc.)
- Often require specific keywords in the player's description
- Have varying chances of being found
- Can provide unique items or permanent stat bonuses

Examples include:

- Ancient runes carved into trees that boost mystic affinity
- Hidden berries that can be gathered for food
- Crystal fragments that appear in mountains during clear weather
- Magical desert sand that can only be gathered during magical storms
- Shadow essence that can be touched in the darkest shadows at night

### Environmental Changes

When players interact with the environment in ways that would logically change it, those changes are recorded and persist throughout the game. For example:

- Breaking branches or moving rocks will be visible when returning to an area
- Gathering resources will show that someone has harvested from that location
- Discovered hidden items will be marked as found

These changes enhance the feeling that the player's actions have a real impact on the game world.

### Roleplay Actions

The system recognizes common roleplay actions like dancing, singing, stretching, resting, or laughing, and provides appropriate responses. For any unrecognized actions, it generates a generic but thematic response that acknowledges the player's action.

This feature allows players to express themselves and immerse themselves more deeply in the role of the Last Centaur.

## Integration with Other Systems

The Discovery System integrates with:

1. **Inventory System**: Hidden items are added to the player's inventory when discovered.
2. **Path System**: Certain discoveries can increase affinity with specific paths (Warrior, Stealth, Mystic).
3. **Stats System**: Some rare discoveries can provide permanent stat bonuses.
4. **Weather System**: Weather conditions affect what can be discovered.
5. **Time System**: Time of day influences certain discoveries.

## Implementation Details

The Discovery System consists of several key components:

1. **DiscoverySystem**: The main class that manages interactions, discoveries, and environmental changes.
2. **InteractionType**: An enum defining the types of interactions players can perform.
3. **HiddenDiscovery**: A class representing items or effects that can be discovered.
4. **EnvironmentalChange**: A class representing changes to the environment.

The system is integrated with the CommandParser to interpret natural language commands and with the TileState model to display environmental changes in tile descriptions.

## Example Interactions

Here are some examples of how players might interact with the Discovery System:

```
> examine the ancient tree
As you examine the ancient tree more closely, you notice a strange symbol carved into its bark. It appears to be a rune of some kind, pulsing with a faint magical energy.
(You gained: increased mystic affinity)

> gather some berries from the bush
As you push aside some leaves, you discover a cluster of sweet berries hidden from view. They look delicious and nutritious.
(Added to inventory: forest_berries)

> touch the shadows in the corner
As you reach into the deepest shadow, your hand passes through something cold. You manage to capture a swirling dark essence that seems almost alive.
(Added to inventory: shadow_essence)

> dance around the campfire
You dance gracefully, your centaur form moving with surprising elegance. Your hooves create a rhythmic pattern on the ground.

> break off a branch from the tree
You break off a branch, but nothing interesting happens. The forest continues its gentle symphony of rustling leaves.
```

## Adding New Discoveries

The system is designed to be easily expandable. New discoveries can be added by creating new HiddenDiscovery instances in the `_initialize_discoveries` method of the DiscoverySystem class.

Each discovery requires:

- A unique ID
- Name and description
- Discovery text (what the player sees when they find it)
- Terrain types where it can be found
- Optional weather types and times of day
- Required interaction type and keywords
- Chance to find (0.0-1.0)
- Whether it's unique or can be found multiple times
- Optional item reward and special effects

## Conclusion

The Discovery System transforms "The Last Centaur" from a command-based game into a rich, immersive experience where players can interact with the world naturally and see the results of their actions persist over time. It encourages exploration, experimentation, and roleplay, making the game world feel more alive and responsive to player choices.

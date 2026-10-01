# The Last Centaur — engine design

> **Superseded:** the three-path design below is being replaced by the single-path design in [`GAME_DESIGN.md`](GAME_DESIGN.md).

`centaur/` is the new engine. It is plain Python with no dependencies. The old `src/` tree stays in place until this replaces it.

| File | Role |
|---|---|
| `content.py` | **Single source of truth** for landmarks, NPCs, items, enemies, biomes and what unlocks what. Says nothing about *where*. |
| `worldgen.py` | Seeded 10×10 world: places landmarks, generates a unique tile for every other square, proves all three paths are winnable. |
| `game.py` | The game loop. `Game.do("talk to the hermit")` returns text. All state is JSON-serializable. |
| `play.py` | Terminal runner with autosave (`~/.thelastcentaur/save.json`). |

```
venv/bin/python -m centaur.play                # play (add --new to start over)
venv/bin/python -m centaur.worldgen --seed 7   # print a world
venv/bin/python -m pytest centaur/tests        # content + generation tests
```

## The world

- Every game gets a new layout from a seed. Landmarks are scattered within placement rules (row bands, "near X"). The start is always on the south edge and the Shadow Domain is always on the north edge.
- Non-landmark tiles take the biome of the nearest landmark, so geography clusters naturally. Each one gets a unique name and description.
- Every tile has its own `memory` list, a log of what has happened there. The engine fills it in as you play, and it is saved with the world.
- Movement is 4-directional. Ordinary tiles are always open. A landmark can't be entered until you meet its `enter_requires`.

## Rules of play

- There's no class selection. You're on whichever path your gear says you're on, and you can mix paths.
- Talking to a mentor the first time gives you their item. Some items can only be taken once you hold another one (`take_requires`).
- **Combat is deliberately simple for now.** If you have an enemy's `defeat_requires`, you win and lose half its damage in health. If not, you lose its full damage and it stays. At 0 health you wake back in the Awakening Woods, and the place where you fell remembers it.
- Tiles record first visits, items taken or dropped, victories, falls and anything you `carve`. `look` shows the latest few entries.
- `rest` restores your health anywhere without enemies. The old map reveals the whole map on the `map` command.
- There's no day/night cycle yet, so `night_only` enemies stay hidden.

## The three paths (canonical)

| | Warrior | Mystic | Stealth |
|---|---|---|---|
| Mentor (gives) | Fallen Warrior → `warrior_map` | Hermit Druid → `ancient_scroll` | Shadow Scout → `shadow_key` |
| Step 2 | Ancient Ruins (needs map) → `ancient_sword` | Mystic Mountains: `crystal_focus` (findable only with scroll) | Twilight Glade (needs key) → `stealth_cloak` |
| Step 3 | Warriors' Armory (needs sword) → `war_horn` | Crystal Caves (needs focus) → `druid_staff` | Forgotten Grove (needs cloak) → `phantom_dagger` (only takeable while cloaked) |
| Path boss | Shadow Guardian in Enchanted Valley (needs horn to enter, sword to beat) → `guardian_essence` | Corrupted Druid in Crystal Outpost (needs staff) → `nature_key` | Phantom Assassin (needs cloak + dagger) |
| Domain key | `guardian_essence` | `nature_key` | `phantom_dagger` (cuts the wards) |
| Beat the Shadow Centaur with | sword + horn | focus + staff | cloak + dagger |

## Reconciled from the old code

The old repo described the world in three places that disagreed: `world_design.py`, `map_system.py`, and `warrior_path.py`/`mystic_path.py`/`stealth_path.py`. Decisions:

- **Kept** the world from `world_design.py` and `map_system.py` (areas, items, NPC lines, enemy stats), plus the lore text from `lore.py`, which never imported because of a syntax error. The historical events became readable lore items.
- **Dropped** the third version in the `*_path.py` files: Fallen Champion, Battle Plains, War Fortress, Corrupted Warlord, Corrupted Sage, Whispering Caverns, Void Sanctum, Shadow Hunter, Void Assassin, Champion's Shield, Battle Medallion and Whisper Dagger. These can be brought back as content later if wanted.
- **Fixed** a circular dependency on the stealth path. The Scout required the cloak before giving the key, but the cloak required the key.
- **Fixed** the Crystal Focus lying loose in the Druid's grove. It's now in the mountains and needs the scroll to find.
- **Fixed** the Shadow Domain requiring `guardian_essence` for every path, which forced everyone through the warrior boss. Each path now has its own key.
- **Renamed** `second_centaur` to `shadow_centaur`.
- **Not yet ported:** weather, time of day (only the `night_only` flag), hazards, hunger/resources, achievements/titles and the leaderboard.

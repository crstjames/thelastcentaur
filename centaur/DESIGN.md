# The Last Centaur — engine

`centaur/` is the new engine. It is plain Python with no dependencies. **What the game is** lives in [`GAME_DESIGN.md`](GAME_DESIGN.md); this file is about **how the code is laid out**. The old `src/` tree is untouched and will be deleted once the new engine covers it.

```
venv/bin/python -m centaur.play          # play (add --new to start over)
venv/bin/python -m centaur.worldgen      # print the map
venv/bin/python -m centaur.solver        # check content + fairness
venv/bin/python -m pytest centaur/tests
```

| File | Role |
|---|---|
| `content.py` | **All the story.** Landmarks (fixed positions), NPC lines, items, features, interactions, sequences, echoes, signals, hazards. Also `validate_content()`. |
| `biomes.py` | Vocabulary for generating ordinary tiles. |
| `worldgen.py` | Builds the 10×10 world: landmarks plus generated ordinary tiles (fixed seed). Seeds the echoes into tile memory. |
| `game.py` | The generic engine. `Game.do(text)` returns text. It evaluates `Condition`s and applies `Effects`, and knows nothing story-specific. |
| `solver.py` | Proves the content is **fair**: the goal can be reached by a player who only tries a clue-gated action after seeing one of its clues. |
| `play.py` | Terminal runner with autosave (`~/.thelastcentaur/save.json`). |

## How content works

- A **Condition** is items carried + flags set/unset + time of day. Almost everything has one: whether a feature is visible, whether a landmark can be entered, which line an NPC says, whether an interaction works.
- **Effects** are what happens: message, items given, flags set, clues seen, tile memory written, pride.
- A **Feature** is something examinable in a place. An **Interaction** is *verb + feature/item + place + condition → effects*, and it lists the **clues** that point to it. A **Sequence** is an ordered set of interactions (the crystal chord).
- An **Echo** is a past-self carving, already in a tile's memory. A **Signal** is a hot/cold cue by distance. A **Hazard** hurts you for spending a turn somewhere.
- Time: a day is 4 phases × 6 turns. Looking and examining are free; doing things takes a turn.

## Adding a puzzle

1. Add the features, interaction(s) and their effects to `content.py`.
2. Give every interaction that needs an item, and every sequence, the clues that point to it. Make sure something in the world shows those clues: an echo, a feature, an item's lore, an NPC line or a signal.
3. Run `python -m centaur.solver`. If the goal becomes unreachable, the puzzle isn't fair yet.
4. Extend the walkthrough in `tests/test_slice.py`.

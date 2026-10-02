# The Last Centaur — engine

`centaur/` is the whole game. The engine is plain Python with no dependencies; only the web UI and tests need packages. **What the game is** lives in [`GAME_DESIGN.md`](GAME_DESIGN.md); this file is about **how the code is laid out**.

```
venv/bin/python -m centaur.server        # play in the browser at http://localhost:8765
venv/bin/python -m centaur.play          # play in the terminal (add --new to start over)
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
| `server.py` + `web/index.html` | Browser UI: a small FastAPI wrapper plus one page with the pixel-art background, theme music and CRT look (assets in `web/assets/`). It shares the terminal's save file. Add `#play` to the URL to skip the title screen. |

## How content works

- A **Condition** is items carried + flags set/unset + time of day. Almost everything has one: whether a feature is visible, whether a landmark can be entered, which line an NPC says, whether an interaction works.
- **Effects** are what happens: message, items given, flags set, clues seen, tile memory written, pride.
- A **Feature** is something examinable in a place. An **Interaction** is *verb + feature/item + place + condition → effects*, and it lists the **clues** that point to it. A **Sequence** is an ordered set of interactions (the crystal chord).
- An **Echo** is a past-self carving, already in a tile's memory. A **Signal** is a hot/cold cue by distance. A **Hazard** hurts you for spending a turn somewhere.
- A **place** is a landmark id, a tile `(x, y)`, or `"near:<landmark>"` for any tile beside a landmark (e.g. blowing the horn at the valley mouth).
- A landmark can have `approach_from`: it can only be entered from a neighbour on those sides (the ruins, from the north).
- An enemy with `yields=True` doesn't die when beaten. It kneels, and interactions (`spare`, or `fight` again) decide what happens. `Effects.remove_enemies` takes it off the tile.
- An interaction's `words` add names for its target, and `bare=True` lets the verb alone match ("spare"). If its condition fails and it has no `otherwise` text, the command falls through to the normal verb.
- A hazard can be tied to an enemy, so it stops once that enemy is gone (the wolves).
- Time: a day is 4 phases × 6 turns. Looking and examining are free; doing things takes a turn.

## Adding a puzzle

1. Add the features, interaction(s) and their effects to `content.py`.
2. Give every interaction that needs an item, and every sequence, the clues that point to it. Make sure something in the world shows those clues: an echo, a feature, an item's lore, an NPC line or a signal.
3. Run `python -m centaur.solver`. If the goal becomes unreachable, the puzzle isn't fair yet.
4. Extend the walkthrough in `tests/test_slice.py`.

# The Last Centaur

A text adventure in the spirit of Myst. You wake on cold earth, stripped of your power, with no idea what is going on, and the only way forward is to look closely, notice things, and work it out.

There's no quest log and no one tells you what to do. The world remembers what happens in each place, and some of those memories were there before you arrived.

**Status:** the Prologue, Act I (Insight) and Act II (Valor) are playable. See [`centaur/GAME_DESIGN.md`](centaur/GAME_DESIGN.md) for the full design. (It contains spoilers.)

## Play

Requires Python 3.9+.

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

python -m centaur.server     # in the browser: http://localhost:8765
python -m centaur.play       # or in the terminal
```

Both use the same save file (`~/.thelastcentaur/save.json`), so you can switch between them mid-game. Use **New game** in the browser, or `python -m centaur.play --new`, to start over.

## Develop

```bash
pytest                          # engine, fairness and web tests
python -m centaur.solver        # check the content is consistent and every puzzle is fair
python -m centaur.worldgen      # print the map (spoilers)
```

| | |
|---|---|
| `centaur/content.py` | All the story: places, characters, items, puzzles, clues |
| `centaur/game.py` | The engine. Generic: it evaluates conditions and applies effects |
| `centaur/solver.py` | Proves every puzzle can be solved from clues the player can actually find |
| `centaur/worldgen.py` | Builds the fixed 10×10 world |
| `centaur/server.py`, `centaur/web/` | Browser UI |
| `centaur/play.py` | Terminal UI |

See [`centaur/DESIGN.md`](centaur/DESIGN.md) for how the engine works and how to add a puzzle.

## License

MIT

"""
Vercel entry point. Vercel serves the FastAPI `app` from here, and
vercel.json sends every path to it.

Hosted like this, the server keeps no save file: each browser keeps its own
game. See centaur/server.py.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from centaur.server import app  # noqa: E402,F401

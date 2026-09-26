"""Runtime state and local paths.

Estado en memoria y rutas locales.
"""

import json
import threading
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "office-data.json"
AGENTS = ROOT / "agents"
AGENTS.mkdir(exist_ok=True)
LOCK = threading.RLock()
STATE = {
    "base_url": "http://localhost:1337/v1",
    "model": "",
    "model_timeout": 600,
    "stream": False,
    "temperature": None,
    "agents": [
        {
            "id": "planner",
            "name": "Planner",
            "role": "Break the task into a practical plan.",
            "skill": "",
            "x": 0,
            "y": 0,
            "color": "#8b9eff",
        },
        {
            "id": "builder",
            "name": "Builder",
            "role": "Produce the requested answer or artifact as text.",
            "skill": "",
            "x": 0,
            "y": 0,
            "color": "#f4b76a",
        },
        {
            "id": "reviewer",
            "name": "Reviewer",
            "role": "Check the result for errors and improve it.",
            "skill": "",
            "x": 0,
            "y": 0,
            "color": "#76d4ab",
        },
    ],
    "runs": [],
}
if DATA.exists():
    try:
        stored = json.loads(DATA.read_text())
        for key in (
            "base_url",
            "model",
            "model_timeout",
            "stream",
            "temperature",
        ):
            if key in stored:
                STATE[key] = stored[key]
    except (ValueError, OSError):
        pass

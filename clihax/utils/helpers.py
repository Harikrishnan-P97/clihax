# utils/helpers.py

import json
from pathlib import Path
from datetime import datetime

DATA_FILE = Path("data/tools.json")
META_FILE = Path("data/meta.json")

def load_tools():
    if not DATA_FILE.exists():
        return []
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_tools(tools):
    with open(DATA_FILE, "w") as f:
        json.dump(tools, f, indent=2)
    update_meta("last_edit")

def load_meta():
    if META_FILE.exists():
        with open(META_FILE, "r") as f:
            return json.load(f)
    return {}

def update_meta(action):
    meta = load_meta()
    timestamp = datetime.now().isoformat(timespec='seconds')
    if action == "import":
        meta["last_import"] = timestamp
    elif action == "export":
        meta["last_export"] = timestamp
    elif action == "last_edit":
        meta["last_edit"] = timestamp
    with open(META_FILE, "w") as f:
        json.dump(meta, f, indent=2)

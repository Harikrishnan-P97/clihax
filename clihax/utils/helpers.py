# utils/helpers.py
"""Storage helpers for CliHax.

All runtime data (tools database, metadata, drop logs, backups) lives in a
per-user data directory instead of the current working directory:

    Linux:   ~/.local/share/clihax
    macOS:   ~/Library/Application Support/clihax
    Windows: C:\\Users\\<you>\\AppData\\Local\\clihax

Set the ``CLIHAX_HOME`` environment variable to use a different location
(handy for tests or for keeping the database in a synced folder).
"""

import json
import os
import shutil
import tempfile
from datetime import datetime
from pathlib import Path

from platformdirs import user_data_dir

APP_NAME = "clihax"
ENV_HOME = "CLIHAX_HOME"


# ========= Paths ========= #
# Resolved on every call (not at import time) so CLIHAX_HOME can change at runtime.

def get_data_dir() -> Path:
    """Return the data directory, creating it if needed."""
    override = os.environ.get(ENV_HOME)
    path = Path(override).expanduser() if override else Path(user_data_dir(APP_NAME))
    path.mkdir(parents=True, exist_ok=True)
    return path


def tools_file() -> Path:
    return get_data_dir() / "tools.json"


def meta_file() -> Path:
    return get_data_dir() / "meta.json"


def backups_dir() -> Path:
    path = get_data_dir() / "backups"
    path.mkdir(parents=True, exist_ok=True)
    return path


def logs_dir() -> Path:
    path = get_data_dir() / "logs"
    path.mkdir(parents=True, exist_ok=True)
    return path


def drops_log_file() -> Path:
    return logs_dir() / "drops.json"


# ========= JSON I/O ========= #

def _write_json_atomic(path: Path, data) -> None:
    """Write JSON to a temp file, then rename, so a crash can't corrupt the DB."""
    fd, tmp_name = tempfile.mkstemp(dir=path.parent, prefix=path.name + ".", suffix=".tmp")
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(data, f, indent=2)
        os.replace(tmp_name, path)
    except BaseException:
        if os.path.exists(tmp_name):
            os.unlink(tmp_name)
        raise


# ========= Tools database ========= #

def load_tools():
    path = tools_file()
    if not path.exists():
        return []
    with open(path, "r") as f:
        return json.load(f)


def save_tools(tools):
    _write_json_atomic(tools_file(), tools)
    update_meta("last_edit")


# ========= Metadata ========= #

def load_meta():
    path = meta_file()
    if path.exists():
        with open(path, "r") as f:
            return json.load(f)
    return {}


def update_meta(action):
    meta = load_meta()
    timestamp = datetime.now().isoformat(timespec="seconds")
    if action == "import":
        meta["last_import"] = timestamp
    elif action == "export":
        meta["last_export"] = timestamp
    elif action == "last_edit":
        meta["last_edit"] = timestamp
    _write_json_atomic(meta_file(), meta)


# ========= Legacy migration ========= #

def migrate_legacy_data(legacy_root=None):
    """Copy data from the old ./data, ./logs, ./backups layout (v1.0) once.

    Only runs when the new database does not exist yet, and never overwrites
    anything. Returns a list of migrated paths (empty if nothing happened).
    """
    root = Path(legacy_root) if legacy_root else Path.cwd()
    old_tools = root / "data" / "tools.json"
    if not old_tools.exists() or tools_file().exists():
        return []

    # Nothing worth migrating if the old database is empty or unreadable.
    try:
        with open(old_tools, "r") as f:
            old_data = json.load(f)
    except (OSError, ValueError):
        return []
    if not old_data:
        return []

    migrated = []
    copies = [
        (old_tools, tools_file()),
        (root / "data" / "meta.json", meta_file()),
        (root / "logs" / "drops.json", drops_log_file()),
    ]
    old_backups = root / "backups"
    if old_backups.is_dir():
        copies += [(p, backups_dir() / p.name) for p in old_backups.glob("*.json")]

    for src, dst in copies:
        if src.exists() and not dst.exists():
            shutil.copy2(src, dst)
            migrated.append(dst)
    return migrated

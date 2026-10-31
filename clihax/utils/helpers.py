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
from typing import Any

import click
from platformdirs import user_data_dir

APP_NAME = "clihax"
ENV_HOME = "CLIHAX_HOME"

# A tool entry as stored in tools.json.
ToolDict = dict[str, Any]


class StorageError(click.ClickException):
    """The tools database could not be read (shown as a one-line error, no traceback)."""


def now_iso() -> str:
    """Current local time as an ISO-8601 string with second precision."""
    return datetime.now().isoformat(timespec="seconds")


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
    try:
        with open(path) as f:
            tools = json.load(f)
        if not isinstance(tools, list):
            raise ValueError("expected a JSON list of tools")
    except (OSError, ValueError) as exc:
        raise StorageError(
            f"Could not read {path}: {exc}\n"
            f"Fix or delete that file, or restore a backup from {backups_dir()}."
        ) from exc
    return tools


def save_tools(tools):
    _write_json_atomic(tools_file(), tools)
    update_meta("last_edit")


# ========= Drop log and backups ========= #

def load_drop_log() -> list:
    """Return the recorded drop events (empty list if there are none yet)."""
    path = drops_log_file()
    if not path.exists():
        return []
    with open(path) as f:
        return json.load(f)


def save_drop_log(entries: list) -> None:
    _write_json_atomic(drops_log_file(), entries)


def write_backup(tools: list) -> Path:
    """Save a timestamped copy of the tools database and return its path."""
    timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
    path = backups_dir() / f"tools_backup_{timestamp}.json"
    _write_json_atomic(path, tools)
    return path


# ========= Metadata ========= #

def load_meta():
    """Return the metadata (timestamps). Unreadable metadata is treated as empty."""
    path = meta_file()
    if not path.exists():
        return {}
    try:
        with open(path) as f:
            meta = json.load(f)
    except (OSError, ValueError):
        return {}
    return meta if isinstance(meta, dict) else {}


def update_meta(action):
    meta = load_meta()
    timestamp = now_iso()
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
        with open(old_tools) as f:
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


# ========= Validation ========= #

def tool_key(tool: ToolDict) -> tuple:
    """Identity of a tool entry: two entries with the same key are duplicates."""
    return (tool.get("tool"), tool.get("command"))


def normalize_tool(entry):
    """Return a well-formed tool dict, or None if the entry is unusable.

    A usable entry is a dict with a non-empty ``tool`` and ``command``.
    Missing optional fields get sensible defaults so other commands never
    hit a KeyError.
    """
    if not isinstance(entry, dict):
        return None
    tool = str(entry.get("tool", "")).strip()
    command = str(entry.get("command", "")).strip()
    if not tool or not command:
        return None

    tags = entry.get("tags", [])
    if isinstance(tags, str):
        tags = [t.strip() for t in tags.split(",") if t.strip()]
    elif isinstance(tags, list):
        tags = [str(t).strip() for t in tags if str(t).strip()]
    else:
        tags = []

    now = now_iso()
    created = entry.get("created_at") or now
    return {
        "tool": tool,
        "command": command,
        "description": str(entry.get("description", "")),
        "tags": tags,
        "category": str(entry.get("category", "")),
        "created_at": created,
        "updated_at": entry.get("updated_at") or created,
    }


# ========= Read-only storage summary (never creates folders) ========= #

def count_backups() -> int:
    """Number of saved backups (0 if the folder does not exist yet)."""
    folder = get_data_dir() / "backups"
    return len(list(folder.glob("tools_backup_*.json"))) if folder.is_dir() else 0


def count_drop_events() -> int:
    """Number of logged drop events (0 if there is no usable log)."""
    path = get_data_dir() / "logs" / "drops.json"
    if not path.is_file():
        return 0
    try:
        with open(path) as f:
            events = json.load(f)
    except (OSError, ValueError):
        return 0
    return len(events) if isinstance(events, list) else 0

"""Tests for storage helpers added alongside the module split."""

import json
import re

import pytest

from clihax import ui
from clihax.utils import helpers


@pytest.fixture
def home(tmp_path, monkeypatch):
    monkeypatch.setenv("CLIHAX_HOME", str(tmp_path / "home"))
    return tmp_path / "home"


def test_now_iso_format():
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}", helpers.now_iso())


def test_tool_key_identifies_duplicates():
    a = {"tool": "nmap", "command": "nmap -sV", "tags": ["x"]}
    b = {"tool": "nmap", "command": "nmap -sV", "tags": ["y"]}
    c = {"tool": "nmap", "command": "nmap -A"}
    assert helpers.tool_key(a) == helpers.tool_key(b)
    assert helpers.tool_key(a) != helpers.tool_key(c)


def test_drop_log_starts_empty_and_roundtrips(home):
    assert helpers.load_drop_log() == []
    helpers.save_drop_log([{"total_dropped": 2}])
    assert helpers.load_drop_log() == [{"total_dropped": 2}]


def test_write_backup_saves_a_copy(home):
    tools = [{"tool": "a", "command": "b"}]
    path = helpers.write_backup(tools)
    assert path.parent == helpers.backups_dir()
    assert path.name.startswith("tools_backup_") and path.suffix == ".json"
    assert json.loads(path.read_text()) == tools
    assert not list(helpers.backups_dir().glob("*.tmp"))


# ---------- ui helpers ----------

def test_format_tags_handles_bad_values():
    assert ui.format_tags({"tags": ["a", "b"]}) == "a, b"
    assert ui.format_tags({"tags": "nope"}) == ""
    assert ui.format_tags({}) == ""


def test_cell_never_parses_markup():
    assert ui.cell("[port] [/x]").plain == "[port] [/x]"


def test_quick_line_format():
    tool = {"tool": "nmap", "command": "nmap -sV", "category": "recon", "tags": ["a", "b"]}
    assert ui.quick_line(3, tool) == "[3] nmap: nmap -sV (recon)  # a, b"


def test_highlight_is_case_insensitive_and_skips_empty_terms():
    text = ui.highlight(ui.cell("NMap scan"), ["nmap", ""])
    assert [text.plain[s.start:s.end] for s in text.spans] == ["NMap"]


# ---------- unreadable files ----------

def test_corrupt_tools_file_raises_friendly_error(home):
    helpers.tools_file().write_text("{broken")
    with pytest.raises(helpers.StorageError) as exc:
        helpers.load_tools()
    assert "tools.json" in exc.value.format_message()


def test_tools_file_with_wrong_shape_is_rejected(home):
    helpers.tools_file().write_text('{"tool": "nmap"}')
    with pytest.raises(helpers.StorageError):
        helpers.load_tools()


def test_corrupt_meta_is_treated_as_empty(home):
    helpers.meta_file().write_text("{broken")
    assert helpers.load_meta() == {}
    helpers.save_tools([])  # must still be able to save
    assert "last_edit" in helpers.load_meta()

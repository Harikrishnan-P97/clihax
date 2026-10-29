import json

import pytest

from clihax.utils import helpers


@pytest.fixture
def home(tmp_path, monkeypatch):
    monkeypatch.setenv("CLIHAX_HOME", str(tmp_path / "home"))
    return tmp_path / "home"


def test_data_dir_honours_env_override(home):
    assert helpers.get_data_dir() == home
    assert home.is_dir()


def test_load_tools_empty_when_no_database(home):
    assert helpers.load_tools() == []


def test_save_and_load_roundtrip(home):
    tools = [{"tool": "nmap", "command": "nmap -sV <target>", "tags": ["scan"]}]
    helpers.save_tools(tools)
    assert helpers.load_tools() == tools
    assert (home / "tools.json").exists()


def test_save_records_last_edit(home):
    helpers.save_tools([])
    assert "last_edit" in helpers.load_meta()


def test_update_meta_import_and_export(home):
    helpers.update_meta("import")
    helpers.update_meta("export")
    meta = helpers.load_meta()
    assert "last_import" in meta and "last_export" in meta


def test_atomic_write_leaves_no_temp_files(home):
    helpers.save_tools([{"tool": "a", "command": "b"}])
    assert not list(home.glob("*.tmp"))


def test_backups_and_logs_live_in_data_dir(home):
    assert helpers.backups_dir() == home / "backups"
    assert helpers.drops_log_file() == home / "logs" / "drops.json"
    assert helpers.backups_dir().is_dir()
    assert helpers.logs_dir().is_dir()


def _make_legacy(root, tools):
    (root / "data").mkdir(parents=True)
    (root / "logs").mkdir()
    (root / "backups").mkdir()
    (root / "data" / "tools.json").write_text(json.dumps(tools))
    (root / "data" / "meta.json").write_text(json.dumps({"last_edit": "2025-01-01T00:00:00"}))
    (root / "logs" / "drops.json").write_text("[]")
    (root / "backups" / "tools_backup_x.json").write_text("[]")


def test_migrates_legacy_layout_once(home, tmp_path):
    legacy = tmp_path / "old"
    _make_legacy(legacy, [{"tool": "nmap", "command": "nmap"}])

    migrated = helpers.migrate_legacy_data(legacy)

    assert len(migrated) == 4
    assert helpers.load_tools() == [{"tool": "nmap", "command": "nmap"}]
    assert (home / "backups" / "tools_backup_x.json").exists()
    # second run is a no-op
    assert helpers.migrate_legacy_data(legacy) == []


def test_migration_never_overwrites_existing_database(home, tmp_path):
    legacy = tmp_path / "old"
    _make_legacy(legacy, [{"tool": "old", "command": "old"}])
    helpers.save_tools([{"tool": "new", "command": "new"}])

    assert helpers.migrate_legacy_data(legacy) == []
    assert helpers.load_tools() == [{"tool": "new", "command": "new"}]


def test_migration_skips_empty_legacy_database(home, tmp_path):
    legacy = tmp_path / "old"
    _make_legacy(legacy, [])
    assert helpers.migrate_legacy_data(legacy) == []
    assert not (home / "tools.json").exists()


def test_migration_noop_without_legacy_files(home, tmp_path):
    assert helpers.migrate_legacy_data(tmp_path / "nothing") == []

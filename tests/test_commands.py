"""Behaviour tests for every CLI command, written against the public CLI only."""

import json

from clihax.cli import cli
from clihax.utils import helpers

from .conftest import SAMPLE_TOOLS, make_tool, plain

ALL_COMMANDS = [
    "add", "delete", "drop", "edit", "export", "import",
    "info", "list", "logs", "search", "searchfilter", "show", "starter", "completion",
]


def run(runner, *args, input=None):
    result = runner.invoke(cli, list(args), input=input)
    return result, plain(result.output)


# ---------- top level ----------

def test_no_arguments_prints_help(runner):
    result, out = run(runner)
    assert result.exit_code == 0
    assert "Commands:" in out


def test_help_lists_every_command(runner):
    _, out = run(runner, "--help")
    for name in ALL_COMMANDS:
        assert name in out


def test_legacy_data_is_migrated_on_first_run(runner, tmp_path):
    (tmp_path / "data").mkdir()
    (tmp_path / "data" / "tools.json").write_text(json.dumps([SAMPLE_TOOLS[0]]))

    _, out = run(runner, "info", "--quick")

    assert "Migrated" in out
    assert len(helpers.load_tools()) == 1


# ---------- list ----------

def test_list_empty_database(runner):
    result, out = run(runner, "list")
    assert result.exit_code == 0
    assert "No tools found" in out


def test_list_table_shows_every_tool(seeded):
    _, out = run(seeded, "list")
    for entry in SAMPLE_TOOLS:
        assert entry["tool"] in out


def test_list_all_table_has_full_details(seeded):
    _, out = run(seeded, "list", "--all")
    # The table is wide, so cell text may wrap; check headings and short values.
    assert "Full Tool List" in out
    assert "Index" in out and "Updated" in out
    assert "recon" in out


def test_list_quick_all_prints_detail_blocks(seeded):
    _, out = run(seeded, "list", "--quick", "--all")
    assert "Command    : nmap -sV" in out
    assert "Created At : 2025-01-01T00:00:00" in out


# ---------- show ----------

def test_show_displays_details(seeded):
    _, out = run(seeded, "show", "2")
    assert "Details for Tool [2]: hydra" in out
    assert "password brute force" in out
    assert "brute-force, ftp" in out


def test_show_invalid_index(seeded):
    _, out = run(seeded, "show", "9")
    assert "Invalid index" in out


# ---------- delete ----------

def test_delete_removes_the_right_tool(seeded):
    _, out = run(seeded, "delete", "2")
    assert "Deleted" in out
    assert [t["tool"] for t in helpers.load_tools()] == ["nmap", "msfvenom"]


def test_delete_invalid_index_changes_nothing(seeded):
    for bad in ("0", "4"):
        _, out = run(seeded, "delete", bad)
        assert "Invalid index" in out
    assert len(helpers.load_tools()) == 3


# ---------- edit ----------

def test_edit_with_blank_answers_keeps_values(seeded):
    result, _ = run(seeded, "edit", "1", input="\n\n\n\n\n")
    assert result.exit_code == 0
    saved = helpers.load_tools()[0]
    assert saved["tool"] == "nmap"
    assert saved["command"] == "nmap -sV"
    assert saved["tags"] == ["scan", "nmap"]
    assert saved["created_at"] == "2025-01-01T00:00:00"
    assert saved["updated_at"] != "2025-01-01T00:00:00"


def test_edit_changes_fields(seeded):
    run(seeded, "edit", "1", input="nmap2\nnmap -A\nnew desc\nx, y\nscan\n")
    saved = helpers.load_tools()[0]
    assert saved["tool"] == "nmap2"
    assert saved["command"] == "nmap -A"
    assert saved["description"] == "new desc"
    assert saved["tags"] == ["x", "y"]
    assert saved["category"] == "scan"


def test_edit_invalid_index(seeded):
    _, out = run(seeded, "edit", "9")
    assert "Invalid index" in out


# ---------- search ----------

def test_search_matches_tag_and_hides_others(seeded):
    _, out = run(seeded, "search", "ftp")
    assert "hydra" in out
    assert "msfvenom" not in out


def test_search_multiple_keywords_is_or(seeded):
    _, out = run(seeded, "search", "ftp,payload")
    assert "hydra" in out and "msfvenom" in out and "nmap" not in out


def test_search_is_case_insensitive(seeded):
    _, out = run(seeded, "search", "NMAP")
    assert "nmap" in out


def test_search_no_match(seeded):
    _, out = run(seeded, "search", "zzz")
    assert "No matches found" in out


def test_search_only_separators_matches_nothing(seeded):
    _, out = run(seeded, "search", ",")
    assert "No matches found" in out


def test_search_quick_prints_numbered_lines(seeded):
    _, out = run(seeded, "search", "ftp", "--quick")
    assert "[1]" in out and "hydra" in out


def test_search_copy_uses_displayed_index(seeded, clipboard):
    _, out = run(seeded, "search", "ftp,payload", "--copy", "2")
    assert clipboard == ["msfvenom -p x"]
    assert "Copied" in out


def test_search_copy_invalid_index(seeded, clipboard):
    _, out = run(seeded, "search", "ftp", "--copy", "5")
    assert "Invalid index" in out
    assert clipboard == []


# ---------- searchfilter ----------

def test_filter_by_tag(seeded):
    _, out = run(seeded, "searchfilter", "-t", "brute-force")
    assert "hydra" in out and "nmap" not in out


def test_filter_by_category(seeded):
    _, out = run(seeded, "searchfilter", "-c", "post")
    assert "msfvenom" in out and "hydra" not in out


def test_filter_combines_category_tag_and_keyword(seeded):
    _, out = run(seeded, "searchfilter", "-c", "attack", "-t", "brute-force", "ftp")
    assert "hydra" in out


def test_filter_conflicting_options_match_nothing(seeded):
    _, out = run(seeded, "searchfilter", "-c", "recon", "-t", "brute-force")
    assert "No matches found" in out


def test_filter_without_options_lists_everything(seeded):
    _, out = run(seeded, "searchfilter")
    for entry in SAMPLE_TOOLS:
        assert entry["tool"] in out


def test_filter_quick(seeded):
    _, out = run(seeded, "searchfilter", "-c", "recon", "-q")
    assert "[1]" in out


def test_filter_copy(seeded, clipboard):
    run(seeded, "searchfilter", "-c", "post", "--copy", "1")
    assert clipboard == ["msfvenom -p x"]


def test_filter_copy_invalid_index(seeded, clipboard):
    _, out = run(seeded, "searchfilter", "-c", "post", "--copy", "3")
    assert "Invalid index" in out
    assert clipboard == []


# ---------- info ----------
# (the full layout is covered in test_info.py)

def test_info_quick(seeded):
    _, out = run(seeded, "info", "--quick")
    assert "Total tools   : 3" in out
    assert "Data dir" in out


def test_info_full_runs(seeded):
    result, out = run(seeded, "info")
    assert result.exit_code == 0
    assert "Toolbox" in out


# ---------- export ----------

def test_export_writes_json(seeded, tmp_path):
    target = tmp_path / "out.json"
    _, out = run(seeded, "export", str(target))
    assert "Exported 3 of 3" in out
    assert [t["tool"] for t in json.loads(target.read_text())] == ["nmap", "hydra", "msfvenom"]
    assert "last_export" in helpers.load_meta()


def test_export_skips_duplicates(runner, tmp_path):
    entry = make_tool("a", "b")
    helpers.save_tools([entry, dict(entry), make_tool("c", "d")])
    target = tmp_path / "out.json"
    _, out = run(runner, "export", str(target))
    assert "Exported 2 of 3" in out
    assert "Skipped 1" in out


def test_export_empty_database(runner, tmp_path):
    target = tmp_path / "out.json"
    _, out = run(runner, "export", str(target))
    assert "No tools to export" in out
    assert not target.exists()


def test_export_default_filename(seeded, tmp_path):
    run(seeded, "export")
    assert (tmp_path / "exported_tools.json").exists()


# ---------- import (error paths) ----------

def test_import_missing_file(runner):
    _, out = run(runner, "import", "nope.json")
    assert "File not found" in out


def test_import_bad_json(runner, tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text("{not json")
    _, out = run(runner, "import", str(bad))
    assert "Failed to read or parse JSON" in out


# ---------- drop ----------

def test_drop_empty_database(runner):
    _, out = run(runner, "drop")
    assert "No tools to drop" in out


def test_drop_with_backup(seeded):
    _, out = run(seeded, "drop", input="y\ny\n")
    assert helpers.load_tools() == []
    backups = list(helpers.backups_dir().glob("tools_backup_*.json"))
    assert len(backups) == 1
    assert len(json.loads(backups[0].read_text())) == 3
    entry = json.loads(helpers.drops_log_file().read_text())[-1]
    assert entry["total_dropped"] == 3
    assert entry["forced"] is False
    assert entry["backup_created"] is True
    assert "dropped" in out.lower()


def test_drop_without_backup(seeded):
    run(seeded, "drop", input="y\nn\n")
    assert helpers.load_tools() == []
    assert not list(helpers.backups_dir().glob("*.json"))
    assert json.loads(helpers.drops_log_file().read_text())[-1]["backup_created"] == "skipped"


def test_drop_can_be_cancelled(seeded):
    _, out = run(seeded, "drop", input="n\n")
    assert len(helpers.load_tools()) == 3
    assert "cancelled" in out.lower()
    assert not helpers.drops_log_file().exists()


# ---------- logs ----------

def test_logs_none_yet(runner):
    _, out = run(runner, "logs")
    assert "No drop logs found" in out


def test_logs_shows_history(seeded):
    run(seeded, "drop", "--force")
    _, out = run(seeded, "logs")
    assert "Drop History Log" in out
    assert "3 tools" in out


def test_logs_clear(seeded):
    run(seeded, "drop", "--force")
    _, out = run(seeded, "logs", "--clear")
    assert "cleared" in out
    assert json.loads(helpers.drops_log_file().read_text()) == []


def test_logs_clear_without_file(runner):
    _, out = run(runner, "logs", "--clear")
    assert "No log file found" in out


def test_logs_handles_corrupt_file(runner):
    helpers.drops_log_file().write_text("{broken")
    _, out = run(runner, "logs")
    assert "Error reading log file" in out


# ---------- behaviour added with the module split ----------

def test_filter_ignores_trailing_comma_in_keywords(seeded):
    _, out = run(seeded, "searchfilter", "ftp,")
    assert "hydra" in out
    assert "nmap" not in out and "msfvenom" not in out


def test_drop_backup_prompt_defaults_to_yes(seeded):
    run(seeded, "drop", input="y\n\n")
    assert len(list(helpers.backups_dir().glob("tools_backup_*.json"))) == 1


def test_drop_aborts_when_backup_fails_and_user_declines(seeded, monkeypatch):
    def broken_backup(_tools):
        raise OSError("disk full")

    monkeypatch.setattr("clihax.commands.data.write_backup", broken_backup)

    _, out = run(seeded, "drop", input="y\ny\nn\n")

    assert "Backup failed" in out
    assert "cancelled" in out.lower()
    assert len(helpers.load_tools()) == 3
    assert not helpers.drops_log_file().exists()


def test_drop_continues_without_backup_only_if_user_insists(seeded, monkeypatch):
    def broken_backup(_tools):
        raise OSError("disk full")

    monkeypatch.setattr("clihax.commands.data.write_backup", broken_backup)

    run(seeded, "drop", input="y\ny\ny\n")

    assert helpers.load_tools() == []
    assert json.loads(helpers.drops_log_file().read_text())[-1]["backup_created"] is False


def test_python_dash_m_entry_point(runner, monkeypatch, capsys):
    import runpy

    import pytest

    monkeypatch.setattr("sys.argv", ["clihax", "--version"])
    with pytest.raises(SystemExit) as exc:
        runpy.run_module("clihax", run_name="__main__")
    assert exc.value.code == 0
    assert "CliHax v" in capsys.readouterr().out


def test_corrupt_database_shows_one_line_error_not_traceback(runner):
    helpers.tools_file().write_text("{broken")
    result = runner.invoke(cli, ["list"])
    assert result.exit_code == 1
    assert "Could not read" in plain(result.output)
    assert "Traceback" not in plain(result.output)

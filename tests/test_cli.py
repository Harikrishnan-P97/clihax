import json

import pyperclip
import pytest
from click.testing import CliRunner

import clihax
from clihax import ui
from clihax.cli import cli
from clihax.utils import helpers

NMAP = {
    "tool": "nmap",
    "command": "nmap -sV <target>",
    "description": "scan service versions",
    "tags": ["scan", "nmap"],
    "category": "recon",
    "created_at": "2025-01-01T00:00:00",
    "updated_at": "2025-01-01T00:00:00",
}


@pytest.fixture
def runner(tmp_path, monkeypatch):
    monkeypatch.setenv("CLIHAX_HOME", str(tmp_path / "home"))
    # run from an empty folder so legacy migration never triggers
    monkeypatch.chdir(tmp_path)
    return CliRunner()


def test_list_prints_table_directly(runner):
    helpers.save_tools([NMAP])
    result = runner.invoke(cli, ["list"])
    assert result.exit_code == 0
    assert "nmap" in result.output


def test_list_quick(runner):
    helpers.save_tools([NMAP])
    result = runner.invoke(cli, ["list", "--quick"])
    assert result.exit_code == 0
    assert "[1] nmap: nmap -sV <target> (recon)" in result.output


def test_add_stores_tool_with_tags(runner):
    result = runner.invoke(
        cli, ["add"], input="nmap\nnmap -sV <target>\nscan versions\nrecon\nscan, nmap\n"
    )
    assert result.exit_code == 0
    saved = helpers.load_tools()
    assert len(saved) == 1
    assert saved[0]["tags"] == ["scan", "nmap"]


def test_add_with_blank_tags_stores_empty_list(runner):
    result = runner.invoke(cli, ["add"], input="nmap\nnmap -sV\ndesc\nrecon\n\n")
    assert result.exit_code == 0
    assert helpers.load_tools()[0]["tags"] == []


@pytest.mark.parametrize("flag", ["--copy", "-C"])
def test_show_copy_copies_and_still_displays(runner, monkeypatch, flag):
    helpers.save_tools([NMAP])
    copied = []
    monkeypatch.setattr(ui, "copy_to_clipboard", lambda text: copied.append(text) or True)

    result = runner.invoke(cli, ["show", "1", flag])

    assert result.exit_code == 0
    assert copied == ["nmap -sV <target>"]
    assert "nmap" in result.output
    assert "Copied" in result.output


def test_clipboard_failure_shows_message_not_traceback(runner, monkeypatch):
    helpers.save_tools([NMAP])

    def broken_copy(_text):
        raise pyperclip.PyperclipException("no clipboard")

    monkeypatch.setattr(pyperclip, "copy", broken_copy)

    result = runner.invoke(cli, ["show", "1", "-C"])

    assert result.exit_code == 0
    assert "Clipboard unavailable" in result.output


def test_import_skips_invalid_entries(runner, tmp_path):
    source = tmp_path / "in.json"
    source.write_text(json.dumps([NMAP, {"tool": "x"}, "junk", {"command": "y"}]))

    result = runner.invoke(cli, ["import", str(source)])

    assert result.exit_code == 0
    assert len(helpers.load_tools()) == 1
    assert "Skipped 3 invalid entries" in result.output


def test_import_fills_missing_fields(runner, tmp_path):
    source = tmp_path / "in.json"
    source.write_text(json.dumps([{"tool": "ls", "command": "ls -la"}]))

    runner.invoke(cli, ["import", str(source)])

    saved = helpers.load_tools()[0]
    assert saved["description"] == ""
    assert saved["tags"] == []
    assert saved["created_at"]


def test_import_twice_skips_duplicates(runner, tmp_path):
    source = tmp_path / "in.json"
    source.write_text(json.dumps([NMAP]))

    runner.invoke(cli, ["import", str(source)])
    second = runner.invoke(cli, ["import", str(source)])

    assert len(helpers.load_tools()) == 1
    assert "No new tools to import" in second.output


def test_import_rejects_non_list_json(runner, tmp_path):
    source = tmp_path / "in.json"
    source.write_text(json.dumps({"tool": "nmap"}))

    result = runner.invoke(cli, ["import", str(source)])

    assert result.exit_code == 0
    assert helpers.load_tools() == []
    assert "Failed to read or parse JSON" in result.output


def test_drop_force_empties_database_and_logs_event(runner):
    helpers.save_tools([NMAP])

    result = runner.invoke(cli, ["drop", "--force"])

    assert result.exit_code == 0
    assert helpers.load_tools() == []
    log = json.loads(helpers.drops_log_file().read_text())
    assert log[-1]["total_dropped"] == 1
    assert log[-1]["forced"] is True


def test_version_and_info_report_the_same_version(runner):
    version_out = runner.invoke(cli, ["--version"]).output
    info_out = runner.invoke(cli, ["info", "--quick"]).output
    assert clihax.__version__ in version_out
    assert clihax.__version__ in info_out

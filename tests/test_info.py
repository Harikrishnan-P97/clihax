"""Tests for the `clihax info` page."""

from pathlib import Path

import pytest

import clihax
from clihax.cli import cli
from clihax.utils import helpers

from .conftest import plain


def info(runner, *args):
    result = runner.invoke(cli, ["info", *args])
    return result, plain(result.output)


def test_full_info_has_banner_and_three_sections(seeded):
    result, out = info(seeded)
    assert result.exit_code == 0
    assert "\u2588\u2588" in out  # the banner is kept
    for heading in ("About", "Toolbox", "Activity"):
        assert heading in out


def test_full_info_shows_author_repo_and_license(seeded):
    _, out = info(seeded)
    assert "Harikrishnan-P97" in out
    assert "github.com/Harikrishnan-P97/clihax" in out
    assert "MIT" in out
    assert clihax.__version__ in out


def test_full_info_summarises_the_toolbox(seeded):
    _, out = info(seeded)
    assert "recon (1)" in out
    assert "7 distinct" in out
    assert "tools.json" in out


def test_full_info_with_empty_database(runner):
    result, out = info(runner)
    assert result.exit_code == 0
    assert "none yet" in out
    assert "not created yet" in out
    assert out.count("never") == 3


def test_info_reports_backups_and_drop_events(seeded):
    seeded.invoke(cli, ["drop"], input="y\ny\n")
    _, out = info(seeded)
    assert "1 file" in out and "1 event" in out


def test_info_does_not_create_backup_or_log_folders(runner):
    info(runner)
    info(runner, "--quick")
    data_dir = helpers.get_data_dir()
    assert not (data_dir / "backups").exists()
    assert not (data_dir / "logs").exists()


def test_quick_info_lists_author_and_repository(seeded):
    _, out = info(seeded, "--quick")
    assert "Author        : Harikrishnan-P97" in out
    assert "Repository    : https://github.com/Harikrishnan-P97/clihax" in out
    assert "\u2588" not in out


def test_info_survives_a_narrow_terminal(seeded, monkeypatch):
    monkeypatch.setenv("COLUMNS", "40")
    result, out = info(seeded)
    assert result.exit_code == 0
    assert "Toolbox" in out


def test_project_constants_match_pyproject():
    tomllib = pytest.importorskip("tomllib")  # standard library from Python 3.11
    pyproject = Path(__file__).resolve().parent.parent / "pyproject.toml"
    project = tomllib.loads(pyproject.read_text())["project"]
    assert project["authors"][0]["name"] == clihax.__author__
    assert project["urls"]["Repository"] == clihax.__repo_url__
    assert project["urls"]["Homepage"] == clihax.__repo_url__

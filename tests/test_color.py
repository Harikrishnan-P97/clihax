"""Tests for colour handling: plain output when piped, --no-color and NO_COLOR."""

import click
import pytest

from clihax import ui
from clihax.cli import cli

ESC = "\x1b["


@pytest.fixture(autouse=True)
def _clean_env(monkeypatch):
    monkeypatch.delenv("NO_COLOR", raising=False)


def test_search_output_is_plain_when_piped(seeded):
    for args in (["search", "nmap"], ["search", "nmap", "-q"], ["searchfilter", "-c", "recon"]):
        result = seeded.invoke(cli, args)
        assert result.exit_code == 0
        assert ESC not in result.output, args


def test_messages_are_coloured_when_colour_is_forced(runner):
    result = runner.invoke(cli, ["list"], color=True)
    assert "No tools found" in result.output
    assert ESC in result.output


def test_no_color_flag_removes_colour_from_messages(runner):
    result = runner.invoke(cli, ["--no-color", "list"], color=True)
    assert "No tools found" in result.output
    assert ESC not in result.output


@pytest.mark.parametrize("value, coloured", [("1", False), ("", True)])
def test_no_color_environment_variable(runner, monkeypatch, value, coloured):
    monkeypatch.setenv("NO_COLOR", value)
    result = runner.invoke(cli, ["list"], color=True)
    assert (ESC in result.output) is coloured


def test_make_console_follows_the_click_context():
    with click.Context(cli, color=False):
        assert ui.make_console().no_color is True
    with click.Context(cli):
        assert ui.make_console().no_color is False
    assert ui.make_console().no_color is False  # outside any command


def test_make_console_respects_no_color_environment(monkeypatch):
    monkeypatch.setenv("NO_COLOR", "1")
    assert ui.make_console().no_color is True


def test_no_color_flag_works_with_every_kind_of_command(seeded):
    for args in (["list"], ["search", "nmap"], ["info"], ["show", "1"], ["list", "--json"]):
        result = seeded.invoke(cli, ["--no-color", *args], color=True)
        assert result.exit_code == 0, args
        assert ESC not in result.output, args


def test_help_mentions_no_color(runner):
    assert "--no-color" in runner.invoke(cli, ["--help"]).output

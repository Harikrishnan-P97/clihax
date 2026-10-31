"""Stored commands must be shown literally, even when they look like rich markup."""

from clihax.cli import cli
from clihax.utils import helpers

from .conftest import make_tool, plain

BRACKETS = make_tool("netcat", "nc -lvnp [port]", "recon", ["[ip]"], "listen on [port]")


def test_list_shows_square_brackets_literally(runner):
    helpers.save_tools([BRACKETS])
    out = plain(runner.invoke(cli, ["list"]).output)
    assert "[port]" in out
    assert "[ip]" in out


def test_show_shows_square_brackets_literally(runner):
    helpers.save_tools([BRACKETS])
    out = plain(runner.invoke(cli, ["show", "1"]).output)
    assert "nc -lvnp [port]" in out
    assert "listen on [port]" in out


def test_search_results_show_square_brackets_literally(runner):
    helpers.save_tools([BRACKETS])
    out = plain(runner.invoke(cli, ["search", "netcat"]).output)
    assert "[port]" in out


def test_closing_tag_like_text_does_not_crash(runner):
    helpers.save_tools([make_tool("weird", "echo [/bold] done")])
    result = runner.invoke(cli, ["list"])
    assert result.exit_code == 0
    assert "[/bold]" in plain(result.output)


def test_import_message_survives_brackets_in_filename(runner, tmp_path):
    odd = tmp_path / "[red]tools.json"
    odd.write_text("[]")
    result = runner.invoke(cli, ["import", str(odd)])
    assert result.exit_code == 0

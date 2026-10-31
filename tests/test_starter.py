"""Tests for the starter pack data and the `clihax starter` command."""

from clihax.cli import cli
from clihax.starter import STARTER_TOOLS
from clihax.utils import helpers

from .conftest import SAMPLE_TOOLS, plain


def starter(runner, *args, input=None):
    result = runner.invoke(cli, ["starter", *args], input=input)
    return result, plain(result.output)


# ---------- the data itself ----------

def test_every_starter_entry_is_valid():
    for entry in STARTER_TOOLS:
        assert helpers.normalize_tool(entry) is not None, entry
        assert entry["description"] and entry["category"] and entry["tags"], entry


def test_starter_entries_are_unique():
    keys = [helpers.tool_key(entry) for entry in STARTER_TOOLS]
    assert len(keys) == len(set(keys))


def test_starter_pack_is_a_reasonable_size_and_covers_core_tools():
    assert len(STARTER_TOOLS) >= 25
    names = {entry["tool"] for entry in STARTER_TOOLS}
    assert {"nmap", "ffuf", "gobuster", "hydra", "sqlmap", "msfvenom"} <= names


# ---------- the command ----------

def test_list_shows_the_pack_and_changes_nothing(runner):
    result, out = starter(runner, "--list")
    assert result.exit_code == 0
    assert "tools to add" in out and "nmap" in out
    assert helpers.load_tools() == []


def test_yes_adds_the_whole_pack(runner):
    result, out = starter(runner, "--yes")
    assert result.exit_code == 0
    assert "Added" in out
    assert len(helpers.load_tools()) == len(STARTER_TOOLS)


def test_confirmation_prompt_accepts_enter(runner):
    starter(runner, input="\n")
    assert len(helpers.load_tools()) == len(STARTER_TOOLS)


def test_declining_the_prompt_adds_nothing(runner):
    result, _ = starter(runner, input="n\n")
    assert result.exit_code == 1  # click's Abort
    assert helpers.load_tools() == []


def test_running_twice_does_not_duplicate(runner):
    starter(runner, "-y")
    _, out = starter(runner, "-y")
    assert "already in your database" in out
    assert len(helpers.load_tools()) == len(STARTER_TOOLS)


def test_existing_tools_are_kept_and_duplicates_skipped(seeded):
    # SAMPLE_TOOLS[0] is nmap -sV; add one entry that exactly matches a starter entry.
    first = dict(STARTER_TOOLS[0])
    helpers.save_tools([dict(t) for t in SAMPLE_TOOLS] + [first])

    _, out = starter(seeded, "-y")

    tools = helpers.load_tools()
    assert [t["tool"] for t in tools[:3]] == ["nmap", "hydra", "msfvenom"]  # untouched, same order
    assert len(tools) == 4 + len(STARTER_TOOLS) - 1
    assert "will be skipped" in out


def test_starter_commands_are_stored_exactly(runner):
    starter(runner, "-y")
    stored = {t["command"] for t in helpers.load_tools()}
    assert "nmap -sC -sV -oA scan <target>" in stored  # <target> must survive intact


def test_help_lists_starter(runner):
    result = runner.invoke(cli, ["--help"])
    assert "starter" in plain(result.output)

"""Tests for shell completion: the script command and database-aware completers."""

import pytest

from clihax.cli import cli
from clihax.utils import helpers

from .conftest import plain


def complete(runner, words, shell="bash"):
    """Simulate pressing Tab: what would the shell offer after `words`?"""
    cword = len(words) - 1
    result = runner.invoke(
        cli,
        [],
        prog_name="clihax",
        env={
            "_CLIHAX_COMPLETE": f"{shell}_complete",
            "COMP_WORDS": " ".join(words),
            "COMP_CWORD": str(cword),
        },
    )
    assert result.exit_code == 0
    return [line.split(",", 1)[1] for line in result.output.splitlines() if "," in line]


# ---------- the script command ----------

@pytest.mark.parametrize("shell", ["bash", "zsh", "fish"])
def test_completion_prints_a_script_for_each_shell(runner, shell):
    result = runner.invoke(cli, ["completion", shell])
    assert result.exit_code == 0
    assert "_CLIHAX_COMPLETE" in result.output
    assert "clihax" in result.output


def test_completion_rejects_unknown_shells(runner):
    result = runner.invoke(cli, ["completion", "powershell"])
    assert result.exit_code == 2
    assert "bash" in plain(result.stderr)


def test_completion_script_is_only_the_script(runner):
    # it is meant for: eval "$(clihax completion bash)"
    result = runner.invoke(cli, ["completion", "bash"])
    assert result.stderr == ""
    assert not result.output.startswith("Migrated")


# ---------- pressing Tab ----------

def test_commands_are_completed(runner):
    offered = complete(runner, ["clihax", "sta"])
    assert offered == ["starter"]


def test_new_options_are_completed(runner):
    assert "--json" in complete(runner, ["clihax", "list", "--j"])
    assert "--no-color" in complete(runner, ["clihax", "--no"])


def test_categories_come_from_the_database(seeded):
    assert complete(seeded, ["clihax", "searchfilter", "--category", ""]) == ["attack", "post", "recon"]
    assert complete(seeded, ["clihax", "searchfilter", "-c", "re"]) == ["recon"]


def test_tags_come_from_the_database(seeded):
    assert complete(seeded, ["clihax", "searchfilter", "--tag", "me"]) == ["meterpreter"]
    assert "brute-force" in complete(seeded, ["clihax", "searchfilter", "-t", ""])


def test_tool_numbers_are_completed_for_show_edit_delete(seeded):
    for command in ("show", "edit", "delete"):
        assert complete(seeded, ["clihax", command, ""]) == ["1", "2", "3"]
    assert complete(seeded, ["clihax", "show", "2"]) == ["2"]


def test_completion_is_silent_with_an_empty_database(runner):
    assert complete(runner, ["clihax", "searchfilter", "-c", ""]) == []
    assert complete(runner, ["clihax", "show", ""]) == []


def test_completion_survives_a_broken_database(runner):
    helpers.tools_file().write_text("{broken")
    assert complete(runner, ["clihax", "searchfilter", "-c", ""]) == []
    assert complete(runner, ["clihax", "show", ""]) == []


def test_completion_never_modifies_the_database(seeded):
    before = helpers.tools_file().read_text()
    complete(seeded, ["clihax", "show", ""])
    complete(seeded, ["clihax", "searchfilter", "-t", ""])
    assert helpers.tools_file().read_text() == before

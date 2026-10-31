"""Tests for --json output on list, show, search and searchfilter."""

import json

import pytest

from clihax.cli import cli
from clihax.utils import helpers

from .conftest import SAMPLE_TOOLS, make_tool

JSON_COMMANDS = [
    ["list", "--json"],
    ["search", "nmap", "--json"],
    ["searchfilter", "-c", "recon", "--json"],
    ["show", "1", "--json"],
]


def run_json(runner, *args):
    result = runner.invoke(cli, list(args))
    return result, result.stdout


def test_list_json_is_valid_with_indexes_and_all_fields(seeded):
    result, out = run_json(seeded, "list", "--json")
    data = json.loads(out)
    assert result.exit_code == 0
    assert [t["index"] for t in data] == [1, 2, 3]
    assert [t["tool"] for t in data] == ["nmap", "hydra", "msfvenom"]
    assert data[0]["tags"] == ["scan", "nmap"]
    assert data[0]["created_at"] == "2025-01-01T00:00:00"


def test_list_json_with_empty_database_is_an_empty_list(runner):
    result, out = run_json(runner, "list", "--json")
    assert result.exit_code == 0
    assert json.loads(out) == []


def test_json_keeps_brackets_and_unicode_exactly(runner):
    helpers.save_tools([make_tool("nmap", "nmap -p [port] <target>", description="caf\u00e9 \u2713")])
    _, out = run_json(runner, "list", "--json")
    entry = json.loads(out)[0]
    assert entry["command"] == "nmap -p [port] <target>"
    assert entry["description"] == "caf\u00e9 \u2713"
    assert "\\u" not in out  # readable, not escaped


def test_json_output_has_no_colour_codes(seeded):
    for args in JSON_COMMANDS:
        _, out = run_json(seeded, *args)
        assert "\x1b" not in out
        json.loads(out)  # whole stdout is JSON, nothing else


def test_show_json_returns_one_object(seeded):
    result, out = run_json(seeded, "show", "2", "--json")
    data = json.loads(out)
    assert result.exit_code == 0
    assert data["index"] == 2 and data["tool"] == "hydra"


def test_show_json_invalid_index_fails_with_status_1(seeded):
    result, out = run_json(seeded, "show", "9", "--json")
    assert result.exit_code == 1
    assert out == ""
    assert "Invalid index" in result.stderr


def test_search_json_indexes_are_displayed_positions(seeded):
    _, out = run_json(seeded, "search", "ftp,payload", "--json")
    data = json.loads(out)
    assert [(t["index"], t["tool"]) for t in data] == [(1, "hydra"), (2, "msfvenom")]


def test_search_json_without_matches_is_an_empty_list(seeded):
    result, out = run_json(seeded, "search", "zzz", "--json")
    assert result.exit_code == 0
    assert json.loads(out) == []


def test_searchfilter_json(seeded):
    _, out = run_json(seeded, "searchfilter", "-c", "attack", "-t", "brute-force", "--json")
    assert [t["tool"] for t in json.loads(out)] == ["hydra"]


def test_searchfilter_json_no_match(seeded):
    _, out = run_json(seeded, "searchfilter", "-c", "recon", "-t", "brute-force", "--json")
    assert json.loads(out) == []


@pytest.mark.parametrize(
    "args",
    [
        ["list", "--json", "--quick"],
        ["list", "--json", "--pager"],
        ["show", "1", "--json", "--copy"],
        ["search", "nmap", "--json", "--quick"],
        ["search", "nmap", "--json", "--copy", "1"],
        ["searchfilter", "-c", "recon", "--json", "--quick"],
        ["searchfilter", "-c", "recon", "--json", "--copy", "1"],
    ],
)
def test_json_cannot_be_combined_with_display_flags(seeded, args):
    result = seeded.invoke(cli, args)
    assert result.exit_code == 2
    assert "--json cannot be combined with" in result.stderr


def test_json_does_not_modify_the_database(seeded):
    before = helpers.tools_file().read_text()
    for args in JSON_COMMANDS:
        seeded.invoke(cli, args)
    assert helpers.tools_file().read_text() == before


def test_sample_tools_round_trip_through_list_json(seeded):
    _, out = run_json(seeded, "list", "--json")
    stripped = [{k: v for k, v in t.items() if k != "index"} for t in json.loads(out)]
    assert stripped == SAMPLE_TOOLS

"""Tests for typo-tolerant search (a fallback that only runs when nothing matches exactly)."""

import json

import pytest

from clihax.cli import cli
from clihax.utils.search import filter_tools, fuzzy_matches_keywords

from .conftest import SAMPLE_TOOLS, make_tool, plain


def names(tools):
    return [t["tool"] for t in tools]


# ---------- the matching logic ----------

def test_fuzzy_is_off_by_default():
    assert filter_tools(SAMPLE_TOOLS, keywords=["nmpa"]) == []


@pytest.mark.parametrize(
    ("typo", "expected"),
    [("nmpa", "nmap"), ("hydar", "hydra"), ("msfvnom", "msfvenom"), ("scna", "nmap")],
)
def test_common_typos_are_found(typo, expected):
    assert expected in names(filter_tools(SAMPLE_TOOLS, keywords=[typo], fuzzy=True))


def test_typo_in_a_multi_word_keyword():
    found = filter_tools(SAMPLE_TOOLS, keywords=["reverse shel"], fuzzy=True)
    assert names(found) == ["msfvenom"]


def test_typo_in_a_hyphenated_tag():
    found = filter_tools(SAMPLE_TOOLS, keywords=["brute-forse"], fuzzy=True)
    assert names(found) == ["hydra"]


def test_unrelated_words_do_not_match():
    assert filter_tools(SAMPLE_TOOLS, keywords=["zzzz", "kubernetes"], fuzzy=True) == []


def test_very_short_keywords_are_never_fuzzy():
    assert not fuzzy_matches_keywords(make_tool("ssh", "ssh host"), ["sh", "ss"])


def test_fuzzy_never_loosens_tag_or_category():
    assert filter_tools(SAMPLE_TOOLS, keywords=["nmpa"], category="post", fuzzy=True) == []
    assert filter_tools(SAMPLE_TOOLS, keywords=["nmpa"], tag="ftp", fuzzy=True) == []
    assert names(filter_tools(SAMPLE_TOOLS, keywords=["nmpa"], category="recon", fuzzy=True)) == ["nmap"]


def test_fuzzy_copes_with_malformed_tools():
    assert filter_tools([{}, {"tool": None, "tags": "x"}], keywords=["nmpa"], fuzzy=True) == []


# ---------- the commands ----------

def test_search_finds_typos_and_says_so(seeded):
    result = seeded.invoke(cli, ["search", "nmpa"])
    assert result.exit_code == 0
    assert "nmap" in plain(result.stdout)
    assert "close matches" in plain(result.stderr)


def test_exact_search_gives_no_notice(seeded):
    result = seeded.invoke(cli, ["search", "nmap"])
    assert "close matches" not in plain(result.stderr)


def test_close_matches_are_not_mixed_into_exact_results(runner):
    from clihax.utils import helpers

    helpers.save_tools([make_tool("nmap", "nmap -sV"), make_tool("namp", "namp --other")])
    result = runner.invoke(cli, ["search", "nmap", "--json"])
    assert names(json.loads(result.stdout)) == ["nmap"]
    assert result.stderr == ""


def test_search_without_any_match_still_says_so(seeded):
    result = seeded.invoke(cli, ["search", "zzzz"])
    assert "No matches found" in plain(result.output)


def test_search_json_with_a_typo_keeps_stdout_clean(seeded):
    result = seeded.invoke(cli, ["search", "nmpa", "--json"])
    assert names(json.loads(result.stdout)) == ["nmap"]
    assert "close matches" in plain(result.stderr)


def test_searchfilter_typo_in_keywords(seeded):
    result = seeded.invoke(cli, ["searchfilter", "-c", "recon", "nmpa"])
    assert "nmap" in plain(result.stdout)
    assert "close matches" in plain(result.stderr)


def test_searchfilter_category_stays_exact(seeded):
    result = seeded.invoke(cli, ["searchfilter", "-c", "post", "nmpa"])
    assert "No matches found" in plain(result.output)


def test_searchfilter_without_keywords_is_unchanged(seeded):
    result = seeded.invoke(cli, ["searchfilter", "-c", "recon", "--json"])
    assert names(json.loads(result.stdout)) == ["nmap"]
    assert result.stderr == ""

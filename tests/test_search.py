"""Unit tests for the pure search/filter logic."""

from clihax.utils.search import filter_tools, matches_keywords, parse_keywords

from .conftest import SAMPLE_TOOLS


def names(tools):
    return [t["tool"] for t in tools]


# ---------- parse_keywords ----------

def test_parse_keywords_splits_lowercases_and_drops_empties():
    assert parse_keywords("FTP, nmap,, ") == ["ftp", "nmap"]


def test_parse_keywords_handles_none_and_blank():
    assert parse_keywords(None) == []
    assert parse_keywords("") == []
    assert parse_keywords(" , ") == []


# ---------- matches_keywords ----------

def test_keyword_matches_substring_of_name_command_or_description():
    nmap = SAMPLE_TOOLS[0]
    assert matches_keywords(nmap, ["nma"])
    assert matches_keywords(nmap, ["-sv"])
    assert matches_keywords(nmap, ["service"])


def test_keyword_must_equal_a_tag_exactly():
    hydra = SAMPLE_TOOLS[1]
    assert matches_keywords(hydra, ["brute-force"])
    assert not matches_keywords(hydra, ["brute-for-ce"])


def test_no_keywords_never_matches():
    assert not matches_keywords(SAMPLE_TOOLS[0], [])


def test_malformed_tool_does_not_crash():
    broken = {"tool": None, "tags": "not-a-list", "command": 5}
    assert not matches_keywords(broken, ["zzz"])


# ---------- filter_tools ----------

def test_no_conditions_returns_everything():
    assert names(filter_tools(SAMPLE_TOOLS)) == ["nmap", "hydra", "msfvenom"]


def test_filter_by_tag_is_exact_and_case_insensitive():
    assert names(filter_tools(SAMPLE_TOOLS, tag="BRUTE-FORCE")) == ["hydra"]
    assert filter_tools(SAMPLE_TOOLS, tag="brute") == []


def test_filter_by_category_is_exact():
    assert names(filter_tools(SAMPLE_TOOLS, category="Post")) == ["msfvenom"]
    assert filter_tools(SAMPLE_TOOLS, category="pos") == []


def test_filter_conditions_are_anded():
    assert names(filter_tools(SAMPLE_TOOLS, category="attack", tag="ftp", keywords=["admin"])) == ["hydra"]
    assert filter_tools(SAMPLE_TOOLS, category="recon", tag="ftp") == []


def test_filter_tolerates_missing_or_null_category():
    tools = [{"tool": "a", "command": "b", "category": None}, {"tool": "c", "command": "d"}]
    assert filter_tools(tools, category="x") == []

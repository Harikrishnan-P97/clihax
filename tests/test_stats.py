"""Tests for the pure summary and formatting helpers behind `clihax info`."""

from datetime import datetime, timezone

import pytest

from clihax.utils.stats import format_when, human_size, humanize_age, toolbox_stats

from .conftest import SAMPLE_TOOLS, make_tool


def test_stats_for_empty_toolbox():
    stats = toolbox_stats([])
    assert (stats.total, stats.categories, stats.tag_count) == (0, [], 0)


def test_stats_counts_tools_categories_and_tags():
    stats = toolbox_stats(SAMPLE_TOOLS)
    assert stats.total == 3
    assert stats.tag_count == 7
    assert dict(stats.categories) == {"recon": 1, "attack": 1, "post": 1}


def test_categories_sorted_by_count_then_name_and_case_insensitive():
    tools = [
        make_tool("a", "a", "Recon"),
        make_tool("b", "b", "recon"),
        make_tool("c", "c", "zeta"),
        make_tool("d", "d", "alpha"),
        make_tool("e", "e", ""),
    ]
    assert toolbox_stats(tools).categories == [("recon", 2), ("alpha", 1), ("zeta", 1)]


def test_stats_ignore_bad_entries():
    tools = [make_tool("a", "a", tags=["X", "x"]), "junk", {"tags": "nope"}]
    stats = toolbox_stats(tools)
    assert stats.tag_count == 1
    assert stats.total == 3


@pytest.mark.parametrize(
    ("size", "text"),
    [
        (0, "0 B"),
        (428, "428 B"),
        (1023, "1023 B"),
        (1536, "1.5 KB"),
        (5 * 1024 * 1024, "5.0 MB"),
        (3 * 1024**3, "3.0 GB"),
    ],
)
def test_human_size(size, text):
    assert human_size(size) == text


@pytest.mark.parametrize(
    ("seconds", "text"),
    [
        (0, "just now"),
        (59, "just now"),
        (60, "1 min ago"),
        (3599, "59 min ago"),
        (3600, "1 h ago"),
        (86399, "23 h ago"),
        (86400, "1 day ago"),
        (2 * 86400, "2 days ago"),
        (30 * 86400, "1 month ago"),
        (90 * 86400, "3 months ago"),
        (365 * 86400, "1 year ago"),
        (800 * 86400, "2 years ago"),
    ],
)
def test_humanize_age(seconds, text):
    assert humanize_age(seconds) == text


NOW = datetime(2026, 10, 31, 12, 0, 0)


def test_format_when_with_age():
    assert format_when("2026-10-29T12:00:00", now=NOW) == "2026-10-29 12:00 (2 days ago)"


@pytest.mark.parametrize("value", [None, "", "N/A"])
def test_format_when_missing_is_never(value):
    assert format_when(value) == "never"


def test_format_when_keeps_unparseable_text():
    assert format_when("last tuesday") == "last tuesday"


def test_format_when_skips_age_on_timezone_mismatch():
    value = datetime(2026, 10, 29, 12, 0, tzinfo=timezone.utc).isoformat()
    assert format_when(value, now=NOW) == "2026-10-29 12:00"

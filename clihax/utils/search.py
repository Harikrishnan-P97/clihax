"""Pure search and filter logic (no I/O and no printing), so it is easy to test."""

import re
from collections.abc import Iterable
from difflib import get_close_matches

from clihax.utils.helpers import ToolDict

FUZZY_CUTOFF = 0.75  # how similar two words must be (0 to 1) to count as a typo of each other
MIN_FUZZY_LENGTH = 3  # shorter words are never fuzzy-matched (too many false positives)


def parse_keywords(raw: str | None) -> list[str]:
    """Split 'a, b,,c' into ['a', 'b', 'c'] (lower-cased, empty parts dropped)."""
    if not raw:
        return []
    return [kw.strip().lower() for kw in raw.split(",") if kw.strip()]


def _tags(tool: ToolDict) -> list[str]:
    tags = tool.get("tags", [])
    return [str(tag).lower() for tag in tags] if isinstance(tags, list) else []


def _haystack(tool: ToolDict) -> str:
    parts = (tool.get("tool", ""), tool.get("command", ""), tool.get("description", ""))
    return " ".join(str(part) for part in parts).lower()


def matches_keywords(tool: ToolDict, keywords: Iterable[str]) -> bool:
    """True if any keyword is inside the name/command/description or equals a tag."""
    haystack = _haystack(tool)
    tags = _tags(tool)
    return any(kw in haystack or kw in tags for kw in keywords)


def _words(tool: ToolDict) -> list[str]:
    """Every separate word in the name, command, description and tags."""
    text = _haystack(tool) + " " + " ".join(_tags(tool))
    return sorted(set(re.findall(r"[a-z0-9]+", text)))


def fuzzy_matches_keywords(tool: ToolDict, keywords: Iterable[str]) -> bool:
    """True if any keyword is a close misspelling of words in the tool ("nmpa" ~ "nmap").

    A keyword made of several words needs every word to be close to some word of the tool.
    """
    words = _words(tool)
    for keyword in keywords:
        parts = re.findall(r"[a-z0-9]+", keyword.lower())
        if parts and all(
            len(part) >= MIN_FUZZY_LENGTH and get_close_matches(part, words, n=1, cutoff=FUZZY_CUTOFF)
            for part in parts
        ):
            return True
    return False


def filter_tools(
    tools: Iterable[ToolDict],
    *,
    keywords: Iterable[str] = (),
    tag: str | None = None,
    category: str | None = None,
    fuzzy: bool = False,
) -> list[ToolDict]:
    """Return the tools that satisfy every given condition.

    ``tag`` must equal one of the tool's tags, ``category`` must equal its
    category (both case-insensitive), and when ``keywords`` is non-empty at
    least one keyword must match. With no conditions every tool is returned.
    With ``fuzzy`` a keyword may also match a close misspelling; tag and
    category are always exact.
    """
    keywords = list(keywords)
    tag = tag.lower() if tag else None
    category = category.lower() if category else None

    matched = []
    for tool in tools:
        if tag and tag not in _tags(tool):
            continue
        if category and str(tool.get("category") or "").lower() != category:
            continue
        if keywords and not (
            matches_keywords(tool, keywords) or (fuzzy and fuzzy_matches_keywords(tool, keywords))
        ):
            continue
        matched.append(tool)
    return matched

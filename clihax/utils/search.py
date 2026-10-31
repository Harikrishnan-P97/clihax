"""Pure search and filter logic (no I/O and no printing), so it is easy to test."""

from collections.abc import Iterable

from clihax.utils.helpers import ToolDict


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


def filter_tools(
    tools: Iterable[ToolDict],
    *,
    keywords: Iterable[str] = (),
    tag: str | None = None,
    category: str | None = None,
) -> list[ToolDict]:
    """Return the tools that satisfy every given condition.

    ``tag`` must equal one of the tool's tags, ``category`` must equal its
    category (both case-insensitive), and when ``keywords`` is non-empty at
    least one keyword must match. With no conditions every tool is returned.
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
        if keywords and not matches_keywords(tool, keywords):
            continue
        matched.append(tool)
    return matched

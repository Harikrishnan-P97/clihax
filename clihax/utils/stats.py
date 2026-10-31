"""Pure helpers that summarise the toolbox and format values for display."""

from collections import Counter
from dataclasses import dataclass
from datetime import datetime

from clihax.utils.helpers import ToolDict


@dataclass(frozen=True)
class ToolboxStats:
    total: int
    categories: list[tuple[str, int]]  # (name, how many tools), most used first
    tag_count: int  # number of distinct tags


def toolbox_stats(tools: list[ToolDict]) -> ToolboxStats:
    """Count tools, categories and distinct tags (case-insensitive)."""
    categories: Counter[str] = Counter()
    tags: set[str] = set()
    for tool in tools:
        if not isinstance(tool, dict):
            continue
        category = str(tool.get("category") or "").strip().lower()
        if category:
            categories[category] += 1
        raw_tags = tool.get("tags", [])
        if isinstance(raw_tags, list):
            tags.update(str(tag).strip().lower() for tag in raw_tags if str(tag).strip())
    ranked = sorted(categories.items(), key=lambda item: (-item[1], item[0]))
    return ToolboxStats(total=len(tools), categories=ranked, tag_count=len(tags))


def human_size(num_bytes: int) -> str:
    """1536 -> '1.5 KB'."""
    if num_bytes < 1024:
        return f"{num_bytes} B"
    size = num_bytes / 1024
    for unit in ("KB", "MB"):
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} GB"


def humanize_age(seconds: float) -> str:
    """Seconds since an event -> 'just now', '5 min ago', '2 days ago', ..."""
    seconds = int(seconds)
    if seconds < 60:
        return "just now"
    minutes = seconds // 60
    if minutes < 60:
        return f"{minutes} min ago"
    hours = minutes // 60
    if hours < 24:
        return f"{hours} h ago"
    days = hours // 24
    if days < 30:
        return f"{days} day{'s' if days != 1 else ''} ago"
    months = days // 30
    if months < 12:
        return f"{months} month{'s' if months != 1 else ''} ago"
    years = max(1, days // 365)
    return f"{years} year{'s' if years != 1 else ''} ago"


def format_when(value: object, now: datetime | None = None) -> str:
    """'2026-10-29T14:04:20' -> '2026-10-29 14:04 (2 days ago)'.

    Missing values give 'never'; text that is not a timestamp is returned as is.
    """
    if not value or value == "N/A":
        return "never"
    try:
        moment = datetime.fromisoformat(str(value))
    except ValueError:
        return str(value)
    stamp = f"{moment:%Y-%m-%d %H:%M}"
    try:
        age = ((now or datetime.now()) - moment).total_seconds()
    except TypeError:  # timezone-aware vs naive: skip the "ago" part
        return stamp
    return f"{stamp} ({humanize_age(age)})"

"""Commands that find tools: search and searchfilter."""

import click

from clihax import ui
from clihax.utils.helpers import ToolDict, load_tools
from clihax.utils.search import filter_tools, parse_keywords


def _copy_result(matches: list[ToolDict], position: int) -> None:
    """Copy the command of result number ``position`` (1-based, as displayed)."""
    if not 1 <= position <= len(matches):
        ui.error(f"Invalid index: {position}. Use a number between 1 and {len(matches)}.")
        return
    tool = matches[position - 1]
    if ui.copy_to_clipboard(tool["command"]):
        click.secho(f"📋 Copied command from result [{position}] ({tool['tool']})", fg="green")


def _find(
    terms: list[str], *, tag: str | None = None, category: str | None = None
) -> list[ToolDict]:
    """Exact matches; if there are none, close matches (typos) with a notice."""
    tools = load_tools()
    matches = filter_tools(tools, keywords=terms, tag=tag, category=category)
    if matches or not terms:
        return matches
    matches = filter_tools(tools, keywords=terms, tag=tag, category=category, fuzzy=True)
    if matches:
        ui.notice(f"No exact match for '{', '.join(terms)}'. Showing close matches.")
    return matches


def _print_json(matches: list[ToolDict]) -> None:
    """Matches as JSON; the index is the displayed position, as used by --copy."""
    ui.print_json([ui.tool_json(i, tool) for i, tool in enumerate(matches, start=1)])


def _show_results(matches: list[ToolDict], title: str, terms: list[str], quick: bool) -> None:
    console = ui.make_console()
    if quick:
        ui.print_quick_results(console, matches, terms)
    else:
        ui.print_results_table(console, title, matches, terms)


# ========= search ========= #

@click.command(help="Search tools using keyword(s). Matches tool name, command, description, and tags.")
@click.argument("keywords", required=True)
@click.option("--quick", "-q", is_flag=True, help="Minimal output (no table formatting)")
@click.option("--copy", "-C", default=None, type=int, help="Copy command at specified displayed index (1-based)")
@click.option("--json", "as_json", is_flag=True, help="Print matches as JSON (for scripts).")
def search(keywords: str, quick: bool, copy: int | None, as_json: bool) -> None:
    if as_json:
        ui.reject_json_conflicts({"--quick": quick, "--copy": copy is not None})
    terms = parse_keywords(keywords)
    matches = _find(terms) if terms else []

    if as_json:
        _print_json(matches)
        return
    if not matches:
        ui.error("No matches found.")
        return
    if copy is not None:
        _copy_result(matches, copy)
        return

    _show_results(matches, f"Search Results (keywords: {', '.join(terms)})", terms, quick)


# ========= searchfilter ========= #

@click.command(help="Advanced filter by tag (-t), category (-c), and/or keywords.")
@click.option("--tag", "-t", help="Filter by tag (e.g., recon, smb, brute-force)")
@click.option("--category", "-c", help="Filter by category (e.g., recon, attack, post)")
@click.argument("keywords", required=False)
@click.option("--quick", "-q", is_flag=True, help="Minimal output")
@click.option("--copy", "-C", default=None, type=int, help="Copy command at specified displayed index (1-based)")
@click.option("--json", "as_json", is_flag=True, help="Print matches as JSON (for scripts).")
def searchfilter(
    tag: str | None,
    category: str | None,
    keywords: str | None,
    quick: bool,
    copy: int | None,
    as_json: bool,
) -> None:
    """Filter tools by tag, category, and/or keyword(s) (comma-separated)."""
    if as_json:
        ui.reject_json_conflicts({"--quick": quick, "--copy": copy is not None})
    tag = tag.lower() if tag else None
    category = category.lower() if category else None
    terms = parse_keywords(keywords)

    matches = _find(terms, tag=tag, category=category)

    if as_json:
        _print_json(matches)
        return

    if not matches:
        ui.error("No matches found.")
        return
    if copy is not None:
        _copy_result(matches, copy)
        return

    title = "Filtered Results"
    if category:
        title += f" | Category: {category}"
    if tag:
        title += f" | Tag: {tag}"
    if terms:
        title += f" | Keywords: {', '.join(terms)}"

    highlight_terms = terms + [term for term in (tag, category) if term]
    _show_results(matches, title, highlight_terms, quick)

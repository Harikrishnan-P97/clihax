"""Terminal presentation: consoles, banner, tables, highlighting and clipboard access.

Everything that decides how CliHax *looks* lives here, so command modules
only decide *what* to show.
"""

import json
import re
from collections.abc import Iterable, Mapping, Sequence

import click
import pyperclip
from rich.console import Console
from rich.panel import Panel
from rich.style import Style
from rich.table import Table
from rich.text import Text

from clihax.utils.helpers import ToolDict

BANNER = """\

 ██████╗██╗     ██╗██╗  ██╗ █████╗ ██╗  ██╗
██╔════╝██║     ██║██║  ██║██╔══██╗╚██╗██╔╝
██║     ██║     ██║███████║███████║ ╚███╔╝
██║     ██║     ██║██╔══██║██╔══██║ ██╔██╗
╚██████╗███████╗██║██║  ██║██║  ██║██╔╝ ██╗
 ╚═════╝╚══════╝╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝
"""


DASH = "\u2014"  # shown when a tool has no category


# ========= Messages ========= #

def error(message: str) -> None:
    click.secho(f"\u274c {message}", fg="red")


def notice(message: str) -> None:
    """A hint for the user, written to stderr so piped output (and --json) stays clean."""
    click.secho(f"\u2139\ufe0f  {message}", fg="yellow", err=True)


def success(message: str) -> None:
    click.secho(f"\u2705 {message}", fg="green")


# ========= Console, banner, clipboard ========= #

def make_console() -> Console:
    """A rich console that colours only on a real terminal.

    Piped or redirected output stays plain. ``--no-color`` (stored on the click
    context by the main command) removes colour on a terminal too; rich itself
    already honours the NO_COLOR environment variable.
    """
    ctx = click.get_current_context(silent=True)
    return Console(no_color=True if ctx is not None and ctx.color is False else None)


def show_banner(console: Console | None = None) -> None:
    console = console or make_console()
    banner = Text(BANNER, style="bold cyan")
    console.print(Panel(banner, expand=False, border_style="cyan", padding=(0, 2)))


def copy_to_clipboard(text: str) -> bool:
    """Copy text to the clipboard. Returns True on success, False otherwise."""
    try:
        pyperclip.copy(text)
    except pyperclip.PyperclipException:
        error(
            "Clipboard unavailable. On Linux install xclip or wl-clipboard "
            "(e.g. sudo apt install xclip)."
        )
        return False
    return True


# ========= Formatting helpers ========= #

def format_tags(tool: ToolDict) -> str:
    tags = tool.get("tags", [])
    return ", ".join(str(tag) for tag in tags) if isinstance(tags, list) else ""


def cell(value: object) -> Text:
    """Wrap a value so rich shows it literally.

    Plain strings in a table are parsed as markup, which silently drops text
    such as ``[port]`` from a stored command. ``Text`` is never parsed.
    """
    return Text(str(value))


def highlight(text: Text, terms: Iterable[str]) -> Text:
    """Highlight every (case-insensitive) occurrence of each term, in place."""
    for term in dict.fromkeys(terms):
        if term:
            text.highlight_regex(rf"(?i){re.escape(term)}", style="bold yellow")
    return text


# ========= JSON output (--json) ========= #

def tool_json(index: int, tool: ToolDict) -> ToolDict:
    """A tool as shown in JSON output: its 1-based index first, then the stored fields."""
    return {"index": index, **tool}


def print_json(data: object) -> None:
    """Print data as pretty JSON on stdout (nothing else is ever printed in --json mode)."""
    click.echo(json.dumps(data, indent=2, ensure_ascii=False))


def reject_json_conflicts(flags: Mapping[str, bool]) -> None:
    """--json prints machine-readable output only, so it can't be mixed with display flags."""
    used = [name for name, enabled in flags.items() if enabled]
    if used:
        raise click.UsageError(f"--json cannot be combined with {', '.join(used)}.")


# ========= Plain "quick" output ========= #

def quick_line(index: int, tool: ToolDict) -> str:
    name = tool.get("tool", "N/A")
    command = tool.get("command", "N/A")
    category = tool.get("category", DASH)
    return f"[{index}] {name}: {command} ({category})  # {format_tags(tool)}"


def quick_detail(index: int, tool: ToolDict) -> str:
    return "\n".join(
        [
            f"[{index}] {tool.get('tool', 'N/A')}",
            f"  Command    : {tool.get('command', 'N/A')}",
            f"  Desc       : {tool.get('description', '')}",
            f"  Category   : {tool.get('category', DASH)}",
            f"  Tags       : {format_tags(tool)}",
            f"  Created At : {tool.get('created_at', '')}",
            f"  Updated At : {tool.get('updated_at', '')}",
        ]
    )


# ========= Tables ========= #

def build_tools_table(
    tools: Sequence[ToolDict], *, full: bool = False, title: str | None = None
) -> Table:
    """Table used by ``list``; ``full`` adds description and timestamps."""
    default_title = "CliHax Full Tool List" if full else "CliHax Tool List"
    table = Table(title=title or default_title, show_lines=True)
    table.add_column("Index", justify="center", style="bold cyan")
    table.add_column("Tool", style="magenta", overflow="fold")
    table.add_column("Command", style="green", overflow="fold")
    if full:
        table.add_column("Description", style="white", overflow="fold")
    table.add_column("Category", style="blue", overflow="fold")
    table.add_column("Tags", style="yellow", overflow="fold")
    if full:
        table.add_column("Created At", style="dim")
        table.add_column("Updated At", style="dim")

    for index, tool in enumerate(tools, start=1):
        row = [str(index), cell(tool.get("tool", "N/A")), cell(tool.get("command", "N/A"))]
        if full:
            row.append(cell(tool.get("description", "")))
        row += [cell(tool.get("category", DASH)), cell(format_tags(tool))]
        if full:
            row += [cell(tool.get("created_at", "")), cell(tool.get("updated_at", ""))]
        table.add_row(*row)
    return table


def build_detail_table(index: int, tool: ToolDict) -> Table:
    """Field/value table used by ``show``."""
    table = Table(title=f"Details for Tool [{index}]: {tool.get('tool', 'N/A')}")
    table.add_column("Field", style="cyan", no_wrap=True)
    table.add_column("Value", style="white")
    for key in ("tool", "command", "description", "category"):
        table.add_row(key.capitalize(), cell(tool.get(key, "N/A")))
    table.add_row("Tags", cell(format_tags(tool) or "None"))
    table.add_row("Created At", cell(tool.get("created_at", "N/A")))
    table.add_row("Last Updated", cell(tool.get("updated_at", "N/A")))
    return table


def print_quick_results(console: Console, matches: Sequence[ToolDict], terms: Iterable[str]) -> None:
    """One highlighted line per match (used by ``search`` and ``searchfilter``)."""
    terms = list(terms)
    for index, tool in enumerate(matches, start=1):
        line = Text()
        line.append(f"[{index}] ", style="bold cyan")
        line.append(f"{tool['tool']}: ", style="bold magenta")
        line.append(str(tool["command"]), style="green")
        if tool.get("description"):
            line.append(f"  # {tool['description']}", style="dim")
        console.print(highlight(line, terms))


def print_results_table(
    console: Console, title: str, matches: Sequence[ToolDict], terms: Iterable[str]
) -> None:
    """Highlighted result table (used by ``search`` and ``searchfilter``)."""
    terms = list(terms)
    table = Table(title=title, show_lines=True)
    table.add_column("Index", justify="center", style="bold cyan")
    table.add_column("Tool", style="magenta")
    table.add_column("Command", style="green")
    table.add_column("Tags", style="blue")

    for index, tool in enumerate(matches, start=1):
        table.add_row(
            str(index),
            highlight(cell(tool["tool"]), terms),
            highlight(cell(tool["command"]), terms),
            highlight(cell(format_tags(tool)), terms),
        )
    console.print(table)


# ========= Info page ========= #

INFO_WIDTH = 76  # width of the info panels (shrinks on narrow terminals)

InfoRows = Sequence[tuple[str, "str | Text"]]


def link(label: str, url: str) -> Text:
    """Underlined text that is clickable in terminals that support hyperlinks."""
    return Text(label, style=Style(color="bright_blue", underline=True, link=url))


def _info_panel(title: str, rows: InfoRows, width: int) -> Panel:
    grid = Table.grid(padding=(0, 2))
    grid.add_column(style="bold cyan", no_wrap=True)
    grid.add_column(overflow="fold")
    for label, value in rows:
        grid.add_row(label, value if isinstance(value, Text) else cell(value))
    return Panel(
        grid,
        title=Text(title, style="bold"),
        title_align="left",
        border_style="cyan",
        width=width,
        padding=(0, 1),
    )


def print_info(
    console: Console,
    *,
    headline: Text,
    description: str,
    sections: Sequence[tuple[str, InfoRows]],
    footer: Text,
) -> None:
    """Banner, headline and one titled panel per section (used by ``info``)."""
    width = min(console.width, INFO_WIDTH)
    console.print()
    show_banner(console)
    console.print(headline)
    console.print(Text(description, style="dim"))
    console.print()
    for title, rows in sections:
        console.print(_info_panel(title, rows, width))
    console.print(footer)

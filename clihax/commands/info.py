"""The info command."""

import platform

import click
from rich.text import Text

from clihax import __author__, __license__, __repo_url__, __version__, ui
from clihax.utils.helpers import (
    ToolDict,
    count_backups,
    count_drop_events,
    get_data_dir,
    load_meta,
    load_tools,
    tools_file,
)
from clihax.utils.stats import format_when, human_size, toolbox_stats

TAGLINE = "Hack smart. Document smarter."
DESCRIPTION = "Store, search and recall pentesting tool syntax right from your terminal."
MAX_CATEGORIES_SHOWN = 4


def _last_edit(tools: list[ToolDict]) -> str:
    """Newest created/updated timestamp across all tools ('N/A' if none)."""
    stamps = [tool.get("updated_at") or tool.get("created_at") for tool in tools]
    return max((stamp for stamp in stamps if stamp), default="N/A")


def _count_text(count: int, word: str) -> str:
    """0 -> 'none', 1 -> '1 file', 3 -> '3 files'."""
    if count == 0:
        return "none"
    return f"{count} {word}" if count == 1 else f"{count} {word}s"


def _categories_text(categories: list[tuple[str, int]]) -> str:
    if not categories:
        return "none yet"
    shown = ", ".join(f"{name} ({count})" for name, count in categories[:MAX_CATEGORIES_SHOWN])
    hidden = len(categories) - MAX_CATEGORIES_SHOWN
    summary = f"{len(categories)} \u00b7 {shown}"
    return f"{summary}, +{hidden} more" if hidden > 0 else summary


def _database_text() -> str:
    path = tools_file()
    if not path.is_file():
        return "tools.json \u00b7 not created yet"
    return f"tools.json \u00b7 {human_size(path.stat().st_size)}"


@click.command(help="Show general information about the tool.")
@click.option("--quick", "-q", is_flag=True, help="Minimal/plain output (no banner or rich formatting).")
def info(quick: bool) -> None:
    tools = load_tools()
    meta = load_meta()
    last_edit = _last_edit(tools)
    last_import = meta.get("last_import", "N/A")
    last_export = meta.get("last_export", "N/A")

    if quick:
        click.echo(f"🧰 CliHax v{__version__}")
        click.echo("A lightweight CLI reference manager for pentesters.")
        click.echo()
        click.echo(f"Total tools   : {len(tools)}")
        click.echo(f"Last edit     : {last_edit}")
        click.echo(f"Last import   : {last_import}")
        click.echo(f"Last export   : {last_export}")
        click.echo(f"Data dir      : {get_data_dir()}")
        click.echo(f"Author        : {__author__}")
        click.echo(f"Repository    : {__repo_url__}")
        return

    stats = toolbox_stats(tools)
    about = [
        ("Version", __version__),
        ("Author", ui.link(__author__, f"https://github.com/{__author__}")),
        ("Repository", ui.link(__repo_url__.removeprefix("https://"), __repo_url__)),
        ("License", __license__),
        ("Python", f"{platform.python_version()} on {platform.system()}"),
    ]
    toolbox = [
        ("Tools", str(stats.total)),
        ("Categories", _categories_text(stats.categories)),
        ("Tags", f"{stats.tag_count} distinct"),
        ("Data folder", str(get_data_dir())),
        ("Database", _database_text()),
        ("Backups", _count_text(count_backups(), "file")),
        ("Drop log", _count_text(count_drop_events(), "event")),
    ]
    activity = [
        ("Last edit", format_when(last_edit)),
        ("Last import", format_when(last_import)),
        ("Last export", format_when(last_export)),
    ]

    headline = Text.assemble(
        ("CliHax ", "bold green"),
        (f"v{__version__}", "bold"),
        ("  \u00b7  ", "dim"),
        (TAGLINE, "italic"),
    )
    footer = Text.assemble(
        ("\nRun ", "dim"),
        ("clihax --help", "bold"),
        (" to see every command. Found a bug? ", "dim"),
        ui.link("Open an issue", f"{__repo_url__}/issues"),
        ("\n", "dim"),
    )
    ui.print_info(
        ui.make_console(),
        headline=headline,
        description=DESCRIPTION,
        sections=[("About", about), ("Toolbox", toolbox), ("Activity", activity)],
        footer=footer,
    )

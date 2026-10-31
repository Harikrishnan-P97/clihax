"""The info command."""

import click

from clihax import __version__, ui
from clihax.utils.helpers import ToolDict, get_data_dir, load_meta, load_tools


def _last_edit(tools: list[ToolDict]) -> str:
    """Newest created/updated timestamp across all tools ('N/A' if none)."""
    stamps = [tool.get("updated_at") or tool.get("created_at") for tool in tools]
    return max((stamp for stamp in stamps if stamp), default="N/A")


@click.command(help="Show general information about the tool.")
@click.option("--quick", "-q", is_flag=True, help="Minimal/plain output (no banner or rich formatting).")
def info(quick: bool) -> None:
    tools = load_tools()
    meta = load_meta()

    total = len(tools)
    last_edit = _last_edit(tools)
    last_import = meta.get("last_import", "N/A")
    last_export = meta.get("last_export", "N/A")

    if quick:
        click.echo(f"🧰 CliHax v{__version__}")
        click.echo("A lightweight CLI reference manager for pentesters.")
        click.echo()
        click.echo(f"Total tools   : {total}")
        click.echo(f"Last edit     : {last_edit}")
        click.echo(f"Last import   : {last_import}")
        click.echo(f"Last export   : {last_export}")
        click.echo(f"Data dir      : {get_data_dir()}")
        return

    console = ui.make_console()
    console.print("")
    ui.show_banner(console)
    console.print(f"\n[bold green]🧰 CliHax v{__version__}[/]")
    console.print(
        "A lightweight CLI reference manager for pentesters to store and retrieve "
        "common tool commands with ease.\n"
    )

    console.print("[bold cyan]📦 CliHax Tool Info[/]")
    console.print(f"🔢 Total Tools Stored     : [green]{total}[/]")
    console.print("🧑 Author                 : [magenta]LordSec[/]")
    console.print(f"🕓 Last Edit              : [yellow]{last_edit}[/]")
    console.print(f"📥 Last Import            : [blue]{last_import}[/]")
    console.print(f"📤 Last Export            : [blue]{last_export}[/]")
    console.print(f"📁 Data Directory         : [cyan]{get_data_dir()}[/]")

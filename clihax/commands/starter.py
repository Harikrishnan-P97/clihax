"""The starter command: add the built-in pack of common pentesting commands."""

import click

from clihax import ui
from clihax.starter import STARTER_TOOLS
from clihax.utils.helpers import load_tools, normalize_tool, save_tools, tool_key


def new_starter_tools(existing: list) -> list:
    """Starter entries that are not in the database yet (same tool + command = duplicate)."""
    known = {tool_key(tool) for tool in existing if isinstance(tool, dict)}
    fresh = []
    for entry in STARTER_TOOLS:
        tool = normalize_tool(entry)
        if tool is not None and tool_key(tool) not in known:
            known.add(tool_key(tool))
            fresh.append(tool)
    return fresh


@click.command(help="Add a ready-made pack of common pentesting commands (existing tools are kept).")
@click.option("--list", "-l", "list_only", is_flag=True, help="Only show what would be added.")
@click.option("--yes", "-y", is_flag=True, help="Add without asking for confirmation.")
def starter(list_only: bool, yes: bool) -> None:
    console = ui.make_console()
    existing = load_tools()
    fresh = new_starter_tools(existing)

    if not fresh:
        console.print("[yellow]ℹ️ The starter pack is already in your database. Nothing to add.[/]")
        return

    already = len(STARTER_TOOLS) - len(fresh)
    console.print(ui.build_tools_table(fresh, title=f"Starter pack: {len(fresh)} tools to add"))
    if already:
        console.print(f"[dim]{already} starter tool(s) are already in your database and will be skipped.[/]")
    if list_only:
        return

    if not yes:
        click.confirm(f"Add these {len(fresh)} tools to your database?", default=True, abort=True)

    save_tools(existing + fresh)
    console.print(f"[green]✅ Added {len(fresh)} starter tools.[/] Try [bold]clihax list[/] or [bold]clihax search nmap[/].")

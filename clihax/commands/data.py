"""Commands that move or remove the whole database: import, export, drop, logs."""

import json
import os
from datetime import datetime

import click
from rich.markup import escape
from rich.table import Table

from clihax import ui
from clihax.utils.helpers import (
    drops_log_file,
    load_drop_log,
    load_tools,
    normalize_tool,
    save_drop_log,
    save_tools,
    tool_key,
    update_meta,
    write_backup,
)

# ========= import ========= #

@click.command(name="import", help="Import tools from a JSON file (merged with existing tools).")
@click.argument("filename")
def import_tools(filename: str) -> None:
    """Import tools from a JSON file and merge with existing entries."""
    console = ui.make_console()

    if not os.path.exists(filename):
        console.print(f"[red]❌ File not found:[/] {escape(filename)}")
        return

    try:
        with open(filename) as f:
            imported = json.load(f)
        if not isinstance(imported, list):
            raise ValueError("Invalid format: expected a list of tool dictionaries.")
    except (OSError, ValueError) as exc:
        console.print(f"[red]❌ Failed to read or parse JSON:[/] {escape(str(exc))}")
        return

    valid = [tool for tool in map(normalize_tool, imported) if tool is not None]
    invalid = len(imported) - len(valid)
    if invalid:
        console.print(
            f"[yellow]⚠️ Skipped {invalid} invalid entr{'y' if invalid == 1 else 'ies'} "
            "(each needs a 'tool' and a 'command').[/]"
        )

    existing = load_tools()
    known = {tool_key(tool) for tool in existing}
    new_tools = []
    for tool in valid:
        if tool_key(tool) not in known:
            known.add(tool_key(tool))
            new_tools.append(tool)

    if not new_tools:
        console.print("[yellow]⚠️ No new tools to import. All entries are duplicates or invalid.[/]")
        return

    save_tools(existing + new_tools)
    update_meta("import")

    console.print(f"[green]✅ Imported {len(new_tools)} new tools from '{escape(filename)}' (merged).[/]")
    if len(new_tools) < len(valid):
        console.print(f"[yellow]⚠️ {len(valid) - len(new_tools)} duplicate entries were skipped.[/]")


# ========= export ========= #

@click.command(name="export", help="Export all tools to a JSON file.")
@click.argument("filename", required=False, default="exported_tools.json")
def export_tools(filename: str) -> None:
    """Export tools to a JSON file."""
    console = ui.make_console()
    tools = load_tools()

    if not tools:
        console.print("[red]❌ No tools to export.[/]")
        return

    seen = set()
    unique_tools = []
    for tool in tools:
        if tool_key(tool) not in seen:
            seen.add(tool_key(tool))
            unique_tools.append(tool)

    try:
        with open(filename, "w") as f:
            json.dump(unique_tools, f, indent=2)
    except OSError as exc:
        console.print(f"[red]❌ Failed to export tools:[/] {escape(str(exc))}")
        return

    console.print(
        f"[green]✅ Exported {len(unique_tools)} of {len(tools)} tools to:[/] [cyan]{escape(filename)}[/]"
    )
    if len(unique_tools) < len(tools):
        console.print(
            f"[yellow]⚠️  Skipped {len(tools) - len(unique_tools)} duplicate entries "
            "based on (tool, command)[/]"
        )
    update_meta("export")


# ========= drop ========= #

DROP_WARNING = (
    "\n⚠️  WARNING: You are about to delete ALL stored tools permanently.\n"
    "This action CANNOT be undone.\n"
)


def _log_drop(console, *, total: int, forced: bool, backup_created: bool | str) -> None:
    """Append a drop event to the drop log."""
    entry = {
        "timestamp": datetime.now().isoformat(),
        "total_dropped": total,
        "forced": forced,
        "backup_created": backup_created,
    }
    try:
        events = load_drop_log()
        events.append(entry)
        save_drop_log(events)
    except (OSError, ValueError) as exc:
        console.print(f"[bold red]Failed to log drop event:[/bold red] {escape(str(exc))}")
    else:
        console.print("[bold green]Drop event logged successfully.[/bold green]")


@click.command(help="Delete all stored tools after confirmation or with --force.")
@click.option("--force", "-f", is_flag=True, help="Force drop without confirmation or backup.")
def drop(force: bool) -> None:
    """Drop all tools from the database after confirmation or force."""
    console = ui.make_console()
    tools = load_tools()

    if not tools:
        console.print("[bold yellow]No tools to drop.[/bold yellow]")
        return

    backup_created: bool | str = "skipped"

    if force:
        save_tools([])
        backup_created = False
        console.print("[bold red]All tools dropped successfully (forced).[/bold red]")
    else:
        click.secho(DROP_WARNING, fg="red", bold=True)
        if not click.confirm("Are you sure you want to continue?", default=False):
            console.print("[bold green]Drop cancelled.[/bold green]")
            return

        if click.confirm("Do you want to back up your tools before dropping them?", default=True):
            try:
                path = write_backup(tools)
            except OSError as exc:
                console.print(f"[bold red]Backup failed:[/bold red] {escape(str(exc))}")
                if not click.confirm("Drop all tools WITHOUT a backup?", default=False):
                    console.print("[bold green]Drop cancelled.[/bold green]")
                    return
                backup_created = False
            else:
                console.print(f"[bold cyan]Backup saved to:[/bold cyan] {escape(str(path))}")
                backup_created = True

        save_tools([])
        console.print("[bold red]All tools dropped successfully.[/bold red]")

    _log_drop(console, total=len(tools), forced=force, backup_created=backup_created)


# ========= logs ========= #

@click.command(help="View drop history logs or clear them.")
@click.option("--clear", is_flag=True, help="Clear all drop logs.")
def logs(clear: bool) -> None:
    """Show or clear logged drop events."""
    console = ui.make_console()
    log_path = drops_log_file()

    if clear:
        if not log_path.exists():
            console.print("[bold yellow]No log file found to clear.[/bold yellow]")
            return
        try:
            save_drop_log([])
        except OSError as exc:
            console.print(f"[bold red]Failed to clear logs:[/bold red] {escape(str(exc))}")
        else:
            console.print("[bold red]All drop logs cleared.[/bold red]")
        return

    if not log_path.exists():
        console.print("[bold yellow]No drop logs found.[/bold yellow]")
        return

    try:
        events = load_drop_log()
        if not isinstance(events, list):
            raise ValueError("log file does not contain a list")
        events = [event for event in events if isinstance(event, dict)]
    except (OSError, ValueError) as exc:
        console.print(f"[bold red]Error reading log file:[/bold red] {escape(str(exc))}")
        return

    if not events:
        console.print("[bold yellow]Drop log is empty.[/bold yellow]")
        return

    table = Table(title="🧾 Drop History Log", show_lines=True)
    table.add_column("ID", style="bold cyan", justify="right")
    table.add_column("Timestamp", style="green")
    table.add_column("Dropped", style="magenta", justify="center")
    table.add_column("Forced", style="red", justify="center")
    table.add_column("Backup", style="blue", justify="center")

    for index, event in enumerate(events, start=1):
        table.add_row(
            str(index),
            str(event.get("timestamp", "N/A")).split(".")[0],
            f"{event.get('total_dropped', 0)} tools",
            str(event.get("forced", False)),
            str(event.get("backup_created", "skipped")).capitalize(),
        )
    console.print(table)

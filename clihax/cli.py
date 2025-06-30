# cli.py

VERSION = "1.0"
TOOL_NAME = "CliHax"

# ========= Imports ========= #
import click
import pyperclip
import textwrap
import re
import os
import json
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.text import Text
from rich.panel import Panel
from clihax.utils.helpers import load_tools, save_tools, update_meta, load_meta

#========== Banner =============#

def show_banner():
    ascii_banner = """\

 ██████╗██╗     ██╗██╗  ██╗ █████╗ ██╗  ██╗
██╔════╝██║     ██║██║  ██║██╔══██╗╚██╗██╔╝
██║     ██║     ██║███████║███████║ ╚███╔╝ 
██║     ██║     ██║██╔══██║██╔══██║ ██╔██╗ 
╚██████╗███████╗██║██║  ██║██║  ██║██╔╝ ██╗
 ╚═════╝╚══════╝╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝
"""

    console = Console()
    banner_text = Text(ascii_banner, style="bold cyan")
    panel = Panel(banner_text, expand=False, border_style="cyan", padding=(0, 2))
    console.print(panel)


# ========= Main CLI Group ========= #

@click.group(
    invoke_without_command=True,
    help="CliHax - A command reference manager for hackers and pentesters.",
    context_settings=dict(help_option_names=["--help"]),
    epilog="""
Common Flags:

    -q, --quick
        → Minimal/plain output

    -C, --copy
        → Copy command to clipboard

    -v, --version
        → Show current version


Usage Examples:

    # List tools
        clihax list 
        clihax list --quick

    # Add, show, edit, delete     
        clihax add     
        clihax show 1 --copy
        clihax edit 2     
        clihax delete 3

    # Search tools
        clihax search "ftp,nmap"
        clihax search "reverse shell" --quick
        clihax search "brute-force" --copy 1

    # Filter tools     
        clihax searchfilter -t smb
        clihax searchfilter -c post     
        clihax searchfilter -c attack -t brute-force "ftp,nmap"
        clihax searchfilter -t recon --copy 1     
        clihax searchfilter -c post -t meterpreter "reverse,shell" --quick

    # Import/export     
        clihax import tools.json     
        clihax export output.json

    # Tool info     
        clihax info
        clihax info --quick
"""
)
@click.version_option(
    VERSION,
    "--version",
    "-v",
    prog_name=TOOL_NAME,
    message="%(prog)s v%(version)s"
)
@click.pass_context
def cli(ctx):
    """
    CliHax - Manage and search hacking tool syntax with ease.
    """
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())



# ========= list ========= #

@cli.command(name="list", help="List all tools with optional quick mode and full detail mode.")
@click.option('--quick', '-q', is_flag=True, help="Minimal/plain output without rich tables.")
@click.option('--all', '-a', 'show_all', is_flag=True, help="Show full details including description, timestamps.")
def list_tools(quick, show_all):
    tools = load_tools()
    if not tools:
        click.secho("\u274C No tools found in database.", fg="red")
        return

    console = Console()

    if quick:
        for idx, tool in enumerate(tools, start=1):  # Start index from 1
            tool_name = tool.get("tool", "N/A")
            command = tool.get("command", "N/A")
            category = tool.get("category", "—")
            tags = ", ".join(tool.get("tags", [])) if isinstance(tool.get("tags", []), list) else ""

            if show_all:
                description = tool.get("description", "")
                created = tool.get("created_at", "")
                updated = tool.get("updated_at", "")
                output = f"""
[{idx}] {tool_name}
  Command    : {command}
  Desc       : {description}
  Category   : {category}
  Tags       : {tags}
  Created At : {created}
  Updated At : {updated}
"""
            else:
                output = f"[{idx}] {tool_name}: {command} ({category})  # {tags}"
            print(output.strip())
        return

    # Rich table output
    if show_all:
        console.print("[bold yellow]💡 Tip:[/] For best readability, use full-screen terminal or scroll with [green]Shift+PageUp/PageDown[/] or pipe to [blue]less -R[/].\n")
        
        table = Table(title="CliHax Full Tool List", show_lines=True)
        table.add_column("Index", justify="center", style="bold cyan")
        table.add_column("Tool", style="magenta", overflow="fold")
        table.add_column("Command", style="green", overflow="fold")
        table.add_column("Description", style="white", overflow="fold")
        table.add_column("Category", style="blue", overflow="fold")
        table.add_column("Tags", style="yellow", overflow="fold")
        table.add_column("Created At", style="dim")
        table.add_column("Updated At", style="dim")

        for idx, tool in enumerate(tools, start=1):  # Start index from 1
            table.add_row(
                str(idx),
                tool.get("tool", "N/A"),
                tool.get("command", "N/A"),
                tool.get("description", ""),
                tool.get("category", "—"),
                ", ".join(tool.get("tags", [])) if isinstance(tool.get("tags", []), list) else "",
                tool.get("created_at", ""),
                tool.get("updated_at", "")
            )
    else:
        table = Table(title="CliHax Tool List", show_lines=True)
        table.add_column("Index", justify="center", style="bold cyan")
        table.add_column("Tool", style="magenta", overflow="fold")
        table.add_column("Command", style="green", overflow="fold")
        table.add_column("Category", style="blue", overflow="fold")
        table.add_column("Tags", style="yellow", overflow="fold")

        for idx, tool in enumerate(tools, start=1):  # Start index from 1
            table.add_row(
                str(idx),
                tool.get("tool", "N/A"),
                tool.get("command", "N/A"),
                tool.get("category", "—"),
                ", ".join(tool.get("tags", [])) if isinstance(tool.get("tags", []), list) else ""
            )

    with console.pager():
        console.print(table)


# ========= add ========= #

@cli.command(help="Add a new tool/command.")
def add():
    tool = click.prompt("Enter tool name")
    command = click.prompt("Enter command")
    description = click.prompt("Enter description")
    category = click.prompt("Category (e.g., recon, scan, attack, post)")
    tags = [tag.strip() for tag in click.prompt("Tags (comma-separated)").split(",")]

    now = datetime.now().isoformat(timespec='seconds')

    tools = load_tools()
    tools.append({
        "tool": tool,
        "command": command,
        "description": description,
        "tags": tags,
        "category": category,
        "created_at": now,
        "updated_at": now
    })
    save_tools(tools)

    click.secho(f"\u2705 Added '{tool}' command successfully!", fg="green")


# ========= delete ========= #

@cli.command(help="Delete a tool by its index")
@click.argument("index", type=int)
def delete(index):
    tools = load_tools()
    index -= 1  # Convert to 0-based index

    if index < 0 or index >= len(tools):
        click.secho("❌ Invalid index. Use 'list' to see available entries (starting from 1).", fg="red")
        return

    removed = tools.pop(index)
    save_tools(tools)

    click.secho(f"🗑️ Deleted entry [{index + 1}] ({removed['tool']}) successfully.", fg="yellow")


# ========= edit ========= #

@cli.command(help="Edit a tool by its index (1-based).")
@click.argument("index", type=int)
def edit(index):
    tools = load_tools()
    index -= 1  # Convert to 0-based index

    if index < 0 or index >= len(tools):
        click.secho("❌ Invalid index. Use 'list' to see valid entries (starting from 1).", fg="red")
        return

    t = tools[index]
    click.secho(f"✏️ Editing tool [{index + 1}] - {t['tool']}", fg="cyan")

    updated = {
        "tool": click.prompt("Tool name", default=t["tool"]),
        "command": click.prompt("Command", default=t["command"]),
        "description": click.prompt("Description", default=t["description"]),
        "tags": [tag.strip() for tag in click.prompt("Tags (comma-separated)", default=", ".join(t["tags"])).split(",")],
        "category": click.prompt("Category", default=t["category"]),
        "created_at": t.get("created_at", datetime.now().isoformat(timespec='seconds')),
        "updated_at": datetime.now().isoformat(timespec='seconds')
    }

    tools[index] = updated
    save_tools(tools)

    click.secho(f"✅ Tool at index [{index + 1}] updated successfully!", fg="green")


# ========= show ========= #

@cli.command(help="Show detailed info of a tool by index (1-based).")
@click.argument("index", type=int)
@click.option('--copy', '-c', is_flag=True, help="Copy the command to clipboard")
def show(index, copy):
    tools = load_tools()
    index -= 1  # Convert to 0-based index

    if index < 0 or index >= len(tools):
        click.secho("❌ Invalid index. Use 'list' to see available entries (starting from 1).", fg="red")
        return

    tool = tools[index]
    if copy:
        pyperclip.copy(tool["command"])
        click.secho(f"📋 Copied command from '{tool['tool']}' to clipboard!", fg="green")
        return

    table = Table(title=f"Details for Tool [{index + 1}]: {tool['tool']}")
    table.add_column("Field", style="cyan", no_wrap=True)
    table.add_column("Value", style="white")
    for k in ["tool", "command", "description", "category"]:
        table.add_row(k.capitalize(), tool.get(k, "N/A"))
    table.add_row("Tags", ", ".join(tool.get("tags", [])) or "None")
    table.add_row("Created At", tool.get("created_at", "N/A"))
    table.add_row("Last Updated", tool.get("updated_at", "N/A"))
    Console().print(table)



# ========= search ========= #

@cli.command(
    help="Search tools using keyword(s). Matches tool name, command, description, and tags."
)
@click.argument("keywords", required=True)
@click.option('--quick', '-q', is_flag=True, help="Minimal output (no table formatting)")
@click.option('--copy', '-C', default=None, type=int, help="Copy command at specified displayed index (1-based)")
def search(keywords, quick, copy):
    tools = load_tools()
    kw_list = [kw.strip().lower() for kw in keywords.split(",") if kw.strip()]
    matched = []

    for idx, tool in enumerate(tools):
        searchable = f"{tool.get('tool', '')} {tool.get('command', '')} {tool.get('description', '')}".lower()
        tags = [t.lower() for t in tool.get("tags", [])]
        if any(kw in searchable or kw in tags for kw in kw_list):
            matched.append((idx, tool))

    if not matched:
        click.secho("❌ No matches found.", fg="red")
        return

    if copy is not None:
        one_based = copy - 1
        if 0 <= one_based < len(matched):
            pyperclip.copy(matched[one_based][1]["command"])
            click.secho(f"📋 Copied command from result [{copy}] ({matched[one_based][1]['tool']})", fg="green")
        else:
            click.secho(f"❌ Invalid index: {copy}. Use a number between 1 and {len(matched)}.", fg="red")
        return

    console = Console(force_terminal=True)

    if quick:
        for i, (orig_idx, t) in enumerate(matched, start=1):  # Displayed index starts from 1
            line = Text()
            line.append(f"[{i}] ", style="bold cyan")
            line.append(f"{t['tool']}: ", style="bold magenta")
            line.append(t['command'], style="green")
            if t.get('description'):
                line.append(f"  # {t['description']}", style="dim")
            for kw in kw_list:
                line.highlight_words([kw], style="bold yellow")
            console.print(line)
        return

    # Full table output
    table = Table(title=f"Search Results (keywords: {', '.join(kw_list)})", show_lines=True)
    table.add_column("Index", justify="center", style="bold cyan")
    table.add_column("Tool", style="magenta")
    table.add_column("Command", style="green")
    table.add_column("Tags", style="blue")

    for i, (_, t) in enumerate(matched, start=1):  # Displayed index starts from 1
        tool_text = Text(t["tool"])
        command_text = Text(t["command"])
        tags_text = Text(", ".join(t.get("tags", [])))

        for kw in kw_list:
            tool_text.highlight_words([kw], style="bold yellow")
            command_text.highlight_words([kw], style="bold yellow")
            tags_text.highlight_words([kw], style="bold yellow")

        table.add_row(str(i), tool_text, command_text, tags_text)

    console.print(table)



# ========= searchfilter ========= #

@cli.command(help="Advanced filter by tag (-t), category (-c), and/or keywords.")
@click.option('--tag', '-t', help="Filter by tag (e.g., recon, smb, brute-force)")
@click.option('--category', '-c', help="Filter by category (e.g., recon, attack, post)")
@click.argument('keywords', required=False)
@click.option('--quick', '-q', is_flag=True, help="Minimal output")
@click.option('--copy', '-C', default=None, type=int, help="Copy command at specified displayed index (1-based)")
def searchfilter(tag, category, keywords, quick, copy):
    """Filter tools by tag, category, and/or keyword(s) (comma-separated)."""
    tools = load_tools()
    tag = tag.lower() if tag else None
    category = category.lower() if category else None
    kw_list = [kw.strip().lower() for kw in keywords.split(",")] if keywords else []

    highlight_terms = kw_list.copy()
    if tag:
        highlight_terms.append(tag)
    if category:
        highlight_terms.append(category)

    matched = []
    for idx, tool in enumerate(tools):
        tags = [t.lower() for t in tool.get("tags", [])]
        searchable = f"{tool.get('tool', '')} {tool.get('command', '')} {tool.get('description', '')}".lower()

        if tag and tag not in tags:
            continue
        if category and tool.get("category", "").lower() != category:
            continue
        if kw_list and not any(kw in searchable or kw in tags for kw in kw_list):
            continue

        matched.append(tool)

    if not matched:
        click.secho("❌ No matches found.", fg="red")
        return

    if copy is not None:
        one_based = copy - 1
        if 0 <= one_based < len(matched):
            pyperclip.copy(matched[one_based]["command"])
            click.secho(f"📋 Copied command from result [{copy}] ({matched[one_based]['tool']})", fg="green")
        else:
            click.secho(f"❌ Invalid index: {copy}. Use a number between 1 and {len(matched)}.", fg="red")
        return

    console = Console(force_terminal=True)

    if quick:
        for i, t in enumerate(matched, start=1):
            line = Text(f"[{i}] {t['tool']}: {t['command']}  # {t.get('description', '')}")
            for term in set(highlight_terms):
                if term:
                    line.highlight_regex(rf"(?i){re.escape(term)}", style="bold yellow")
            console.print(line)
        return

    filter_title = "Filtered Results"
    if category:
        filter_title += f" | Category: {category}"
    if tag:
        filter_title += f" | Tag: {tag}"
    if kw_list:
        filter_title += f" | Keywords: {', '.join(kw_list)}"

    table = Table(title=filter_title, show_lines=True)
    table.add_column("Index", justify="center", style="bold cyan")
    table.add_column("Tool", style="magenta")
    table.add_column("Command", style="green")
    table.add_column("Tags", style="blue")

    for i, t in enumerate(matched, start=1):
        tool_text = Text(t["tool"])
        cmd_text = Text(t["command"])
        tags_text = Text(", ".join(t.get("tags", [])))

        for term in set(highlight_terms):
            if term:
                pattern = rf"(?i){re.escape(term)}"
                tool_text.highlight_regex(pattern, style="bold yellow")
                cmd_text.highlight_regex(pattern, style="bold yellow")
                tags_text.highlight_regex(pattern, style="bold yellow")

        table.add_row(str(i), tool_text, cmd_text, tags_text)

    console.print(table)


# ========= Info ============== #

@cli.command(help="Show general information about the tool.")
@click.option('--quick', '-q', is_flag=True,
              help="Minimal/plain output (no banner or rich formatting).")
def info(quick):
    tools = load_tools()
    meta  = load_meta()

    total_tools = len(tools)
    last_edit = max(
        (
            t.get("updated_at") or t.get("created_at")
            for t in tools
            if t.get("updated_at") or t.get("created_at")
        ),
        default="N/A"
    )

    if quick:
        # --- Plain-text / quick mode ---
        print(f"🧰 CliHax v{VERSION}")
        print("A lightweight CLI reference manager for pentesters.")
        print()
        print(f"Total tools   : {total_tools}")
        print(f"Last edit     : {last_edit}")
        print(f"Last import   : {meta.get('last_import', 'N/A')}")
        print(f"Last export   : {meta.get('last_export', 'N/A')}")
        return

    # --- Rich / full mode ---
    console = Console()
    console.print("")
    show_banner()
    console.print("\n[bold green]🧰 CliHax v1.0[/]")
    console.print("A lightweight CLI reference manager for pentesters to store and retrieve common tool commands with ease.\n")

    console.print("[bold cyan]📦 CliHax Tool Info[/]")
    console.print(f"🔢 Total Tools Stored     : [green]{total_tools}[/]")
    console.print(f"🧑 Author                 : [magenta]LordSec[/]")
    console.print(f"🕓 Last Edit              : [yellow]{last_edit}[/]")
    console.print(f"📥 Last Import            : [blue]{meta.get('last_import', 'N/A')}[/]")
    console.print(f"📤 Last Export            : [blue]{meta.get('last_export', 'N/A')}[/]")


# ========= Import ============== #

@cli.command(name="import", help="Import tools from a JSON file (merged with existing tools).")
@click.argument("filename")
def import_tools(filename):
    """Import tools from a JSON file and merge with existing entries."""
    from builtins import list as list_type
    from datetime import datetime
    console = Console()

    if not os.path.exists(filename):
        console.print(f"[red]❌ File not found:[/] {filename}")
        return

    try:
        with open(filename, "r") as f:
            imported = json.load(f)
        if not isinstance(imported, list_type):
            raise ValueError("Invalid format: expected a list of tool dictionaries.")
    except Exception as e:
        console.print(f"[red]❌ Failed to read or parse JSON:[/] {e}")
        return

    existing = load_tools()
    existing_set = {(t["tool"], t["command"]) for t in existing}
    new_tools = [t for t in imported if (t["tool"], t["command"]) not in existing_set]

    if not new_tools:
        console.print("[yellow]⚠️ No new tools to import. All entries are duplicates.[/]")
        return

    existing.extend(new_tools)
    save_tools(existing)

    # ✅ Write last_import timestamp to meta.json
    update_meta("import")

    console.print(f"[green]✅ Imported {len(new_tools)} new tools from '{filename}' (merged).[/]")
    if len(new_tools) < len(imported):
        console.print(f"[yellow]⚠️ {len(imported) - len(new_tools)} duplicate entries were skipped.[/]")

# ========= Export ===========#

@cli.command(name="export", help="Export all tools to a JSON file.")
@click.argument("filename", required=False, default="exported_tools.json")
def export_tools(filename):
    """Export tools to a JSON file."""
    console = Console()
    tools = load_tools()

    if not tools:
        console.print("[red]❌ No tools to export.[/]")
        return

    # ✅ Deduplicate based on (tool, command)
    seen = set()
    unique_tools = []
    for t in tools:
        key = (t.get("tool"), t.get("command"))
        if key not in seen:
            seen.add(key)
            unique_tools.append(t)

    try:
        with open(filename, "w") as f:
            json.dump(unique_tools, f, indent=2)

        console.print(
            f"[green]✅ Exported {len(unique_tools)} of {len(tools)} tools to:[/] [cyan]{filename}[/]"
        )

        if len(unique_tools) < len(tools):
            console.print(
                f"[yellow]⚠️  Skipped {len(tools) - len(unique_tools)} duplicate entries based on (tool, command)[/]"
            )

        update_meta("export")
    except Exception as e:
        console.print(f"[red]❌ Failed to export tools:[/] {e}")

# ========= Drop ========= #

@cli.command(help="Delete all stored tools after confirmation or with --force.")
@click.option('--force', '-f', is_flag=True, help="Force drop without confirmation or backup.")
def drop(force):
    """Drop all tools from the database after confirmation or force."""
    from rich.console import Console
    from rich.text import Text
    import os
    import json
    from datetime import datetime

    console = Console()
    tools = load_tools()

    if not tools:
        console.print("[bold yellow]No tools to drop.[/bold yellow]")
        return

    backup_created = "skipped"

    # ======= Forced Drop (no prompt, no backup) ======= #
    if force:
        save_tools([])
        update_meta({"tools_count": 0})
        backup_created = False
        console.print("[bold red]All tools dropped successfully (forced).[/bold red]")
    else:
        # ======= Interactive Drop ======= #
        warning_text = Text("""
⚠️  WARNING: You are about to delete ALL stored tools permanently.
This action CANNOT be undone.

Are you sure you want to continue? (y/n): 
""", style="bold red")

        response = input(warning_text.plain).strip().lower()
        if response not in ['y', 'yes']:
            console.print("[bold green]Drop cancelled.[/bold green]")
            return

        # Ask for auto-backup
        backup_response = input("Do you want to back up your tools before dropping them? (y/n): ").strip().lower()
        if backup_response in ['y', 'yes']:
            timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
            backup_dir = "backups"
            os.makedirs(backup_dir, exist_ok=True)
            backup_path = os.path.join(backup_dir, f"tools_backup_{timestamp}.json")

            try:
                with open(backup_path, "w") as f:
                    json.dump(tools, f, indent=2)
                console.print(f"[bold cyan]Backup saved to:[/bold cyan] {backup_path}")
                backup_created = True
            except Exception as e:
                console.print(f"[bold red]Backup failed:[/bold red] {e}")
                console.print("[bold yellow]Proceeding with drop anyway...[/bold yellow]")
                backup_created = False

        # Proceed with drop
        save_tools([])
        update_meta({"tools_count": 0})
        console.print("[bold red]All tools dropped successfully.[/bold red]")

    # ======= Logging Drop Event ======= #
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "total_dropped": len(tools),
        "forced": force,
        "backup_created": backup_created
    }

    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, "drops.json")

    try:
        if os.path.exists(log_path):
            with open(log_path, "r") as f:
                log_data = json.load(f)
        else:
            log_data = []

        log_data.append(log_entry)

        with open(log_path, "w") as f:
            json.dump(log_data, f, indent=2)

        console.print("[bold green]Drop event logged successfully.[/bold green]")
    except Exception as e:
        console.print(f"[bold red]Failed to log drop event:[/bold red] {e}")

# ======== Logs ========#

@cli.command(help="View drop history logs or clear them.")
@click.option('--clear', is_flag=True, help="Clear all drop logs.")
def logs(clear):
    """Show or clear logged drop events."""
    from rich.console import Console
    from rich.table import Table
    import os
    import json

    console = Console()
    log_path = "logs/drops.json"

    if clear:
        # ===== Clear logs =====
        if os.path.exists(log_path):
            try:
                with open(log_path, "w") as f:
                    json.dump([], f, indent=2)
                console.print("[bold red]All drop logs cleared.[/bold red]")
            except Exception as e:
                console.print(f"[bold red]Failed to clear logs:[/bold red] {e}")
        else:
            console.print("[bold yellow]No log file found to clear.[/bold yellow]")
        return

    # ===== View logs =====
    if not os.path.exists(log_path):
        console.print("[bold yellow]No drop logs found.[/bold yellow]")
        return

    try:
        with open(log_path, "r") as f:
            log_data = json.load(f)

        if not log_data:
            console.print("[bold yellow]Drop log is empty.[/bold yellow]")
            return

        table = Table(title="🧾 Drop History Log", show_lines=True)
        table.add_column("ID", style="bold cyan", justify="right")
        table.add_column("Timestamp", style="green")
        table.add_column("Dropped", style="magenta", justify="center")
        table.add_column("Forced", style="red", justify="center")
        table.add_column("Backup", style="blue", justify="center")

        for idx, entry in enumerate(log_data, start=1):
            table.add_row(
                str(idx),
                entry.get("timestamp", "N/A").split(".")[0],
                f"{entry.get('total_dropped', 0)} tools",
                str(entry.get("forced", False)),
                str(entry.get("backup_created", "skipped")).capitalize()
            )

        console.print(table)

    except Exception as e:
        console.print(f"[bold red]Error reading log file:[/bold red] {e}")


# ========= Entry Point ========= #

if __name__ == "__main__":
    cli()

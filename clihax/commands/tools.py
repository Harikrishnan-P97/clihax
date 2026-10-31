"""Commands that manage individual tool entries: list, add, edit, delete, show."""

import click

from clihax import ui
from clihax.commands.completion import complete_index
from clihax.utils.helpers import load_tools, now_iso, save_tools


def _parse_tags(raw: str) -> list[str]:
    """Turn 'a, b,,c' into ['a', 'b', 'c'] (empty input gives [])."""
    return [tag.strip() for tag in raw.split(",") if tag.strip()]


INVALID_INDEX = "Invalid index. Use 'list' to see available entries (starting from 1)."


def _resolve_index(tools: list, index: int, *, strict: bool = False) -> int | None:
    """Convert a 1-based index typed by the user into a list position.

    When the index is out of range, prints an error and returns None, or
    (``strict``) exits with status 1 so scripts can detect the failure.
    """
    if 1 <= index <= len(tools):
        return index - 1
    if strict:
        raise click.ClickException(INVALID_INDEX)
    ui.error(INVALID_INDEX)
    return None


# ========= list ========= #

@click.command(name="list", help="List all tools with optional quick mode and full detail mode.")
@click.option("--quick", "-q", is_flag=True, help="Minimal/plain output without rich tables.")
@click.option("--all", "-a", "show_all", is_flag=True, help="Show full details including description, timestamps.")
@click.option("--pager", "-p", is_flag=True, help="Show the table in a scrollable pager (press q to quit).")
@click.option("--json", "as_json", is_flag=True, help="Print all tools as JSON (for scripts).")
def list_tools(quick: bool, show_all: bool, pager: bool, as_json: bool) -> None:
    if as_json:
        ui.reject_json_conflicts({"--quick": quick, "--pager": pager})
        ui.print_json([ui.tool_json(i, tool) for i, tool in enumerate(load_tools(), start=1)])
        return

    tools = load_tools()
    if not tools:
        ui.error("No tools found in database.")
        return

    if quick:
        render = ui.quick_detail if show_all else ui.quick_line
        for index, tool in enumerate(tools, start=1):
            click.echo(render(index, tool))
        return

    console = ui.make_console()
    if show_all:
        console.print(
            "[bold yellow]💡 Tip:[/] For best readability, use full-screen terminal or scroll with "
            "[green]Shift+PageUp/PageDown[/] or pipe to [blue]less -R[/].\n"
        )
    table = ui.build_tools_table(tools, full=show_all)

    if pager:
        with console.pager():
            console.print(table)
    else:
        console.print(table)


# ========= add ========= #

@click.command(help="Add a new tool/command.")
def add() -> None:
    tool = click.prompt("Enter tool name")
    command = click.prompt("Enter command")
    description = click.prompt("Enter description")
    category = click.prompt("Category (e.g., recon, scan, attack, post)")
    tags = _parse_tags(click.prompt("Tags (comma-separated, optional)", default="", show_default=False))

    now = now_iso()
    tools = load_tools()
    tools.append(
        {
            "tool": tool,
            "command": command,
            "description": description,
            "tags": tags,
            "category": category,
            "created_at": now,
            "updated_at": now,
        }
    )
    save_tools(tools)

    ui.success(f"Added '{tool}' command successfully!")


# ========= edit ========= #

@click.command(help="Edit a tool by its index (1-based).")
@click.argument("index", type=int, shell_complete=complete_index)
def edit(index: int) -> None:
    tools = load_tools()
    position = _resolve_index(tools, index)
    if position is None:
        return

    current = tools[position]
    click.secho(f"✏️ Editing tool [{index}] - {current.get('tool', '')}", fg="cyan")

    tools[position] = {
        "tool": click.prompt("Tool name", default=current.get("tool", "")),
        "command": click.prompt("Command", default=current.get("command", "")),
        "description": click.prompt("Description", default=current.get("description", "")),
        "tags": _parse_tags(click.prompt("Tags (comma-separated)", default=ui.format_tags(current))),
        "category": click.prompt("Category", default=current.get("category", "")),
        "created_at": current.get("created_at") or now_iso(),
        "updated_at": now_iso(),
    }
    save_tools(tools)

    ui.success(f"Tool at index [{index}] updated successfully!")


# ========= delete ========= #

@click.command(help="Delete a tool by its index")
@click.argument("index", type=int, shell_complete=complete_index)
def delete(index: int) -> None:
    tools = load_tools()
    position = _resolve_index(tools, index)
    if position is None:
        return

    removed = tools.pop(position)
    save_tools(tools)

    click.secho(f"🗑️ Deleted entry [{index}] ({removed.get('tool', '?')}) successfully.", fg="yellow")


# ========= show ========= #

@click.command(help="Show detailed info of a tool by index (1-based).")
@click.argument("index", type=int, shell_complete=complete_index)
@click.option("--copy", "-C", is_flag=True, help="Copy the command to clipboard")
@click.option("--json", "as_json", is_flag=True, help="Print the tool as JSON (for scripts).")
def show(index: int, copy: bool, as_json: bool) -> None:
    if as_json:
        ui.reject_json_conflicts({"--copy": copy})
    tools = load_tools()
    position = _resolve_index(tools, index, strict=as_json)
    if position is None:
        return

    tool = tools[position]
    if as_json:
        ui.print_json(ui.tool_json(index, tool))
        return
    if copy and ui.copy_to_clipboard(tool.get("command", "")):
        click.secho(f"📋 Copied command from '{tool.get('tool', '')}' to clipboard!", fg="green")

    ui.make_console().print(ui.build_detail_table(index, tool))

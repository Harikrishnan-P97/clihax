"""Shell completion: the `completion` command and the dynamic completers.

Click already completes command and option names. The helpers here also
complete values that live in your database (tags, categories, tool numbers).
They run while you press Tab, so they must never fail or print anything.
"""

import click
from click.shell_completion import CompletionItem, get_completion_class

from clihax.utils.helpers import load_tools
from clihax.utils.stats import toolbox_stats

SHELLS = ("bash", "zsh", "fish")
COMPLETE_VAR = "_CLIHAX_COMPLETE"


def _tools() -> list:
    try:
        return [tool for tool in load_tools() if isinstance(tool, dict)]
    except Exception:  # completion must stay silent whatever is wrong
        return []


def complete_categories(ctx: click.Context, param: click.Parameter, incomplete: str) -> list[CompletionItem]:
    names = [name for name, _count in toolbox_stats(_tools()).categories]
    return [CompletionItem(name) for name in names if name.startswith(incomplete.lower())]


def complete_tags(ctx: click.Context, param: click.Parameter, incomplete: str) -> list[CompletionItem]:
    tags: set[str] = set()
    for tool in _tools():
        raw = tool.get("tags", [])
        if isinstance(raw, list):
            tags.update(str(tag).strip().lower() for tag in raw if str(tag).strip())
    return [CompletionItem(tag) for tag in sorted(tags) if tag.startswith(incomplete.lower())]


def complete_index(ctx: click.Context, param: click.Parameter, incomplete: str) -> list[CompletionItem]:
    """Tool numbers, with the tool name as the hint (shown by zsh and fish)."""
    items = []
    for number, tool in enumerate(_tools(), start=1):
        if str(number).startswith(incomplete):
            items.append(CompletionItem(str(number), help=str(tool.get("tool", ""))))
    return items


@click.command(help="Print the Tab-completion script for your shell (bash, zsh or fish).")
@click.argument("shell", type=click.Choice(SHELLS))
def completion(shell: str) -> None:
    from clihax.cli import cli  # imported here: cli.py imports this module

    completer = get_completion_class(shell)(cli, {}, "clihax", COMPLETE_VAR)
    click.echo(completer.source())

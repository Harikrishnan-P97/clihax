"""CliHax command-line entry point.

This module only defines the top-level command group; the commands
themselves live in the ``clihax.commands`` package.
"""

import click

from clihax import __version__
from clihax.commands import data, info, search, tools
from clihax.utils.helpers import get_data_dir, migrate_legacy_data

TOOL_NAME = "CliHax"

EPILOG = """
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


@click.group(
    invoke_without_command=True,
    help="CliHax - A command reference manager for hackers and pentesters.",
    context_settings={"help_option_names": ["--help"]},
    epilog=EPILOG,
)
@click.version_option(
    __version__,
    "--version",
    "-v",
    prog_name=TOOL_NAME,
    message="%(prog)s v%(version)s",
)
@click.pass_context
def cli(ctx: click.Context) -> None:
    """CliHax - Manage and search hacking tool syntax with ease."""
    migrated = migrate_legacy_data()
    if migrated:
        click.secho(
            f"ℹ️  Migrated {len(migrated)} file(s) from ./data to {get_data_dir()}",
            fg="cyan",
            err=True,
        )
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


for command in (
    tools.list_tools,
    tools.add,
    tools.edit,
    tools.delete,
    tools.show,
    search.search,
    search.searchfilter,
    info.info,
    data.import_tools,
    data.export_tools,
    data.drop,
    data.logs,
):
    cli.add_command(command)

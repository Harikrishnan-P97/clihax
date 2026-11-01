"""Regenerate the README screenshots (assets/*.svg) from real CliHax output.

Run from the project folder:

    poetry run python scripts/make_screenshots.py

It uses a throw-away data folder, so your own tools are never touched.
"""

import os
import re
import tempfile
from pathlib import Path

ASSETS = Path(__file__).resolve().parent.parent / "assets"

# (file name, window title, command-line arguments, terminal width)
SHOTS = [
    ("info.svg", "clihax info", ["info"], 78),
    ("search.svg", 'clihax search "ssh,smb"', ["search", "ssh,smb"], 100),
]


def main() -> None:
    from click.testing import CliRunner
    from rich.console import Console

    with tempfile.TemporaryDirectory() as scratch:
        os.environ["CLIHAX_HOME"] = str(Path(scratch) / "home")
        os.chdir(scratch)

        import clihax.commands.info as info_module
        from clihax import ui
        from clihax.cli import cli
        from clihax.utils import helpers

        current: dict[str, Console] = {}
        ui.make_console = lambda: current["console"]
        # Fixed values so the screenshots look the same on every machine.
        info_module.get_data_dir = lambda: Path("/home/you/.local/share/clihax")
        info_module.platform.python_version = lambda: "3.12.3"

        runner = CliRunner()
        current["console"] = Console(file=open(os.devnull, "w"))
        result = runner.invoke(cli, ["starter", "--yes"])
        assert result.exit_code == 0, result.output
        helpers.write_backup(helpers.load_tools())

        ASSETS.mkdir(exist_ok=True)
        for name, title, args, width in SHOTS:
            console = Console(
                record=True,
                force_terminal=True,
                width=width,
                color_system="truecolor",
                file=open(os.devnull, "w"),
            )
            current["console"] = console
            result = runner.invoke(cli, args)
            assert result.exit_code == 0, result.output
            svg = console.export_svg(title=title)
            # Drop the web font download so the image works offline and loads instantly.
            svg = re.sub(r"@font-face\s*\{.*?\}", "", svg, flags=re.S)
            (ASSETS / name).write_text(svg, encoding="utf-8")
            print(f"wrote assets/{name}")


if __name__ == "__main__":
    main()

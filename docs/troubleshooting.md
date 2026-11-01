# Troubleshooting

Solutions for the problems people most often meet when installing and using CliHax. If yours is not listed, please open an [issue](https://github.com/Harikrishnan-P97/clihax/issues).

## Installation

### `clihax: command not found`

After `pipx install`, the folder that pipx uses for commands may not be on your `PATH` yet:

```bash
pipx ensurepath
```

Then open a new terminal. If you installed from a source checkout, run the command through Poetry instead: `poetry run clihax`.

### `pipx: command not found`

On Debian and Ubuntu:

```bash
sudo apt install pipx
pipx ensurepath
```

On other systems follow the [pipx installation guide](https://pipx.pypa.io/stable/installation/).

### The Python version is too old

CliHax needs Python 3.10 or newer. Check with `python3 --version`. If your default Python is older, install a newer one and tell pipx to use it:

```bash
pipx install --python python3.12 git+https://github.com/Harikrishnan-P97/clihax.git
```

### Installing from source with Poetry

**`poetry: command not found`.** Add Poetry's folder to your `PATH` and make it permanent by adding the line to `~/.bashrc` or `~/.zshrc`:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

**A dependency fails to build.** This is rare, because the dependencies ship pre-built wheels, but on a minimal system you may need compiler tools:

```bash
sudo apt install build-essential python3-dev
```

**The install hangs at a `keyring` step.** Disable Poetry's keyring integration and try again; add `-vvv` for detailed logs:

```bash
poetry config keyring.enabled false
poetry install -vvv
```

**`ModuleNotFoundError: No module named 'clihax'`.** Run the command from the project folder through Poetry (`poetry run clihax --help`), or reinstall with `poetry install`.

## Using CliHax

### "Clipboard unavailable"

`--copy` needs a clipboard tool on Linux. Install `xclip` (X11) or `wl-clipboard` (Wayland):

```bash
sudo apt install xclip
```

### "Could not read ... tools.json"

CliHax names the file it could not read. The file is probably not valid JSON, for example after a manual edit. You can fix it in an editor, delete it to start fresh, or restore a backup.

### Restoring from a backup

`clihax drop` saves a backup first (see `clihax info` for the data folder). To restore one, move the broken database out of the way and import the backup:

```bash
cd ~/.local/share/clihax
ls backups/
mv tools.json tools.json.broken
clihax import backups/tools_backup_<timestamp>.json
```

### My tools are missing, or I see a different toolbox

CliHax keeps one toolbox per data folder. Run `clihax info` and check the **Data folder** line. A different folder is used when the `CLIHAX_HOME` environment variable is set, so check `echo $CLIHAX_HOME`. Data from version 1.0 (a `data/` folder next to where you ran it) is copied over automatically once, the first time you run `clihax` in that folder.

### A search finds nothing

- Several keywords are separated by commas: `clihax search "ftp,ssh"`. A phrase with a space is matched as a whole.
- `search` looks in the tool name, command and description, and matches tags exactly. Use `clihax list` to see what is stored.
- If nothing matches exactly, CliHax shows close matches for misspelled words and says so. Words shorter than three characters are never matched that way.

### `--json cannot be combined with --quick`

`--json` prints machine-readable output only, so it cannot be mixed with `--quick`, `--pager` or `--copy`. Use one or the other.

### Colour codes appear in a file or pipe

Colours are only used on a real terminal, so piped and redirected output is plain. If you still see escape codes, set `NO_COLOR=1` or use `clihax --no-color ...` (the option goes before the command).

### Tab completion does nothing

Check that the `eval "$(clihax completion bash)"` line (or the zsh/fish equivalent from the [README](../README.md#shell-completion)) is in your shell's startup file, then open a new terminal. Completion only works when `clihax` is on your `PATH`; with a source checkout, start a shell inside the project environment with `poetry run bash` first.

## Starting over

To remove all stored tools, use `clihax drop`. To remove everything CliHax has stored, including backups and logs, delete its data folder (for example `rm -rf ~/.local/share/clihax` on Linux) after uninstalling with `pipx uninstall clihax`.

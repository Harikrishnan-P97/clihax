# Contributing to CliHax

Thanks for helping! Bug reports, ideas and pull requests are all welcome.

## Set up

You need Python 3.10+ and [Poetry](https://python-poetry.org/).

```bash
git clone https://github.com/Harikrishnan-P97/clihax.git
cd clihax
poetry install
poetry run pytest -q
poetry run ruff check .
```

Both commands must pass before you open a pull request. CI runs them on Python 3.10 to 3.14.

Tests never touch your real toolbox: they use a temporary folder through the `CLIHAX_HOME` environment variable (see `tests/conftest.py`). Use the same variable when you try things by hand:

```bash
CLIHAX_HOME=/tmp/clihax-dev poetry run clihax starter --yes
```

## How the code is organised

| Where | What belongs there |
|-------|--------------------|
| `clihax/commands/` | One module per group of commands. A command decides **what** to show and does the work. |
| `clihax/ui.py` | Everything about **how** things look: tables, banner, colours, JSON output. |
| `clihax/utils/` | Storage, search and statistics. No printing, so it is easy to test. |
| `clihax/starter.py` | The built-in starter pack data. |
| `tests/` | One test module per area; shared helpers live in `conftest.py`. |

## Making a change

1. Create a branch from `main` (`git checkout -b feat/short-description`).
2. Keep the change small and focused. One idea per pull request.
3. Add or update tests. New behaviour needs a test, and a bug fix needs a test that fails without the fix.
4. Update `CHANGELOG.md` (under **Unreleased**) and the README or `docs/` if users will notice the change.
5. Run `poetry run pytest -q` and `poetry run ruff check .`.
6. Open a pull request and describe what changed and why.

### Things to keep in mind

- **Never lose user data.** Databases are written atomically, and anything destructive asks first and makes a backup.
- **Show stored text literally.** Commands such as `nmap -p [port] <target>` contain characters that rich would treat as markup. Wrap values with `ui.cell()` before putting them in a table.
- **Machine-readable output stays clean.** With `--json` only JSON goes to stdout. Hints and notices go to stderr (`ui.notice`).
- **Support Python 3.10.** Avoid syntax and library features that need a newer version.

### Adding a command

Create a function in the matching `clihax/commands/` module (or a new module), register it in `clihax/cli.py`, and add it to `ALL_COMMANDS` in `tests/test_commands.py`.

### Adding to the starter pack

Add an entry in `clihax/starter.py`. Each entry needs a tool name, a command, a short description, a category and tags. Use placeholders such as `<target>`, `<domain>`, `<lhost>` and `<lport>`. The tests check that every entry is valid and unique.

### Screenshots

The images in the README are generated from real output. After changing how a command looks, run:

```bash
poetry run python scripts/make_screenshots.py
```

## Reporting bugs and ideas

Open an [issue](https://github.com/Harikrishnan-P97/clihax/issues) and include the output of `clihax --version`, your operating system, and the steps to reproduce the problem. Please never paste real credentials or client data.

## Responsible use

CliHax only stores command text. Contributions must not turn it into an attack tool: no exploit code, payloads or target-specific data.

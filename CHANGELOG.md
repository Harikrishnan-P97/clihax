# 📓 Changelog

All notable changes to this project will be documented in this file.

This project adheres to [Semantic Versioning](https://semver.org/).

---

## [Unreleased]
### Changed
- The author is now shown as `Harikrishnan-P97` (matching GitHub) in `info` and `pyproject.toml`, which also gains project URLs; the deprecated licence classifier was removed
- Split the 750-line `cli.py` into small modules: `commands/` (tools, search, data, info), `ui.py` for presentation and `utils/search.py` for pure search logic. Behaviour is unchanged unless listed below
- `searchfilter --quick` now uses the same colours as `search --quick`; both highlight matches case-insensitively
- The same "Invalid index" wording is used by `show`, `edit` and `delete`
- `drop` now uses standard prompts, offers the backup by default (press Enter to accept) and, if the backup fails, asks before deleting without one (previously it deleted anyway)
- A corrupted `tools.json` now gives a one-line error pointing at the file instead of a traceback; an unreadable `meta.json` is ignored
- Narrower error handling and a message when the clipboard is unavailable

### Removed
- The empty git-sync stub and the unused `gitpython` and `prompt-toolkit` dependencies; the README no longer advertises git sync (use `export`/`import` or keep your own copy in Git)

### Fixed
- Stored commands containing text like `[port]` were silently altered in `list` and `show`, and `[/x]` crashed them; commands are now shown exactly as stored
- `searchfilter "ftp,"` (trailing comma) no longer matches every tool
- README project tree, install instructions and docs pointed at old file locations

### Added
- Redesigned `clihax info`: the banner is kept, followed by About (version, author, repository link, license, Python), Toolbox (tool, category and tag counts, data folder, database size, backups, drop log) and Activity (last edit/import/export with a relative time) panels; `info --quick` now also prints the author and repository
- `python -m clihax` entry point
- Tests for every command, the search logic, markup safety and storage (110 in total)
- Tools database, metadata, drop logs and backups now live in a per-user data directory (override with `CLIHAX_HOME`) instead of the current working directory, so `clihax` works from any folder
- Database writes are atomic (temp file + rename)

### Fixed
- `list` printed nothing visible because its table opened in a pager; it now prints directly (use `list --pager` for the scrolling view)
- `import` no longer crashes on malformed entries; invalid ones are skipped and counted, and missing fields get defaults
- `show --copy` now also displays the tool, and the copy flag is `-C` in every command
- Clipboard problems (e.g. xclip missing) show a clear message instead of a traceback
- `add` no longer stores an empty tag when tags are left blank
- `drop` no longer calls the metadata updater with an invalid argument
- Version is read from package metadata, so `--version`, `info` and `pyproject.toml` always agree

### Added
- Automatic one-time migration from the v1.0 `./data`, `./logs`, `./backups` layout
- `clihax info` shows the active data directory
- Unit tests for the storage layer

---

## [v1.0.0] - 2025-06-30
### Added
- Initial public release of CliHax 🎉
- Add, edit, delete tool commands
- Search tools by keyword or tag
- Tag tools by hacking phase (e.g., recon, exploit)
- Rich-styled CLI output using `rich`
- Clipboard copy support with `--copy`
- JSON-based persistent tool storage
- Import/export tool database
- `--quick` mode for silent use
- Drop command with auto-backup and action logs
- GitHub Actions workflow for build validation
- Documentation in `/docs` directory
- Project badges in `README.md`
- Initial release tag and GitHub release

---

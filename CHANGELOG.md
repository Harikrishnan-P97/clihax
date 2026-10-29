# 📓 Changelog

All notable changes to this project will be documented in this file.

This project adheres to [Semantic Versioning](https://semver.org/).

---

## [Unreleased]
### Changed
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

# ⚔️ CliHax

<p align="center">
  <img src="assets/clihax-bannerimage.png" alt="CliHax Banner" width="700"/>
</p>

> A command-line tool for hackers and pentesters to manage and recall tool syntax, flags, and notes — right from the terminal.

[![MIT License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![Status](https://img.shields.io/badge/status-active-brightgreen)](https://github.com/Harikrishnan-P97/clihax)
[![Last Commit](https://img.shields.io/github/last-commit/Harikrishnan-P97/clihax)](https://github.com/Harikrishnan-P97/clihax/commits)
[![Open Issues](https://img.shields.io/github/issues/Harikrishnan-P97/clihax)](https://github.com/Harikrishnan-P97/clihax/issues)
[![Stars](https://img.shields.io/github/stars/Harikrishnan-P97/clihax?style=social)](https://github.com/Harikrishnan-P97/clihax/stargazers)
[![Build Status](https://github.com/Harikrishnan-P97/clihax/actions/workflows/python.yml/badge.svg)](https://github.com/Harikrishnan-P97/clihax/actions)

---

## 📚 Overview

**CliHax** is a Python-based CLI utility designed for ethical hackers, red teamers, bug bounty hunters, and CTF players who want to **organize, search, and recall tool syntax and notes quickly**.

Instead of Googling commands every time, create your own searchable, shareable command reference from the terminal.

---

📒 [Changelog](CHANGELOG.md)

---

## ✨ Features

- ✅ Add, edit, delete tools with syntax and descriptions
- 🔍 Search tools by keyword or filter by tags/category
- 🏷️ Tag tools by hacking phase (e.g., recon, exploit)
- 📋 Copy command syntax directly to your clipboard
- 🌈 Styled output with [Rich](https://github.com/Textualize/rich)
- 💾 JSON-based persistent storage
- 🧠 Import/export entire tool DB
- ⚡ Quick mode (`--quick`) for silent terminal use
- 🔐 Drop tool database with auto-backup and action logs

---

## 📦 Requirements

- **Python** `3.10+`
- **Poetry** (for dependency & virtualenv management)

### 🔧 Install Dependencies

```bash
poetry install
```

You can also run CliHax as a Python module:

```bash
poetry run python -m clihax --help
```

---

## 🚀 Getting Started

### 📂 Clone the Repo

```bash
git clone https://github.com/Harikrishnan-P97/clihax.git
cd clihax
poetry install
```

### 🛠️ Troubleshooting

For detailed setup help and solutions to common issues, check the [Troubleshooting Guide](docs/troubleshooting.md).

### 🏃 Run the CLI

```bash
poetry run clihax --help
```

You’ll see:

```
Usage: clihax [OPTIONS] COMMAND [ARGS]...

  CliHax - A command reference manager for hackers and pentesters.
```

---

## 🔧 Core Commands

| Command              | Description                                  |
|----------------------|----------------------------------------------|
| `add`                | Add a new tool with command and notes        |
| `list`               | View all tools in a Rich-styled table        |
| `show <index>`       | Display a specific tool's full info          |
| `edit <index>`       | Modify an existing tool entry                |
| `delete <index>`     | Remove a specific tool                       |
| `search <term>`      | Search by keyword                            |
| `searchfilter <tag>` | Filter tools by tag or category              |
| `export <file>`      | Export your database to a JSON file          |
| `import <file>`      | Import tools from a JSON file                |
| `drop`               | Delete all tools (with confirmation & backup)|
| `logs`               | View or clear drop history                   |

---

## 🖼️ Example Tool Entry

```json
{
  "tool": "nmap",
  "command": "nmap -sV <target>",
  "category": "recon",
  "description": "Scan open ports and service versions",
  "tags": ["nmap", "scan", "version"]
}
```

---

## 📁 Project Structure

```
CliHax/
├── assets/                  # Banner image for the README
│   └── clihax-bannerimage.png
│
├── clihax/                  # Main source code
│   ├── __init__.py          # Package version (read from pyproject.toml)
│   ├── __main__.py          # `python -m clihax` entry point
│   ├── cli.py               # Top-level command group
│   ├── ui.py                # Tables, banner, highlighting, clipboard
│   ├── commands/            # One module per group of commands
│   │   ├── tools.py         # list, add, edit, delete, show
│   │   ├── search.py        # search, searchfilter
│   │   ├── data.py          # import, export, drop, logs
│   │   └── info.py          # info
│   └── utils/
│       ├── helpers.py       # Storage: data dir, JSON I/O, backups, migration
│       └── search.py        # Pure search/filter logic
│
├── data/                    # Legacy v1.0 data folder (migrated automatically)
├── docs/                    # Guides and CLI reference
├── tests/                   # pytest suite
│
├── .github/workflows/       # GitHub Actions CI
│   └── python.yml
│
├── .gitignore
├── LICENSE                  # MIT License
├── README.md
├── CHANGELOG.md             # Version history
├── pyproject.toml           # Project configuration (Poetry)
└── poetry.lock              # Locked dependencies
```

---

## 🧪 Example Usage

```bash
poetry run clihax add
poetry run clihax search nmap
poetry run clihax show 2 --copy
poetry run clihax export mybackup.json
poetry run clihax drop
```

---

## 🗄️ Where Your Data Lives

CliHax stores your tools in a per-user data directory, so it works from any folder:

| OS      | Location                                  |
| ------- | ----------------------------------------- |
| Linux   | `~/.local/share/clihax/`                  |
| macOS   | `~/Library/Application Support/clihax/`   |
| Windows | `%LOCALAPPDATA%\clihax\`                  |

Set `CLIHAX_HOME=/some/path` to use a different location. Run `clihax info` to see the active path.

Upgrading from v1.0? If you run `clihax` from a folder that still contains the old `data/tools.json`, it is copied over automatically (once, without overwriting anything).

---

## 🔐 Drop & Backup System

- Drops are **logged** with timestamps to `logs/drops.json` in your data directory
- Backups are **auto-saved** in `backups/` in your data directory before mass deletion
- View logs with: `clihax logs`
- Clear logs: `clihax logs --clear`

---

## 🎯 Ideal For

- 🛡️ Penetration testers
- 🧠 Bug bounty hunters
- 🧪 CTF players
- 🧰 Red teamers
- 👨‍🎓 Cybersecurity students

---

## 📜 License

This project is licensed under the [MIT License](LICENSE).

---

## 👤 Author

Made with 💻 and 🧠 by [Harikrishnan](https://github.com/Harikrishnan-P97)

> _"Hack smart. Document smarter."_ — CliHax


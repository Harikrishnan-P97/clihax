# CliHax

**CliHax** is a Python-based command-line tool that helps penetration testers and ethical hackers quickly reference syntax, commands, and notes for common cybersecurity tools.

It allows you to organize, search, and manage commonly used commands across different tools and hacking phases — all from the terminal.

---

## 🚀 Features

- 📋 Add, edit, delete tools with custom command syntax
- 🔍 Search tools by name or keyword
- 🧠 Categorize tools by hacking phase (e.g., recon, enum, exploit)
- 🏷️ Tag tools for flexible filtering and searching
- 🌈 Rich table output using `rich`
- 📎 Copy command syntax directly to clipboard
- 🛠️ Import/Export your tool database as JSON
- ⚡ Quick mode (`--quick`) for minimal terminal output
- 🔁 Git version control support for database

---

## 📦 Requirements

- Python 3.10+
- Poetry
- Dependencies:
  - `click`
  - `rich`
  - `pyperclip`
  - `gitpython`
  - `prompt-toolkit`

Install them with:

```bash
poetry install
```

---

## 🛠 Usage

### Run the tool:

```bash
poetry run clihax --help
```

### List all tools:

```bash
clihax list
```

### Add a new tool:

```bash
clihax add
```

### Search by keyword:

```bash
clihax search nmap
```

### Export or Import:

```bash
clihax export tools.json
clihax import tools.json
```

---

## 📁 Project Structure

```
CliHax/
├── cli.py               # Main CLI logic (Click)
├── utils/helpers.py     # Load/save JSON data
├── data/tools.json      # Your command database
├── pyproject.toml       # Poetry config and CLI entry
└── README.md            # This file
```

---

## ✅ Example Tool Entry

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

## 🔐 Ideal For

- Bug bounty hunters
- CTF players
- Ethical hackers
- Red teamers
- Students learning security tools

---

## 🧠 Author

Made with 🧠 and ❤️ by **Lord**

---

## 📜 License

This project is licensed under the MIT License.

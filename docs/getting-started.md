# Getting Started with **CliHax**

Welcome to **CliHax** – a command‑line tool reference manager built for hackers and pentesters.
This guide shows you how to install, run, and update CliHax on your machine.

---
## 1 Prerequisites
- **Python 3.10+**
- **Poetry** for dependency and virtual‑environment management  
  Install Poetry:  
  ```bash
  curl -sSL https://install.python-poetry.org | python3 -
  ```

---
## 2 Clone the Repository
```bash
git clone https://github.com/Harikrishnan-P97/clihax.git
cd clihax
```

---
## 3 Install Dependencies
```bash
poetry install
```

This creates an isolated virtual environment and installs all dependencies listed in **pyproject.toml**.

---
## 4 Run CliHax
```bash
poetry run clihax --help
```

You should see the global help menu with all available commands.

---
## 5 Updating CliHax
```bash
git pull
poetry install
```

---
## 6 Uninstalling
Simply remove the project folder and (optionally) delete backups/logs:
```bash
rm -rf clihax
```

Happy hacking! ⚔️
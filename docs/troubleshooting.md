
# 🔧 CliHax Troubleshooting Guide

This guide helps you install CliHax and resolve common issues during setup or execution.

---

## 🚀 Step-by-Step Installation

### 1. Update your system
```bash
sudo apt update && sudo apt upgrade
```

---

### 2. Install required system packages
```bash
sudo apt install build-essential python3-dev libssl-dev libffi-dev -y
```

---

### 3. Clone the CliHax repository
```bash
git clone https://github.com/Harikrishnan-P97/clihax.git
cd clihax
```

---

### 4. Install Poetry using `sudo`
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

---

### 5. Check if Poetry is installed
```bash
which poetry
```

If it shows no output, add Poetry to your PATH:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

Add it permanently by appending that line to your shell config file (`~/.bashrc`, `~/.zshrc`, etc.)

---

### 6. Install CliHax with verbose logging
```bash
poetry install -vvv
```

---

### 🧯 If installation is stuck at `keyring` step:

Run this command to disable keyring integration:
```bash
poetry config keyring.enabled false
```

Then reinstall:
```bash
poetry install -vvv
```

---

### 7. Run CliHax
```bash
poetry run clihax --help
```

---

## ❓ Common Runtime Issues

### ⚠️ `ModuleNotFoundError` (e.g., `No module named 'clihax'`)

**Fix:**
- Ensure folder structure:
  ```
  clihax/
  ├── __init__.py
  └── cli.py
  ```
- Ensure `pyproject.toml` has:
  ```toml
  [project.scripts]
  clihax = "clihax.cli:cli"
  ```

- Reinstall:
  ```bash
  poetry install
  ```

---

### 💥 JSON Error or Crashes

**Fix:**
- Validate or fix `tools.json`.
- Or restore from `data/backup_<timestamp>.json`.
- Or delete `tools.json` to reset.

---

### 🧪 Virtual Environment Issues

Use:
```bash
poetry shell
```
Or run directly:
```bash
poetry run clihax
```
---

_Updated: 2025-07-01_

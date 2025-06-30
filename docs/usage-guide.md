# Usage Guide

This document walks through common CliHax workflows.

---
## 1 Adding a Tool
```bash
poetry run clihax add
```
Follow the interactive prompts to enter:
- Tool name
- Command syntax
- Category / Phase
- Description
- Tags (comma‑separated)

---
## 2 Listing Tools
```bash
poetry run clihax list
```
Shows all tools in a Rich‑styled table with index numbers.

---
## 3 Viewing Details
```bash
poetry run clihax show 3
```
Displays full information for the tool at index **3**.

---
## 4 Editing / Deleting
```bash
clihax edit 3
clihax delete 3
```

---
## 5 Searching
```bash
clihax search smb
clihax searchfilter enum
```

---
## 6 Quick Mode
```bash
clihax list --quick
```
Minimal output – ideal for scripting.

---
## 7 Import / Export
```bash
clihax export mytools.json
clihax import mytools.json
```

---
## 8 Dropping All Tools
```bash
clihax drop            # prompts & backup
clihax drop -f         # force drop
```

---
## 9 Viewing Logs
```bash
clihax logs
clihax logs --clear
```
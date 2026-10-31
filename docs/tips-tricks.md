# Tips & Tricks

## Clipboard Copy
```bash
clihax show 1 --copy
```
Copies the command to your clipboard (requires `pyperclip`).

---
## Rich Filtering
Tag your tools well (`ftp`, `post`, `priv‑esc`) so searches stay sharp.

---
## Back Up and Share Your Tools
Export a copy you can keep in Git, cloud storage or another machine:
```bash
clihax export my-tools.json
```
Bring it back (or share it with a teammate) with:
```bash
clihax import my-tools.json
```
Imports are merged and duplicates are skipped.

---
## Restore from Backup
`clihax drop` saves a backup first. Backups live in your data directory
(`clihax info` shows where; on Linux it is `~/.local/share/clihax/`):
```bash
ls ~/.local/share/clihax/backups/
clihax import ~/.local/share/clihax/backups/tools_backup_<timestamp>.json
```

---
## Shell Alias
Add to `~/.bashrc`:
```bash
alias ch="poetry run clihax"
```
Then call:
```bash
ch list
```

---
Happy hacking! ⚔️
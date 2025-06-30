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
## Git Versioning
Sync `data/tools.json` with Git:
```bash
git add data/tools.json
git commit -m "Update tools DB"
git push
```

---
## Restore from Backup
```bash
cp backups/tools_backup_<timestamp>.json data/tools.json
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
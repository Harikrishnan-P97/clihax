# CLI Reference

| Command | Flags / Options | Description |
|---------|-----------------|-------------|
| `add` | `--quick` | Interactive prompt to add a new tool |
| `list` | `--quick` | List all tools |
| `show <index>` | `--copy` | Show tool details; optionally copy command |
| `edit <index>` | | Edit a tool entry |
| `delete <index>` | | Delete a tool |
| `search <term>` | | Keyword search |
| `searchfilter <tag>` | | Filter by tag/category |
| `starter` | `--list`, `--yes` | Add the built-in pack of common commands (skips ones you already have) |
| `import <file>` | | Import tools from JSON |
| `export <file>` | | Export tools to JSON |
| `drop` | `-f, --force` | Delete **all** tools |
| `logs` | `--clear` | View or clear drop logs |
| `config` (future) | | Manage user settings |

Use `clihax <command> --help` for per‑command help.

## JSON output

`list`, `show`, `search` and `searchfilter` accept `--json`. Only JSON is printed
on stdout, so it is safe to pipe into other tools:

```bash
clihax list --json
clihax search nmap --json | jq '.[].command'
clihax show 2 --json
```

- Every tool includes an `index` (its 1-based position as displayed), then the stored fields.
- No matches (or an empty database) gives `[]` and exit status 0.
- `show` with an invalid index prints the error on stderr and exits with status 1.
- `--json` cannot be combined with `--quick`, `--pager` or `--copy`.

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
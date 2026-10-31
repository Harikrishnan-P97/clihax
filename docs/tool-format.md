# Tool Data Format

CliHax stores tools in **tools.json** inside your data directory
(`~/.local/share/clihax/` on Linux; run `clihax info` to see the path).
Each entry follows this schema:

```jsonc
{
  "tool": "string",         // Tool name (e.g., "nmap")
  "command": "string",      // Full command syntax
  "category": "string",     // Recon, enum, exploit, post, misc...
  "description": "string",  // Short human‑readable note
  "tags": ["string", ...],  // Arbitrary tags for searching/filtering
  "created_at": "string",   // Set automatically (ISO 8601)
  "updated_at": "string"    // Set automatically (ISO 8601)
}
```

### Field Guidelines
| Field | Notes |
|-------|-------|
| `tool` | Lowercase, no spaces if possible |
| `category` | One of: recon, enum, exploit, post, misc |
| `tags` | Use hyphenated single words, avoid spaces |

### Backup Files
Backups are timestamped copies of **tools.json** stored in the `backups/` folder of the data directory.

### Metadata
Timestamps of the last edit, import and export live in **meta.json** in the same folder.
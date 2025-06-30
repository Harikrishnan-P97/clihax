# Tool Data Format

CliHax stores tools in **data/tools.json**. Each entry follows this
schema:

```jsonc
{
  "tool": "string",         // Tool name (e.g., "nmap")
  "command": "string",      // Full command syntax
  "category": "string",     // Recon, enum, exploit, post, misc...
  "description": "string",  // Short human‑readable note
  "tags": ["string", ...]   // Arbitrary tags for searching/filtering
}
```

### Field Guidelines
| Field | Notes |
|-------|-------|
| `tool` | Lowercase, no spaces if possible |
| `category` | One of: recon, enum, exploit, post, misc |
| `tags` | Use hyphenated single words, avoid spaces |

### Backup Files
Backups are timestamped copies of **tools.json** stored in `/backups/`.

### Metadata
Additional info (e.g., total count) lives in **data/meta.json**.
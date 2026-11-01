# Data format

CliHax stores your tools in `tools.json` inside its data folder (`~/.local/share/clihax/` on Linux; run `clihax info` to see the path). The same format is used by `clihax export` and `clihax import`, so you can edit a file by hand or generate one with another tool.

## Tool entries

The file is a JSON array of objects:

```jsonc
[
  {
    "tool": "nmap",                                   // required: the tool's name
    "command": "nmap -sC -sV -oA scan <target>",      // required: the command, with placeholders
    "description": "Default scripts and versions",    // short note
    "category": "recon",                              // for example recon, web, passwords, post
    "tags": ["nmap", "scan"],                         // used by search and --tag
    "created_at": "2026-11-01T11:38:21",              // set automatically (ISO 8601)
    "updated_at": "2026-11-01T11:38:21"               // set automatically (ISO 8601)
  }
]
```

(Comments are shown for explanation only; JSON files cannot contain them.)

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `tool` | string | yes | Lowercase, one word where possible. |
| `command` | string | yes | Stored and displayed exactly as written, including characters such as `[` and `<`. |
| `description` | string | no | Searched together with the name and command. |
| `category` | string | no | One per phase of work. Matched exactly by `--category`. |
| `tags` | array of strings | no | Short, hyphenated words. Matched exactly by `--tag` and by keywords. |
| `created_at`, `updated_at` | string | no | Filled in automatically when missing. |

The pair `tool` and `command` identifies an entry: two entries with the same pair are duplicates.

## Importing

`clihax import FILE` accepts a JSON array in the format above and merges it into your tools:

- An entry without a `tool` or a `command` is skipped and counted in the summary.
- Missing optional fields get defaults (empty description and category, no tags, current time as timestamps).
- `tags` may be an array or a comma-separated string (`"scan, nmap"`).
- Entries that duplicate an existing tool and command are skipped, so importing the same file twice is safe.

The smallest valid file:

```json
[
  { "tool": "ls", "command": "ls -la" }
]
```

## Other files in the data folder

| Path | Contents |
|------|----------|
| `meta.json` | Times of the last edit, import and export (`last_edit`, `last_import`, `last_export`). |
| `backups/tools_backup_<timestamp>.json` | A copy of `tools.json` saved by `clihax drop`. |
| `logs/drops.json` | One object per drop: `timestamp`, `total_dropped`, `forced` and `backup_created`. |

All files are written atomically (to a temporary file that is then renamed), so an interrupted write cannot corrupt them.

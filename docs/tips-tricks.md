# Tips and tricks

Practical ways to get more out of CliHax. The full command syntax is in the [README](../README.md#command-reference).

## Copy a command and fill in the placeholders

Entries use placeholders such as `<target>`, `<domain>`, `<lhost>` and `<lport>`. Copy a command and edit it in your shell, or substitute the values directly:

```bash
clihax show 1 --copy
clihax show 1 --json | jq -r .command | sed 's/<target>/10.10.10.5/'
clihax search "reverse shell" --copy 1
```

## Keep your entries consistent

Good names make searches sharper:

- **Tools**: lowercase, one word where possible (`nmap`, `ffuf`).
- **Categories**: one per phase of work. The starter pack uses `recon`, `web`, `passwords`, `smb`, `shells`, `privesc` and `transfer`.
- **Tags**: short, hyphenated words (`brute-force`, `reverse-shell`). A keyword search matches a tag exactly, so consistent spelling pays off.
- **Descriptions**: say what the command is *for*, because descriptions are searched too.

## Use quick mode in pipelines

`--quick` prints one plain line per result:

```bash
clihax search nmap --quick | less
clihax searchfilter -c recon --quick | grep -i udp
```

## Query your toolbox with jq

`--json` makes the toolbox easy to analyse. [jq](https://jqlang.github.io/jq/) examples:

```bash
clihax list --json | jq 'length'                                           # number of tools
clihax list --json | jq -r 'map(.category) | unique | join(", ")'          # categories in use
clihax list --json | jq -r '.[] | select(.category=="recon") | .command'   # commands in one category
clihax search smb --json | jq -r '.[] | "\(.index) \(.tool)"'              # index and name of each match
```

## Use separate toolboxes

`CLIHAX_HOME` selects the data folder, so you can keep a separate toolbox per engagement, CTF or team:

```bash
CLIHAX_HOME=~/ctf-notes clihax list
alias ctf='CLIHAX_HOME=~/ctf-notes clihax'
```

Pointing `CLIHAX_HOME` at a folder inside a synced or version-controlled directory keeps your toolbox in sync across machines.

## Back up and share

Export a copy you can keep in Git, in cloud storage or on another machine, and merge it back anywhere:

```bash
clihax export my-tools.json
clihax import my-tools.json
```

Imports are merged and duplicates (same tool and command) are skipped, so importing the same file twice is safe. `clihax delete` does not ask for confirmation, so export first when you are cleaning up.

## Restore from a backup

`clihax drop` saves a backup first. Backups live in the `backups/` folder of your data directory (`clihax info` shows where). See [Troubleshooting](troubleshooting.md#restoring-from-a-backup) for the restore steps.

## Shortcuts

```bash
alias ch=clihax        # add to ~/.bashrc or ~/.zshrc
```

Turn on [Tab completion](../README.md#shell-completion) as well: it completes your own tags, categories and tool numbers.

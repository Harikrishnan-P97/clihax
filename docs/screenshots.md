# Screenshots

Screenshots 1 to 8 were captured on Linux from CliHax v1.1.0, using a temporary toolbox loaded from the built-in starter pack. The [README](../README.md) has the full command reference.

## Overview

![clihax --help listing every command](screenshots/01-help.png)

All commands at a glance, with usage examples in the help text.

## Starter pack

![clihax starter --list previewing the built-in commands](screenshots/02-starter.png)

A built-in set of 33 common pentesting commands, so the tool is useful from the first run.

## Search

![clihax search with highlighted matches](screenshots/03-search.png)

Keyword search across name, command, description and tags, with matches highlighted.

## Typo-tolerant search

![clihax search finding gobuster from the typo gobsuter](screenshots/04-typo-search.png)

A mistyped query (`gobsuter`) still finds `gobuster`, and says that the match is approximate.

## Scripting

![clihax search --json piped into a script](screenshots/05-json-scripting.png)

Results as clean JSON on stdout, ready to pipe into other tools.

## Info dashboard

![clihax info showing version, toolbox statistics and activity](screenshots/06-info.png)

Version, author, toolbox statistics, data location and recent activity in one view.

## Shell completion

![Tab completion offering the toolbox's tags](screenshots/07-completion.png)

Tab completion offers the user's own tags, categories and tool numbers, not just command names.

## Quality gates

![ruff and pytest passing](screenshots/08-quality.png)

Linting passes and all tests pass.

## Release

![The v1.1.0 release page on GitHub](screenshots/09-release.png)

Versioned release v1.1.0 with release notes, built from a maintained changelog.

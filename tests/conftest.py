"""Shared fixtures and helpers for the CliHax test suite."""

import re

import pytest
from click.testing import CliRunner

from clihax.utils import helpers

_ANSI = re.compile(r"\x1b\[[0-9;]*m")


def plain(text):
    """Strip ANSI colour codes so assertions do not depend on terminal styling."""
    return _ANSI.sub("", text)


def make_tool(tool, command, category="", tags=(), description=""):
    """Build a tool entry with fixed timestamps (keeps tests deterministic)."""
    return {
        "tool": tool,
        "command": command,
        "description": description,
        "tags": list(tags),
        "category": category,
        "created_at": "2025-01-01T00:00:00",
        "updated_at": "2025-01-01T00:00:00",
    }


SAMPLE_TOOLS = [
    make_tool("nmap", "nmap -sV", "recon", ["scan", "nmap"], "scan service versions"),
    make_tool("hydra", "hydra -l admin", "attack", ["brute-force", "ftp"], "password brute force"),
    make_tool("msfvenom", "msfvenom -p x", "post", ["meterpreter", "reverse", "shell"], "payload builder"),
]


@pytest.fixture
def runner(tmp_path, monkeypatch):
    """CLI runner with an isolated data dir, run from an empty working folder."""
    monkeypatch.setenv("CLIHAX_HOME", str(tmp_path / "home"))
    monkeypatch.chdir(tmp_path)
    return CliRunner()


@pytest.fixture
def seeded(runner):
    """Runner whose database already holds the three sample tools."""
    helpers.save_tools([dict(t) for t in SAMPLE_TOOLS])
    return runner


@pytest.fixture
def clipboard(monkeypatch):
    """Capture clipboard writes instead of touching a real clipboard."""
    import pyperclip

    copied = []
    monkeypatch.setattr(pyperclip, "copy", copied.append)
    return copied

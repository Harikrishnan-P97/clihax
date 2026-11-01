"""Guard against broken links and images in the project's markdown files."""

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
DOCS = ["README.md", "CONTRIBUTING.md", *sorted(str(p.relative_to(ROOT)) for p in (ROOT / "docs").glob("*.md"))]


def local_targets(text):
    found = re.findall(r"\]\(([^)\s]+)\)", text) + re.findall(r'(?:src|href)="([^"]+)"', text)
    return [t.split("#")[0] for t in found if not t.startswith(("http", "mailto:", "#"))]


@pytest.mark.parametrize("doc", DOCS)
def test_relative_links_and_images_exist(doc):
    path = ROOT / doc
    for target in local_targets(path.read_text(encoding="utf-8")):
        if target:
            assert (path.parent / target).exists(), f"{doc} links to missing {target}"


def test_readme_documents_the_install_command():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "pipx install git+https://github.com/Harikrishnan-P97/clihax.git" in readme


def test_readme_mentions_every_command():
    from clihax.cli import cli

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    for name in cli.commands:
        assert f"`{name}" in readme, f"README does not mention the {name} command"

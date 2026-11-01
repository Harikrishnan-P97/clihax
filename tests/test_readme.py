"""Guard against broken links, images and section anchors in the project's markdown files."""

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
DOCS = [
    "README.md",
    "CONTRIBUTING.md",
    *sorted(str(p.relative_to(ROOT)) for p in (ROOT / "docs").glob("*.md")),
]


def links(text):
    """Yield (file, anchor) for every relative link, image and in-page anchor."""
    found = re.findall(r"\]\(([^)\s]+)\)", text) + re.findall(r'(?:src|href)="([^"]+)"', text)
    for target in found:
        if not target.startswith(("http", "mailto:")):
            file, _, anchor = target.partition("#")
            yield file, anchor


def slug(heading):
    """GitHub's anchor for a heading: lower case, punctuation dropped, spaces to hyphens."""
    return re.sub(r"[^a-z0-9 _-]", "", heading.strip().lower()).replace(" ", "-")


def anchors(path):
    """All heading anchors of a markdown file (ignoring lines inside code blocks)."""
    found, in_code = set(), False
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("```"):
            in_code = not in_code
        elif not in_code and (match := re.match(r"#{1,6}\s+(.*)", line)):
            found.add(slug(match.group(1).replace("`", "")))
    return found


@pytest.mark.parametrize("doc", DOCS)
def test_relative_links_images_and_anchors_exist(doc):
    path = ROOT / doc
    for file, anchor in links(path.read_text(encoding="utf-8")):
        target = (path.parent / file) if file else path
        assert target.exists(), f"{doc} links to missing {file}"
        if anchor and target.suffix == ".md":
            assert anchor in anchors(target), f"{doc} links to missing section #{anchor} in {target.name}"


def test_readme_documents_the_install_command():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "pipx install git+https://github.com/Harikrishnan-P97/clihax.git" in readme


def test_readme_mentions_every_command():
    from clihax.cli import cli

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    for name in cli.commands:
        assert f"`{name}" in readme, f"README does not mention the {name} command"


def test_every_doc_page_is_listed_in_the_docs_index():
    index = (ROOT / "docs" / "README.md").read_text(encoding="utf-8")
    for page in (ROOT / "docs").glob("*.md"):
        if page.name != "README.md":
            assert page.name in index, f"docs/README.md does not link to {page.name}"

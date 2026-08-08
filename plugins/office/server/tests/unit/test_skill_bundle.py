"""Structural/invariant tests for the `presentations` Agent Skill package.

These tests enforce package quality and portability invariants from the
skill redesign brief (plugins/office/docs/OFFICE_PRESENTATION_SKILLS_REDESIGN_BRIEF.md).
They do not and cannot judge aesthetics or writing quality.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import cast

import yaml

SKILL_ROOT = Path(__file__).resolve().parents[3] / "skills" / "presentations"
SKILL_MD = SKILL_ROOT / "SKILL.md"
REFERENCES_DIR = SKILL_ROOT / "references"

_REFERENCE_PATH_RE = re.compile(r"references/[\w.-]+\.md")
_MARKDOWN_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")


def _frontmatter(text: str) -> dict[str, object]:
    assert text.startswith("---\n"), "SKILL.md must start with YAML frontmatter"
    end = text.index("\n---", 4)
    data = yaml.safe_load(text[4:end])
    assert isinstance(data, dict)
    return cast("dict[str, object]", data)


def test_skill_md_exists() -> None:
    assert SKILL_MD.is_file()


def test_skill_directory_matches_frontmatter_name() -> None:
    frontmatter = _frontmatter(SKILL_MD.read_text())
    assert frontmatter.get("name") == "presentations"
    assert SKILL_ROOT.name == frontmatter["name"]


def test_description_present_and_bounded() -> None:
    frontmatter = _frontmatter(SKILL_MD.read_text())
    description = frontmatter.get("description")
    assert isinstance(description, str)
    assert description.strip()
    assert len(description) <= 1024


def test_no_non_portable_frontmatter_fields() -> None:
    frontmatter = _frontmatter(SKILL_MD.read_text())
    assert "disable-model-invocation" not in frontmatter
    assert set(frontmatter) <= {"name", "description"}


def test_skill_md_size_limit() -> None:
    line_count = len(SKILL_MD.read_text().splitlines())
    assert line_count <= 500, f"SKILL.md has {line_count} lines, spec target is <=500"


def test_skill_md_links_to_every_reference_file() -> None:
    text = SKILL_MD.read_text()
    linked_targets = {target for _label, target in _MARKDOWN_LINK_RE.findall(text)}
    linked_names = {Path(target).name for target in linked_targets if target.endswith(".md")}
    actual_reference_files = {p.name for p in REFERENCES_DIR.glob("*.md")}
    missing_from_skill_md = actual_reference_files - linked_names
    assert not missing_from_skill_md, (
        f"SKILL.md does not directly link to: {sorted(missing_from_skill_md)}"
    )


def test_no_dangling_reference_links() -> None:
    all_files = [SKILL_MD, *REFERENCES_DIR.glob("*.md")]
    for path in all_files:
        text = path.read_text()
        for match in _REFERENCE_PATH_RE.findall(text):
            target = SKILL_ROOT / match
            relative = path.relative_to(SKILL_ROOT)
            assert target.is_file(), f"{relative} references missing file {match}"


def test_reference_files_are_reasonably_scoped() -> None:
    # Keep individual references focused; the design atlas/compositions catalogues
    # are explicitly allowed to be larger per the brief, so only bound the rest.
    large_catalogues = {"design-atlas.md", "compositions.md", "genres.md", "motifs.md"}
    for path in REFERENCES_DIR.glob("*.md"):
        if path.name in large_catalogues:
            continue
        line_count = len(path.read_text().splitlines())
        assert line_count <= 250, f"{path.name} has grown to {line_count} lines"


def test_sources_file_exists_with_content() -> None:
    sources = SKILL_ROOT / "SOURCES.md"
    assert sources.is_file()
    assert len(sources.read_text().strip()) > 200


def test_design_atlas_states_optionality() -> None:
    text = (REFERENCES_DIR / "design-atlas.md").read_text().lower()
    required_phrases = [
        "optional inspiration",
        "not a preset",
        "existing brand",
        "combine",
        "reinterpret",
        "ignore",
    ]
    missing = [phrase for phrase in required_phrases if phrase not in text]
    assert not missing, f"design-atlas.md is missing optionality language: {missing}"


def test_design_atlas_has_substantial_breadth() -> None:
    text = (REFERENCES_DIR / "design-atlas.md").read_text()
    entry_count = len(re.findall(r"^### ", text, flags=re.MULTILINE))
    assert entry_count >= 60, f"design atlas has only {entry_count} visual-language entries"


def test_compositions_catalogue_has_substantial_breadth() -> None:
    text = (REFERENCES_DIR / "compositions.md").read_text()
    entry_count = len(re.findall(r"^### ", text, flags=re.MULTILINE))
    assert entry_count >= 30, f"compositions catalogue has only {entry_count} archetypes"


def test_only_one_discovered_presentations_skill() -> None:
    skills_dir = SKILL_ROOT.parent
    discovered = [p for p in skills_dir.iterdir() if p.is_dir() and (p / "SKILL.md").is_file()]
    assert [p.name for p in discovered] == ["presentations"]

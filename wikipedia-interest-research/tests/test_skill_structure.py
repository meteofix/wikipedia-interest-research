"""Structural acceptance checks (A1–A4): spec-compliant SKILL.md, size budget, no binaries, no leaks."""

from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path

import pytest

SKILL = Path(__file__).resolve().parents[1]
TEXT = (SKILL / "SKILL.md").read_text(encoding="utf-8")


def frontmatter() -> dict:
    import yaml

    m = re.match(r"^---\n(.*?)\n---\n", TEXT, re.S)
    assert m, "SKILL.md must start with YAML frontmatter"
    data = yaml.safe_load(m.group(1))  # fails on invalid YAML, e.g. an unquoted ": " in the description
    assert isinstance(data, dict)
    return data


def test_frontmatter_follows_spec():
    fm = frontmatter()
    name = fm["name"]
    assert re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", name) and len(name) <= 64
    assert name == SKILL.name, "name must match the directory name"
    assert 0 < len(fm["description"]) <= 1024
    assert len(fm.get("compatibility", "")) <= 500
    assert all(isinstance(v, str) for v in (fm.get("metadata") or {}).values())
    assert set(fm) <= {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}


def test_skill_md_budget():
    body = TEXT.split("---", 2)[2]
    assert len(TEXT.splitlines()) <= 500
    assert len(body) / 4 <= 5000, "body must stay under ~5000 tokens"


def test_referenced_files_exist():
    for ref in re.findall(r"\]\(([^)#]+)\)", TEXT):
        assert (SKILL / ref).exists(), f"SKILL.md links to missing {ref}"
    assert (SKILL / "scripts" / "wiki.py").exists()


def test_dependencies_declared_and_locked():
    script = (SKILL / "scripts" / "wiki.py").read_text(encoding="utf-8")
    assert "# /// script" in script and "dependencies" in script
    assert (SKILL / "scripts" / "wiki.py.lock").exists()
    assert (SKILL / "requirements.txt").exists()


def test_no_compiled_binaries():
    magic = (b"\x7fELF", b"\xcf\xfa\xed\xfe", b"\xfe\xed\xfa\xcf", b"MZ", b"\xca\xfe\xba\xbe")
    for p in SKILL.rglob("*"):
        if p.is_file() and "__pycache__" not in p.parts and ".pytest_cache" not in p.parts:
            head = p.read_bytes()[:4]
            assert not any(head.startswith(m) for m in magic), f"binary executable found: {p}"


@pytest.mark.skipif(not os.environ.get("WIKI_CONTACT"), reason="needs WIKI_CONTACT to know what to look for")
def test_private_contact_not_in_repo_or_history():
    secret = os.environ["WIKI_CONTACT"].strip()
    repo = SKILL.parent
    for p in SKILL.rglob("*"):
        if p.is_file() and "__pycache__" not in p.parts:
            assert secret.encode() not in p.read_bytes(), f"contact leaked into {p}"
    log = subprocess.run(["git", "-C", str(repo), "log", "--all", "-p", "--format=%an %ae %cn %ce %B"],
                         capture_output=True, text=True, errors="replace").stdout
    assert secret not in log, "contact found in git history"

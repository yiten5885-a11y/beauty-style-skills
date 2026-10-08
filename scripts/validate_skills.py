#!/usr/bin/env python3
"""Validate the public multi-skill bundle without inspecting private media."""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {
    "facial-style-preview",
    "hairstyle-style-preview",
    "nail-design-board",
    "eyewear-style-preview",
    "personal-outfit-studio",
    "intimate-loungewear-board",
}
PRIVATE_SUFFIXES = {".docx", ".pdf", ".jpg", ".jpeg", ".webp", ".heic", ".json"}
LOCAL_PREFIX = "/" + "Users/"


def validate() -> list[str]:
    errors: list[str] = []
    skills_root = ROOT / "skills"
    actual = {path.name for path in skills_root.iterdir() if path.is_dir() and path.name != "hairstyle-upgrade-board"}
    if actual != EXPECTED:
        errors.append(f"skill set mismatch: expected {sorted(EXPECTED)}, found {sorted(actual)}")

    for name in sorted(EXPECTED):
        package = skills_root / name
        required = [package / "SKILL.md", package / "README.md", package / "agents/openai.yaml", package / "assets/cover.png"]
        for path in required:
            if not path.is_file():
                errors.append(f"{name}: missing {path.relative_to(ROOT)}")
        skill = package / "SKILL.md"
        agent = package / "agents/openai.yaml"
        readme = package / "README.md"
        if skill.is_file():
            text = skill.read_text(encoding="utf-8")
            if not re.search(rf"(?m)^name:\s*{re.escape(name)}\s*$", text):
                errors.append(f"{name}: frontmatter name mismatch")
            if LOCAL_PREFIX in text or "..\\" in text:
                errors.append(f"{name}: private or parent path in SKILL.md")
        if agent.is_file() and f"${name}" not in agent.read_text(encoding="utf-8"):
            errors.append(f"{name}: default prompt does not invoke ${name}")
        if readme.is_file() and "使用方法" not in readme.read_text(encoding="utf-8"):
            errors.append(f"{name}: README lacks 使用方法")

    for path in ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts or "__pycache__" in path.parts:
            continue
        if path.suffix.lower() in PRIVATE_SUFFIXES:
            errors.append(f"private/source asset type is packaged: {path.relative_to(ROOT)}")
        if path.suffix.lower() in {".md", ".py", ".yaml", ".yml", ".txt"}:
            text = path.read_text(encoding="utf-8")
            if LOCAL_PREFIX in text:
                errors.append(f"absolute local path in {path.relative_to(ROOT)}")
    return errors


def main() -> int:
    errors = validate()
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"Validated {len(EXPECTED)} public Skill packages and their cover/usage contracts.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

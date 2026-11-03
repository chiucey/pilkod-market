#!/usr/bin/env python3
"""Validate the use-wisely Agent Skill package without third-party deps."""
from __future__ import annotations

import json
import re
import sys
import zipfile
from pathlib import Path
from typing import Dict, List, Tuple

NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SECRET_PATTERNS = [
    re.compile(r"sk-[A-Za-z0-9_-]{20,}"),
    re.compile(r"(?i)(api[_-]?key|secret|token)\s*=\s*['\"][^'\"]{12,}['\"]"),
]

REQUIRED_FILES = [
    "SKILL.md",
    "README.md",
    "references/programming-style.md",
    "references/emotional-support-cn.md",
    "references/skill-routing.md",
    "references/china-crisis-resources.md",
    "references/trigger-eval.json",
    "scripts/requirements.txt",
]


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def parse_frontmatter(path: Path) -> Tuple[Dict[str, str], str]:
    text = read(path)
    if not text.startswith("---\n"):
        raise ValueError("SKILL.md must start with YAML frontmatter delimiter '---'")
    end = text.find("\n---", 4)
    if end == -1:
        raise ValueError("SKILL.md missing closing YAML frontmatter delimiter")
    raw, body = text[4:end], text[end + 4 :]
    fields: Dict[str, str] = {}
    key = None
    buf: List[str] = []

    def flush() -> None:
        nonlocal key, buf
        if key:
            fields[key] = "\n".join(buf).strip().strip('"')
        key = None
        buf = []

    for line in raw.splitlines():
        if not line.strip():
            continue
        if line.startswith("  ") and key:
            buf.append(line.strip())
            continue
        if ":" in line:
            flush()
            k, v = line.split(":", 1)
            key = k.strip()
            v = v.strip()
            buf = [] if v in {">", "|"} else [v]
    flush()
    return fields, body


def validate(root: Path) -> List[str]:
    errors: List[str] = []
    if not root.exists() or not root.is_dir():
        return [f"not a directory: {root}"]

    for rel in REQUIRED_FILES:
        if not (root / rel).exists():
            errors.append(f"missing required file: {rel}")

    skill = root / "SKILL.md"
    if skill.exists():
        try:
            fields, body = parse_frontmatter(skill)
            name = fields.get("name", "")
            desc = fields.get("description", "")
            if not NAME_RE.match(name):
                errors.append("frontmatter name must be lowercase kebab-case")
            if name and root.name != name:
                errors.append(f"directory '{root.name}' must match skill name '{name}'")
            if len(desc) < 200:
                errors.append("description is too short for safe wide triggering")
            if "Use widely" not in desc and "use widely" not in desc:
                errors.append("description should include use widely")
            if len(body) > 30000:
                errors.append("SKILL.md body is too long; move details to references")
            for phrase in ["编程", "情感", "12356", "USE_WISELY_SKILL_DIRS"]:
                if phrase not in body:
                    errors.append(f"SKILL.md missing key phrase: {phrase}")
        except Exception as exc:
            errors.append(str(exc))

    trigger = root / "references" / "trigger-eval.json"
    if trigger.exists():
        try:
            data = json.loads(read(trigger))
            if not isinstance(data, list) or len(data) < 5:
                errors.append("trigger-eval.json should contain at least 5 cases")
        except Exception as exc:
            errors.append(f"trigger-eval.json invalid: {exc}")

    meta = root / "_meta.json"
    if meta.exists():
        try:
            data = json.loads(read(meta))
            if data.get("name") != root.name:
                errors.append("_meta.json name must match directory name")
        except Exception as exc:
            errors.append(f"_meta.json invalid: {exc}")

    for path in root.rglob("*"):
        if path.is_dir() or path.suffix.lower() in {".zip", ".png", ".jpg", ".jpeg", ".gif", ".webp"}:
            continue
        try:
            text = read(path)
        except UnicodeDecodeError:
            errors.append(f"not UTF-8: {path.relative_to(root)}")
            continue
        for pat in SECRET_PATTERNS:
            if pat.search(text):
                errors.append(f"possible hardcoded secret: {path.relative_to(root)}")
                break
    return errors


def validate_zip(zip_path: Path) -> List[str]:
    errors: List[str] = []
    try:
        with zipfile.ZipFile(zip_path, "r") as zf:
            bad = zf.testzip()
            if bad:
                errors.append(f"zip corrupt at: {bad}")
            names = zf.namelist()
            if not names or not all(n.startswith("use-wisely/") for n in names):
                errors.append("zip must contain a single root folder: use-wisely/")
            if "use-wisely/SKILL.md" not in names:
                errors.append("zip missing use-wisely/SKILL.md")
    except Exception as exc:
        errors.append(f"zip invalid: {exc}")
    return errors


def main() -> int:
    target = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    errors = validate_zip(target) if target.suffix == ".zip" else validate(target)
    if errors:
        print("❌ Validation failed")
        for err in errors:
            print(f"- {err}")
        return 1
    print("✅ Validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""
Initialize a new skill directory with SKILL.md and _meta.json.

Important:
- The skill id must come from the `generate_skill_id` tool.
- Pass that value via --id when running this script.
"""

import argparse
import json
import re
import sys
from pathlib import Path

MAX_SKILL_NAME_LENGTH = 64
DEFAULT_VERSION = "1.0.0"
SEMVER_PATTERN = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:[-+][0-9A-Za-z.-]+)?$")


SKILL_TEMPLATE = """---
name: {skill_name}
description: [TODO: Describe what this skill does and when to trigger it]
---

# {skill_title}

## Overview

[TODO: Briefly describe the skill workflow]
"""


def normalize_skill_name(raw: str) -> str:
    value = raw.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = re.sub(r"-{2,}", "-", value).strip("-")
    return value


def to_title(name: str) -> str:
    return " ".join(part.capitalize() for part in name.split("-"))


def is_valid_semver(version: str) -> bool:
    return bool(SEMVER_PATTERN.match(version))


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def init_skill(skill_name: str, output_path: Path, skill_id: str, version: str) -> Path:
    target_dir = output_path.resolve() / skill_name
    if target_dir.exists():
        raise FileExistsError(f"Skill directory already exists: {target_dir}")

    target_dir.mkdir(parents=True, exist_ok=False)

    skill_md = target_dir / "SKILL.md"
    skill_md.write_text(
        SKILL_TEMPLATE.format(skill_name=skill_name, skill_title=to_title(skill_name)),
        encoding="utf-8",
    )

    meta_file = target_dir / "_meta.json"
    write_json(meta_file, {"id": skill_id, "version": version})

    return target_dir


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Initialize a new skill directory.")
    parser.add_argument("skill_name", help="Skill name (will be normalized to hyphen-case)")
    parser.add_argument("--path", required=True, help="Base output directory")
    parser.add_argument(
        "--id",
        required=True,
        dest="skill_id",
        help="Skill id from generate_skill_id tool",
    )
    parser.add_argument(
        "--version",
        default=DEFAULT_VERSION,
        help=f"Initial semantic version (default: {DEFAULT_VERSION})",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    normalized_name = normalize_skill_name(args.skill_name)
    if not normalized_name:
        print("ERROR: skill_name must contain at least one letter or digit")
        return 1
    if len(normalized_name) > MAX_SKILL_NAME_LENGTH:
        print(
            f"ERROR: skill_name is too long ({len(normalized_name)} chars). "
            f"Max is {MAX_SKILL_NAME_LENGTH}."
        )
        return 1

    skill_id = args.skill_id.strip()
    if not skill_id:
        print("ERROR: --id is required and must be non-empty")
        print("Hint: call generate_skill_id tool first, then pass the result to --id.")
        return 1

    version = args.version.strip()
    if not is_valid_semver(version):
        print(f"ERROR: invalid semantic version: {version}")
        return 1

    if normalized_name != args.skill_name:
        print(f"Note: normalized skill name to '{normalized_name}'")

    try:
        created = init_skill(
            skill_name=normalized_name,
            output_path=Path(args.path),
            skill_id=skill_id,
            version=version,
        )
    except Exception as exc:
        print(f"ERROR: {exc}")
        return 1

    print(f"OK: created skill at {created}")
    print("Next steps:")
    print(f"1) Edit {created / 'SKILL.md'}")
    print(f"2) Validate with: uv run python scripts/quick_validate.py {created}")
    print(f"3) Package with: uv run python scripts/package_skill.py {created}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

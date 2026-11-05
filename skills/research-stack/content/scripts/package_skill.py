#!/usr/bin/env python3
"""
Research Stack Skill Packager
Packages a multi-role skill into a distributable .skill archive.

Usage:
    python package_skill.py <skill_path> [--output <output_path>]
"""

import argparse
import json
import os
import shutil
import sys
import tarfile
from datetime import datetime
from pathlib import Path


def find_skill_files(skill_path: Path) -> dict:
    """Find all SKILL.md and _meta.json files in the skill directory."""
    skill_files = {
        "root": [],
        "roles": []
    }

    # Find root-level SKILL.md files
    for pattern in ["SKILL.md", "ORCHESTRATOR.md", "_meta.json"]:
        matches = list(skill_path.glob(pattern))
        skill_files["root"].extend(matches)

    # Find references and scripts
    skill_files["references"] = list((skill_path / "references").glob("*.md")) if (skill_path / "references").exists() else []
    skill_files["scripts"] = list((skill_path / "scripts").glob("*.py")) if (skill_path / "scripts").exists() else []

    # Find role skills
    roles_dir = skill_path / "roles"
    if roles_dir.exists():
        for role_dir in roles_dir.iterdir():
            if role_dir.is_dir():
                role_files = {
                    "path": role_dir,
                    "skills": [],
                    "meta": None
                }
                for f in role_dir.glob("*.md"):
                    role_files["skills"].append(f)
                meta_file = role_dir / "_meta.json"
                if meta_file.exists():
                    role_files["meta"] = meta_file
                if role_files["skills"] or role_files["meta"]:
                    skill_files["roles"].append(role_files)

    return skill_files


def validate_skill_structure(skill_path: Path) -> list:
    """Validate skill directory structure and return list of errors."""
    errors = []

    # Check root-level requirements
    root_skill = skill_path / "SKILL.md"
    if not root_skill.exists():
        errors.append(f"Missing root SKILL.md at {root_skill}")

    meta_file = skill_path / "_meta.json"
    if not meta_file.exists():
        errors.append(f"Missing _meta.json at {meta_file}")
    else:
        try:
            with open(meta_file) as f:
                meta = json.load(f)
                if "id" not in meta:
                    errors.append("_meta.json missing 'id' field")
                if "version" not in meta:
                    errors.append("_meta.json missing 'version' field")
        except json.JSONDecodeError as e:
            errors.append(f"_meta.json is not valid JSON: {e}")

    # Check frontmatter in root SKILL.md
    if root_skill.exists():
        with open(root_skill) as f:
            content = f.read()
            if not content.startswith("---"):
                errors.append("SKILL.md must start with YAML frontmatter (---)")

            # Parse frontmatter
            lines = content.split("\n")
            if len(lines) > 2 and lines[1].startswith("name:"):
                name = lines[1].replace("name:", "").strip()
                if not name:
                    errors.append("SKILL.md frontmatter 'name' is empty")
            else:
                errors.append("SKILL.md frontmatter missing 'name' field")

    # Check role directories
    roles_dir = skill_path / "roles"
    if roles_dir.exists():
        for role_dir in roles_dir.iterdir():
            if role_dir.is_dir() and not role_dir.name.startswith("."):
                role_skill = role_dir / "SKILL.md"
                if role_skill.exists():
                    with open(role_skill) as f:
                        content = f.read()
                        if not content.startswith("---"):
                            errors.append(f"{role_skill} must start with YAML frontmatter")

    return errors


def package_skill(skill_path: Path, output_path: Path = None) -> str:
    """Package the skill into a .skill archive."""
    skill_path = Path(skill_path).resolve()

    if not skill_path.exists():
        raise FileNotFoundError(f"Skill path not found: {skill_path}")

    # Validate before packaging
    errors = validate_skill_structure(skill_path)
    if errors:
        print("Validation errors found:")
        for error in errors:
            print(f"  - {error}")
        raise ValueError("Skill validation failed. Please fix errors before packaging.")

    # Generate output filename
    if output_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        skill_name = skill_path.name
        output_path = skill_path.parent / f"{skill_name}_{timestamp}.skill"

    output_path = Path(output_path)

    # Create archive
    with tarfile.open(output_path, "w:gz") as tar:
        # Add root files
        for pattern in ["SKILL.md", "ORCHESTRATOR.md", "_meta.json"]:
            for f in skill_path.glob(pattern):
                tar.add(f, arcname=f.name)

        # Add references
        if (skill_path / "references").exists():
            for f in (skill_path / "references").glob("*.md"):
                tar.add(f, arcname=f"references/{f.name}")

        # Add scripts
        if (skill_path / "scripts").exists():
            for f in (skill_path / "scripts").glob("*.py"):
                tar.add(f, arcname=f"scripts/{f.name}")

        # Add roles
        roles_dir = skill_path / "roles"
        if roles_dir.exists():
            for role_dir in roles_dir.iterdir():
                if role_dir.is_dir() and not role_dir.name.startswith("."):
                    for f in role_dir.glob("*.md"):
                        tar.add(f, arcname=f"roles/{role_dir.name}/{f.name}")
                    meta = role_dir / "_meta.json"
                    if meta.exists():
                        tar.add(meta, arcname=f"roles/{role_dir.name}/_meta.json")

    return str(output_path)


def main():
    parser = argparse.ArgumentParser(description="Package Research Stack skill")
    parser.add_argument("skill_path", help="Path to the skill directory")
    parser.add_argument("--output", "-o", help="Output .skill file path")
    args = parser.parse_args()

    try:
        output_file = package_skill(args.skill_path, args.output)
        print(f"Successfully packaged skill to: {output_file}")
        return 0
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
Skill Packaging Script for Wall Street Quant Team
Packages the skill into a .skill file for distribution
"""

import os
import json
import tarfile
from pathlib import Path

def validate_skill(skill_dir: Path) -> bool:
    """Validate skill structure and frontmatter"""
    print("Validating skill structure...")

    # Check required files
    if not (skill_dir / "SKILL.md").exists():
        print("ERROR: SKILL.md not found")
        return False

    if not (skill_dir / "_meta.json").exists():
        print("ERROR: _meta.json not found")
        return False

    # Validate _meta.json
    with open(skill_dir / "_meta.json") as f:
        meta = json.load(f)

    if "id" not in meta or "version" not in meta:
        print("ERROR: _meta.json must contain 'id' and 'version'")
        return False

    # Validate SKILL.md frontmatter
    with open(skill_dir / "SKILL.md") as f:
        content = f.read()

    if not content.startswith("---"):
        print("ERROR: SKILL.md must start with frontmatter (---)")
        return False

    frontmatter_end = content.find("---", 3)
    if frontmatter_end == -1:
        print("ERROR: SKILL.md frontmatter not properly closed")
        return False

    frontmatter = content[3:frontmatter_end].strip()

    required_fields = ["name:", "description:"]
    for field in required_fields:
        if field not in frontmatter:
            print(f"ERROR: Required field '{field}' missing in frontmatter")
            return False

    print("Validation passed!")
    return True

def package_skill(skill_dir: Path, output_path: Path):
    """Package skill directory into .skill file"""
    print(f"Packaging skill from {skill_dir}...")

    # Create tarball
    with tarfile.open(output_path, "w:gz") as tar:
        tar.add(skill_dir, arcname=skill_dir.name)

    print(f"Packaged skill to: {output_path}")

    # List contents
    with tarfile.open(output_path, "r:gz") as tar:
        print("\nPackage contents:")
        for member in tar.getmembers():
            print(f"  {member.name}")

def main():
    skill_dir = Path("/workspace/temp-skills/wall-street-quant-team")
    output_path = Path("/workspace/temp-skills/wall-street-quant-team.skill")

    if validate_skill(skill_dir):
        package_skill(skill_dir, output_path)
        print("\n✅ Skill packaging successful!")
        print(f"Output: {output_path}")
    else:
        print("\n❌ Validation failed. Please fix errors before packaging.")
        exit(1)

if __name__ == "__main__":
    main()

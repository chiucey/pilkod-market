"""
AI Drama Director Skill - Quick Validation Script
Validates skill structure integrity and naming conventions
"""

import os
import re
import json
from pathlib import Path


def validate_skill_structure(skill_path: str) -> dict:
    """Validate skill directory structure"""
    results = {
        "passed": [],
        "failed": [],
        "warnings": []
    }

    skill_path = Path(skill_path)

    # Check required files
    required_files = ["SKILL.md", "_meta.json"]
    for file in required_files:
        file_path = skill_path / file
        if file_path.exists():
            results["passed"].append(f"OK {file} exists")
        else:
            results["failed"].append(f"FAIL {file} missing")

    # Check SKILL.md frontmatter
    skill_md = skill_path / "SKILL.md"
    if skill_md.exists():
        content = skill_md.read_text(encoding="utf-8")

        # Check starts with ---
        if content.startswith("---"):
            results["passed"].append("OK SKILL.md frontmatter format correct")
        else:
            results["failed"].append("FAIL SKILL.md must start with ---")

        # Extract frontmatter
        frontmatter_match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
        if frontmatter_match:
            frontmatter = frontmatter_match.group(1)

            # Check required fields
            if "name:" in frontmatter:
                results["passed"].append("OK name field exists")
            else:
                results["failed"].append("FAIL name field missing")

            if "description:" in frontmatter:
                results["passed"].append("OK description field exists")
            else:
                results["failed"].append("FAIL description field missing")
        else:
            results["failed"].append("FAIL Cannot parse frontmatter")

    # Check _meta.json
    meta_json = skill_path / "_meta.json"
    if meta_json.exists():
        try:
            meta = json.loads(meta_json.read_text(encoding="utf-8"))
            if "id" in meta:
                results["passed"].append("OK _meta.json contains id")
            else:
                results["failed"].append("FAIL _meta.json missing id")

            if "version" in meta:
                results["passed"].append("OK _meta.json contains version")
            else:
                results["failed"].append("FAIL _meta.json missing version")
        except json.JSONDecodeError:
            results["failed"].append("FAIL _meta.json format error")

    return results


def main():
    import sys

    skill_path = sys.argv[1] if len(sys.argv) > 1 else "/workspace/temp-skills/ai-drama-director"

    print(f"Validating skill: {skill_path}\n")
    results = validate_skill_structure(skill_path)

    print("=== Passed Checks ===")
    for item in results["passed"]:
        print(item)

    if results["failed"]:
        print("\n=== Failed Checks ===")
        for item in results["failed"]:
            print(item)

    if results["warnings"]:
        print("\n=== Warnings ===")
        for item in results["warnings"]:
            print(item)

    # Return exit code
    return 0 if not results["failed"] else 1


if __name__ == "__main__":
    exit(main())

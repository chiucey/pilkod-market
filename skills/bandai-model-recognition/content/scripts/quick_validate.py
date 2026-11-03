#!/usr/bin/env python3
"""
Bandai Model Recognition Skill - Quick Validation Script
Validates SKILL.md structure and content compliance
"""

import os
import json
import re
import sys
from pathlib import Path

def validate_skill(skill_path):
    """Validate skill file structure and content"""
    results = {
        "passed": [],
        "failed": [],
        "warnings": []
    }

    skill_md = Path(skill_path) / "SKILL.md"
    meta_json = Path(skill_path) / "_meta.json"

    # Check 1: SKILL.md exists
    if not skill_md.exists():
        results["failed"].append("SKILL.md file not found")
        return results
    results["passed"].append("SKILL.md file exists")

    # Check 2: Read SKILL.md content
    content = skill_md.read_text(encoding="utf-8")

    # Check 3: Frontmatter must start at first line
    if not content.startswith("---"):
        results["failed"].append("Frontmatter must start at file first line")
    else:
        results["passed"].append("Frontmatter format correct")

    # Check 4: Parse frontmatter
    fm_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if fm_match:
        fm_text = fm_match.group(1)

        # Check required fields
        if "name:" in fm_text:
            results["passed"].append("name field exists")
            name_match = re.search(r'name:\s*(.+)', fm_text)
            if name_match:
                name = name_match.group(1).strip()
                if len(name) <= 64:
                    results["passed"].append(f"name length compliant: {len(name)} chars")
                else:
                    results["failed"].append(f"name exceeds 64 chars: {len(name)}")
        else:
            results["failed"].append("name field missing")

        if "description:" in fm_text:
            results["passed"].append("description field exists")
        else:
            results["failed"].append("description field missing")
    else:
        results["failed"].append("Cannot parse frontmatter")

    # Check 5: _meta.json validation
    if not meta_json.exists():
        results["failed"].append("_meta.json file not found")
    else:
        results["passed"].append("_meta.json file exists")
        try:
            meta = json.loads(meta_json.read_text(encoding="utf-8"))
            if "id" in meta:
                results["passed"].append("meta.id field exists")
            else:
                results["failed"].append("meta missing id field")

            if "version" in meta:
                results["passed"].append("meta.version field exists")
            else:
                results["failed"].append("meta missing version field")
        except json.JSONDecodeError as e:
            results["failed"].append(f"_meta.json JSON format error: {e}")

    # Check 6: Directory structure
    references_dir = Path(skill_path) / "references"
    scripts_dir = Path(skill_path) / "scripts"

    if references_dir.exists():
        results["passed"].append("references directory exists")
        md_files = list(references_dir.glob("*.md"))
        results["warnings"].append(f"references directory contains {len(md_files)} markdown files")
    else:
        results["warnings"].append("references directory does not exist (optional)")

    if scripts_dir.exists():
        results["passed"].append("scripts directory exists")
    else:
        results["warnings"].append("scripts directory does not exist (optional)")

    return results

def main():
    skill_path = "/workspace/temp-skills/bandai-model-recognition"

    if len(sys.argv) > 1:
        skill_path = sys.argv[1]

    print("=" * 50)
    print("Bandai Model Recognition Skill - Validation Report")
    print("=" * 50)
    print(f"Validation path: {skill_path}\n")

    results = validate_skill(skill_path)

    print("Passed items:")
    for item in results["passed"]:
        print(f"  + {item}")

    if results["warnings"]:
        print("\nWarnings:")
        for item in results["warnings"]:
            print(f"  ! {item}")

    if results["failed"]:
        print("\nFailed items:")
        for item in results["failed"]:
            print(f"  - {item}")
        print("\nResult: FAILED")
        sys.exit(1)
    else:
        print("\nResult: ALL PASSED")
        sys.exit(0)

if __name__ == "__main__":
    main()

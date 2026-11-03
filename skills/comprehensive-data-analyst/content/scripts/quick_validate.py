#!/usr/bin/env python3
"""
Quality validation script for Comprehensive Data Analyst skill.
Validates frontmatter format, structure, and required fields.
"""

import os
import re
import sys

def validate_frontmatter(skill_path: str) -> dict:
    """Validate SKILL.md frontmatter format and required fields."""
    errors = []
    warnings = []

    skill_md_path = os.path.join(skill_path, "SKILL.md")

    if not os.path.exists(skill_md_path):
        errors.append(f"SKILL.md not found at {skill_md_path}")
        return {"valid": False, "errors": errors, "warnings": warnings}

    with open(skill_md_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Check 1: File must start with ---
    if not content.startswith("---"):
        errors.append("SKILL.md must start with YAML frontmatter (---)")

    # Extract frontmatter
    lines = content.split("\n")
    if len(lines) < 3 or lines[0] != "---":
        errors.append("Invalid frontmatter structure")
        return {"valid": False, "errors": errors, "warnings": warnings}

    # Find end of frontmatter
    end_idx = None
    for i, line in enumerate(lines[1:], 1):
        if line.strip() == "---":
            end_idx = i
            break

    if end_idx is None:
        errors.append("Frontmatter not closed with ---")
        return {"valid": False, "errors": errors, "warnings": warnings}

    # Parse frontmatter
    frontmatter_lines = lines[1:end_idx]
    frontmatter_text = "\n".join(frontmatter_lines)

    # Check required fields
    if not re.search(r"^name:\s*.+$", frontmatter_text, re.MULTILINE):
        errors.append("Missing required field: name")

    if not re.search(r"^description:\s*.+$", frontmatter_text, re.MULTILINE):
        errors.append("Missing required field: description")

    # Extract name for further validation
    name_match = re.search(r"^name:\s*(.+)$", frontmatter_text, re.MULTILINE)
    if name_match:
        name = name_match.group(1).strip()
        # Check name format (hyphen-case)
        if not re.match(r"^[a-z0-9]+(-[a-z0-9]+)*$", name):
            errors.append(f"Name must be hyphen-case: '{name}'")
        # Check name length
        if len(name) > 64:
            warnings.append(f"Name length ({len(name)}) exceeds recommended 64 characters")

    # Extract description for further validation
    desc_match = re.search(r"^description:\s*(.+)$", frontmatter_text, re.MULTILINE)
    if desc_match:
        desc = desc_match.group(1).strip()
        # Check description ends with proper trigger phrase
        if not desc.endswith("。"):
            warnings.append("Description should end with '。' (Chinese period)")
        if "c.li2024@outlook.com" not in desc:
            warnings.append("Description should include contact email")

    # Check 2: No markdown heading before frontmatter
    if re.search(r"^#\s+\w+", content):
        # Make sure there's no # before the first ---
        first_line = content.split("\n")[0]
        if not first_line.startswith("---") and first_line.startswith("#"):
            errors.append("Markdown heading (#) found before frontmatter")

    # Check 3: No content after frontmatter before another ---
    if end_idx + 1 < len(lines):
        next_line = lines[end_idx + 1].strip()
        if next_line.startswith("#") and "---" not in content[:content.find("\n" + next_line)]:
            pass  # This is the main title, which is correct
        elif next_line and not next_line.startswith("```") and not next_line.startswith("|"):
            pass  # Content continues normally

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings
    }

def validate_meta_json(skill_path: str) -> dict:
    """Validate _meta.json exists and has required fields."""
    errors = []

    meta_path = os.path.join(skill_path, "_meta.json")

    if not os.path.exists(meta_path):
        errors.append("_meta.json not found")
        return {"valid": False, "errors": errors}

    import json
    with open(meta_path, "r", encoding="utf-8") as f:
        try:
            meta = json.load(f)
        except json.JSONDecodeError as e:
            errors.append(f"Invalid JSON in _meta.json: {e}")
            return {"valid": False, "errors": errors}

    # Check required fields
    if "id" not in meta:
        errors.append("Missing required field in _meta.json: id")
    if "version" not in meta:
        errors.append("Missing required field in _meta.json: version")

    # Validate id format
    if "id" in meta:
        if not isinstance(meta["id"], str):
            errors.append("_meta.json id must be a string")

    # Validate version format (semver)
    if "version" in meta:
        version = meta["version"]
        if not re.match(r"^\d+\.\d+\.\d+$", version):
            errors.append(f"Version should follow semver format (x.y.z): {version}")

    return {
        "valid": len(errors) == 0,
        "errors": errors
    }

def validate_structure(skill_path: str) -> dict:
    """Validate directory structure."""
    errors = []
    warnings = []

    # Check skill directory exists
    if not os.path.isdir(skill_path):
        errors.append(f"Skill directory not found: {skill_path}")
        return {"valid": False, "errors": errors, "warnings": warnings}

    # Check for required files
    required_files = ["SKILL.md", "_meta.json"]
    for fname in required_files:
        fpath = os.path.join(skill_path, fname)
        if not os.path.exists(fpath):
            errors.append(f"Required file missing: {fname}")

    # Check for optional directories
    references_path = os.path.join(skill_path, "references")
    if os.path.isdir(references_path):
        # Check references are not empty
        ref_files = [f for f in os.listdir(references_path) if os.path.isfile(os.path.join(references_path, f))]
        if not ref_files:
            warnings.append("references/ directory exists but is empty")

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings
    }

def main():
    skill_path = os.path.dirname(os.path.abspath(__file__))
    skill_path = os.path.dirname(skill_path)  # Go up from scripts/

    print("=" * 60)
    print("Comprehensive Data Analyst - Quality Validation")
    print("=" * 60)

    all_valid = True

    # Run validations
    print("\n[1/3] Validating structure...")
    struct_result = validate_structure(skill_path)
    if struct_result["valid"]:
        print("    ✅ Structure validation passed")
    else:
        print("    ❌ Structure validation failed:")
        for err in struct_result["errors"]:
            print(f"       - {err}")
        all_valid = False

    print("\n[2/3] Validating frontmatter...")
    fm_result = validate_frontmatter(skill_path)
    if fm_result["valid"]:
        print("    ✅ Frontmatter validation passed")
    else:
        print("    ❌ Frontmatter validation failed:")
        for err in fm_result["errors"]:
            print(f"       - {err}")
        all_valid = False
    if fm_result["warnings"]:
        print("    ⚠️  Warnings:")
        for warn in fm_result["warnings"]:
            print(f"       - {warn}")

    print("\n[3/3] Validating _meta.json...")
    meta_result = validate_meta_json(skill_path)
    if meta_result["valid"]:
        print("    ✅ _meta.json validation passed")
    else:
        print("    ❌ _meta.json validation failed:")
        for err in meta_result["errors"]:
            print(f"       - {err}")
        all_valid = False

    print("\n" + "=" * 60)
    if all_valid:
        print("✅ All validations passed!")
        return 0
    else:
        print("❌ Validation failed. Please fix errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
Quick validation script for skill quality checks.
Validates frontmatter, structure, and naming conventions.
"""

import json
import os
import re
import sys
from pathlib import Path


class SkillValidator:
    """Validates skill structure and frontmatter compliance."""

    def __init__(self, skill_path: str):
        self.skill_path = Path(skill_path)
        self.errors = []
        self.warnings = []
        self.passed = []

    def validate_all(self) -> bool:
        """Run all validation checks."""
        print(f"Validating skill at: {self.skill_path}")
        print("=" * 50)

        checks = [
            ("Directory structure", self.check_directory_structure),
            ("SKILL.md exists", self.check_skill_md_exists),
            ("Frontmatter format", self.check_frontmatter),
            ("_meta.json exists", self.check_meta_json),
            ("Naming conventions", self.check_naming_conventions),
            ("Path validation", self.check_paths_english_only),
        ]

        all_passed = True
        for name, check_func in checks:
            try:
                result = check_func()
                if result:
                    self.passed.append(name)
                    print(f"[PASS] {name}")
                else:
                    all_passed = False
            except Exception as e:
                self.errors.append(f"{name}: {str(e)}")
                print(f"[ERROR] {name}: {str(e)}")
                all_passed = False

        self.print_summary()
        return all_passed

    def check_directory_structure(self) -> bool:
        """Check if required directories exist."""
        required_dirs = ["."]
        for dir_name in required_dirs:
            dir_path = self.skill_path / dir_name
            if not dir_path.exists():
                self.errors.append(f"Directory does not exist: {dir_name}")
                return False
        return True

    def check_skill_md_exists(self) -> bool:
        """Check if SKILL.md exists and is readable."""
        skill_md = self.skill_path / "SKILL.md"
        if not skill_md.exists():
            self.errors.append("SKILL.md not found")
            return False

        content = skill_md.read_text(encoding="utf-8")
        if len(content.strip()) < 100:
            self.errors.append("SKILL.md is too short or empty")
            return False

        return True

    def check_frontmatter(self) -> bool:
        """Validate frontmatter format and required fields."""
        skill_md = self.skill_path / "SKILL.md"
        content = skill_md.read_text(encoding="utf-8")

        # Check if file starts with ---
        if not content.startswith("---"):
            self.errors.append("SKILL.md must start with --- (frontmatter delimiter)")
            return False

        # Extract frontmatter
        lines = content.split("\n")
        frontmatter_end = -1
        for i, line in enumerate(lines):
            if i > 0 and line.strip() == "---":
                frontmatter_end = i
                break

        if frontmatter_end == -1:
            self.errors.append("Frontmatter closing --- not found")
            return False

        frontmatter_text = "\n".join(lines[1:frontmatter_end])

        # Check required fields
        required_fields = ["name", "description"]
        for field in required_fields:
            pattern = rf"^{field}:\s*.+"
            if not re.search(pattern, frontmatter_text, re.MULTILINE):
                self.errors.append(f"Required frontmatter field '{field}' is missing")
                return False

        # Extract name and verify format
        name_match = re.search(r"^name:\s*(.+)", frontmatter_text, re.MULTILINE)
        if name_match:
            name = name_match.group(1).strip()
            if not re.match(r"^[a-z0-9-]+$", name):
                self.errors.append(f"Name '{name}' must be lowercase with hyphens only")
                return False

            # Check name matches folder name
            folder_name = self.skill_path.name
            if name != folder_name:
                self.errors.append(f"Frontmatter name '{name}' does not match folder name '{folder_name}'")
                return False

        # Check description length
        desc_match = re.search(r"^description:\s*(.+)", frontmatter_text, re.MULTILINE)
        if desc_match:
            desc = desc_match.group(1).strip()
            if len(desc) < 20:
                self.warnings.append("Description is too short (< 20 characters)")
            if len(desc) > 500:
                self.warnings.append("Description is very long (> 500 characters)")

        return True

    def check_meta_json(self) -> bool:
        """Check if _meta.json exists and has valid structure."""
        meta_path = self.skill_path / "_meta.json"
        if not meta_path.exists():
            self.errors.append("_meta.json not found")
            return False

        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))

            # Check required fields
            required_fields = ["id", "version"]
            for field in required_fields:
                if field not in meta:
                    self.errors.append(f"_meta.json missing required field: {field}")
                    return False

            # Validate id is a number/string
            if not isinstance(meta["id"], (str, int)):
                self.errors.append("_meta.json 'id' must be string or number")
                return False

            # Validate version format
            version = str(meta["version"])
            if not re.match(r"^\d+\.\d+\.\d+$", version):
                self.warnings.append(f"Version '{version}' should follow semantic versioning (x.y.z)")

            return True
        except json.JSONDecodeError as e:
            self.errors.append(f"_meta.json is not valid JSON: {e}")
            return False

    def check_naming_conventions(self) -> bool:
        """Check that all file and directory names are English only."""
        invalid_names = []
        for root, dirs, files in os.walk(self.skill_path):
            for name in dirs + files:
                # Skip hidden files and common non-code files
                if name.startswith(".") or name in ["__pycache__"]:
                    continue
                # Check for non-ASCII characters
                if not name.isascii():
                    invalid_names.append(name)

        if invalid_names:
            self.errors.append(f"Non-English names found: {invalid_names}")
            return False

        return True

    def check_paths_english_only(self) -> bool:
        """Verify all paths use English characters only."""
        for item in self.skill_path.rglob("*"):
            if not item.name.isascii() and item.is_dir():
                self.errors.append(f"Non-ASCII directory name: {item}")
                return False
        return True

    def print_summary(self):
        """Print validation summary."""
        print("\n" + "=" * 50)
        print("VALIDATION SUMMARY")
        print("=" * 50)

        if self.passed:
            print(f"\nPassed ({len(self.passed)}):")
            for item in self.passed:
                print(f"  - {item}")

        if self.warnings:
            print(f"\nWarnings ({len(self.warnings)}):")
            for item in self.warnings:
                print(f"  - {item}")

        if self.errors:
            print(f"\nErrors ({len(self.errors)}):")
            for item in self.errors:
                print(f"  - {item}")
            print("\n[FAILED] Validation failed with errors")
        else:
            print("\n[SUCCESS] All validation checks passed!")


def main():
    if len(sys.argv) < 2:
        print("Usage: python quick_validate.py <skill_path>")
        sys.exit(1)

    skill_path = sys.argv[1]
    validator = SkillValidator(skill_path)
    success = validator.validate_all()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

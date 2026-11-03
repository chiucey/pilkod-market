#!/usr/bin/env python3
"""
Quick validation script for research-to-ppt skill.
Checks frontmatter, structure, and naming conventions.
"""

import os
import re
import sys
import json
from pathlib import Path


class ValidationError:
    def __init__(self, level, message, file=None, line=None):
        self.level = level
        self.message = message
        self.file = file
        self.line = line

    def __str__(self):
        location = f"{self.file}:{self.line}" if self.file and self.line else self.file or "unknown"
        return f"[{self.level.upper()}] {location}: {self.message}"


class SkillValidator:
    def __init__(self, skill_path):
        self.skill_path = Path(skill_path)
        self.errors = []
        self.warnings = []

    def validate(self):
        """Run all validation checks."""
        print(f"Validating skill at: {self.skill_path}")
        print("=" * 60)

        self.check_directory_structure()
        self.check_skill_md()
        self.check_meta_json()
        self.check_references()
        self.check_scripts()

        self.print_results()
        return len(self.errors) == 0

    def check_directory_structure(self):
        """Check if required directories exist."""
        required_dirs = ["scripts", "references"]

        for dir_name in required_dirs:
            dir_path = self.skill_path / dir_name
            if not dir_path.exists():
                self.warnings.append(ValidationError("warning", f"Optional directory '{dir_name}' not found"))
            else:
                print(f"✓ Directory '{dir_name}' exists")

    def check_skill_md(self):
        """Validate SKILL.md frontmatter and content."""
        skill_md = self.skill_path / "SKILL.md"

        if not skill_md.exists():
            self.errors.append(ValidationError("error", "SKILL.md not found", str(skill_md)))
            return

        print("✓ SKILL.md found")

        content = skill_md.read_text(encoding="utf-8")

        # Check frontmatter is at the beginning
        if not content.startswith("---"):
            self.errors.append(ValidationError("error", "SKILL.md must start with YAML frontmatter (---)",
                                               str(skill_md), 1))
            return

        # Extract frontmatter
        match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
        if not match:
            self.errors.append(ValidationError("error", "Invalid frontmatter format", str(skill_md)))
            return

        frontmatter_text = match.group(1)
        frontmatter = self._parse_yaml_simple(frontmatter_text)

        # Check required fields
        required_fields = ["name", "description"]
        for field in required_fields:
            if field not in frontmatter:
                self.errors.append(ValidationError("error", f"Missing required frontmatter field: {field}",
                                                   str(skill_md)))
            else:
                print(f"✓ Frontmatter '{field}' present")

        # Validate name format (hyphen-case, <=64 chars)
        if "name" in frontmatter:
            name = frontmatter["name"]
            if not re.match(r'^[a-z0-9-]+$', name):
                self.errors.append(ValidationError("error", f"Name '{name}' must be lowercase with hyphens only",
                                                   str(skill_md)))
            if len(name) > 64:
                self.errors.append(ValidationError("error", f"Name '{name}' exceeds 64 characters",
                                                   str(skill_md)))

        # Check name matches directory
        expected_name = self.skill_path.name
        if "name" in frontmatter and frontmatter["name"] != expected_name:
            self.errors.append(ValidationError("error",
                                               f"Name '{frontmatter['name']}' in frontmatter doesn't match directory '{expected_name}'",
                                               str(skill_md)))

    def check_meta_json(self):
        """Validate _meta.json file."""
        meta_json = self.skill_path / "_meta.json"

        if not meta_json.exists():
            self.errors.append(ValidationError("error", "_meta.json not found", str(meta_json)))
            return

        print("✓ _meta.json found")

        try:
            meta = json.loads(meta_json.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            self.errors.append(ValidationError("error", f"Invalid JSON: {e}", str(meta_json)))
            return

        # Check required fields
        required_fields = ["id", "version"]
        for field in required_fields:
            if field not in meta:
                self.errors.append(ValidationError("error", f"Missing required field: {field}", str(meta_json)))
            else:
                print(f"✓ _meta.json '{field}' present")

        # Validate id is integer
        if "id" in meta and not isinstance(meta["id"], int):
            self.errors.append(ValidationError("error", "id must be an integer", str(meta_json)))

        # Validate version format (semver)
        if "version" in meta:
            if not re.match(r'^\d+\.\d+\.\d+$', meta["version"]):
                self.errors.append(ValidationError("error", "version must follow semver format (e.g., 1.0.0)",
                                                   str(meta_json)))

    def check_references(self):
        """Check reference files referenced in SKILL.md exist."""
        skill_md = self.skill_path / "SKILL.md"
        if not skill_md.exists():
            return

        content = skill_md.read_text(encoding="utf-8")

        # Find all reference links like [xxx.md](references/xxx.md)
        pattern = r'\[([^\]]+)\]\((references/[^\)]+\.md)\)'
        matches = re.findall(pattern, content)

        refs_dir = self.skill_path / "references"
        if not refs_dir.exists():
            if matches:
                self.warnings.append(ValidationError("warning", "references directory not found but referenced in SKILL.md"))
            return

        for name, path in matches:
            ref_file = self.skill_path / path
            if not ref_file.exists():
                self.warnings.append(ValidationError("warning", f"Referenced file '{path}' not found"))
            else:
                print(f"✓ Reference '{name}' exists")

    def check_scripts(self):
        """Check scripts if they exist."""
        scripts_dir = self.skill_path / "scripts"

        expected_scripts = ["quick_validate.py", "package_skill.py"]
        for script_name in expected_scripts:
            script_path = scripts_dir / script_name
            if script_path.exists():
                print(f"✓ Script '{script_name}' exists")

                # Check if script is executable or has shebang
                content = script_path.read_text(encoding="utf-8")
                if not content.startswith("#!"):
                    self.warnings.append(ValidationError("warning", f"Script '{script_name}' missing shebang line"))

    def _parse_yaml_simple(self, yaml_text):
        """Simple YAML parser for frontmatter only."""
        result = {}
        current_key = None
        current_value = []
        in_list = False
        list_items = []

        for line in yaml_text.split('\n'):
            # Check for list item
            if line.startswith('  - '):
                list_items.append(line[4:].strip().strip('"').strip("'"))
                in_list = True
                continue

            # End of list
            if in_list and not line.startswith('  '):
                if list_items:
                    result[current_key] = list_items
                list_items = []
                in_list = False

            # Key-value pair
            match = re.match(r'^([a-z_]+):\s*(.*)$', line.strip())
            if match:
                key, value = match.groups()

                # Save previous list
                if list_items:
                    result[current_key] = list_items
                    list_items = []

                current_key = key
                value = value.strip().strip('"').strip("'")
                if value:
                    result[key] = value
                in_list = False

        # Save last list
        if list_items and current_key:
            result[current_key] = list_items

        return result

    def print_results(self):
        """Print validation results."""
        print("=" * 60)

        if self.warnings:
            print(f"\nWarnings ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  {warning}")

        if self.errors:
            print(f"\nErrors ({len(self.errors)}):")
            for error in self.errors:
                print(f"  {error}")
            print(f"\n❌ Validation FAILED with {len(self.errors)} error(s)")
        else:
            print("\n✅ Validation PASSED - No errors found")


def main():
    if len(sys.argv) < 2:
        # Default to current directory
        skill_path = Path(__file__).parent.parent
    else:
        skill_path = Path(sys.argv[1])

    validator = SkillValidator(skill_path)
    success = validator.validate()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

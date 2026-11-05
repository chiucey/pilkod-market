#!/usr/bin/env python3
"""
Quick validation script for skill packages.
Validates SKILL.md frontmatter, _meta.json, and directory structure.
"""

import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple


class ValidationError:
    def __init__(self, message: str, severity: str = "error"):
        self.message = message
        self.severity = severity

    def __str__(self):
        return f"[{self.severity.upper()}] {self.message}"


class SkillValidator:
    REQUIRED_META_KEYS = ["id", "version"]
    REQUIRED_FRONTMATTER_KEYS = ["name", "description"]
    ALLOWED_TOOLS = ["Read", "Write", "Edit", "Grep", "Glob", "AskUserQuestion",
                     "Bash", "TodoWrite", "Task", "mcp__matrix__*"]

    def __init__(self, skill_path: str):
        self.skill_path = Path(skill_path)
        self.errors: List[ValidationError] = []
        self.warnings: List[ValidationError] = []

    def validate_all(self) -> bool:
        """Run all validations and return True if all pass."""
        self._validate_structure()
        self._validate_meta_json()
        self._validate_skill_md()

        has_errors = len(self.errors) > 0
        if has_errors:
            print("\n❌ Validation FAILED")
        else:
            print("\n✅ Validation PASSED")

        return not has_errors

    def _validate_structure(self):
        """Check directory structure."""
        if not self.skill_path.exists():
            self.errors.append(ValidationError(f"Skill path does not exist: {self.skill_path}"))
            return

        required_files = ["SKILL.md", "_meta.json"]
        for fname in required_files:
            fpath = self.skill_path / fname
            if not fpath.exists():
                self.errors.append(ValidationError(f"Missing required file: {fname}"))

    def _validate_meta_json(self):
        """Validate _meta.json format and content."""
        meta_path = self.skill_path / "_meta.json"
        if not meta_path.exists():
            return

        try:
            with open(meta_path, 'r', encoding='utf-8') as f:
                meta = json.load(f)
        except json.JSONDecodeError as e:
            self.errors.append(ValidationError(f"Invalid JSON in _meta.json: {e}"))
            return

        # Check required keys
        for key in self.REQUIRED_META_KEYS:
            if key not in meta:
                self.errors.append(ValidationError(f"Missing required key in _meta.json: {key}"))

        # Validate version format
        if "version" in meta:
            version = meta["version"]
            if not re.match(r'^\d+\.\d+\.\d+$', version):
                self.errors.append(ValidationError(f"Invalid version format: {version} (expected semver)"))

        # Check for ownerId and slug (should be present)
        if "ownerId" not in meta:
            self.warnings.append(ValidationError("Missing ownerId in _meta.json"))
        if "slug" not in meta:
            self.warnings.append(ValidationError("Missing slug in _meta.json"))

    def _validate_skill_md(self):
        """Validate SKILL.md frontmatter."""
        skill_path = self.skill_path / "SKILL.md"
        if not skill_path.exists():
            return

        with open(skill_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check frontmatter at start
        if not content.startswith('---'):
            self.errors.append(ValidationError("SKILL.md must start with YAML frontmatter (---)"))
            return

        # Extract frontmatter
        frontmatter_end = content.find('\n---\n')
        if frontmatter_end == -1:
            # Try single line ---
            if content.startswith('---') and content[3:4] == '\n':
                next_dash = content.find('\n---', 4)
                if next_dash != -1:
                    frontmatter_end = next_dash
                else:
                    self.errors.append(ValidationError("Cannot find closing --- in frontmatter"))
                    return
            else:
                self.errors.append(ValidationError("Invalid frontmatter format"))
                return

        frontmatter_text = content[3:frontmatter_end].strip()
        frontmatter: Dict[str, str] = {}

        # Parse frontmatter
        for line in frontmatter_text.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                frontmatter[key.strip()] = value.strip().strip('"\'')

        # Check required keys
        for key in self.REQUIRED_FRONTMATTER_KEYS:
            if key not in frontmatter:
                self.errors.append(ValidationError(f"Missing required frontmatter key: {key}"))

        # Validate name format (hyphen-case, <= 64 chars)
        if "name" in frontmatter:
            name = frontmatter["name"]
            if not re.match(r'^[a-z0-9]+(?:-[a-z0-9]+)*$', name):
                self.errors.append(ValidationError(f"Invalid name format: {name} (use hyphen-case)"))
            if len(name) > 64:
                self.errors.append(ValidationError(f"Name too long: {len(name)} chars (max 64)"))

        # Validate description (should have trigger phrases)
        if "description" in frontmatter:
            desc = frontmatter["description"]
            if len(desc) < 10:
                self.errors.append(ValidationError("Description too short (< 10 chars)"))
            if "触发词" not in desc and "Trigger" not in desc.lower():
                self.warnings.append(ValidationError("Description should include trigger phrases (触发词/Trigger)"))

        # Check allowed-tools if present
        if "allowed-tools" in frontmatter:
            tools_str = content[content.find("allowed-tools:"):]
            tools_str = tools_str[:tools_str.find('\n\n') if '\n\n' in tools_str else len(tools_str)]
            # Basic check - tools should be listed
            pass

    def print_report(self):
        """Print validation report."""
        print("\n" + "="*50)
        print("VALIDATION REPORT")
        print("="*50)

        if self.warnings:
            print(f"\n⚠️  Warnings ({len(self.warnings)}):")
            for w in self.warnings:
                print(f"  {w}")

        if self.errors:
            print(f"\n❌ Errors ({len(self.errors)}):")
            for e in self.errors:
                print(f"  {e}")
        elif not self.warnings:
            print("\n✅ No issues found")


def main():
    if len(sys.argv) < 2:
        print("Usage: python quick_validate.py <skill_path>")
        sys.exit(1)

    skill_path = sys.argv[1]
    validator = SkillValidator(skill_path)
    success = validator.validate_all()
    validator.print_report()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

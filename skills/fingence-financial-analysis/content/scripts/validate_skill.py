#!/usr/bin/env python3
"""
Fingence Financial Analysis Skill Validator
Validates SKILL.md frontmatter, structure, and references integrity
"""

import os
import re
import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Any

# ANSI color codes
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'
BOLD = '\033[1m'

class SkillValidator:
    def __init__(self, skill_path: str):
        self.skill_path = Path(skill_path)
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.passed: List[str] = []

    def run_all(self) -> bool:
        """Run all validation checks"""
        print(f"\n{BOLD}🔍 Validating Skill: {self.skill_path.name}{RESET}\n")

        # Run checks
        self.check_frontmatter()
        self.check_meta_json()
        self.check_naming()
        self.check_references()
        self.check_required_sections()

        # Report
        self.print_report()

        return len(self.errors) == 0

    def check_frontmatter(self):
        """Verify SKILL.md has valid frontmatter"""
        skill_md = self.skill_path / "SKILL.md"

        if not skill_md.exists():
            self.errors.append("SKILL.md not found")
            return

        content = skill_md.read_text(encoding='utf-8')

        # Check 1: Must start with ---
        if not content.startswith('---'):
            self.errors.append("SKILL.md must start with YAML frontmatter (---)")
            return

        # Extract frontmatter
        lines = content.split('\n')
        frontmatter_lines = []
        in_frontmatter = False

        for i, line in enumerate(lines):
            if line.strip() == '---' and not in_frontmatter:
                in_frontmatter = True
                continue
            elif line.strip() == '---' and in_frontmatter:
                break
            if in_frontmatter:
                frontmatter_lines.append((i + 1, line))

        # Parse frontmatter
        frontmatter = {}
        for line_num, line in frontmatter_lines:
            if ':' in line:
                key, value = line.split(':', 1)
                frontmatter[key.strip()] = value.strip()

        # Check required fields
        required_fields = ['name', 'description']
        for field in required_fields:
            if field not in frontmatter:
                self.errors.append(f"Frontmatter missing required field: {field}")
            else:
                self.passed.append(f"Frontmatter has '{field}'")

        # Check name format (hyphen-case)
        if 'name' in frontmatter:
            name = frontmatter['name']
            if not re.match(r'^[a-z0-9]+(?:-[a-z0-9]+)*$', name):
                self.errors.append(f"Name '{name}' should be hyphen-case (e.g., 'my-skill')")
            else:
                self.passed.append(f"Name format is valid: {name}")

        # Check description triggers
        if 'description' in frontmatter:
            desc = frontmatter['description']
            if 'Use when' not in desc and 'when' not in desc.lower():
                self.warnings.append("Description should contain trigger phrases like 'Use when...'")
            else:
                self.passed.append("Description contains trigger phrases")

        # Check for markdown title before frontmatter
        if content.startswith('#'):
            self.errors.append("Markdown title (#) should NOT appear before frontmatter")

    def check_meta_json(self):
        """Verify _meta.json exists and is valid"""
        meta_path = self.skill_path / "_meta.json"

        if not meta_path.exists():
            self.errors.append("_meta.json not found")
            return

        try:
            meta = json.loads(meta_path.read_text(encoding='utf-8'))

            required_fields = ['id', 'version']
            for field in required_fields:
                if field not in meta:
                    self.errors.append(f"_meta.json missing required field: {field}")
                else:
                    self.passed.append(f"_meta.json has '{field}': {meta[field]}")

            # Validate id is integer
            if 'id' in meta:
                if not isinstance(meta['id'], int):
                    self.errors.append(f"_meta.json id should be integer, got {type(meta['id'])}")
                else:
                    self.passed.append(f"ID is valid integer: {meta['id']}")

            # Validate version format
            if 'version' in meta:
                version = meta['version']
                if not re.match(r'^\d+\.\d+\.\d+$', version):
                    self.warnings.append(f"Version '{version}' should follow semantic versioning (x.y.z)")
                else:
                    self.passed.append(f"Version format valid: {version}")

        except json.JSONDecodeError as e:
            self.errors.append(f"_meta.json is not valid JSON: {e}")

    def check_naming(self):
        """Check folder name matches frontmatter name"""
        skill_md = self.skill_path / "SKILL.md"

        if not skill_md.exists():
            return

        # Get folder name
        folder_name = self.skill_path.name

        # Skip check if folder name is empty (running from .)
        if not folder_name:
            self.passed.append("Skipped folder name check (running from current directory)")
            return

        # Get frontmatter name
        content = skill_md.read_text(encoding='utf-8')
        match = re.search(r'^name:\s*(.+)$', content, re.MULTILINE)

        if match:
            frontmatter_name = match.group(1).strip()
            if folder_name != frontmatter_name:
                self.errors.append(f"Folder name '{folder_name}' should match frontmatter name '{frontmatter_name}'")
            else:
                self.passed.append(f"Folder name matches frontmatter name")

    def check_references(self):
        """Verify references directory and files"""
        ref_path = self.skill_path / "references"

        if not ref_path.exists():
            self.warnings.append("references/ directory not found (optional but recommended)")
            return

        if not ref_path.is_dir():
            self.errors.append("references should be a directory")
            return

        # Check for expected reference files
        expected_files = [
            'financial-functions.md',
            'analysis-models.md',
            'suggestion-templates.md'
        ]

        ref_files = list(ref_path.glob("*.md"))

        for exp_file in expected_files:
            found = any(f.name == exp_file for f in ref_files)
            if found:
                self.passed.append(f"Found reference file: {exp_file}")
            else:
                self.warnings.append(f"Missing recommended reference: {exp_file}")

    def check_required_sections(self):
        """Check SKILL.md contains required sections"""
        skill_md = self.skill_path / "SKILL.md"

        if not skill_md.exists():
            return

        content = skill_md.read_text(encoding='utf-8')

        required_sections = [
            ('工作流程', 'Workflow section'),
            ('数据接入', 'Data input section'),
            ('函数计算', 'Financial functions section'),
            ('分析', 'Analysis section'),
            ('建议', 'Suggestion section'),
        ]

        for keyword, section_name in required_sections:
            if keyword in content:
                self.passed.append(f"Found section: {section_name}")
            else:
                self.warnings.append(f"Missing section: {section_name}")

    def print_report(self):
        """Print validation report"""
        print(f"{BOLD}{'='*60}{RESET}")

        if self.errors:
            print(f"\n{RED}{BOLD}❌ ERRORS ({len(self.errors)}){RESET}")
            for err in self.errors:
                print(f"  {RED}✗{RESET} {err}")

        if self.warnings:
            print(f"\n{YELLOW}{BOLD}⚠️ WARNINGS ({len(self.warnings)}){RESET}")
            for warn in self.warnings:
                print(f"  {YELLOW}⚠{RESET} {warn}")

        if self.passed:
            print(f"\n{GREEN}{BOLD}✅ PASSED ({len(self.passed)}){RESET}")
            for p in self.passed[:10]:  # Show first 10
                print(f"  {GREEN}✓{RESET} {p}")
            if len(self.passed) > 10:
                print(f"  {GREEN}... and {len(self.passed) - 10} more{RESET}")

        print(f"\n{BOLD}{'='*60}{RESET}")

        if not self.errors:
            print(f"\n{GREEN}{BOLD}🎉 Validation PASSED!{RESET}")
        else:
            print(f"\n{RED}{BOLD}❌ Validation FAILED!{RESET}")
            sys.exit(1)

def main():
    if len(sys.argv) > 1:
        skill_path = sys.argv[1]
    else:
        # Default to current directory
        skill_path = "."

    validator = SkillValidator(skill_path)
    success = validator.run_all()

    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()

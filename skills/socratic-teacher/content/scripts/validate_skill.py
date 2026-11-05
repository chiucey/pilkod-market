#!/usr/bin/env python3
"""
Skill Validator for Socratic Teacher Skill

Validates the skill structure, frontmatter, and quality standards.
"""

import os
import sys
import json
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# ANSI color codes
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
BOLD = '\033[1m'
RESET = '\033[0m'

class SkillValidator:
    def __init__(self, skill_path: str):
        self.skill_path = Path(skill_path)
        self.skill_name = self.skill_path.name
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.passed: List[str] = []

    def validate_all(self) -> bool:
        """Run all validations"""
        print(f"\n{BOLD}{'='*60}{RESET}")
        print(f"{BOLD}🔍 Validating Skill: {self.skill_name}{RESET}")
        print(f"{BOLD}{'='*60}{RESET}\n")

        checks = [
            ("Directory Structure", self.check_directory_structure),
            ("SKILL.md Existence", self.check_skill_md_exists),
            ("SKILL.md Frontmatter", self.check_frontmatter),
            ("_meta.json Existence", self.check_meta_json_exists),
            ("_meta.json Validity", self.check_meta_json_valid),
            ("Frontmatter Name Match", self.check_name_consistency),
            ("Frontmatter Description", self.check_description_quality),
            ("Trigger Phrases", self.check_trigger_phrases),
            ("No Non-English Paths", self.check_path_names),
            ("File Content Encoding", self.check_file_encoding),
        ]

        all_passed = True
        for name, check_func in checks:
            print(f"Checking: {name}...", end=" ")
            try:
                passed = check_func()
                if passed:
                    print(f"{GREEN}✓ PASS{RESET}")
                    self.passed.append(name)
                else:
                    print(f"{RED}✗ FAIL{RESET}")
                    all_passed = False
            except Exception as e:
                print(f"{RED}✗ ERROR: {e}{RESET}")
                self.errors.append(f"{name}: {e}")
                all_passed = False

        self.print_summary()
        return all_passed

    def check_directory_structure(self) -> bool:
        """Check if required directories exist"""
        required_dirs = []
        if not self.skill_path.exists():
            self.errors.append(f"Skill directory does not exist: {self.skill_path}")
            return False

        for dir_name in required_dirs:
            dir_path = self.skill_path / dir_name
            if not dir_path.exists():
                self.warnings.append(f"Optional directory not found: {dir_name}")

        return True

    def check_skill_md_exists(self) -> bool:
        """Check if SKILL.md exists"""
        skill_md = self.skill_path / "SKILL.md"
        if not skill_md.exists():
            self.errors.append("SKILL.md file not found")
            return False
        return True

    def check_frontmatter(self) -> bool:
        """Check frontmatter format and required fields"""
        skill_md = self.skill_path / "SKILL.md"
        if not skill_md.exists():
            return False

        content = skill_md.read_text(encoding='utf-8')

        # Check frontmatter starts at beginning
        if not content.startswith('---'):
            self.errors.append("SKILL.md must start with YAML frontmatter (---)")
            return False

        # Extract frontmatter
        lines = content.split('\n')
        frontmatter_lines = []
        in_frontmatter = False
        frontmatter_end_line = -1

        for i, line in enumerate(lines):
            if line.strip() == '---':
                if not in_frontmatter:
                    in_frontmatter = True
                    continue
                else:
                    frontmatter_end_line = i
                    break

        if frontmatter_end_line == -1:
            self.errors.append("Frontmatter closing (---) not found")
            return False

        frontmatter_text = '\n'.join(lines[:frontmatter_end_line])

        # Check for markdown before frontmatter
        for line in lines[:frontmatter_end_line]:
            if line.startswith('#'):
                self.errors.append("Markdown heading found before frontmatter")
                return False

        # Parse frontmatter
        try:
            import yaml
            frontmatter = yaml.safe_load(frontmatter_text)
        except ImportError:
            # Fallback to regex parsing
            frontmatter = self._parse_frontmatter_regex(frontmatter_text)
        except Exception as e:
            self.errors.append(f"Failed to parse YAML frontmatter: {e}")
            return False

        if frontmatter is None:
            self.errors.append("Frontmatter is empty or invalid")
            return False

        # Check required fields
        if 'name' not in frontmatter:
            self.errors.append("Frontmatter missing required field: name")
            return False

        if 'description' not in frontmatter:
            self.errors.append("Frontmatter missing required field: description")
            return False

        # Check field types
        if not isinstance(frontmatter.get('name'), str):
            self.errors.append("Field 'name' must be a string")
            return False

        if not isinstance(frontmatter.get('description'), str):
            self.errors.append("Field 'description' must be a string")
            return False

        # Check name format (hyphen-case)
        name = frontmatter['name']
        if not re.match(r'^[a-z][a-z0-9-]*$', name):
            self.errors.append(f"Name '{name}' must be in hyphen-case (e.g., 'my-skill')")
            return False

        # Check name length
        if len(name) > 64:
            self.errors.append(f"Name '{name}' exceeds 64 characters")
            return False

        return True

    def _parse_frontmatter_regex(self, text: str) -> Optional[Dict]:
        """Fallback YAML parser using regex"""
        result = {}
        for line in text.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()
                if value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
                elif value.startswith("'") and value.endswith("'"):
                    value = value[1:-1]
                result[key] = value
        return result if result else None

    def check_meta_json_exists(self) -> bool:
        """Check if _meta.json exists"""
        meta_json = self.skill_path / "_meta.json"
        if not meta_json.exists():
            self.errors.append("_meta.json file not found")
            return False
        return True

    def check_meta_json_valid(self) -> bool:
        """Check _meta.json structure"""
        meta_json = self.skill_path / "_meta.json"
        if not meta_json.exists():
            return False

        try:
            data = json.loads(meta_json.read_text(encoding='utf-8'))
        except json.JSONDecodeError as e:
            self.errors.append(f"_meta.json is not valid JSON: {e}")
            return False

        # Check required fields
        required_fields = ['id', 'version']
        for field in required_fields:
            if field not in data:
                self.errors.append(f"_meta.json missing required field: {field}")
                return False

        # Check version format (semver)
        version = data['version']
        if not re.match(r'^\d+\.\d+\.\d+$', version):
            self.errors.append(f"Version '{version}' must follow semver format (x.y.z)")
            return False

        return True

    def check_name_consistency(self) -> bool:
        """Check if frontmatter name matches folder name"""
        skill_md = self.skill_path / "SKILL.md"
        if not skill_md.exists():
            return False

        content = skill_md.read_text(encoding='utf-8')
        # Extract name from frontmatter
        match = re.search(r'^name:\s*(.+?)\s*$', content, re.MULTILINE)
        if not match:
            return False

        frontmatter_name = match.group(1).strip()
        folder_name = self.skill_path.name

        if frontmatter_name != folder_name:
            self.errors.append(
                f"Name mismatch: frontmatter has '{frontmatter_name}' but folder is '{folder_name}'"
            )
            return False

        return True

    def check_description_quality(self) -> bool:
        """Check description quality"""
        skill_md = self.skill_path / "SKILL.md"
        if not skill_md.exists():
            return False

        content = skill_md.read_text(encoding='utf-8')
        match = re.search(r'^description:\s*(.+?)\s*$', content, re.MULTILINE)
        if not match:
            return False

        description = match.group(1).strip()

        # Check minimum length
        if len(description) < 20:
            self.warnings.append("Description may be too short (< 20 characters)")
            return True  # Warning, not error

        # Check for trigger phrase indicators
        trigger_words = ['when', 'use', 'ask', 'request', 'trigger']
        has_trigger = any(word in description.lower() for word in trigger_words)
        if not has_trigger:
            self.warnings.append("Description should include trigger phrases (e.g., 'Use when...')")

        return True

    def check_trigger_phrases(self) -> bool:
        """Check if _meta.json has trigger phrases"""
        meta_json = self.skill_path / "_meta.json"
        if not meta_json.exists():
            return False

        try:
            data = json.loads(meta_json.read_text(encoding='utf-8'))
        except:
            return False

        if 'trigger_phrases' in data:
            if not isinstance(data['trigger_phrases'], list):
                self.errors.append("trigger_phrases must be an array")
                return False
            if len(data['trigger_phrases']) == 0:
                self.warnings.append("trigger_phrases is empty")
            return True

        self.warnings.append("Consider adding trigger_phrases to _meta.json for better routing")
        return True  # Optional field

    def check_path_names(self) -> bool:
        """Check for non-English characters in paths"""
        import glob

        # Check directory name
        if not re.match(r'^[a-zA-Z0-9_-]+$', self.skill_path.name):
            self.errors.append(f"Directory name contains non-English characters: {self.skill_path.name}")
            return False

        # Check file names
        for pattern in ['**/*.md', '**/*.json', '**/*.py', '**/*.js']:
            for file_path in glob.glob(str(self.skill_path / pattern), recursive=True):
                rel_path = Path(file_path).relative_to(self.skill_path)
                if not re.match(r'^[a-zA-Z0-9_./-]+$', str(rel_path)):
                    self.errors.append(f"File path contains non-English characters: {rel_path}")
                    return False

        return True

    def check_file_encoding(self) -> bool:
        """Check file encoding"""
        import glob

        for pattern in ['**/*.md', '**/*.json', '**/*.py']:
            for file_path in glob.glob(str(self.skill_path / pattern), recursive=True):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        f.read()
                except UnicodeDecodeError:
                    self.errors.append(f"File encoding issue: {file_path}")
                    return False

        return True

    def print_summary(self):
        """Print validation summary"""
        print(f"\n{BOLD}{'='*60}{RESET}")
        print(f"{BOLD}📊 Validation Summary{RESET}")
        print(f"{BOLD}{'='*60}{RESET}")

        print(f"\n{GREEN}✓ Passed: {len(self.passed)}{RESET}")
        for p in self.passed:
            print(f"  - {p}")

        if self.warnings:
            print(f"\n{YELLOW}⚠ Warnings: {len(self.warnings)}{RESET}")
            for w in self.warnings:
                print(f"  - {w}")

        if self.errors:
            print(f"\n{RED}✗ Errors: {len(self.errors)}{RESET}")
            for e in self.errors:
                print(f"  - {e}")

        print()

def main():
    if len(sys.argv) < 2:
        skill_path = "/workspace/temp-skills/socratic-teacher"
    else:
        skill_path = sys.argv[1]

    validator = SkillValidator(skill_path)
    success = validator.validate_all()

    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()

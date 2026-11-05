#!/usr/bin/env python3
"""
Package skill for distribution.
Creates a .skill archive file from a skill directory.
"""

import json
import os
import shutil
import sys
import zipfile
from datetime import datetime
from pathlib import Path
from typing import List, Optional


class SkillPacker:
    ALLOWED_EXTENSIONS = ['.md', '.json', '.py', '.txt', '.yaml', '.yml']
    BLOCKED_PATTERNS = ['__pycache__', '.pyc', '.git', '.DS_Store', '.env']
    BLOCKED_NAMES = ['.skill', 'secrets.json']

    def __init__(self, skill_path: str, output_dir: Optional[str] = None):
        self.skill_path = Path(skill_path).resolve()
        self.output_dir = Path(output_dir) if output_dir else self.skill_path.parent
        self.skill_name = self.skill_path.name
        self.warnings: List[str] = []

    def package(self) -> Path:
        """Create a .skill package and return the path."""
        if not self.skill_path.exists():
            raise FileNotFoundError(f"Skill path not found: {self.skill_path}")

        # Read metadata
        meta = self._load_meta()
        version = meta.get("version", "0.0.0")
        slug = meta.get("slug", self.skill_name)

        # Create output filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.output_dir / f"{slug}_v{version}_{timestamp}.skill"

        # Create package
        self._create_package(output_file)

        # Print summary
        self._print_summary(output_file, meta)

        return output_file

    def _load_meta(self) -> dict:
        """Load _meta.json."""
        meta_path = self.skill_path / "_meta.json"
        if meta_path.exists():
            with open(meta_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def _should_include(self, path: Path) -> bool:
        """Check if file should be included in package."""
        name = path.name

        # Check blocked patterns
        for pattern in self.BLOCKED_PATTERNS:
            if pattern in str(path):
                return False

        # Check blocked names
        if name in self.BLOCKED_NAMES:
            return False

        # Check extensions
        if path.is_file():
            ext = path.suffix.lower()
            if ext in self.ALLOWED_EXTENSIONS:
                return True
            # Allow files without extension if they look like readme/license
            if path.name.upper() in ['README', 'LICENSE', 'CHANGELOG']:
                return True
            return False

        return True

    def _create_package(self, output_path: Path):
        """Create the .skill zip archive."""
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for root, dirs, files in os.walk(self.skill_path):
                # Filter directories
                dirs[:] = [d for d in dirs if self._should_include(Path(root) / d)]

                for file in files:
                    file_path = Path(root) / file
                    if self._should_include(file_path):
                        # Calculate archive name (relative to skill root)
                        arcname = file_path.relative_to(self.skill_path)
                        zf.write(file_path, arcname)
                    else:
                        self.warnings.append(f"Excluded: {file_path.relative_to(self.skill_path)}")

    def _print_summary(self, output_path: Path, meta: dict):
        """Print packaging summary."""
        size = output_path.stat().st_size
        size_str = f"{size / 1024:.1f} KB" if size > 1024 else f"{size} bytes"

        print("\n" + "="*50)
        print("PACKAGE CREATED")
        print("="*50)
        print(f"📦 Output: {output_path}")
        print(f"📊 Size: {size_str}")
        print(f"📝 Skill: {self.skill_name}")
        print(f"🏷️  Version: {meta.get('version', 'N/A')}")
        print(f"🔖 Slug: {meta.get('slug', 'N/A')}")

        if self.warnings:
            print(f"\n⚠️  Excluded files ({len(self.warnings)}):")
            for w in self.warnings[:5]:  # Show first 5
                print(f"  - {w}")
            if len(self.warnings) > 5:
                print(f"  ... and {len(self.warnings) - 5} more")


def main():
    if len(sys.argv) < 2:
        print("Usage: python package_skill.py <skill_path> [output_dir]")
        print("Example: python package_skill.py /workspace/skills/humanizer")
        sys.exit(1)

    skill_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None

    try:
        packer = SkillPacker(skill_path, output_dir)
        output_file = packer.package()
        print(f"\n✅ Successfully packaged skill to: {output_file}")
    except Exception as e:
        print(f"\n❌ Packaging failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

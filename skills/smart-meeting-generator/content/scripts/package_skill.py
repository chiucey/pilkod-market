#!/usr/bin/env python3
"""
Package skill for distribution.
Creates a .skill bundle from the skill directory.
"""

import json
import os
import shutil
import sys
import zipfile
from datetime import datetime
from pathlib import Path


class SkillPackager:
    """Packages a skill for distribution."""

    def __init__(self, skill_path: str):
        self.skill_path = Path(skill_path)
        self.output_dir = Path("dist")
        self.exclude_patterns = [
            "__pycache__",
            "*.pyc",
            ".git",
            ".DS_Store",
            "*.log",
            ".env",
            "node_modules",
        ]

    def package(self) -> Path:
        """Create a .skill package."""
        # Validate skill first
        if not self.validate_for_packaging():
            raise ValueError("Skill validation failed")

        # Create output directory
        self.output_dir.mkdir(exist_ok=True)

        # Generate package filename
        skill_name = self.skill_path.name
        meta = self.read_meta()
        version = meta.get("version", "1.0.0")
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        package_name = f"{skill_name}-v{version}-{timestamp}.skill"
        output_path = self.output_dir / package_name

        # Create package
        print(f"Creating package: {output_path}")
        self.create_package(output_path)

        print(f"Package created successfully: {output_path}")
        return output_path

    def validate_for_packaging(self) -> bool:
        """Validate skill can be packaged."""
        required_files = ["SKILL.md", "_meta.json"]
        for filename in required_files:
            if not (self.skill_path / filename).exists():
                print(f"Missing required file: {filename}")
                return False
        return True

    def read_meta(self) -> dict:
        """Read skill metadata."""
        meta_path = self.skill_path / "_meta.json"
        if meta_path.exists():
            return json.loads(meta_path.read_text(encoding="utf-8"))
        return {}

    def should_exclude(self, path: Path) -> bool:
        """Check if path should be excluded from package."""
        path_str = str(path)
        for pattern in self.exclude_patterns:
            if pattern in path_str or path.name == pattern:
                return True
        return False

    def create_package(self, output_path: Path):
        """Create the .skill package file."""
        with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for root, dirs, files in os.walk(self.skill_path):
                # Filter directories
                dirs[:] = [d for d in dirs if not self.should_exclude(Path(d))]

                for file in files:
                    file_path = Path(root) / file
                    if self.should_exclude(file_path):
                        continue

                    # Calculate archive name (relative path)
                    arcname = file_path.relative_to(self.skill_path)
                    zf.write(file_path, arcname)
                    print(f"  Added: {arcname}")

    def create_skill_info(self) -> dict:
        """Create skill info for metadata."""
        meta = self.read_meta()
        skill_md = self.skill_path / "SKILL.md"

        # Extract description from frontmatter
        description = meta.get("description", "")
        if not description and skill_md.exists():
            content = skill_md.read_text(encoding="utf-8")
            if content.startswith("---"):
                lines = content.split("\n")
                for line in lines:
                    if line.startswith("description:"):
                        description = line.split(":", 1)[1].strip()
                        break

        return {
            "name": self.skill_path.name,
            "version": meta.get("version", "1.0.0"),
            "id": meta.get("id", ""),
            "description": description,
            "created_at": meta.get("created_at", datetime.now().strftime("%Y-%m-%d")),
            "files": self.list_files(),
        }

    def list_files(self) -> list:
        """List all files in skill."""
        files = []
        for root, _, filenames in os.walk(self.skill_path):
            for filename in filenames:
                if not self.should_exclude(Path(filename)):
                    file_path = Path(root) / filename
                    rel_path = file_path.relative_to(self.skill_path)
                    files.append(str(rel_path))
        return files


def main():
    if len(sys.argv) < 2:
        print("Usage: python package_skill.py <skill_path>")
        sys.exit(1)

    skill_path = sys.argv[1]
    packager = SkillPackager(skill_path)

    try:
        output_path = packager.package()
        print(f"\nSkill packaged successfully!")
        print(f"Output: {output_path}")
        sys.exit(0)
    except Exception as e:
        print(f"Packaging failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

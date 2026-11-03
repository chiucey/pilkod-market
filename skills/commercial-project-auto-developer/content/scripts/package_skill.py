#!/usr/bin/env python3
"""
Skill Packager Script
Packages the commercial-project-auto-developer skill for distribution
"""

import json
import shutil
import zipfile
from datetime import datetime
from pathlib import Path


class SkillPackager:
    """Packages skill for distribution"""

    def __init__(self, skill_path: str, output_dir: str = None):
        self.skill_path = Path(skill_path)
        self.output_dir = Path(output_dir) if output_dir else Path('./dist')
        self.skill_name = self.skill_path.name
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    def package(self) -> Path:
        """Create skill package"""
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Create package name
        package_name = f"{self.skill_name}_{self.timestamp}.skill"
        package_path = self.output_dir / package_name

        # Read meta for version
        meta_path = self.skill_path / '_meta.json'
        version = "unknown"
        if meta_path.exists():
            with open(meta_path, 'r', encoding='utf-8') as f:
                meta = json.load(f)
                version = meta.get('version', 'unknown')

        print(f"Packaging skill: {self.skill_name} v{version}")
        print(f"Output: {package_path}")

        # Create zip archive
        with zipfile.ZipFile(package_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in self.skill_path.rglob('*'):
                if file_path.is_file():
                    # Skip cache and temp files
                    if any(part.startswith('.') for part in file_path.parts):
                        continue
                    if file_path.suffix in ['.pyc', '__pycache__']:
                        continue

                    arcname = file_path.relative_to(self.skill_path)
                    zipf.write(file_path, arcname)
                    print(f"  + {arcname}")

        print(f"\n✅ Package created: {package_path}")
        print(f"   Size: {package_path.stat().st_size / 1024:.2f} KB")

        return package_path

    def create_distribution_folder(self) -> Path:
        """Create a clean distribution folder"""
        dist_path = self.output_dir / 'skills' / self.skill_name
        dist_path.mkdir(parents=True, exist_ok=True)

        # Copy all files
        for file_path in self.skill_path.rglob('*'):
            if file_path.is_file():
                rel_path = file_path.relative_to(self.skill_path)
                dest_path = dist_path / rel_path
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(file_path, dest_path)

        print(f"\n✅ Distribution folder created: {dist_path}")
        return dist_path


def main():
    """Main entry point"""
    import sys

    skill_path = Path(__file__).parent.parent
    output_dir = Path(__file__).parent.parent.parent / 'dist'

    packager = SkillPackager(skill_path, output_dir)

    # Create distribution folder
    packager.create_distribution_folder()

    # Create package
    package_path = packager.package()

    print(f"\n📦 Ready for distribution: {package_path}")


if __name__ == '__main__':
    main()

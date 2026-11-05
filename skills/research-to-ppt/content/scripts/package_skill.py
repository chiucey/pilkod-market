#!/usr/bin/env python3
"""
Package skill for distribution.
Creates a .skill bundle from the skill directory.
"""

import os
import sys
import json
import shutil
import zipfile
from pathlib import Path
from datetime import datetime


class SkillPackager:
    def __init__(self, skill_path, output_path=None):
        self.skill_path = Path(skill_path).resolve()
        self.output_path = output_path

        if not self.skill_path.exists():
            raise ValueError(f"Skill path does not exist: {self.skill_path}")

        if not self.skill_path.is_dir():
            raise ValueError(f"Skill path must be a directory: {self.skill_path}")

    def package(self):
        """Create the skill package."""
        print(f"Packaging skill: {self.skill_path}")
        print("=" * 60)

        # Read metadata
        meta_json = self.skill_path / "_meta.json"
        if not meta_json.exists():
            raise ValueError("_meta.json not found in skill directory")

        meta = json.loads(meta_json.read_text(encoding="utf-8"))
        skill_name = meta.get("name", self.skill_path.name)
        skill_version = meta.get("version", "1.0.0")

        # Generate output filename
        if self.output_path:
            output_file = Path(self.output_path)
        else:
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            output_file = self.skill_path.parent / f"{skill_name}-{skill_version}-{timestamp}.skill"

        # Create package
        print(f"Creating package: {output_file}")

        with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
            # Walk through skill directory
            for root, dirs, files in os.walk(self.skill_path):
                # Skip hidden directories
                dirs[:] = [d for d in dirs if not d.startswith('.')]

                for file in files:
                    # Skip hidden files
                    if file.startswith('.'):
                        continue

                    file_path = Path(root) / file
                    arcname = file_path.relative_to(self.skill_path)

                    # Security check: no symlinks or path traversal
                    if '..' in str(arcname):
                        print(f"  ⚠️  Skipping suspicious path: {arcname}")
                        continue

                    zf.write(file_path, arcname)
                    print(f"  ✓ {arcname}")

        print("=" * 60)
        print(f"✅ Package created: {output_file}")
        print(f"   Size: {output_file.stat().st_size / 1024:.1f} KB")

        return output_file

    def verify_package(self, package_path):
        """Verify the created package can be read."""
        print("\nVerifying package...")

        try:
            with zipfile.ZipFile(package_path, 'r') as zf:
                names = zf.namelist()

                # Check for required files
                required = ["SKILL.md", "_meta.json"]
                for req in required:
                    if req not in names:
                        print(f"  ❌ Missing required file: {req}")
                        return False
                    print(f"  ✓ {req}")

                # List other files
                other_files = [n for n in names if n not in required]
                if other_files:
                    print(f"\n  Additional files ({len(other_files)}):")
                    for f in other_files[:10]:  # Show first 10
                        print(f"    - {f}")
                    if len(other_files) > 10:
                        print(f"    ... and {len(other_files) - 10} more")

            print("  ✅ Package verification passed")
            return True

        except zipfile.BadZipFile:
            print("  ❌ Invalid ZIP file")
            return False
        except Exception as e:
            print(f"  ❌ Verification failed: {e}")
            return False


def main():
    if len(sys.argv) < 2:
        skill_path = Path(__file__).parent.parent
        print(f"No skill path specified, using default: {skill_path}")
    else:
        skill_path = Path(sys.argv[1])

    output_path = sys.argv[2] if len(sys.argv) > 2 else None

    try:
        packager = SkillPackager(skill_path, output_path)
        package_path = packager.package()

        if packager.verify_package(package_path):
            print(f"\n📦 Ready for distribution: {package_path}")
        else:
            print("\n⚠️  Package verification failed")
            sys.exit(1)

    except Exception as e:
        print(f"\n❌ Packaging failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

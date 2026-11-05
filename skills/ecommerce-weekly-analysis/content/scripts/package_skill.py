#!/usr/bin/env python3
"""
Package script for ecommerce-weekly-analysis skill
Creates a distributable .skill file
"""

import os
import zipfile
import sys
from pathlib import Path
from datetime import datetime

def package_skill(skill_path: Path, output_path: Path) -> bool:
    """Package skill into a .skill archive"""

    if not skill_path.exists():
        print(f"❌ Skill path not found: {skill_path}")
        return False

    # Create zip archive
    skill_name = skill_path.name
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_name = f"{skill_name}_{timestamp}.skill"
    zip_path = output_path / zip_name

    try:
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for file_path in skill_path.rglob("*"):
                if file_path.is_file():
                    arcname = file_path.relative_to(skill_path)
                    zf.write(file_path, arcname)
                    print(f"  + {arcname}")

        print(f"\n✅ Skill packaged successfully!")
        print(f"   Output: {zip_path}")
        print(f"   Size: {zip_path.stat().st_size / 1024:.2f} KB")
        return True

    except Exception as e:
        print(f"❌ Failed to package skill: {e}")
        return False

def main():
    skill_path = Path(os.environ.get("SKILL_PATH", "/workspace/temp-skills/ecommerce-weekly-analysis"))
    output_path = Path(os.environ.get("OUTPUT_PATH", "/workspace/temp-skills"))

    print(f"📦 Packaging skill: {skill_path}")
    print(f"   Output: {output_path}")
    print("   Files:")

    success = package_skill(skill_path, output_path)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()

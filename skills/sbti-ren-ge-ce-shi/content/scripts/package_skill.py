#!/usr/bin/env python3
"""Package the SBTI personality test skill into a .skill archive."""

import zipfile
from pathlib import Path


def package_skill(skill_path: str) -> Path:
    root = Path(skill_path).resolve()
    archive = Path(f"{root.name}.skill")
    
    # Create the skill package
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as zip_handle:
        for path in root.rglob("*"):
            if path.is_file():
                rel = path.relative_to(root)
                arcname = Path(root.name) / rel
                zip_handle.write(path, arcname)
                print(f"  added: {arcname}")
    
    print(f"Packaged skill at: {archive}")
    return archive


if __name__ == "__main__":
    skill_path = "/workspace/temp-skills/sbti-ren-ge-ce-shi"
    result = package_skill(skill_path)
    print(f"\nSkill package created: {result.absolute()}")

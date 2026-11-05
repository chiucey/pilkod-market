#!/usr/bin/env python3
"""
Package skill folder into a .skill file
"""
import os
import zipfile
import json
import sys

def package_skill(skill_dir, output_file):
    """Package skill directory into a .skill zip file"""

    if not os.path.isdir(skill_dir):
        print(f"Error: {skill_dir} is not a directory")
        sys.exit(1)

    # Check for required files
    skill_md = os.path.join(skill_dir, "SKILL.md")
    meta_json = os.path.join(skill_dir, "_meta.json")

    if not os.path.exists(skill_md):
        print(f"Error: SKILL.md not found in {skill_dir}")
        sys.exit(1)

    if not os.path.exists(meta_json):
        print(f"Error: _meta.json not found in {skill_dir}")
        sys.exit(1)

    # Validate _meta.json
    with open(meta_json, 'r') as f:
        meta = json.load(f)

    if 'id' not in meta or 'version' not in meta:
        print("Error: _meta.json must contain 'id' and 'version'")
        sys.exit(1)

    # Create .skill file (which is just a zip)
    if not output_file.endswith('.skill'):
        output_file += '.skill'

    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(skill_dir):
            # Skip scripts directory in packaging
            if 'scripts' in dirs:
                dirs.remove('scripts')
            for file in files:
                if file.endswith('.py'):
                    continue  # Skip Python files
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, os.path.dirname(skill_dir))
                zf.write(file_path, arcname)

    print(f"Successfully packaged skill to: {output_file}")
    return output_file

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python package_skill.py <skill_dir> [output_file]")
        sys.exit(1)

    skill_dir = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    if output_file is None:
        # Use skill name as default output
        skill_name = os.path.basename(skill_dir.rstrip('/'))
        output_file = f"{skill_dir}/{skill_name}.skill"

    package_skill(skill_dir, output_file)

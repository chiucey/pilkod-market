#!/usr/bin/env python3
"""
Iran Situation Intelligence Skill Packaging Script
Packages the skill into a distributable .skill file
"""

import os
import json
import shutil
import zipfile
from datetime import datetime
from pathlib import Path


def get_skill_metadata(skill_dir):
    """Read skill metadata"""
    meta_path = os.path.join(skill_dir, '_meta.json')
    with open(meta_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def create_package(skill_dir, output_dir=None):
    """Create skill package"""
    if output_dir is None:
        output_dir = os.path.dirname(skill_dir)

    meta = get_skill_metadata(skill_dir)
    skill_name = meta.get('name', 'unknown-skill')
    version = meta.get('version', '1.0.0')

    # Generate package name
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    package_name = f"{skill_name}_{version}_{timestamp}.skill"
    package_path = os.path.join(output_dir, package_name)

    # Create zip package
    with zipfile.ZipFile(package_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(skill_dir):
            # Exclude hidden files and __pycache__
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']

            for file in files:
                if file.startswith('.') or file.endswith('.pyc'):
                    continue

                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, os.path.dirname(skill_dir))
                zipf.write(file_path, arcname)

    return package_path


def verify_package(package_path, skill_dir):
    """Verify package contents"""
    with zipfile.ZipFile(package_path, 'r') as zipf:
        file_list = zipf.namelist()

        # Check required files
        required = ['SKILL.md', '_meta.json']
        for req in required:
            if not any(req in f for f in file_list):
                print(f"   [ERROR] Missing required file in package: {req}")
                return False

        # Check structural integrity
        expected_files = [
            'SKILL.md',
            '_meta.json',
            'references/information_sources.md',
            'references/hormuz_analysis_framework.md',
            'references/nuclear_risk_assessment.md',
            'scripts/validate_skill.py'
        ]

        for exp in expected_files:
            if not any(exp in f for f in file_list):
                print(f"   [WARN] Recommended file missing: {exp}")

    return True


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    skill_dir = os.path.dirname(script_dir)

    print("=" * 60)
    print("Iran Situation Intelligence Skill - Packaging Tool")
    print("=" * 60)

    # Get metadata
    try:
        meta = get_skill_metadata(skill_dir)
        print(f"\nSkill Name: {meta.get('display_name', meta.get('name'))}")
        print(f"Version: {meta.get('version')}")
        print(f"Skill ID: {meta.get('id')}")
    except Exception as e:
        print(f"\n[ERROR] Unable to read metadata: {e}")
        return 1

    # Package
    print("\nPackaging skill...")
    try:
        package_path = create_package(skill_dir)
        print(f"   [OK] Package created: {package_path}")

        # Verify
        print("\nVerifying package contents...")
        if verify_package(package_path, skill_dir):
            print("   [OK] Package verification passed")

        # Show package size
        package_size = os.path.getsize(package_path)
        print(f"\nPackage size: {package_size / 1024:.2f} KB")

        print("\n" + "=" * 60)
        print("Packaging complete!")
        print("=" * 60)
        print(f"\nPackage path: {package_path}")

        return 0

    except Exception as e:
        print(f"\n[ERROR] Packaging failed: {e}")
        return 1


if __name__ == '__main__':
    import sys
    sys.exit(main())

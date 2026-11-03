#!/usr/bin/env python3
"""
Medical Research Analyzer Skill Packaging Script
Generates distributable .skill file
"""

import os
import json
import shutil
import zipfile
from datetime import datetime
from pathlib import Path

def get_skill_info(skill_path):
    """Get skill information"""
    meta_path = os.path.join(skill_path, '_meta.json')
    skill_md_path = os.path.join(skill_path, 'SKILL.md')

    with open(meta_path, 'r', encoding='utf-8') as f:
        meta = json.load(f)

    with open(skill_md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract frontmatter
    lines = content.split('\n')
    frontmatter = {}
    in_frontmatter = False
    for line in lines[1:]:
        if line.strip() == '---':
            break
        if ':' in line:
            key, value = line.split(':', 1)
            frontmatter[key.strip()] = value.strip()

    return {
        'id': meta.get('id'),
        'version': meta.get('version'),
        'name': frontmatter.get('name', 'unknown'),
        'description': frontmatter.get('description', '')[:100] + '...'
    }

def collect_files(skill_path):
    """Collect skill files"""
    files = []
    for root, dirs, filenames in os.walk(skill_path):
        # Exclude __pycache__ directories
        dirs[:] = [d for d in dirs if d not in ['__pycache__', '.git', 'node_modules']]

        for filename in filenames:
            # Exclude hidden files and Python bytecode
            if filename.startswith('.') or filename.endswith('.pyc'):
                continue

            full_path = os.path.join(root, filename)
            rel_path = os.path.relpath(full_path, skill_path)
            file_size = os.path.getsize(full_path)
            files.append({
                'path': rel_path,
                'full_path': full_path,
                'size': file_size
            })

    return files

def create_package(skill_path, output_path=None):
    """Create skill package"""
    skill_name = os.path.basename(skill_path)

    if output_path is None:
        output_path = os.path.join(os.path.dirname(skill_path), f"{skill_name}.skill")

    # Get skill info
    info = get_skill_info(skill_path)

    # Collect files
    files = collect_files(skill_path)

    print("=" * 60)
    print("Medical Research Analyzer - Skill Packaging")
    print("=" * 60)
    print()

    print(f"[+] Skill Name: {info['name']}")
    print(f"[+] Skill ID: {info['id']}")
    print(f"[+] Version: {info['version']}")
    print()

    # Create ZIP package
    total_size = 0
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for file_info in files:
            zf.write(file_info['full_path'], file_info['path'])
            total_size += file_info['size']
            print(f"  ✓ Added: {file_info['path']} ({file_info['size']} bytes)")

    package_size = os.path.getsize(output_path)

    print()
    print("=" * 60)
    print("Packaging Complete!")
    print("=" * 60)
    print()
    print(f"[+] Output File: {output_path}")
    print(f"[+] Package Size: {package_size} bytes ({package_size/1024:.2f} KB)")
    print(f"[+] Number of Files: {len(files)} files")
    print(f"[+] Pre-compression Size: {total_size} bytes")
    print(f"[+] Compression Rate: {(1 - package_size/total_size)*100:.1f}%")
    print()

    return output_path

def verify_package(package_path):
    """Verify package contents"""
    print("[*] Verifying package contents...")

    with zipfile.ZipFile(package_path, 'r') as zf:
        file_list = zf.namelist()

        # Check required files
        required_files = ['SKILL.md', '_meta.json']
        for req_file in required_files:
            if req_file not in file_list:
                print(f"  ✗ Missing required file: {req_file}")
                return False
            print(f"  ✓ Included: {req_file}")

        # List all files
        print()
        print("[*] Package file list:")
        for f in file_list:
            info = zf.getinfo(f)
            print(f"  - {f} ({info.file_size} bytes)")

    print()
    print("✓ Package content verification passed!")
    return True

def main():
    # Get script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    skill_path = script_dir.replace('/scripts', '')

    print(f"[*] Skill Path: {skill_path}")
    print()

    # Create package
    output = create_package(skill_path)

    print()

    # Verify
    if verify_package(output):
        print()
        print("=" * 60)
        print("Skill Packaging Successful!")
        print("=" * 60)
        print()
        print(f"Skill file location: {output}")
        print()
        print("Next Steps:")
        print("1. Upload .skill file to skill marketplace (if applicable)")
        print("2. Install and test the skill in Matrix Agent")
        print("3. Iterate and optimize based on usage feedback")
    else:
        print("Packaging failed, please check error messages.")
        return 1

    return 0

if __name__ == '__main__':
    exit(main())

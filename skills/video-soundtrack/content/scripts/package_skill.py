#!/usr/bin/env python3
"""
Package script for video-soundtrack skill
Creates a distributable .skill archive
"""

import json
import os
import shutil
import sys
import tarfile
from datetime import datetime
from pathlib import Path

SKILL_DIR = Path(__file__).parent.parent
OUTPUT_DIR = Path("/workspace/temp-skills/output")
GREEN = '\033[92m'
RED = '\033[91m'
RESET = '\033[0m'

def validate_for_packaging():
    """Ensure skill is ready for packaging"""
    # Check required files
    required = ["SKILL.md", "_meta.json"]
    for f in required:
        if not (SKILL_DIR / f).exists():
            print(f"{RED}✗ Missing required file: {f}{RESET}")
            return False
    
    # Validate meta.json
    with open(SKILL_DIR / "_meta.json", 'r') as f:
        meta = json.load(f)
    if 'id' not in meta or 'version' not in meta:
        print(f"{RED}✗ _meta.json missing required fields{RESET}")
        return False
    
    return True

def create_package():
    """Create .skill package"""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Load meta for filename
    with open(SKILL_DIR / "_meta.json", 'r') as f:
        meta = json.load(f)
    
    skill_name = meta.get('id', 'unknown')
    version = meta.get('version', '1.0.0')
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    
    output_file = OUTPUT_DIR / f"video-soundtrack-{version}.skill"
    
    # Create tarball
    with tarfile.open(output_file, 'w:gz') as tar:
        tar.add(SKILL_DIR / "SKILL.md", arcname="SKILL.md")
        tar.add(SKILL_DIR / "_meta.json", arcname="_meta.json")
        
        # Add optional directories
        for subdir in ['scripts', 'references', 'assets']:
            subdir_path = SKILL_DIR / subdir
            if subdir_path.is_dir():
                tar.add(subdir_path, arcname=subdir)
    
    print(f"{GREEN}✓ Package created: {output_file}{RESET}")
    return output_file

def main():
    print("=" * 50)
    print("Video Soundtrack Skill Packaging")
    print("=" * 50)
    
    if not validate_for_packaging():
        print(f"{RED}✗ Validation failed, aborting{RESET}")
        return 1
    
    output = create_package()
    
    print("=" * 50)
    print(f"{GREEN}✓ Packaging complete!{RESET}")
    print(f"Output: {output}")
    print("=" * 50)
    return 0

if __name__ == "__main__":
    sys.exit(main())

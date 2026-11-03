#!/usr/bin/env python3
"""
EduPro Package Script
打包脚本 - 将技能打包为 .skill 文件

Usage:
    python package_skill.py [skill_path] [--output OUTPUT_DIR]
"""

import os
import sys
import json
import zipfile
import shutil
from pathlib import Path
from datetime import datetime

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_success(msg):
    print(f"{Colors.GREEN}✓ {msg}{Colors.RESET}")

def print_error(msg):
    print(f"{Colors.RED}✗ {msg}{Colors.RESET}")

def print_info(msg):
    print(f"{Colors.BLUE}ℹ {msg}{Colors.RESET}")

def print_step(msg):
    print(f"\n{Colors.BOLD}→ {msg}{Colors.RESET}")

def get_skill_metadata(skill_path):
    """从 SKILL.md 和 _meta.json 获取元数据"""
    # Read _meta.json
    meta_path = skill_path / "_meta.json"
    if meta_path.exists():
        with open(meta_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)
    else:
        meta = {}
    
    # Extract name from SKILL.md frontmatter
    skill_md = skill_path / "SKILL.md"
    name = skill_path.name  # Default to directory name
    
    if skill_md.exists():
        with open(skill_md, 'r', encoding='utf-8') as f:
            content = f.read()
            # Simple frontmatter parsing
            if content.startswith('---'):
                lines = content.split('\n', 3)
                for line in lines[1:]:
                    if line.startswith('name:'):
                        name = line.split(':', 1)[1].strip()
                        break
    
    return {
        'name': name,
        'version': meta.get('version', '1.0.0'),
        'id': meta.get('id', 0)
    }

def collect_files(skill_path):
    """收集所有需要打包的文件"""
    files = []
    
    # Walk through skill directory
    for item in skill_path.rglob('*'):
        if item.is_file():
            # Skip __pycache__ and other cache directories
            if '__pycache__' in str(item):
                continue
            
            # Get relative path
            rel_path = item.relative_to(skill_path)
            
            # Skip .DS_Store, Thumbs.db, etc.
            if rel_path.name in ['.DS_Store', 'Thumbs.db']:
                continue
            
            files.append(rel_path)
    
    return sorted(files)

def check_security(file_list, skill_path):
    """安全检查：确保没有路径遍历风险"""
    for rel_path in file_list:
        # Check for path traversal attempts
        path_parts = rel_path.parts
        if any(p.startswith('.') and p not in ['.gitkeep', '.gitignore'] for p in path_parts):
            return False, f"Invalid hidden file: {rel_path}"
        
        # Check for absolute paths or parent directory references
        if '..' in str(rel_path):
            return False, f"Path traversal detected: {rel_path}"
        
        # Ensure we're not escaping the skill directory
        try:
            full_path = (skill_path / rel_path).resolve()
            resolved_skill = skill_path.resolve()
            if not str(full_path).startswith(str(resolved_skill)):
                return False, f"Path outside skill directory: {rel_path}"
        except Exception:
            pass
    
    return True, "Security check passed"

def create_package(skill_path, output_dir=None):
    """创建技能包"""
    
    print_step("Starting package process...")
    
    # Get metadata
    meta = get_skill_metadata(skill_path)
    skill_name = meta['name']
    version = meta['version']
    
    print_info(f"Skill: {skill_name}")
    print_info(f"Version: {version}")
    
    # Collect files
    print_step("Collecting files...")
    files = collect_files(skill_path)
    print_info(f"Found {len(files)} files to package")
    
    # Security check
    print_step("Security check...")
    secure, msg = check_security(files, skill_path)
    if not secure:
        print_error(msg)
        return None
    print_success(msg)
    
    # Create output directory
    if output_dir is None:
        output_dir = skill_path.parent
    else:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
    
    # Create package filename
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    package_name = f"{skill_name}-{version}-{timestamp}.skill"
    package_path = output_dir / package_name
    
    # Create zip file
    print_step("Creating package...")
    try:
        with zipfile.ZipFile(package_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for rel_path in files:
                full_path = skill_path / rel_path
                zipf.write(full_path, rel_path)
        
        print_success(f"Package created: {package_path}")
        
        # Verify package
        print_step("Verifying package...")
        with zipfile.ZipFile(package_path, 'r') as zipf:
            file_count = len(zipf.namelist())
            print_success(f"Package contains {file_count} files")
            
            # List contents
            print_info("\nPackage contents:")
            for name in zipf.namelist()[:20]:  # Show first 20
                print(f"  • {name}")
            if len(zipf.namelist()) > 20:
                print(f"  ... and {len(zipf.namelist()) - 20} more files")
        
        # Return package info
        return {
            'path': str(package_path),
            'name': package_name,
            'size': package_path.stat().st_size,
            'file_count': len(files)
        }
        
    except Exception as e:
        print_error(f"Failed to create package: {e}")
        return None

def main():
    print(f"\n{Colors.BOLD}📦 EduPro Skill Packager{Colors.RESET}\n")
    
    # Parse arguments
    skill_path = None
    output_dir = None
    
    for i, arg in enumerate(sys.argv[1:], 1):
        if arg == '--output' and i + 1 < len(sys.argv):
            output_dir = sys.argv[i + 1]
        else:
            skill_path = Path(arg)
    
    # Default skill path
    if skill_path is None:
        skill_path = Path(__file__).parent.parent
    
    if not skill_path.exists():
        print_error(f"Skill path does not exist: {skill_path}")
        sys.exit(1)
    
    if not (skill_path / "SKILL.md").exists():
        print_error(f"SKILL.md not found in {skill_path}")
        sys.exit(1)
    
    # Create package
    result = create_package(skill_path, output_dir)
    
    if result:
        print(f"\n{Colors.BOLD}{'='*50}{Colors.RESET}")
        print_success(f"Package ready: {result['path']}")
        print_info(f"Size: {result['size']:,} bytes")
        print_info(f"Files: {result['file_count']}")
    else:
        print(f"\n{Colors.BOLD}{'='*50}{Colors.RESET}")
        print_error("Package creation failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
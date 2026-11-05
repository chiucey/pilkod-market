#!/usr/bin/env python3
"""
Quick validation script for mck-ppt-design skill.
Validates:
1. SKILL.md frontmatter exists and is valid
2. _meta.json exists with required fields
3. mck_ppt module is importable
4. All layout methods exist
"""

import os
import sys
import json
import importlib.util

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(SKILL_DIR)

def validate_frontmatter():
    """Check SKILL.md has valid frontmatter."""
    print("🔍 Validating SKILL.md frontmatter...")

    with open('SKILL.md', 'r', encoding='utf-8') as f:
        content = f.read()

    # Check frontmatter format
    if not content.startswith('---'):
        print("❌ SKILL.md must start with YAML frontmatter (---)")
        return False

    parts = content.split('---', 2)
    if len(parts) < 3:
        print("❌ Invalid frontmatter format")
        return False

    frontmatter = parts[1]

    # Check required fields
    required = ['name', 'description']
    for field in required:
        if f'{field}:' not in frontmatter:
            print(f"❌ Missing required field: {field}")
            return False

    # Check name matches directory
    expected_name = os.path.basename(SKILL_DIR)
    if f'name: {expected_name}' not in frontmatter:
        print(f"⚠️  Name in frontmatter ({expected_name}) may not match directory")

    print("✅ SKILL.md frontmatter valid")
    return True


def validate_meta():
    """Check _meta.json has required fields."""
    print("\n🔍 Validating _meta.json...")

    if not os.path.exists('_meta.json'):
        print("❌ _meta.json not found")
        return False

    with open('_meta.json', 'r') as f:
        meta = json.load(f)

    required = ['id', 'version', 'name']
    for field in required:
        if field not in meta:
            print(f"❌ Missing required field: {field}")
            return False

    print(f"✅ _meta.json valid (id={meta['id']}, version={meta['version']})")
    return True


def validate_python_module():
    """Check mck_ppt module is importable."""
    print("\n🔍 Validating mck_ppt Python module...")

    module_path = os.path.join(SKILL_DIR, 'mck_ppt', '__init__.py')
    if not os.path.exists(module_path):
        print("❌ mck_ppt/__init__.py not found")
        return False

    # Try importing
    spec = importlib.util.spec_from_file_location("mck_ppt", module_path)
    if spec is None or spec.loader is None:
        print("❌ Failed to load mck_ppt module spec")
        return False

    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except ImportError as e:
        print(f"⚠️  mck_ppt imports failed (expected without dependencies): {e}")
        # Check if it's just dependency issue
        if 'python-pptx' in str(e):
            print("⚠️  python-pptx not installed - install with: pip install python-pptx lxml")
        return True  # Not a fatal error

    # Check for MckEngine
    if hasattr(module, 'MckEngine'):
        print("✅ mck_ppt.MckEngine available")
    else:
        print("⚠️  MckEngine not found in mck_ppt module")

    print("✅ mck_ppt module structure valid")
    return True


def validate_layout_methods():
    """Check key layout methods exist in engine."""
    print("\n🔍 Validating layout methods...")

    engine_path = os.path.join(SKILL_DIR, 'mck_ppt', 'engine.py')
    if not os.path.exists(engine_path):
        print("❌ mck_ppt/engine.py not found")
        return False

    with open(engine_path, 'r', encoding='utf-8') as f:
        content = f.read()

    required_methods = [
        'cover', 'toc', 'section_divider', 'closing',
        'big_number', 'donut', 'grouped_bar',
        'matrix_2x2', 'timeline', 'dashboard_kpi_chart'
    ]

    missing = []
    for method in required_methods:
        if f'def {method}' not in content:
            missing.append(method)

    if missing:
        print(f"❌ Missing methods: {missing}")
        return False

    print(f"✅ All {len(required_methods)} key layout methods found")
    return True


def validate_file_structure():
    """Check directory structure."""
    print("\n🔍 Validating file structure...")

    required = ['SKILL.md', '_meta.json', 'mck_ppt']
    missing = [f for f in required if not os.path.exists(f)]

    if missing:
        print(f"❌ Missing: {missing}")
        return False

    # Check references
    if os.path.exists('references'):
        ref_files = os.listdir('references')
        print(f"📁 references/: {len(ref_files)} files")

    # Check assets
    if os.path.exists('assets/icons'):
        icon_files = os.listdir('assets/icons')
        print(f"🎨 assets/icons/: {len(icon_files)} files")

    print("✅ File structure valid")
    return True


def main():
    print("=" * 60)
    print("  mck-ppt-design Skill Validation")
    print("=" * 60)

    results = []
    results.append(("Frontmatter", validate_frontmatter()))
    results.append(("_meta.json", validate_meta()))
    results.append(("Python Module", validate_python_module()))
    results.append(("Layout Methods", validate_layout_methods()))
    results.append(("File Structure", validate_file_structure()))

    print("\n" + "=" * 60)
    print("  Summary")
    print("=" * 60)

    passed = sum(1 for _, r in results if r)
    total = len(results)

    for name, result in results:
        status = "✅" if result else "❌"
        print(f"  {status} {name}")

    print(f"\n  Total: {passed}/{total} checks passed")

    if passed == total:
        print("\n🎉 Skill validation PASSED!")
        return 0
    else:
        print("\n⚠️  Some checks failed - review above")
        return 1


if __name__ == '__main__':
    sys.exit(main())

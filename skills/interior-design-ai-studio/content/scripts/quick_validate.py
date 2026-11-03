#!/usr/bin/env python3
"""
室内设计AI工作室 - 快速验证脚本
验证技能结构完整性
"""

import os
import json
from pathlib import Path

def validate_skill(skill_path: str) -> dict:
    """验证技能结构"""
    issues = []
    warnings = []

    skill_path = Path(skill_path)

    # 1. 检查必需文件
    required_files = ['SKILL.md', '_meta.json']
    for f in required_files:
        if not (skill_path / f).exists():
            issues.append(f"Missing required file: {f}")

    # 2. 验证 _meta.json
    meta_path = skill_path / '_meta.json'
    if meta_path.exists():
        try:
            with open(meta_path) as f:
                meta = json.load(f)
            if 'id' not in meta:
                issues.append("Missing 'id' in _meta.json")
            if 'version' not in meta:
                issues.append("Missing 'version' in _meta.json")
        except json.JSONDecodeError as e:
            issues.append(f"Invalid JSON in _meta.json: {e}")

    # 3. 验证 SKILL.md frontmatter
    skill_md = skill_path / 'SKILL.md'
    if skill_md.exists():
        with open(skill_md) as f:
            content = f.read()

        # 检查是否以 --- 开头
        if not content.strip().startswith('---'):
            issues.append("SKILL.md must start with YAML frontmatter (---)")

        # 检查必需字段
        if 'name:' not in content[:500]:
            issues.append("Missing 'name:' in SKILL.md frontmatter")
        if 'description:' not in content[:1000]:
            issues.append("Missing 'description:' in SKILL.md frontmatter")
    else:
        issues.append("Missing SKILL.md")

    # 4. 检查目录结构
    for subdir in ['scripts', 'references', 'assets']:
        if (skill_path / subdir).exists():
            if not list((skill_path / subdir).iterdir()):
                warnings.append(f"Empty directory: {subdir}/")

    return {
        'valid': len(issues) == 0,
        'issues': issues,
        'warnings': warnings
    }

if __name__ == '__main__':
    import sys
    skill_path = sys.argv[1] if len(sys.argv) > 1 else '.'
    result = validate_skill(skill_path)

    print(f"Validation Result: {'✓ PASS' if result['valid'] else '✗ FAIL'}")

    if result['issues']:
        print("\nIssues:")
        for issue in result['issues']:
            print(f"  - {issue}")

    if result['warnings']:
        print("\nWarnings:")
        for warning in result['warnings']:
            print(f"  - {warning}")

    sys.exit(0 if result['valid'] else 1)

#!/usr/bin/env python3
"""美术资产管理脚本 - 验证与打包"""

import json
import os
import sys
from pathlib import Path

def validate_skill(path: str) -> bool:
    """验证技能结构"""
    skill_path = Path(path)

    # 检查必填文件
    required_files = ['SKILL.md', '_meta.json']
    for f in required_files:
        if not (skill_path / f).exists():
            print(f"错误: 缺少 {f}")
            return False

    # 验证 SKILL.md frontmatter
    with open(skill_path / 'SKILL.md', 'r', encoding='utf-8') as f:
        content = f.read()

    if not content.startswith('---'):
        print("错误: SKILL.md 必须以 frontmatter 开始")
        return False

    if 'name:' not in content or 'description:' not in content:
        print("错误: frontmatter 缺少必填字段")
        return False

    # 验证 _meta.json
    with open(skill_path / '_meta.json', 'r', encoding='utf-8') as f:
        meta = json.load(f)

    if 'id' not in meta or 'version' not in meta:
        print("错误: _meta.json 缺少必填字段")
        return False

    print("✓ 验证通过")
    return True

if __name__ == '__main__':
    skill_path = sys.argv[1] if len(sys.argv) > 1 else '.'
    sys.exit(0 if validate_skill(skill_path) else 1)
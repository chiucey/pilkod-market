#!/usr/bin/env python3
"""
技能结构验证脚本
用法：python quick_validate.py <skill_root_dir>
"""

import sys
import json
import re
from pathlib import Path


def validate_skill(skill_root: Path) -> tuple[bool, list[str]]:
    errors = []
    warnings = []

    # 1. 检查必要文件
    required_files = ['SKILL.md', '_meta.json']
    for fname in required_files:
        if not (skill_root / fname).exists():
            errors.append(f'❌ 缺少必要文件: {fname}')

    # 2. 验证 SKILL.md frontmatter
    skill_md = skill_root / 'SKILL.md'
    if skill_md.exists():
        content = skill_md.read_text(encoding='utf-8')
        lines = content.split('\n')

        # 检查第一行必须是 ---
        if not lines[0].strip() == '---':
            errors.append('❌ SKILL.md 第一行必须是 --- (frontmatter 开始)')

        # 提取 frontmatter
        if content.startswith('---'):
            end = content.find('\n---\n', 3)
            if end == -1:
                errors.append('❌ SKILL.md frontmatter 未正确关闭（缺少结束 ---）')
            else:
                fm = content[4:end]
                if 'name:' not in fm:
                    errors.append('❌ SKILL.md frontmatter 缺少 name 字段')
                if 'description:' not in fm:
                    errors.append('❌ SKILL.md frontmatter 缺少 description 字段')

                # 检查 name 格式（连字符英文）
                name_m = re.search(r'name:\s*(.+)', fm)
                if name_m:
                    name = name_m.group(1).strip()
                    if not re.match(r'^[a-z0-9-]+$', name):
                        errors.append(f'❌ name 字段应为小写连字符英文格式，当前: {name}')
                    # 检查文件夹名与 name 是否一致
                    if skill_root.name != name:
                        errors.append(f'❌ 文件夹名 ({skill_root.name}) 与 SKILL.md name ({name}) 不一致')

    # 3. 验证 _meta.json
    meta_file = skill_root / '_meta.json'
    if meta_file.exists():
        try:
            meta = json.loads(meta_file.read_text(encoding='utf-8'))
            if 'id' not in meta:
                errors.append('❌ _meta.json 缺少 id 字段')
            if 'version' not in meta:
                errors.append('❌ _meta.json 缺少 version 字段')
            else:
                # 语义化版本检查
                if not re.match(r'^\d+\.\d+\.\d+$', str(meta.get('version', ''))):
                    warnings.append(f'⚠️  version 建议使用语义化版本格式（如 1.0.0），当前: {meta.get("version")}')
        except json.JSONDecodeError as e:
            errors.append(f'❌ _meta.json JSON 格式错误: {e}')

    # 4. 检查 scripts/ 目录（如存在）
    scripts_dir = skill_root / 'scripts'
    if scripts_dir.exists():
        for py_file in scripts_dir.glob('*.py'):
            content = py_file.read_text(encoding='utf-8', errors='replace')
            # 检查是否包含中文路径（潜在问题）
            if re.search(r'[^\x00-\x7F]{3,}', content[:200]):
                pass  # 中文注释/字符串是允许的

    # 5. 检查安全：不应包含 secrets
    dangerous_patterns = [r'api[_-]?key\s*=\s*["\'][^"\']{8,}', r'password\s*=\s*["\'][^"\']{4,}',
                          r'token\s*=\s*["\'][^"\']{8,}']
    for f in skill_root.rglob('*'):
        if f.is_file() and f.suffix in ('.py', '.md', '.json', '.txt'):
            text = f.read_text(encoding='utf-8', errors='replace')
            for pat in dangerous_patterns:
                if re.search(pat, text, re.I):
                    warnings.append(f'⚠️  {f.name} 可能包含硬编码凭证，请检查')

    return len(errors) == 0, errors + warnings


if __name__ == '__main__':
    skill_root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('.')
    ok, messages = validate_skill(skill_root)

    for msg in messages:
        print(msg)

    if ok:
        print(f'\n✅ 验证通过：{skill_root.name}')
        sys.exit(0)
    else:
        print(f'\n❌ 验证失败，请修复以上错误')
        sys.exit(1)

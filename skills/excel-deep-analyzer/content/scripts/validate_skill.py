#!/usr/bin/env python3
"""
验证Excel深度分析技能的结构和内容
"""

import os
import sys
from pathlib import Path
from typing import Tuple, List
import re


def validate_skill(skill_path: str) -> Tuple[bool, List[str]]:
    """验证技能结构和内容"""
    errors = []
    warnings = []

    skill_path = Path(skill_path)

    # 检查必需文件
    required_files = ['SKILL.md', '_meta.json']
    for file in required_files:
        file_path = skill_path / file
        if not file_path.exists():
            errors.append(f"缺少必需文件: {file}")

    # 验证SKILL.md
    skill_md = skill_path / 'SKILL.md'
    if skill_md.exists():
        content = skill_md.read_text(encoding='utf-8')

        # 检查frontmatter
        if not content.startswith('---'):
            errors.append("SKILL.md 必须以 YAML frontmatter 开头(---)")
        else:
            # 提取frontmatter
            frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
            if frontmatter_match:
                frontmatter = frontmatter_match.group(1)

                # 检查必需字段
                if 'name:' not in frontmatter:
                    errors.append("Frontmatter缺少name字段")
                if 'description:' not in frontmatter:
                    errors.append("Frontmatter缺少description字段")

                # 检查name格式
                name_match = re.search(r'^name:\s*(.+)$', frontmatter, re.MULTILINE)
                if name_match:
                    name = name_match.group(1).strip()
                    if not re.match(r'^[a-z0-9-]+$', name):
                        errors.append(f"name字段格式不正确: '{name}' (应使用小写字母、数字、连字符)")

                # 检查description包含触发短语
                desc_match = re.search(r'^description:\s*(.+)$', frontmatter, re.MULTILINE | re.DOTALL)
                if desc_match:
                    desc = desc_match.group(1)
                    if '当用户' not in desc and 'when' not in desc.lower():
                        warnings.append("description建议包含触发条件描述(当用户...时使用)")

            # 检查没有在frontmatter前有标题
            lines = content.split('\n')
            frontmatter_end = -1
            for i, line in enumerate(lines):
                if line == '---':
                    if frontmatter_end == -1:
                        frontmatter_end = i
                    else:
                        break

            for i in range(frontmatter_end + 1, min(frontmatter_end + 5, len(lines))):
                if lines[i].strip().startswith('#'):
                    errors.append(f"Frontmatter后不应该有markdown标题在第{i+1}行")
                    break

    # 验证_meta.json
    meta_json = skill_path / '_meta.json'
    if meta_json.exists():
        import json
        try:
            meta = json.loads(meta_json.read_text(encoding='utf-8'))

            if 'id' not in meta:
                errors.append("_meta.json缺少id字段")
            if 'version' not in meta:
                errors.append("_meta.json缺少version字段")
            elif not re.match(r'^\d+\.\d+\.\d+$', meta['version']):
                errors.append(f"version字段格式不正确: '{meta['version']}' (应为x.y.z格式)")

        except json.JSONDecodeError as e:
            errors.append(f"_meta.json JSON格式错误: {e}")

    # 检查目录结构
    if not skill_path.name.replace('_', '-').replace('_', '-').isidentifier():
        warnings.append(f"技能名称可能不符合规范: {skill_path.name}")

    # 检查路径名称是否包含中文
    for part in skill_path.parts:
        if re.search(r'[\u4e00-\u9fff]', part):
            errors.append(f"路径包含中文字符: {part}")

    return len(errors) == 0, errors + warnings


def main():
    if len(sys.argv) < 2:
        skill_path = '/workspace/temp-skills/excel-deep-analyzer'
    else:
        skill_path = sys.argv[1]

    print(f"验证技能: {skill_path}")
    print("=" * 60)

    is_valid, messages = validate_skill(skill_path)

    for msg in messages:
        prefix = "❌" if "缺少" in msg or "错误" in msg or "中文" in msg else "⚠️"
        print(f"{prefix} {msg}")

    print("=" * 60)

    if is_valid:
        print("✅ 验证通过!")
        return 0
    else:
        print("❌ 验证失败!")
        return 1


if __name__ == "__main__":
    from typing import Tuple, List
    sys.exit(main())

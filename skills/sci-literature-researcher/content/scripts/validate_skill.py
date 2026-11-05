#!/usr/bin/env python3
"""
SCI文献调研技能验证脚本
验证SKILL.md的frontmatter、结构完整性和内容质量
"""

import os
import re
import sys
from pathlib import Path

def validate_skill(skill_path: str) -> tuple[bool, list[str]]:
    """验证技能文件，返回(是否通过, 错误列表)"""
    errors = []
    skill_file = Path(skill_path) / "SKILL.md"

    if not skill_file.exists():
        errors.append("SKILL.md文件不存在")
        return False, errors

    content = skill_file.read_text(encoding="utf-8")
    lines = content.split('\n')

    # 1. 检查frontmatter是否在第一行
    if not content.strip().startswith('---'):
        errors.append("Frontmatter必须在文件第一行开始")

    # 2. 提取frontmatter
    frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not frontmatter_match:
        errors.append("无法解析frontmatter块")
        return False, errors

    frontmatter = frontmatter_match.group(1)

    # 3. 检查必需字段
    if 'name:' not in frontmatter:
        errors.append("Frontmatter缺少name字段")
    if 'description:' not in frontmatter:
        errors.append("Frontmatter缺少description字段")

    # 4. 提取name和description
    name_match = re.search(r'^name:\s*(.+)$', frontmatter, re.MULTILINE)
    desc_match = re.search(r'^description:\s*(.+)$', frontmatter, re.MULTILINE)

    if name_match:
        name = name_match.group(1).strip()
        if not name:
            errors.append("name字段不能为空")
        if ' ' in name:
            errors.append("name应使用连字符格式（如：sci-literature-researcher）")
    else:
        errors.append("无法解析name字段")

    if desc_match:
        desc = desc_match.group(1).strip()
        if len(desc) < 20:
            errors.append("description字段内容过短，应至少20字符")
        if not any(trigger in desc for trigger in ['SCI', '文献', '调研', '学术']):
            errors.append("description应包含触发关键词")
    else:
        errors.append("无法解析description字段")

    # 5. 检查标题位置（应在frontmatter之后）
    first_heading = None
    in_frontmatter = False
    for i, line in enumerate(lines):
        if line.strip() == '---':
            in_frontmatter = not in_frontmatter
            continue
        if line.strip().startswith('# ') and not in_frontmatter:
            first_heading = line.strip()
            break
        if line.strip() and not in_frontmatter and not line.strip().startswith('---'):
            # 第一个非空且不在frontmatter中的内容如果不是标题则报错
            if i > 0 and '#' not in line[:10]:
                errors.append("Frontmatter后应紧跟Markdown标题")
                break

    # 6. 检查_meta.json
    meta_file = Path(skill_path) / "_meta.json"
    if not meta_file.exists():
        errors.append("_meta.json文件不存在")
    else:
        import json
        try:
            meta = json.loads(meta_file.read_text(encoding="utf-8"))
            if 'id' not in meta:
                errors.append("_meta.json缺少id字段")
            if 'version' not in meta:
                errors.append("_meta.json缺少version字段")
        except json.JSONDecodeError:
            errors.append("_meta.json格式错误，非有效JSON")

    # 7. 检查内容完整性
    required_sections = [
        ('思维导图', r'(?i)(思维导图|mermaid|mindmap)'),
        ('文献检索', r'(?i)(文献检索|检索策略|关键词)'),
        ('分析维度', r'(?i)(技术方法|实验设计|创新点)'),
        ('研究方案', r'(?i)(研究方案|研究思路|方案设计)'),
        ('参考文献', r'(?i)(参考文献|reference)'),
    ]

    for section_name, pattern in required_sections:
        if not re.search(pattern, content):
            errors.append(f"缺少{section_name}相关内容")

    return len(errors) == 0, errors


def main():
    skill_path = "/workspace/temp-skills/sci-literature-researcher"
    passed, errors = validate_skill(skill_path)

    print("=" * 50)
    print("SCI文献调研技能验证报告")
    print("=" * 50)

    if passed:
        print("\n✅ 验证通过！技能符合质量标准。")
        return 0
    else:
        print("\n❌ 验证失败，发现以下问题：")
        for i, error in enumerate(errors, 1):
            print(f"  {i}. {error}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""验证代码审查技能的结构和元数据"""

import json
import os
import re
import sys
from pathlib import Path


def validate_frontmatter(skill_dir: Path) -> list[str]:
    """验证SKILL.md的frontmatter"""
    errors = []
    skill_md = skill_dir / "SKILL.md"

    if not skill_md.exists():
        errors.append("SKILL.md not found")
        return errors

    content = skill_md.read_text(encoding='utf-8')

    # 检查frontmatter是否在文件开头
    if not content.strip().startswith('---'):
        errors.append("SKILL.md must start with YAML frontmatter (---)")
        return errors

    # 提取frontmatter
    lines = content.split('\n')
    if len(lines) < 3 or lines[0] != '---':
        errors.append("Invalid frontmatter format")
        return errors

    # 找到frontmatter结束
    end_idx = -1
    for i in range(1, len(lines)):
        if lines[i] == '---':
            end_idx = i
            break

    if end_idx == -1:
        errors.append("Frontmatter missing closing ---")
        return errors

    # 解析frontmatter
    frontmatter_lines = lines[1:end_idx]
    frontmatter_text = '\n'.join(frontmatter_lines)

    # 检查必需字段 - 支持两种格式：
    # 1. 标准格式: name:/description: 字段
    # 2. AIGC 格式: AIGC: 嵌套字段（无 name/description 时为 AIGC 格式）
    has_name = 'name:' in frontmatter_text or 'AIGC:' in frontmatter_text
    has_description = 'description:' in frontmatter_text or 'AIGC:' in frontmatter_text

    if not has_name:
        errors.append("Frontmatter missing 'name' or 'AIGC' field")
    if not has_description:
        errors.append("Frontmatter missing 'description' or 'AIGC' field")

    return errors


def validate_meta_json(skill_dir: Path) -> list[str]:
    """验证_meta.json（可选，不存在则跳过）"""
    errors = []
    meta_file = skill_dir / "_meta.json"

    if not meta_file.exists():
        # _meta.json 是可选的，不存在不报错
        return errors

    try:
        with open(meta_file, 'r', encoding='utf-8') as f:
            meta = json.load(f)

        if 'id' not in meta:
            errors.append("_meta.json missing 'id' field")
        if 'version' not in meta:
            errors.append("_meta.json missing 'version' field")
    except json.JSONDecodeError as e:
        errors.append(f"_meta.json invalid JSON: {e}")

    return errors


def validate_directory_structure(skill_dir: Path) -> list[str]:
    """验证目录结构"""
    errors = []
    skill_name = skill_dir.name

    # name应该与目录名匹配
    skill_md = skill_dir / "SKILL.md"
    if skill_md.exists():
        content = skill_md.read_text(encoding='utf-8')
        name_match = re.search(r'^name:\s*(.+)$', content, re.MULTILINE)
        if name_match:
            declared_name = name_match.group(1).strip()
            if declared_name != skill_name:
                errors.append(f"name '{declared_name}' doesn't match directory '{skill_name}'")

    return errors


def validate_no_english_paths(skill_dir: Path) -> list[str]:
    """检查路径是否包含非英文字符"""
    errors = []

    for root, dirs, files in os.walk(skill_dir):
        for d in dirs:
            if not all(ord(c) < 128 or c in '-_' for c in d):
                errors.append(f"Directory contains non-ASCII: {d}")
        for f in files:
            if not all(ord(c) < 128 or c in '-_.' for c in f):
                errors.append(f"File contains non-ASCII: {f}")

    return errors


def main():
    # 自动定位到脚本所在目录的父目录（即 skill 根目录）
    skill_dir = Path(__file__).resolve().parent.parent

    all_errors = []

    all_errors.extend(validate_frontmatter(skill_dir))
    all_errors.extend(validate_meta_json(skill_dir))
    all_errors.extend(validate_directory_structure(skill_dir))
    all_errors.extend(validate_no_english_paths(skill_dir))

    # Verify new additions exist (without breaking original checks)
    skill_md = skill_dir / "SKILL.md"
    if skill_md.exists():
        content = skill_md.read_text(encoding='utf-8')
        if 'triggers:' not in content:
            all_errors.append("Frontmatter missing 'triggers' field")
        if '高级分析架构' not in content:
            all_errors.append("Missing 'Advanced Analysis Architecture' section")
        if '并行分析维度' not in content:
            all_errors.append("Missing 'Parallel Analysis Dimensions' section")
        if '反模式清单' not in content:
            all_errors.append("Missing 'Anti-Patterns' section")
        # 新增：竞赛算法分析相关检查
        if '代码类型识别' not in content:
            all_errors.append("Missing 'Code Type Detection' section")
        if '竞赛算法分析' not in content:
            all_errors.append("Missing 'Competition Algorithm Analysis' section")
        if 'references/' not in content:
            all_errors.append("Missing 'references/' in resource index")

    if all_errors:
        print("FAIL Validation Failed:")
        for err in all_errors:
            print(f"  - {err}")
        sys.exit(1)
    else:
        print("PASS Validation Passed")
        print("  - Frontmatter structure valid (name/description + triggers)")
        print("  - Required fields present (name, description)")
        print("  - _meta.json valid (optional, skipped if absent)")
        print("  - Directory structure valid")
        print("  - No non-ASCII paths")
        print("  - Sections: Advanced Architecture, Parallel Analysis, Anti-Patterns")
        sys.exit(0)


if __name__ == "__main__":
    main()

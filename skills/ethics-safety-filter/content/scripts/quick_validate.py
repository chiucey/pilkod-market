#!/usr/bin/env python3
"""
伦理安全过滤器 - 快速验证脚本
验证技能文件的 frontmatter、结构完整性和内容质量
"""

import json
import os
import re
import sys
from pathlib import Path


def validate_frontmatter(skill_path: Path) -> tuple[bool, str]:
    """验证 frontmatter 格式"""
    sk_file = skill_path / "SKILL.md"
    if not sk_file.exists():
        return False, "SKILL.md 文件不存在"

    content = sk_file.read_text(encoding="utf-8")

    # 检查是否以 --- 开头
    if not content.startswith("---"):
        return False, "SKILL.md 必须以 YAML frontmatter 块开头（---）"

    # 提取 frontmatter
    parts = content.split("---", 2)
    if len(parts) < 3:
        return False, "Frontmatter 格式不完整"

    frontmatter = parts[1]

    # 检查必需字段
    if "name:" not in frontmatter:
        return False, "Frontmatter 缺少 'name' 字段"
    if "description:" not in frontmatter:
        return False, "Frontmatter 缺少 'description' 字段"

    # 验证 name 格式（连字符）
    name_match = re.search(r'^name:\s*(.+)$', frontmatter, re.MULTILINE)
    if name_match:
        name = name_match.group(1).strip()
        if not re.match(r'^[a-z0-9-]+$', name):
            return False, f"name '{name}' 必须使用小写字母、数字和连字符"

    return True, "Frontmatter 验证通过"


def validate_meta_json(skill_path: Path) -> tuple[bool, str]:
    """验证 _meta.json 文件"""
    meta_file = skill_path / "_meta.json"
    if not meta_file.exists():
        return False, "_meta.json 文件不存在"

    try:
        meta = json.loads(meta_file.read_text(encoding="utf-8"))

        if "id" not in meta:
            return False, "_meta.json 缺少 'id' 字段"
        if "version" not in meta:
            return False, "_meta.json 缺少 'version' 字段"

        if not isinstance(meta["id"], (int, str)):
            return False, "'id' 必须是数字或字符串"

        if not re.match(r'^\d+\.\d+\.\d+$', meta["version"]):
            return False, "'version' 必须符合语义化版本格式 (x.y.z)"

        return True, "_meta.json 验证通过"
    except json.JSONDecodeError as e:
        return False, f"_meta.json JSON 解析失败: {e}"


def validate_naming(skill_path: Path) -> tuple[bool, str]:
    """验证文件夹和文件命名"""
    # 文件夹名必须与 frontmatter name 一致
    sk_file = skill_path / "SKILL.md"
    content = sk_file.read_text(encoding="utf-8")

    parts = content.split("---", 2)
    frontmatter = parts[1]
    name_match = re.search(r'^name:\s*(.+)$', frontmatter, re.MULTILINE)

    if name_match:
        expected_name = name_match.group(1).strip()
        folder_name = skill_path.name

        if folder_name != expected_name:
            return False, f"文件夹名 '{folder_name}' 与 name '{expected_name}' 不匹配"

    # 检查是否有中文字符（不允许）
    if re.search(r'[\u4e00-\u9fff]', skill_path.name):
        return False, f"文件夹名不能包含中文字符: {skill_path.name}"

    # 检查所有文件
    for f in skill_path.rglob("*"):
        if f.is_file():
            if re.search(r'[\u4e00-\u9fff]', f.name):
                return False, f"文件名不能包含中文字符: {f.name}"

    return True, "命名验证通过"


def validate_content_quality(skill_path: Path) -> tuple[bool, list[str]]:
    """验证内容质量"""
    issues = []
    sk_file = skill_path / "SKILL.md"
    content = sk_file.read_text(encoding="utf-8")

    # 检查触发短语
    if "description:" in content:
        desc_match = re.search(r'^description:\s*(.+)$', content, re.MULTILINE)
        if desc_match:
            desc = desc_match.group(1)
            if len(desc) < 20:
                issues.append("description 太短，应包含足够的触发短语信息")
            if "当" not in desc and "when" not in desc.lower():
                issues.append("description 应包含触发条件描述")

    # 检查是否有有效内容
    body = content.split("---", 2)[2].strip() if "---" in content else content
    if len(body) < 200:
        issues.append("SKILL.md 内容过短，应包含完整的工作流程说明")

    return len(issues) == 0, issues


def main():
    skill_path = Path("/workspace/temp-skills/ethics-safety-filter")

    print("=" * 50)
    print("伦理安全过滤器 - 验证报告")
    print("=" * 50)

    all_passed = True

    # Frontmatter 验证
    passed, msg = validate_frontmatter(skill_path)
    print(f"\n[{'✓' if passed else '✗'}] Frontmatter: {msg}")
    all_passed &= passed

    # Meta JSON 验证
    passed, msg = validate_meta_json(skill_path)
    print(f"[{'✓' if passed else '✗'}] Meta JSON: {msg}")
    all_passed &= passed

    # 命名验证
    passed, msg = validate_naming(skill_path)
    print(f"[{'✓' if passed else '✗'}] 命名规范: {msg}")
    all_passed &= passed

    # 内容质量验证
    passed, issues = validate_content_quality(skill_path)
    print(f"[{'✓' if passed else '✗'}] 内容质量:")
    if issues:
        for issue in issues:
            print(f"    - {issue}")
        all_passed = False
    else:
        print("    - 所有检查通过")

    print("\n" + "=" * 50)
    if all_passed:
        print("✓ 所有验证通过")
        sys.exit(0)
    else:
        print("✗ 存在验证问题，请修复后重试")
        sys.exit(1)


if __name__ == "__main__":
    main()

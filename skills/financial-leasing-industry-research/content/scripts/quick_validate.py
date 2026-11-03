#!/usr/bin/env python3
"""
金融租赁产业研究技能验证脚本
验证 SKILL.md 和目录结构的有效性
"""

import os
import sys
import json
import re
from pathlib import Path


def validate_frontmatter(skill_path: Path) -> tuple[bool, str]:
    """验证 frontmatter 格式"""
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        return False, "SKILL.md 文件不存在"

    content = skill_md.read_text(encoding="utf-8")

    # 检查是否以 --- 开头
    if not content.strip().startswith("---"):
        return False, "SKILL.md 必须以 --- 开头"

    # 提取 frontmatter
    frontmatter_match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not frontmatter_match:
        return False, "无法解析 frontmatter"

    frontmatter_text = frontmatter_match.group(1)

    # 检查必需字段
    required_fields = ["name", "description"]
    for field in required_fields:
        if not re.search(rf"^{field}:", frontmatter_text, re.MULTILINE):
            return False, f"frontmatter 缺少必需字段: {field}"

    # 检查 name 格式（连字符）
    name_match = re.search(r"^name:\s*(.+)$", frontmatter_text, re.MULTILINE)
    if name_match:
        name_value = name_match.group(1).strip()
        if " " in name_value or name_value != name_value.lower():
            return False, f"name 字段格式错误（应使用连字符小写）: {name_value}"

    return True, "验证通过"


def validate_meta_json(skill_path: Path) -> tuple[bool, str]:
    """验证 _meta.json 格式"""
    meta_file = skill_path / "_meta.json"
    if not meta_file.exists():
        return False, "_meta.json 文件不存在"

    try:
        meta = json.loads(meta_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return False, f"_meta.json JSON 解析错误: {e}"

    # 检查必需字段
    required_fields = ["id", "version"]
    for field in required_fields:
        if field not in meta:
            return False, f"_meta.json 缺少必需字段: {field}"

    # 检查 version 格式（语义化版本）
    version = meta.get("version", "")
    if not re.match(r"^\d+\.\d+\.\d+$", version):
        return False, f"version 格式错误（应为语义化版本如 1.0.0）: {version}"

    return True, "验证通过"


def validate_directory_structure(skill_path: Path) -> tuple[bool, str]:
    """验证目录结构"""
    # 检查必需文件
    required_files = ["SKILL.md", "_meta.json"]
    for filename in required_files:
        file_path = skill_path / filename
        if not file_path.exists():
            return False, f"缺少必需文件: {filename}"

    # 检查可选目录
    optional_dirs = ["references", "scripts", "assets"]
    existing_dirs = [d for d in optional_dirs if (skill_path / d).is_dir()]

    return True, f"目录结构验证通过，现有目录: {', '.join(existing_dirs) if existing_dirs else '无'}"


def validate_naming_consistency(skill_path: Path) -> tuple[bool, str]:
    """验证命名一致性"""
    skill_md = skill_path / "SKILL.md"
    meta_file = skill_path / "_meta.json"

    # 从 frontmatter 获取 name
    content = skill_md.read_text(encoding="utf-8")
    frontmatter_match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if frontmatter_match:
        frontmatter_text = frontmatter_match.group(1)
        name_match = re.search(r"^name:\s*(.+)$", frontmatter_text, re.MULTILINE)
        if name_match:
            frontmatter_name = name_match.group(1).strip()

            # 从 meta 获取 name
            meta = json.loads(meta_file.read_text(encoding="utf-8"))
            meta_name = meta.get("name", "")

            # 检查一致性
            if frontmatter_name != meta_name:
                return False, f"name 不一致: SKILL.md={frontmatter_name}, _meta.json={meta_name}"

            # 检查与文件夹名称的一致性
            folder_name = skill_path.name
            if frontmatter_name != folder_name:
                return False, f"文件夹名称与 name 不一致: 文件夹={folder_name}, name={frontmatter_name}"

    return True, "命名一致性验证通过"


def validate_no_profanity(skill_path: Path) -> tuple[bool, str]:
    """检查是否有不安全的内容（如符号链接逃逸）"""
    # 检查是否有符号链接逃逸
    for root, dirs, files in os.walk(skill_path):
        for d in dirs:
            dir_path = Path(root) / d
            if dir_path.is_symlink():
                return False, f"发现符号链接: {dir_path}"

    return True, "安全检查通过"


def main():
    """主验证函数"""
    if len(sys.argv) > 1:
        skill_path = Path(sys.argv[1])
    else:
        script_dir = Path(__file__).parent
        skill_path = script_dir.parent

    print(f"验证技能路径: {skill_path}")
    print("-" * 50)

    validations = [
        ("Frontmatter 验证", validate_frontmatter),
        ("_meta.json 验证", validate_meta_json),
        ("目录结构验证", validate_directory_structure),
        ("命名一致性验证", validate_naming_consistency),
        ("安全检查", validate_no_profanity),
    ]

    all_passed = True
    for name, validator in validations:
        passed, message = validator(skill_path)
        status = "✓" if passed else "✗"
        print(f"{status} {name}: {message}")
        if not passed:
            all_passed = False

    print("-" * 50)
    if all_passed:
        print("所有验证通过！")
        sys.exit(0)
    else:
        print("验证失败，请修复上述问题")
        sys.exit(1)


if __name__ == "__main__":
    main()

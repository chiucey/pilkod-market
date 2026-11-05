#!/usr/bin/env python3
"""
浏览器爬虫技能验证脚本
验证 SKILL.md 和元数据的完整性
"""

import json
import os
import re
import sys
from pathlib import Path

def validate_frontmatter(skill_path: Path) -> tuple[bool, str]:
    """验证 frontmatter 格式"""
    skill_md = skill_path / "SKILL.md"

    if not skill_md.exists():
        return False, "SKILL.md not found"

    content = skill_md.read_text(encoding="utf-8")

    # 检查是否以 --- 开头
    if not content.startswith("---"):
        return False, "SKILL.md must start with --- (frontmatter delimiter)"

    # 检查 frontmatter 结束
    frontmatter_end = content.find("\n---", 3)
    if frontmatter_end == -1:
        return False, "Frontmatter not properly closed with ---"

    frontmatter_text = content[3:frontmatter_end]

    # 验证必填字段
    if "name:" not in frontmatter_text:
        return False, "Frontmatter missing 'name' field"

    if "description:" not in frontmatter_text:
        return False, "Frontmatter missing 'description' field"

    # 检查 name 格式（连字符）
    name_match = re.search(r"name:\s*([a-z0-9-]+)", frontmatter_text)
    if not name_match:
        return False, "Invalid name format (use hyphen-case)"

    return True, "Frontmatter valid"

def validate_meta_json(skill_path: Path) -> tuple[bool, str]:
    """验证 _meta.json 格式"""
    meta_file = skill_path / "_meta.json"

    if not meta_file.exists():
        return False, "_meta.json not found"

    try:
        meta = json.loads(meta_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return False, f"Invalid JSON: {e}"

    # 验证必填字段
    if "id" not in meta:
        return False, "_meta.json missing 'id' field"

    if "version" not in meta:
        return False, "_meta.json missing 'version' field"

    # 验证 id 是数字
    if not isinstance(meta["id"], (int, str)):
        return False, "'id' must be a number or string"

    # 验证 version 格式
    version = str(meta["version"])
    if not re.match(r"^\d+\.\d+\.\d+$", version):
        return False, "'version' must follow semantic versioning (e.g., 1.0.0)"

    return True, "_meta.json valid"

def validate_naming(skill_path: Path, skill_name: str) -> tuple[bool, str]:
    """验证命名一致性"""
    folder_name = skill_path.name

    if folder_name != skill_name:
        return False, f"Folder name '{folder_name}' doesn't match skill name '{skill_name}'"

    return True, "Naming consistent"

def validate_structure(skill_path: Path) -> tuple[bool, str]:
    """验证目录结构"""
    required_files = ["SKILL.md", "_meta.json"]

    for file in required_files:
        if not (skill_path / file).exists():
            return False, f"Missing required file: {file}"

    return True, "Structure valid"

def validate_security_constraints(skill_path: Path) -> tuple[bool, str]:
    """验证安全约束存在"""
    skill_md = skill_path / "SKILL.md"
    content = skill_md.read_text(encoding="utf-8")

    security_keywords = [
        "localhost",
        "内网",
        "intranet",
        "禁止",
        "禁止访问",
        "anti-crawl",
        "反爬"
    ]

    has_security = any(keyword.lower() in content.lower() for keyword in security_keywords)

    if not has_security:
        return False, "Missing security constraint documentation"

    return True, "Security constraints documented"

def validate_output_schema(skill_path: Path) -> tuple[bool, str]:
    """验证输出格式定义"""
    skill_md = skill_path / "SKILL.md"
    content = skill_md.read_text(encoding="utf-8")

    # 检查是否包含输出格式示例
    if '"status"' not in content or '"content"' not in content:
        return False, "Missing output schema definition"

    return True, "Output schema defined"

def run_validations(skill_path: Path):
    """运行所有验证并返回结果"""
    results = []

    validations = [
        ("结构验证", validate_structure),
        ("Frontmatter 验证", validate_frontmatter),
        ("元数据验证", validate_meta_json),
        ("命名验证", lambda p: validate_naming(p, "browser-crawler")),
        ("安全约束验证", validate_security_constraints),
        ("输出格式验证", validate_output_schema),
    ]

    for name, validator in validations:
        try:
            passed, msg = validator(skill_path)
            results.append((name, passed, msg))
        except Exception as e:
            results.append((name, False, str(e)))

    return results

def main():
    skill_path = Path(__file__).parent.parent

    print("=" * 50)
    print("浏览器爬虫技能验证")
    print("=" * 50)

    results = run_validations(skill_path)
    all_passed = True

    for name, passed, msg in results:
        status = "PASS" if passed else "FAIL"
        print(f"[{status}] {name}: {msg}")
        if not passed:
            all_passed = False

    print("=" * 50)
    if all_passed:
        print("验证结果: 全部通过 ✓")
        return 0
    else:
        print("验证结果: 存在失败项 ✗")
        return 1

if __name__ == "__main__":
    sys.exit(main())

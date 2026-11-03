#!/usr/bin/env python3
"""
财务报告分析技能验证脚本
验证SKILL.md格式、frontmatter完整性、目录结构合理性
"""

import os
import re
import sys
from pathlib import Path

def validate_frontmatter(skill_path: str) -> tuple[bool, list[str]]:
    """验证frontmatter格式和必填字段"""
    errors = []
    skill_md = Path(skill_path) / "SKILL.md"

    if not skill_md.exists():
        return False, ["SKILL.md not found"]

    content = skill_md.read_text(encoding="utf-8")

    # 检查是否以---开头
    if not content.startswith("---"):
        errors.append("SKILL.md must start with frontmatter (---)")
        return False, errors

    # 提取frontmatter
    lines = content.split("\n")
    frontmatter_end = -1
    for i, line in enumerate(lines[1:], 1):
        if line.strip() == "---":
            frontmatter_end = i
            break

    if frontmatter_end == -1:
        errors.append("Frontmatter closing (---) not found")
        return False, errors

    frontmatter_text = "\n".join(lines[1:frontmatter_end])

    # 检查必填字段
    required_fields = ["name", "description"]
    for field in required_fields:
        pattern = rf"^{field}:\s*.+$"
        if not re.search(pattern, frontmatter_text, re.MULTILINE):
            errors.append(f"Required field '{field}' not found in frontmatter")

    # 验证name格式（连字符）
    name_match = re.search(r"^name:\s*(.+)$", frontmatter_text, re.MULTILINE)
    if name_match:
        name_value = name_match.group(1).strip()
        if not re.match(r"^[a-z0-9-]+$", name_value):
            errors.append(f"name '{name_value}' should use hyphen-case (lowercase with hyphens)")

    # 检查description是否包含触发词
    desc_match = re.search(r"^description:\s*(.+)$", frontmatter_text, re.MULTILINE)
    if desc_match:
        desc_value = desc_match.group(1).strip()
        if len(desc_value) < 20:
            errors.append("description should be at least 20 characters for proper routing")

    return len(errors) == 0, errors


def validate_meta_json(skill_path: str) -> tuple[bool, list[str]]:
    """验证_meta.json格式"""
    errors = []
    meta_path = Path(skill_path) / "_meta.json"

    if not meta_path.exists():
        return False, ["_meta.json not found"]

    import json
    try:
        with open(meta_path, "r", encoding="utf-8") as f:
            meta = json.load(f)
    except json.JSONDecodeError as e:
        return False, [f"_meta.json is not valid JSON: {e}"]

    # 检查必填字段
    required_fields = ["id", "version"]
    for field in required_fields:
        if field not in meta:
            errors.append(f"Required field '{field}' not found in _meta.json")

    # 验证id是整数
    if "id" in meta and not isinstance(meta["id"], int):
        errors.append("id should be an integer")

    # 验证version格式
    if "version" in meta:
        version = meta["version"]
        if not re.match(r"^\d+\.\d+\.\d+$", version):
            errors.append(f"version '{version}' should follow semantic versioning (e.g., 1.0.0)")

    return len(errors) == 0, errors


def validate_directory_structure(skill_path: str) -> tuple[bool, list[str]]:
    """验证目录结构合理性"""
    errors = []
    skill_name = Path(skill_path).name

    # 检查目录名与name字段匹配
    meta_path = Path(skill_path) / "_meta.json"
    if meta_path.exists():
        import json
        try:
            with open(meta_path, "r", encoding="utf-8") as f:
                meta = json.load(f)
            expected_name = meta.get("name", "")
            if expected_name and expected_name != skill_name:
                errors.append(f"Directory name '{skill_name}' should match 'name' field '{expected_name}'")
        except:
            pass

    # 检查可选目录是否存在且有内容
    optional_dirs = ["scripts", "references", "assets"]
    for dir_name in optional_dirs:
        dir_path = Path(skill_path) / dir_name
        if dir_path.exists():
            # 检查是否有文件
            files = list(dir_path.rglob("*"))
            if len(files) == 0:
                errors.append(f"Directory '{dir_name}' is empty, consider removing it")

    return len(errors) == 0, errors


def validate_file_paths(skill_path: str) -> tuple[bool, list[str]]:
    """验证文件路径不包含非英文字符"""
    errors = []
    skill_path_obj = Path(skill_path)

    for file_path in skill_path_obj.rglob("*"):
        if file_path.is_file():
            # 检查文件名
            name = file_path.name
            if not all(ord(c) < 128 for c in name):
                errors.append(f"File name '{name}' contains non-ASCII characters")

            # 检查目录路径
            rel_path = file_path.relative_to(skill_path_obj)
            path_str = str(rel_path)
            if not all(ord(c) < 128 or c == '/' for c in path_str):
                errors.append(f"Path '{path_str}' contains non-ASCII characters")

    return len(errors) == 0, errors


def main():
    """主验证流程"""
    if len(sys.argv) < 2:
        skill_path = "."
    else:
        skill_path = sys.argv[1]

    print(f"Validating skill at: {skill_path}")
    print("=" * 50)

    all_valid = True
    all_errors = []

    # 执行各项验证
    validations = [
        ("Frontmatter & Format", validate_frontmatter),
        ("_meta.json", validate_meta_json),
        ("Directory Structure", validate_directory_structure),
        ("File Path Encoding", validate_file_paths),
    ]

    for name, validator in validations:
        valid, errors = validator(skill_path)
        status = "PASS" if valid else "FAIL"
        print(f"\n[{status}] {name}")
        if errors:
            for error in errors:
                print(f"  - {error}")
            all_valid = False
            all_errors.extend([f"{name}: {e}" for e in errors])

    print("\n" + "=" * 50)
    if all_valid:
        print("All validations PASSED")
        return 0
    else:
        print(f"FAILED: {len(all_errors)} error(s) found")
        return 1


if __name__ == "__main__":
    sys.exit(main())

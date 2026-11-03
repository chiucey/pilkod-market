#!/usr/bin/env python3
"""
快速验证脚本 - 检查技能结构和frontmatter规范
"""
import os
import re
import sys
import json
from pathlib import Path


def validate_frontmatter(skill_path: Path) -> tuple[bool, list[str]]:
    """验证SKILL.md的frontmatter格式"""
    errors = []
    skill_md = skill_path / "SKILL.md"

    if not skill_md.exists():
        return False, ["SKILL.md 文件不存在"]

    content = skill_md.read_text(encoding="utf-8")

    # 检查第一行是否是frontmatter开始
    if not content.startswith("---"):
        errors.append("错误: SKILL.md 必须以 '---' 开头，frontmatter 必须在第一行")
        return False, errors

    # 提取frontmatter
    lines = content.split("\n")

    # 找到frontmatter结束位置（第一个独立的 ---）
    end_idx = -1
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end_idx = i
            break

    if end_idx == -1:
        errors.append("错误: frontmatter 缺少结束标记 '---'")
        return False, errors

    # 解析frontmatter
    frontmatter_lines = lines[1:end_idx]
    frontmatter = {}
    for line in frontmatter_lines:
        if ":" in line:
            key, value = line.split(":", 1)
            frontmatter[key.strip()] = value.strip()

    # 检查必填字段
    if "name" not in frontmatter:
        errors.append("错误: frontmatter 缺少 'name' 字段")
    else:
        name = frontmatter["name"]
        # 检查名称格式（连字符）
        if not re.match(r'^[a-z0-9]+(-[a-z0-9]+)*$', name):
            errors.append(f"错误: name '{name}' 必须使用连字符格式 (kebab-case)")
        # 检查长度
        if len(name) > 64:
            errors.append(f"错误: name '{name}' 长度不能超过64字符")

    if "description" not in frontmatter:
        errors.append("错误: frontmatter 缺少 'description' 字段")
    elif len(frontmatter.get("description", "")) < 10:
        errors.append("警告: description 太短，建议提供更详细的触发短语描述")

    # 检查是否有markdown标题在frontmatter之前
    if end_idx > 2:
        for line in lines[2:end_idx]:
            if line.strip().startswith("#"):
                errors.append(f"错误: frontmatter 中不能包含 markdown 标题 '{line.strip()}'")
                break

    return len(errors) == 0, errors


def validate_meta_json(skill_path: Path) -> tuple[bool, list[str]]:
    """验证_meta.json文件"""
    errors = []
    meta_file = skill_path / "_meta.json"

    if not meta_file.exists():
        return False, ["_meta.json 文件不存在"]

    try:
        meta = json.loads(meta_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return False, [f"_meta.json JSON格式错误: {e}"]

    if "id" not in meta:
        errors.append("_meta.json 缺少 'id' 字段")
    elif not isinstance(meta["id"], (int, str)):
        errors.append("_meta.json 'id' 必须是数字或字符串")

    if "version" not in meta:
        errors.append("_meta.json 缺少 'version' 字段")
    elif not re.match(r'^\d+\.\d+\.\d+$', meta.get("version", "")):
        errors.append("_meta.json 'version' 必须符合语义化版本格式 (如 1.0.0)")

    return len(errors) == 0, errors


def validate_directory_structure(skill_path: Path) -> tuple[bool, list[str]]:
    """验证目录结构"""
    warnings = []

    # 检查必要文件
    if not (skill_path / "SKILL.md").exists():
        return False, ["缺少 SKILL.md"]

    if not (skill_path / "_meta.json").exists():
        return False, ["缺少 _meta.json"]

    # 检查scripts目录
    scripts_dir = skill_path / "scripts"
    if scripts_dir.exists():
        for script in scripts_dir.glob("*.py"):
            if "validate" in script.name.lower() or "package" in script.name.lower():
                if not os.access(script, os.X_OK):
                    warnings.append(f"建议: {script.name} 应具有执行权限 (chmod +x)")

    # 检查references目录
    if not (skill_path / "references").exists():
        warnings.append("建议: 添加 references/ 目录存放详细文档")

    return True, warnings


def validate_naming(skill_path: Path) -> tuple[bool, list[str]]:
    """验证命名规范"""
    errors = []
    warnings = []

    # 检查技能文件夹名称
    folder_name = skill_path.name
    if not re.match(r'^[a-z0-9-]+$', folder_name):
        errors.append(f"错误: 文件夹名称 '{folder_name}' 必须只包含小写字母、数字和连字符")

    # 检查所有文件名
    for root, dirs, files in os.walk(skill_path):
        for file in files:
            file_path = Path(root) / file
            rel_path = file_path.relative_to(skill_path)

            # 跳过 .git 和隐藏目录
            if any(part.startswith('.') for part in rel_path.parts[:-1]):
                continue

            # 检查文件名是否包含非ASCII字符
            if not all(ord(c) < 128 or c in '/_-.' for c in file):
                errors.append(f"错误: 文件 '{rel_path}' 名称包含非ASCII字符")

            # 检查是否有空格
            if ' ' in file:
                errors.append(f"错误: 文件 '{rel_path}' 名称包含空格")

    return len(errors) == 0, errors + warnings


def main():
    """主验证流程"""
    if len(sys.argv) < 2:
        skill_path = Path.cwd()
    else:
        skill_path = Path(sys.argv[1])

    print(f"验证技能: {skill_path}")
    print("=" * 50)

    all_passed = True
    all_messages = []

    # 执行各项验证
    checks = [
        ("Frontmatter 验证", validate_frontmatter),
        ("_meta.json 验证", validate_meta_json),
        ("目录结构验证", validate_directory_structure),
        ("命名规范验证", validate_naming),
    ]

    for check_name, check_func in checks:
        passed, messages = check_func(skill_path)
        if messages:
            print(f"\n{check_name}:")
            for msg in messages:
                print(f"  - {msg}")

        if not passed:
            all_passed = False
            all_messages.extend(messages)

    print("\n" + "=" * 50)
    if all_passed:
        print("✓ 所有验证通过")
        return 0
    else:
        print("✗ 验证失败")
        return 1


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
BD分析报告技能 - 快速验证脚本

验证技能结构和内容的完整性，确保符合发布标准。

验证项：
1. Frontmatter 格式（name, description必填）
2. SKILL.md 必须在第一行以 --- 开头
3. _meta.json 存在且包含 id 和 version
4. scripts 目录存在且包含必要脚本
5. references 目录存在
6. 无路径名称包含非ASCII字符
7. 无 .DS_Store 等系统文件
"""

import json
import os
import re
import sys
from pathlib import Path


class ValidationError:
    def __init__(self, level: str, message: str, file: str = ""):
        self.level = level  # error, warning
        self.message = message
        self.file = file

    def __str__(self):
        prefix = f"[{self.level.upper()}]" if self.file else f"[{self.level.upper()}]"
        return f"{prefix} {self.message}" + (f" ({self.file})" if self.file else "")


def validate_frontmatter(skill_path: Path) -> list[ValidationError]:
    """验证 SKILL.md frontmatter 格式"""
    errors = []
    skill_md = skill_path / "SKILL.md"

    if not skill_md.exists():
        errors.append(ValidationError("error", "SKILL.md 文件不存在"))
        return errors

    with open(skill_md, "r", encoding="utf-8") as f:
        content = f.read()

    # 检查第一行必须是 ---
    first_line = content.split("\n")[0].strip()
    if first_line != "---":
        errors.append(ValidationError(
            "error",
            f"SKILL.md 必须以 --- 开头，而非 '{first_line}'",
            "SKILL.md"
        ))

    # 检查 frontmatter 是否存在且包含必需字段
    if not content.startswith("---"):
        errors.append(ValidationError("error", "缺少 frontmatter（必须以 --- 开头）", "SKILL.md"))
        return errors

    # 提取 frontmatter
    fm_match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not fm_match:
        errors.append(ValidationError("error", "frontmatter 格式无效", "SKILL.md"))
        return errors

    fm_content = fm_match.group(1)

    # 检查必需字段
    if not re.search(r"^name:\s*\S+", fm_content, re.MULTILINE):
        errors.append(ValidationError("error", "frontmatter 缺少 'name' 字段", "SKILL.md"))

    if not re.search(r"^description:\s*.+", fm_content, re.MULTILINE):
        errors.append(ValidationError("error", "frontmatter 缺少 'description' 字段", "SKILL.md"))

    # 检查 name 格式（连字符）
    name_match = re.search(r"^name:\s*(.+)$", fm_content, re.MULTILINE)
    if name_match:
        name = name_match.group(1).strip()
        if not re.match(r"^[a-z0-9][a-z0-9-]*$", name):
            errors.append(ValidationError(
                "warning",
                f"name '{name}' 应使用连字符格式（hyphen-case）",
                "SKILL.md"
            ))
        if len(name) > 64:
            errors.append(ValidationError(
                "warning",
                f"name 长度 ({len(name)}) 超过建议的64字符限制",
                "SKILL.md"
            ))

    return errors


def validate_meta(skill_path: Path) -> list[ValidationError]:
    """验证 _meta.json 文件"""
    errors = []
    meta_file = skill_path / "_meta.json"

    if not meta_file.exists():
        errors.append(ValidationError("error", "_meta.json 文件不存在"))
        return errors

    try:
        with open(meta_file, "r", encoding="utf-8") as f:
            meta = json.load(f)
    except json.JSONDecodeError as e:
        errors.append(ValidationError("error", f"_meta.json JSON格式错误: {e}"))
        return errors

    if "id" not in meta:
        errors.append(ValidationError("error", "_meta.json 缺少 'id' 字段"))

    if "version" not in meta:
        errors.append(ValidationError("error", "_meta.json 缺少 'version' 字段"))
    elif not re.match(r"^\d+\.\d+\.\d+$", meta["version"]):
        errors.append(ValidationError("warning", f"version '{meta['version']}' 应遵循语义化版本格式（如 1.0.0）"))

    return errors


def validate_directories(skill_path: Path) -> list[ValidationError]:
    """验证目录结构"""
    errors = []

    # 检查 scripts 目录
    scripts_dir = skill_path / "scripts"
    if not scripts_dir.exists():
        errors.append(ValidationError("error", "scripts 目录不存在"))
    else:
        # 检查必要脚本
        required_scripts = ["merge_md.py", "md2html.py"]
        for script in required_scripts:
            if not (scripts_dir / script).exists():
                errors.append(ValidationError(
                    "error",
                    f"scripts/{script} 脚本不存在",
                    "scripts"
                ))

    # 检查 references 目录
    references_dir = skill_path / "references"
    if not references_dir.exists():
        errors.append(ValidationError("error", "references 目录不存在"))

    return errors


def validate_naming(skill_path: Path) -> list[ValidationError]:
    """验证路径和文件名不包含非ASCII字符"""
    errors = []
    forbidden_names = {".DS_Store", "Thumbs.db", "desktop.ini"}

    for root, dirs, files in os.walk(skill_path):
        # 检查目录名
        for d in dirs:
            if d in forbidden_names:
                rel = os.path.relpath(os.path.join(root, d), skill_path)
                errors.append(ValidationError("warning", f"系统文件应删除", rel))

            # 检查非ASCII字符（references 目录下的中文文件名可接受）
            rel_dir = os.path.relpath(os.path.join(root, d), skill_path)
            if not d.isascii() and not rel_dir.startswith("references"):
                errors.append(ValidationError(
                    "warning",
                    f"目录名包含非ASCII字符: {d}",
                    rel_dir
                ))

        # 检查文件名
        for f in files:
            if f in forbidden_names:
                rel = os.path.relpath(os.path.join(root, f), skill_path)
                errors.append(ValidationError("warning", f"系统文件应删除", rel))

            # 检查非ASCII字符（references 目录下的中文文件名可接受）
            rel_file = os.path.relpath(os.path.join(root, f), skill_path)
            if not f.isascii() and not rel_file.startswith("references"):
                errors.append(ValidationError(
                    "warning",
                    f"文件名包含非ASCII字符: {f}",
                    rel_file
                ))

    return errors


def validate_scripts(skill_path: Path) -> list[ValidationError]:
    """验证脚本语法和依赖"""
    errors = []
    scripts_dir = skill_path / "scripts"

    if not scripts_dir.exists():
        return errors

    for script in scripts_dir.glob("*.py"):
        # 尝试编译检查语法
        try:
            with open(script, "r", encoding="utf-8") as f:
                code = f.read()
            compile(code, str(script), "exec")
        except SyntaxError as e:
            errors.append(ValidationError(
                "error",
                f"Python语法错误: {e}",
                f"scripts/{script.name}"
            ))

    return errors


def validate(skill_path: str) -> bool:
    """
    执行完整验证流程

    Args:
        skill_path: 技能根目录路径

    Returns:
        True 如果所有验证通过（无error级别问题）
    """
    skill_path = Path(skill_path)
    all_errors = []

    print(f"=" * 60)
    print(f"开始验证技能: {skill_path.name}")
    print(f"=" * 60)

    # 执行各项验证
    all_errors.extend(validate_frontmatter(skill_path))
    all_errors.extend(validate_meta(skill_path))
    all_errors.extend(validate_directories(skill_path))
    all_errors.extend(validate_naming(skill_path))
    all_errors.extend(validate_scripts(skill_path))

    # 输出结果
    errors = [e for e in all_errors if e.level == "error"]
    warnings = [e for e in all_errors if e.level == "warning"]

    print("\n--- 验证结果 ---")
    for e in errors:
        print(f"  ❌ {e}")
    for w in warnings:
        print(f"  ⚠️  {w}")

    print(f"\n总计: {len(errors)} 个错误, {len(warnings)} 个警告")

    if errors:
        print("\n❌ 验证失败 - 请修复上述错误")
        return False
    else:
        print("\n✅ 验证通过")
        return True


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="验证技能结构和内容")
    parser.add_argument("skill_path", nargs="?", default=".", help="技能目录路径")
    args = parser.parse_args()

    success = validate(args.skill_path)
    sys.exit(0 if success else 1)

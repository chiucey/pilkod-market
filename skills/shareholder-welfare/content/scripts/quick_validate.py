#!/usr/bin/env python3
"""
技能验证脚本
验证 shareholder-welfare 技能的结构和内容是否符合规范
"""

import json
import os
import re
import sys
from pathlib import Path


class ValidationResult:
    """验证结果容器"""
    def __init__(self):
        self.passed = []
        self.warnings = []
        self.errors = []

    def add_pass(self, message):
        self.passed.append(message)

    def add_warning(self, message):
        self.warnings.append(message)

    def add_error(self, message):
        self.errors.append(message)

    def is_valid(self):
        return len(self.errors) == 0

    def print_report(self):
        """打印验证报告"""
        print("=" * 60)
        print("技能验证报告")
        print("=" * 60)

        if self.passed:
            print(f"\n✅ 通过 ({len(self.passed)})")
            for msg in self.passed:
                print(f"  ✓ {msg}")

        if self.warnings:
            print(f"\n⚠️  警告 ({len(self.warnings)})")
            for msg in self.warnings:
                print(f"  ⚡ {msg}")

        if self.errors:
            print(f"\n❌ 错误 ({len(self.errors)})")
            for msg in self.errors:
                print(f"  ✗ {msg}")

        print("\n" + "=" * 60)
        if self.is_valid():
            print("验证结果: ✅ 通过")
        else:
            print("验证结果: ❌ 失败")
        print("=" * 60)

        return self.is_valid()


def validate_skill_directory(skill_path: str) -> ValidationResult:
    """
    验证技能目录结构

    Args:
        skill_path: 技能目录路径

    Returns:
        ValidationResult: 验证结果
    """
    result = ValidationResult()
    skill_dir = Path(skill_path)

    # 检查目录是否存在
    if not skill_dir.exists():
        result.add_error(f"技能目录不存在: {skill_path}")
        return result

    if not skill_dir.is_dir():
        result.add_error(f"路径不是目录: {skill_path}")
        return result

    result.add_pass("技能目录存在")

    # 检查必需文件
    required_files = ["SKILL.md", "_meta.json"]
    for filename in required_files:
        file_path = skill_dir / filename
        if file_path.exists():
            result.add_pass(f"必需文件存在: {filename}")
        else:
            result.add_error(f"缺少必需文件: {filename}")

    # 检查目录结构
    subdirs = ["scripts", "references", "assets"]
    for subdir in subdirs:
        dir_path = skill_dir / subdir
        if dir_path.exists():
            result.add_pass(f"目录存在: {subdir}/")

    return result


def validate_skill_md(skill_path: str) -> ValidationResult:
    """
    验证 SKILL.md 文件

    Args:
        skill_path: 技能目录路径

    Returns:
        ValidationResult: 验证结果
    """
    result = ValidationResult()
    skill_md_path = Path(skill_path) / "SKILL.md"

    if not skill_md_path.exists():
        result.add_error("SKILL.md 文件不存在")
        return result

    # 读取文件内容
    with open(skill_md_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 检查 frontmatter 是否在第一行
    if content.startswith("---"):
        result.add_pass("Frontmatter 在文件开头")
    else:
        result.add_error("Frontmatter 不在文件开头（必须在第一行）")

    # 解析 frontmatter
    if content.startswith("---"):
        lines = content.split("\n")
        frontmatter_end = None
        for i, line in enumerate(lines[1:], 1):
            if line.strip() == "---":
                frontmatter_end = i
                break

        if frontmatter_end is None:
            result.add_error("Frontmatter 未正确关闭（缺少结束 ---）")
            return result

        frontmatter_text = "\n".join(lines[1:frontmatter_end])
        result.add_pass("Frontmatter 结构正确")

        # 解析 YAML frontmatter
        try:
            frontmatter = {}
            current_key = None
            current_value = []

            for line in lines[1:frontmatter_end]:
                if ":" in line:
                    if current_key:
                        value = "\n".join(current_value).strip()
                        if value:
                            frontmatter[current_key] = value
                    parts = line.split(":", 1)
                    current_key = parts[0].strip()
                    current_value = [parts[1].strip()] if len(parts) > 1 else []
                elif line.startswith("    ") or line.startswith("\t"):
                    current_value.append(line.strip())

            if current_key:
                value = "\n".join(current_value).strip()
                if value:
                    frontmatter[current_key] = value

        except Exception as e:
            result.add_warning(f"Frontmatter 解析可能存在问题: {e}")

    # 检查必需字段
    required_fields = ["name", "description"]
    for field in required_fields:
        # 简单检查字段是否存在
        if re.search(rf"^{field}:", frontmatter_text, re.MULTILINE):
            result.add_pass(f"必需字段存在: {field}")
        else:
            result.add_error(f"缺少必需字段: {field}")

    # 检查 name 字段格式（连字符格式）
    name_match = re.search(r"^name:\s*(.+)$", frontmatter_text, re.MULTILINE)
    if name_match:
        name_value = name_match.group(1).strip()
        if re.match(r"^[a-z0-9]+(-[a-z0-9]+)*$", name_value):
            result.add_pass(f"name 格式正确: {name_value}")
        else:
            result.add_warning(f"name 应使用连字符格式（kebab-case）: {name_value}")

    # 检查 name 长度
    if name_match:
        name_value = name_match.group(1).strip()
        if len(name_value) <= 64:
            result.add_pass(f"name 长度符合要求 ({len(name_value)} <= 64)")
        else:
            result.add_error(f"name 长度超出限制 ({len(name_value)} > 64)")

    # 检查 description 长度（建议不超过 500 字符）
    desc_match = re.search(r"^description:\s*(.+)$", frontmatter_text, re.MULTILINE | re.DOTALL)
    if desc_match:
        desc_value = desc_match.group(1).strip()
        if len(desc_value) <= 500:
            result.add_pass(f"description 长度合理 ({len(desc_value)} <= 500)")
        else:
            result.add_warning(f"description 较长 ({len(desc_value)} > 500)，建议精简")

    # 检查是否有 markdown 标题在 frontmatter 之前
    # 只有在 frontmatter 结束之前的 # 才算错误
    lines = content.split("\n")
    frontmatter_ended = False
    for line in lines[:10]:
        if line.strip() == "---":
            frontmatter_ended = True
            continue
        if frontmatter_ended:
            break
        if line.startswith("#"):
            result.add_error(f"发现 markdown 标题在 frontmatter 之前: {line}")
            break

    # 检查文件末尾是否有无效元数据
    lines = content.strip().split("\n")
    last_lines = lines[-5:]
    for line in last_lines:
        if re.match(r"^skill by \w+", line, re.IGNORECASE):
            result.add_warning(f"发现可能的无效元数据: {line}")

    return result


def validate_meta_json(skill_path: str) -> ValidationResult:
    """
    验证 _meta.json 文件

    Args:
        skill_path: 技能目录路径

    Returns:
        ValidationResult: 验证结果
    """
    result = ValidationResult()
    meta_path = Path(skill_path) / "_meta.json"

    if not meta_path.exists():
        result.add_error("_meta.json 文件不存在")
        return result

    # 读取并解析 JSON
    try:
        with open(meta_path, "r", encoding="utf-8") as f:
            meta = json.load(f)
        result.add_pass("_meta.json 格式正确（有效的 JSON）")
    except json.JSONDecodeError as e:
        result.add_error(f"_meta.json 格式错误: {e}")
        return result

    # 检查必需字段
    required_fields = ["id", "version"]
    for field in required_fields:
        if field in meta:
            result.add_pass(f"必需字段存在: {field}")
        else:
            result.add_error(f"缺少必需字段: {field}")

    # 验证 id 字段
    if "id" in meta:
        id_value = meta["id"]
        if isinstance(id_value, int) and id_value > 0:
            result.add_pass(f"id 格式正确: {id_value}")
        else:
            result.add_error(f"id 应为正整数: {id_value}")

    # 验证 version 字段（语义化版本）
    if "version" in meta:
        version = meta["version"]
        if re.match(r"^\d+\.\d+\.\d+$", version):
            result.add_pass(f"version 格式正确: {version}")
        else:
            result.add_error(f"version 应符合语义化版本格式 (x.y.z): {version}")

    return result


def validate_scripts(skill_path: str) -> ValidationResult:
    """
    验证 scripts 目录中的脚本

    Args:
        skill_path: 技能目录路径

    Returns:
        ValidationResult: 验证结果
    """
    result = ValidationResult()
    scripts_dir = Path(skill_path) / "scripts"

    if not scripts_dir.exists():
        result.add_warning("scripts/ 目录不存在")
        return result

    # 检查 scripts 目录中的 Python 文件
    py_files = list(scripts_dir.glob("*.py"))
    if py_files:
        result.add_pass(f"发现 {len(py_files)} 个 Python 脚本")

        for py_file in py_files:
            # 检查脚本是否有执行权限设置（shebang）
            with open(py_file, "r", encoding="utf-8") as f:
                first_line = f.readline()
                if first_line.startswith("#!"):
                    result.add_pass(f"脚本有 shebang: {py_file.name}")
                else:
                    result.add_warning(f"脚本缺少 shebang: {py_file.name}")

            # 尝试语法检查
            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    compile(f.read(), py_file.name, "exec")
                result.add_pass(f"脚本语法正确: {py_file.name}")
            except SyntaxError as e:
                result.add_error(f"脚本语法错误 {py_file.name}: {e}")

    return result


def validate_naming(skill_path: str) -> ValidationResult:
    """
    验证所有文件和目录名称

    Args:
        skill_path: 技能目录路径

    Returns:
        ValidationResult: 验证结果
    """
    result = ValidationResult()
    skill_dir = Path(skill_path)

    # 检查目录名称
    dir_name = skill_dir.name
    if re.match(r"^[a-z0-9-]+$", dir_name):
        result.add_pass(f"目录名称格式正确: {dir_name}")
    else:
        result.add_error(f"目录名称应使用小写字母、数字和连字符: {dir_name}")

    # 递归检查所有文件
    for file_path in skill_dir.rglob("*"):
        if file_path.is_file():
            relative_path = file_path.relative_to(skill_dir)

            # 检查路径是否包含非 ASCII 字符
            path_str = str(relative_path)
            if not all(ord(c) < 128 or c == '/' for c in path_str):
                result.add_error(f"路径包含非ASCII字符: {relative_path}")

            # 检查是否有空格
            if " " in path_str:
                result.add_warning(f"路径包含空格: {relative_path}")

    return result


def validate(skill_path: str) -> bool:
    """
    执行所有验证检查

    Args:
        skill_path: 技能目录路径

    Returns:
        bool: 验证是否通过
    """
    print(f"\n验证技能: {skill_path}\n")

    # 合并所有验证结果
    all_results = []

    # 1. 目录结构验证
    print("检查目录结构...")
    all_results.append(validate_skill_directory(skill_path))

    # 2. SKILL.md 验证
    print("检查 SKILL.md...")
    all_results.append(validate_skill_md(skill_path))

    # 3. _meta.json 验证
    print("检查 _meta.json...")
    all_results.append(validate_meta_json(skill_path))

    # 4. 脚本验证
    print("检查 scripts...")
    all_results.append(validate_scripts(skill_path))

    # 5. 命名验证
    print("检查命名规范...")
    all_results.append(validate_naming(skill_path))

    # 合并结果
    final_result = ValidationResult()
    for r in all_results:
        final_result.passed.extend(r.passed)
        final_result.warnings.extend(r.warnings)
        final_result.errors.extend(r.errors)

    # 打印最终报告
    is_valid = final_result.print_report()

    return is_valid


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="验证技能结构和内容")
    parser.add_argument(
        "skill_path",
        nargs="?",
        default=".",
        help="技能目录路径（默认当前目录）"
    )

    args = parser.parse_args()

    # 获取绝对路径
    skill_path = Path(args.skill_path).resolve()

    # 执行验证
    is_valid = validate(skill_path)

    # 返回退出码
    sys.exit(0 if is_valid else 1)


if __name__ == "__main__":
    main()

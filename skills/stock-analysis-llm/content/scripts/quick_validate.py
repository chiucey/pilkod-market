#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Stock Analysis LLM Skill 验证脚本
验证技能结构和内容是否符合发布标准
"""

import os
import re
import json
import sys
from pathlib import Path


class ValidationResult:
    def __init__(self):
        self.passed = []
        self.warnings = []
        self.errors = []

    def add_pass(self, msg):
        self.passed.append(f"[PASS] {msg}")

    def add_warning(self, msg):
        self.warnings.append(f"[WARN] {msg}")

    def add_error(self, msg):
        self.errors.append(f"[ERROR] {msg}")

    def is_success(self):
        return len(self.errors) == 0

    def print_report(self):
        print("=" * 60)
        print("技能验证报告")
        print("=" * 60)

        for msg in self.passed:
            print(msg)
        for msg in self.warnings:
            print(msg)
        for msg in self.errors:
            print(msg)

        print("-" * 60)
        print(f"通过: {len(self.passed)}, 警告: {len(self.warnings)}, 错误: {len(self.errors)}")
        print("=" * 60)

        return self.is_success()


def validate_frontmatter(skill_path: Path, result: ValidationResult):
    """验证 SKILL.md frontmatter 格式"""
    skill_md = skill_path / "SKILL.md"

    if not skill_md.exists():
        result.add_error("SKILL.md 文件不存在")
        return False

    content = skill_md.read_text(encoding='utf-8')

    # 检查第一行是否为 ---
    lines = content.split('\n')
    if not lines or lines[0].strip() != '---':
        result.add_error("SKILL.md 必须以 --- 开头（frontmatter 标记）")
        return False

    # 查找 frontmatter 结束标记
    end_idx = -1
    for i, line in enumerate(lines[1:], 1):
        if line.strip() == '---':
            end_idx = i
            break

    if end_idx == -1:
        result.add_error("SKILL.md frontmatter 未正确闭合（缺少结束 ---）")
        return False

    # 提取并解析 frontmatter
    frontmatter_text = '\n'.join(lines[1:end_idx])

    try:
        frontmatter = {}
        for line in frontmatter_text.split('\n'):
            if ':' in line:
                key = line.split(':', 1)[0].strip()
                # 跳过复杂的AIGC元数据
                if key not in ['AIGC', 'ReservedCode1', 'ReservedCode2', 'ProduceID', 'PropagateID']:
                    frontmatter[key] = True
    except Exception as e:
        result.add_warning(f"Frontmatter 解析可能有问题: {e}")

    # 检查必需字段
    if 'name' in frontmatter or 'name:' in frontmatter_text:
        result.add_pass("name 字段存在")
    else:
        result.add_error("Frontmatter 缺少 name 字段")

    if 'description' in frontmatter or 'description:' in frontmatter_text:
        result.add_pass("description 字段存在")
    else:
        result.add_error("Frontmatter 缺少 description 字段")

    # 检查 frontmatter 后是否有 markdown 标题
    content_after_fm = '\n'.join(lines[end_idx+1:]).strip()
    if content_after_fm.startswith('#'):
        result.add_pass("Frontmatter 后有有效的内容")
    else:
        result.add_warning("Frontmatter 后的内容可能不符合预期格式")

    return True


def validate_meta_json(skill_path: Path, result: ValidationResult):
    """验证 _meta.json 格式"""
    meta_file = skill_path / "_meta.json"

    if not meta_file.exists():
        result.add_error("_meta.json 文件不存在")
        return False

    try:
        meta = json.loads(meta_file.read_text(encoding='utf-8'))

        # 检查必需字段
        if 'id' not in meta:
            result.add_error("_meta.json 缺少 id 字段")
        elif isinstance(meta['id'], int):
            result.add_pass(f"id 字段有效: {meta['id']}")
        else:
            result.add_error(f"id 必须是整数，当前类型: {type(meta['id'])}")

        if 'version' not in meta:
            result.add_error("_meta.json 缺少 version 字段")
        elif re.match(r'^\d+\.\d+\.\d+$', meta['version']):
            result.add_pass(f"version 字段符合语义化版本: {meta['version']}")
        else:
            result.add_warning(f"version 格式可能不符合语义化版本规范: {meta['version']}")

        return True

    except json.JSONDecodeError as e:
        result.add_error(f"_meta.json 格式错误: {e}")
        return False


def validate_naming(skill_path: Path, result: ValidationResult):
    """验证命名规范"""
    # 文件夹名称
    folder_name = skill_path.name
    if re.match(r'^[a-z0-9][a-z0-9-]*$', folder_name):
        result.add_pass(f"文件夹名称符合规范: {folder_name}")
    else:
        result.add_error(f"文件夹名称不符合规范（应使用小写连字符）: {folder_name}")

    # SKILL.md 中的 name 字段
    skill_md = skill_path / "SKILL.md"
    if skill_md.exists():
        content = skill_md.read_text(encoding='utf-8')
        # 提取 name 字段
        name_match = re.search(r'^name:\s*(.+?)\s*$', content, re.MULTILINE)
        if name_match:
            name_value = name_match.group(1).strip()
            if name_value == folder_name:
                result.add_pass(f"SKILL.md name 与文件夹名称匹配: {name_value}")
            else:
                result.add_error(f"SKILL.md name ({name_value}) 与文件夹名称 ({folder_name}) 不匹配")

    # 检查脚本文件命名
    scripts_dir = skill_path / "scripts"
    if scripts_dir.exists():
        for f in scripts_dir.iterdir():
            if f.suffix == '.py':
                if re.match(r'^[a-zA-Z0-9_]+\.py$', f.name):
                    result.add_pass(f"脚本文件命名规范: {f.name}")
                else:
                    result.add_warning(f"脚本文件命名建议使用规范格式: {f.name}")


def validate_scripts(skill_path: Path, result: ValidationResult):
    """验证脚本文件"""
    scripts_dir = skill_path / "scripts"

    if not scripts_dir.exists():
        result.add_warning("scripts 目录不存在")
        return

    py_files = list(scripts_dir.glob("*.py"))
    if not py_files:
        result.add_warning("scripts 目录中没有 Python 脚本")

    for py_file in py_files:
        content = py_file.read_text(encoding='utf-8')

        # 检查 shebang
        if content.startswith('#!/'):
            result.add_pass(f"{py_file.name} 包含 shebang")

        # 检查编码声明
        if 'coding:' in content or 'coding=' in content or '-*- coding:' in content:
            result.add_pass(f"{py_file.name} 包含编码声明")

        # 检查是否有 docstring
        if '"""' in content or "'''" in content:
            result.add_pass(f"{py_file.name} 包含文档字符串")


def validate_structure(skill_path: Path, result: ValidationResult):
    """验证目录结构"""
    # 检查必要的文件和目录
    required = ['SKILL.md', '_meta.json']
    for item in required:
        if (skill_path / item).exists():
            result.add_pass(f"必需文件存在: {item}")
        else:
            result.add_error(f"缺少必需文件: {item}")

    # 检查可选目录
    optional_dirs = ['scripts', 'references', 'assets']
    for d in optional_dirs:
        dir_path = skill_path / d
        if dir_path.exists() and dir_path.is_dir():
            result.add_pass(f"可选目录存在: {d}")
            # 检查目录是否为空
            if not any(dir_path.iterdir()):
                result.add_warning(f"{d} 目录为空")


def validate_security(skill_path: Path, result: ValidationResult):
    """安全检查：检查是否包含敏感信息"""
    dangerous_patterns = [
        (r'password\s*=\s*["\'][^"\']+["\']', "硬编码密码"),
        (r'api_key\s*=\s*["\'][^"\']+["\']', "硬编码 API Key"),
        (r'secret\s*=\s*["\'][^"\']+["\']', "硬编码密钥"),
        (r'token\s*=\s*["\'][^"\']+["\']', "硬编码 Token"),
    ]

    for py_file in skill_path.rglob("*.py"):
        content = py_file.read_text(encoding='utf-8')
        for pattern, desc in dangerous_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                result.add_warning(f"{py_file.name} 可能包含 {desc}")


def main():
    # 获取技能路径（默认为当前目录）
    skill_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent.parent

    print(f"验证技能: {skill_path}")
    print()

    result = ValidationResult()

    validate_structure(skill_path, result)
    validate_frontmatter(skill_path, result)
    validate_meta_json(skill_path, result)
    validate_naming(skill_path, result)
    validate_scripts(skill_path, result)
    validate_security(skill_path, result)

    success = result.print_report()

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()

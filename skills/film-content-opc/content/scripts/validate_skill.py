#!/usr/bin/env python3
"""
影视内容OPC技能 - 验证脚本
检查SKILL.md和目录结构是否符合规范
"""

import os
import re
import sys
from pathlib import Path

def validate_frontmatter(skill_md_path: Path) -> tuple[bool, str]:
    """验证SKILL.md的frontmatter"""
    with open(skill_md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查frontmatter是否存在
    if not content.startswith('---'):
        return False, "SKILL.md必须以---开头（frontmatter必须在第一行）"

    # 提取frontmatter
    lines = content.split('\n')
    frontmatter_lines = []
    in_frontmatter = False

    for i, line in enumerate(lines):
        if line.strip() == '---':
            if not in_frontmatter:
                in_frontmatter = True
                continue
            else:
                break
        if in_frontmatter:
            frontmatter_lines.append(line)

    # 解析frontmatter
    frontmatter = {}
    for line in frontmatter_lines:
        if ':' in line:
            key, value = line.split(':', 1)
            frontmatter[key.strip()] = value.strip()

    # 检查必填字段
    required_fields = ['name', 'description']
    missing = [f for f in required_fields if f not in frontmatter]
    if missing:
        return False, f"Frontmatter缺少必填字段: {', '.join(missing)}"

    # 检查name格式
    name = frontmatter['name']
    if not re.match(r'^[a-z0-9-]+$', name):
        return False, f"name必须使用连字符格式（小写字母、数字、连字符）: 当前值='{name}'"

    if len(name) > 64:
        return False, f"name长度不能超过64字符: 当前长度={len(name)}"

    # 检查description
    desc = frontmatter['description']
    if len(desc) < 10:
        return False, f"description必须包含足够的描述内容（至少10字符）"

    return True, "Frontmatter验证通过"

def validate_directory_structure(skill_dir: Path) -> tuple[bool, str]:
    """验证目录结构"""
    required_files = [
        "SKILL.md",
        "_meta.json"
    ]

    required_dirs = [
        "scripts",
        "references"
    ]

    # 检查必填文件
    for file in required_files:
        file_path = skill_dir / file
        if not file_path.exists():
            return False, f"缺少必填文件: {file}"

    # 检查必填目录
    for dir_name in required_dirs:
        dir_path = skill_dir / dir_name
        if not dir_path.exists():
            return False, f"缺少必填目录: {dir_name}"
        if not dir_path.is_dir():
            return False, f"{dir_name} 应该是目录而非文件"

    return True, "目录结构验证通过"

def validate_meta_json(meta_path: Path) -> tuple[bool, str]:
    """验证_meta.json"""
    import json

    try:
        with open(meta_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)
    except json.JSONDecodeError as e:
        return False, f"_meta.json格式错误: {e}"

    # 检查必填字段
    required = ['id', 'version']
    missing = [f for f in required if f not in meta]
    if missing:
        return False, f"_meta.json缺少必填字段: {', '.join(missing)}"

    # 验证id是整数
    if not isinstance(meta['id'], int):
        return False, f"_meta.json的id必须是整数: 当前类型={type(meta['id'])}"

    # 验证version格式
    version = meta['version']
    if not re.match(r'^\d+\.\d+\.\d+$', version):
        return False, f"_meta.json的version必须符合语义化版本格式: 当前值='{version}'"

    return True, "_meta.json验证通过"

def run_validation(skill_dir: str) -> bool:
    """运行完整验证"""
    skill_path = Path(skill_dir)

    print(f"\n🔍 验证技能: {skill_path.name}")
    print("=" * 50)

    all_passed = True

    # 1. 目录结构验证
    passed, msg = validate_directory_structure(skill_path)
    print(f"{'✅' if passed else '❌'} 目录结构: {msg}")
    all_passed = all_passed and passed

    # 2. Frontmatter验证
    passed, msg = validate_frontmatter(skill_path / "SKILL.md")
    print(f"{'✅' if passed else '❌'} Frontmatter: {msg}")
    all_passed = all_passed and passed

    # 3. _meta.json验证
    if (skill_path / "_meta.json").exists():
        passed, msg = validate_meta_json(skill_path / "_meta.json")
        print(f"{'✅' if passed else '❌'} _meta.json: {msg}")
        all_passed = all_passed and passed
    else:
        print("⚠️ _meta.json不存在（将在打包时生成）")

    # 4. 脚本存在性检查
    scripts_dir = skill_path / "scripts"
    if scripts_dir.exists():
        py_files = list(scripts_dir.glob("*.py"))
        print(f"📁 脚本文件: {len(py_files)} 个")
        for py_file in py_files:
            print(f"   - {py_file.name}")

    # 5. 参考文档检查
    refs_dir = skill_path / "references"
    if refs_dir.exists():
        md_files = list(refs_dir.glob("*.md"))
        print(f"📚 参考文档: {len(md_files)} 个")
        for md_file in md_files:
            print(f"   - {md_file.name}")

    print("=" * 50)
    print(f"\n{'✅ 所有验证通过' if all_passed else '❌ 存在验证失败项'}")

    return all_passed

if __name__ == "__main__":
    # 默认验证当前目录
    skill_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    success = run_validation(skill_dir)
    sys.exit(0 if success else 1)

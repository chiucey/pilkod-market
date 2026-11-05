#!/usr/bin/env python3
"""
快速验证脚本 - 检查技能结构和格式
"""

import os
import re
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).parent.parent
REQUIRED_FILES = ["SKILL.md", "_meta.json"]
REQUIRED_DIRS = ["scripts", "references"]

def validate_frontmatter(filepath: Path) -> tuple[bool, str]:
    """验证 frontmatter 格式"""
    try:
        content = filepath.read_text(encoding='utf-8')
        lines = content.split('\n')

        # 检查第一行是否是 ---
        if not lines or lines[0].strip() != '---':
            return False, f"SKILL.md 必须以 --- 开头，当前第一行: {lines[0][:50] if lines else '空'}"

        # 找到第二个 ---
        try:
            end_idx = lines[1:].index('---') + 1
        except ValueError:
            return False, "SKILL.md 缺少结束 ---"

        frontmatter = '\n'.join(lines[:end_idx+1])

        # 检查必需字段
        if 'name:' not in frontmatter:
            return False, "frontmatter 缺少 name 字段"

        if 'description:' not in frontmatter:
            return False, "frontmatter 缺少 description 字段"

        # 检查是否有 markdown 标题在 --- 之前
        for line in lines[:end_idx+1]:
            if line.startswith('#'):
                return False, f"frontmatter 中不能有 markdown 标题: {line}"

        return True, "OK"
    except Exception as e:
        return False, f"读取文件失败: {e}"

def validate_meta_json(filepath: Path) -> tuple[bool, str]:
    """验证 _meta.json 格式"""
    try:
        import json
        content = filepath.read_text(encoding='utf-8')
        data = json.loads(content)

        if 'id' not in data:
            return False, "_meta.json 缺少 id 字段"

        if 'version' not in data:
            return False, "_meta.json 缺少 version 字段"

        if not isinstance(data.get('id'), (int, str)):
            return False, "id 必须是数字或字符串"

        if not re.match(r'^\d+\.\d+\.\d+$', data.get('version', '')):
            return False, "version 必须符合语义化版本格式 (如 1.0.0)"

        return True, "OK"
    except json.JSONDecodeError as e:
        return False, f"_meta.json JSON 格式错误: {e}"
    except Exception as e:
        return False, f"读取文件失败: {e}"

def validate_naming(filepath: Path, name_in_frontmatter: str) -> tuple[bool, str]:
    """验证命名规范"""
    # 文件夹名应该是连字符格式
    folder_name = filepath.parent.name
    if not re.match(r'^[a-z0-9][a-z0-9-]*$', folder_name):
        return False, f"文件夹名应该使用连字符格式: {folder_name}"

    # frontmatter 中的 name 应该与文件夹名匹配
    if name_in_frontmatter != folder_name:
        return False, f"name ({name_in_frontmatter}) 应该与文件夹名 ({folder_name}) 匹配"

    return True, "OK"

def extract_name_from_frontmatter(filepath: Path) -> str:
    """从 frontmatter 提取 name"""
    try:
        content = filepath.read_text(encoding='utf-8')
        lines = content.split('\n')
        end_idx = lines[1:].index('---') + 1
        frontmatter = '\n'.join(lines[:end_idx+1])

        match = re.search(r'name:\s*([^\s]+)', frontmatter)
        return match.group(1) if match else ""
    except:
        return ""

def main():
    print(f"验证技能: {SKILL_DIR}")
    print("=" * 50)

    all_passed = True

    # 1. 检查必需文件
    print("\n1. 检查必需文件...")
    for filename in REQUIRED_FILES:
        filepath = SKILL_DIR / filename
        if filepath.exists():
            print(f"   ✓ {filename}")
        else:
            print(f"   ✗ {filename} (缺失)")
            all_passed = False

    # 2. 检查目录结构
    print("\n2. 检查目录结构...")
    for dirname in REQUIRED_DIRS:
        dirpath = SKILL_DIR / dirname
        if dirpath.is_dir():
            print(f"   ✓ {dirname}/")
        else:
            print(f"   ✗ {dirname}/ (缺失)")
            all_passed = False

    # 3. 验证 frontmatter
    print("\n3. 验证 frontmatter...")
    skill_md = SKILL_DIR / "SKILL.md"
    if skill_md.exists():
        passed, msg = validate_frontmatter(skill_md)
        if passed:
            print(f"   ✓ Frontmatter 格式正确")
        else:
            print(f"   ✗ {msg}")
            all_passed = False
    else:
        print(f"   ✗ SKILL.md 不存在")
        all_passed = False

    # 4. 验证 _meta.json
    print("\n4. 验证 _meta.json...")
    meta_json = SKILL_DIR / "_meta.json"
    if meta_json.exists():
        passed, msg = validate_meta_json(meta_json)
        if passed:
            print(f"   ✓ _meta.json 格式正确")
        else:
            print(f"   ✗ {msg}")
            all_passed = False
    else:
        print(f"   ✗ _meta.json 不存在")
        all_passed = False

    # 5. 验证命名一致性
    print("\n5. 验证命名一致性...")
    if skill_md.exists() and meta_json.exists():
        name = extract_name_from_frontmatter(skill_md)
        passed, msg = validate_naming(SKILL_DIR, name)
        if passed:
            print(f"   ✓ 命名一致 ({name})")
        else:
            print(f"   ✗ {msg}")
            all_passed = False
    else:
        print(f"   ✗ 无法验证 (文件缺失)")

    # 6. 检查脚本
    print("\n6. 检查脚本文件...")
    scripts_dir = SKILL_DIR / "scripts"
    if scripts_dir.exists():
        py_files = list(scripts_dir.glob("*.py"))
        if py_files:
            for f in py_files:
                print(f"   ✓ {f.name}")
        else:
            print(f"   ⚠ 没有 Python 脚本")

    # 总结
    print("\n" + "=" * 50)
    if all_passed:
        print("✓ 所有验证通过!")
        return 0
    else:
        print("✗ 部分验证失败，请修复后重试")
        return 1

if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
国基金申报指南技能验证脚本
验证技能文件结构、frontmatter格式和内容完整性
"""

import os
import re
import json
from pathlib import Path

# 技能根目录
SKILL_ROOT = Path(__file__).parent.parent
SKILL_MD = SKILL_ROOT / "SKILL.md"
META_JSON = SKILL_ROOT / "_meta.json"
REFERENCES_DIR = SKILL_ROOT / "references"

# 颜色定义
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'

def print_success(msg):
    print(f"{GREEN}✓ {msg}{RESET}")

def print_error(msg):
    print(f"{RED}✗ {msg}{RESET}")

def print_warning(msg):
    print(f"{YELLOW}⚠ {msg}{RESET}")

def print_info(msg):
    print(f"  {msg}")

def validate_frontmatter():
    """验证SKILL.md的frontmatter格式"""
    print("\n" + "="*50)
    print("验证 Frontmatter 格式")
    print("="*50)

    if not SKILL_MD.exists():
        print_error(f"SKILL.md 文件不存在: {SKILL_MD}")
        return False

    with open(SKILL_MD, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查第一行是否是frontmatter开始
    lines = content.split('\n')
    if lines[0].strip() != '---':
        print_error("Frontmatter 必须以 --- 开头")
        print_info(f"第一行: {lines[0][:50]}")
        return False
    print_success("Frontmatter 以 --- 开头")

    # 查找frontmatter结束标记
    end_index = -1
    for i, line in enumerate(lines[1:], 1):
        if line.strip() == '---':
            end_index = i
            break

    if end_index == -1:
        print_error("Frontmatter 缺少结束 ---")
        return False
    print_success("Frontmatter 有结束标记")

    # 解析frontmatter
    frontmatter_content = '\n'.join(lines[1:end_index])

    # 检查必需的字段
    required_fields = ['name', 'description']
    for field in required_fields:
        if not re.search(rf'^{field}:', frontmatter_content, re.MULTILINE):
            print_error(f"缺少必需字段: {field}")
            return False
        print_success(f"包含字段: {field}")

    # 检查name格式
    name_match = re.search(r'^name:\s*(.+)', frontmatter_content, re.MULTILINE)
    if name_match:
        name = name_match.group(1).strip()
        # 检查是否使用连字符格式
        if ' ' in name:
            print_warning(f"name 使用空格格式: {name}")
        else:
            print_success(f"name 格式正确: {name}")

    # 检查description长度
    desc_match = re.search(r'^description:\s*(.+)', frontmatter_content, re.MULTILINE)
    if desc_match:
        desc = desc_match.group(1).strip()
        if len(desc) < 50:
            print_warning(f"description 较短，可能不够详细")
        else:
            print_success(f"description 长度: {len(desc)} 字符")

    return True

def validate_meta_json():
    """验证_meta.json文件"""
    print("\n" + "="*50)
    print("验证 _meta.json")
    print("="*50)

    if not META_JSON.exists():
        print_error(f"_meta.json 文件不存在: {META_JSON}")
        return False

    try:
        with open(META_JSON, 'r', encoding='utf-8') as f:
            meta = json.load(f)
    except json.JSONDecodeError as e:
        print_error(f"_meta.json JSON格式错误: {e}")
        return False

    # 检查必需字段
    required_fields = ['id', 'version']
    for field in required_fields:
        if field not in meta:
            print_error(f"缺少必需字段: {field}")
            return False
        print_success(f"包含字段: {field} = {meta[field]}")

    # 验证ID是数字
    if not isinstance(meta['id'], (int, str)):
        print_error(f"id 必须是数字类型")
        return False
    print_success(f"id 格式正确")

    # 验证版本号格式
    version = meta.get('version', '')
    if not re.match(r'^\d+\.\d+\.\d+$', version):
        print_warning(f"version 格式应为 x.y.z，当前: {version}")
    else:
        print_success(f"version 格式正确: {version}")

    return True

def validate_directory_structure():
    """验证目录结构"""
    print("\n" + "="*50)
    print("验证目录结构")
    print("="*50)

    # 检查必需文件
    required_files = [
        (SKILL_MD, "SKILL.md"),
        (META_JSON, "_meta.json"),
    ]

    for file_path, name in required_files:
        if file_path.exists():
            print_success(f"存在: {name}")
        else:
            print_error(f"缺失: {name}")
            return False

    # 检查references目录
    if REFERENCES_DIR.exists():
        ref_files = list(REFERENCES_DIR.glob("*.md"))
        print_success(f"references目录存在，包含 {len(ref_files)} 个文件")
        for rf in ref_files:
            print_info(f"  - {rf.name}")
    else:
        print_warning("references目录不存在")

    return True

def validate_naming():
    """验证命名规范"""
    print("\n" + "="*50)
    print("验证命名规范")
    print("="*50)

    # 检查文件夹名是否为英文
    folder_name = SKILL_ROOT.name
    if not re.match(r'^[a-z0-9\-]+$', folder_name):
        print_error(f"文件夹名包含非英文字符: {folder_name}")
        return False
    print_success(f"文件夹名格式正确: {folder_name}")

    # 检查meta.json中的name与文件夹名一致
    with open(META_JSON, 'r', encoding='utf-8') as f:
        meta = json.load(f)

    meta_name = meta.get('name', '')
    if meta_name != folder_name:
        print_warning(f"name ({meta_name}) 与文件夹名 ({folder_name}) 不一致")
    else:
        print_success(f"name 与文件夹名一致")

    return True

def validate_skill_content():
    """验证SKILL.md内容完整性"""
    print("\n" + "="*50)
    print("验证 SKILL.md 内容")
    print("="*50)

    with open(SKILL_MD, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查是否包含主要章节
    sections = [
        (r'#.*摘要|立项依据', '摘要/立项依据部分'),
        (r'#.*研究方案|技术路线', '研究方案部分'),
        (r'#.*学科|代码', '学科代码部分'),
        (r'#.*预算|经费', '经费预算部分'),
        (r'#.*问题|FAQ', '常见问题部分'),
    ]

    for pattern, name in sections:
        if re.search(pattern, content, re.IGNORECASE):
            print_success(f"包含: {name}")
        else:
            print_warning(f"未找到: {name}")

    # 检查字数
    char_count = len(content)
    print_info(f"总字符数: {char_count}")

    if char_count < 2000:
        print_warning("内容可能偏少")
    else:
        print_success("内容长度适中")

    return True

def main():
    print("\n" + "="*60)
    print("国基金申报指南技能 - 验证脚本")
    print("="*60)

    all_passed = True

    # 执行各项验证
    checks = [
        ("Frontmatter验证", validate_frontmatter),
        ("_meta.json验证", validate_meta_json),
        ("目录结构验证", validate_directory_structure),
        ("命名规范验证", validate_naming),
        ("内容完整性验证", validate_skill_content),
    ]

    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
            if not result:
                all_passed = False
        except Exception as e:
            print_error(f"{name} 执行出错: {e}")
            results.append((name, False))
            all_passed = False

    # 总结
    print("\n" + "="*60)
    print("验证结果总结")
    print("="*60)

    for name, result in results:
        status = f"{GREEN}通过{RESET}" if result else f"{RED}失败{RESET}"
        print(f"  {name}: {status}")

    if all_passed:
        print(f"\n{GREEN}所有验证通过！{RESET}")
        return 0
    else:
        print(f"\n{RED}部分验证未通过，请修复后重试{RESET}")
        return 1

if __name__ == "__main__":
    exit(main())

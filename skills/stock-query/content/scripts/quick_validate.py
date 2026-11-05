#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票查询技能验证脚本
检查 SKILL.md 和 _meta.json 的格式是否符合规范
"""

import os
import re
import json
import sys
from pathlib import Path

# 颜色定义
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'

def log_success(msg):
    print(f"{GREEN}✓ {msg}{RESET}")

def log_error(msg):
    print(f"{RED}✗ {msg}{RESET}")

def log_warning(msg):
    print(f"{YELLOW}⚠ {msg}{RESET}")

def log_info(msg):
    print(f"  {msg}")

def validate_frontmatter(skill_md_path):
    """验证 SKILL.md 的 frontmatter 格式"""
    print("\n" + "=" * 50)
    print("1. 验证 Frontmatter 格式")
    print("=" * 50)

    with open(skill_md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查是否以 --- 开头
    if not content.startswith('---'):
        log_error("SKILL.md 必须以 --- 开头")
        return False

    # 提取 frontmatter
    frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not frontmatter_match:
        log_error("无法解析 frontmatter")
        return False

    frontmatter_str = frontmatter_match.group(1)

    # 检查必需字段
    required_fields = ['name', 'description']
    missing_fields = []

    for field in required_fields:
        if not re.search(rf'^{field}:', frontmatter_str, re.MULTILINE):
            missing_fields.append(field)

    if missing_fields:
        log_error(f"缺少必需字段: {', '.join(missing_fields)}")
        return False

    log_success("Frontmatter 格式正确")

    # 提取字段值进行验证
    name_match = re.search(r'^name:\s*(.+)$', frontmatter_str, re.MULTILINE)
    desc_match = re.search(r'^description:\s*(.+)$', frontmatter_str, re.MULTILINE)

    if name_match:
        name = name_match.group(1).strip()
        log_info(f"name: {name}")

        # 检查名称格式（连字符）
        if not re.match(r'^[a-z0-9-]+$', name):
            log_error("name 必须是连字符格式 (如 stock-query)")
            return False

        # 检查名称长度
        if len(name) > 64:
            log_error("name 不能超过 64 字符")
            return False

        log_success("name 格式正确")

    if desc_match:
        desc = desc_match.group(1).strip()
        log_info(f"description 长度: {len(desc)} 字符")

        if len(desc) < 10:
            log_warning("description 可能太短，建议提供更详细的描述")

        log_success("description 已设置")

    return True

def validate_meta_json(meta_path):
    """验证 _meta.json 的格式"""
    print("\n" + "=" * 50)
    print("2. 验证 _meta.json 格式")
    print("=" * 50)

    if not os.path.exists(meta_path):
        log_error("_meta.json 不存在")
        return False

    try:
        with open(meta_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)
    except json.JSONDecodeError as e:
        log_error(f"_meta.json 格式错误: {e}")
        return False

    # 检查必需字段
    required_fields = ['id', 'version']
    missing_fields = []

    for field in required_fields:
        if field not in meta:
            missing_fields.append(field)

    if missing_fields:
        log_error(f"缺少必需字段: {', '.join(missing_fields)}")
        return False

    log_success("必需字段完整")

    # 验证 id
    skill_id = meta.get('id')
    log_info(f"id: {skill_id}")

    if not isinstance(skill_id, (str, int)):
        log_error("id 必须是字符串或整数")
        return False

    # 验证 version
    version = meta.get('version')
    log_info(f"version: {version}")

    if not re.match(r'^\d+\.\d+\.\d+$', version):
        log_error("version 必须是语义化版本格式 (如 1.0.0)")
        return False

    log_success("_meta.json 格式正确")
    return True

def validate_directory_structure(skill_dir):
    """验证目录结构"""
    print("\n" + "=" * 50)
    print("3. 验证目录结构")
    print("=" * 50)

    # 必需的文件/目录
    required_paths = [
        'SKILL.md',
        '_meta.json',
    ]

    # 可选的目录
    optional_dirs = [
        'assets',
        'references',
        'scripts'
    ]

    all_valid = True

    for path in required_paths:
        full_path = os.path.join(skill_dir, path)
        if os.path.exists(full_path):
            log_success(f"✓ {path}")
        else:
            log_error(f"✗ {path} 缺失")
            all_valid = False

    for dir_name in optional_dirs:
        full_path = os.path.join(skill_dir, dir_name)
        if os.path.isdir(full_path):
            log_success(f"✓ {dir_name}/ (可选)")
        else:
            log_warning(f"⚠ {dir_name}/ 未创建 (可选)")

    return all_valid

def validate_code_files(skill_dir):
    """验证代码文件"""
    print("\n" + "=" * 50)
    print("4. 验证代码文件")
    print("=" * 50)

    assets_dir = os.path.join(skill_dir, 'assets')
    if not os.path.isdir(assets_dir):
        log_warning("assets/ 目录不存在，跳过代码验证")
        return True

    # 查找 Python 文件
    py_files = list(Path(assets_dir).glob('*.py'))

    if not py_files:
        log_warning("未找到 Python 代码文件")
        return True

    for py_file in py_files:
        log_info(f"检查: {py_file.name}")
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # 检查是否有 run 函数
            if 'def run(' in content:
                log_success(f"  ✓ 包含 run() 入口函数")
            else:
                log_warning(f"  ⚠ 未找到 run() 入口函数")

            # 检查是否有文档字符串
            if '"""' in content or "'''" in content:
                log_success(f"  ✓ 包含文档字符串")
            else:
                log_warning(f"  ⚠ 未包含文档字符串")

        except Exception as e:
            log_error(f"  ✗ 读取失败: {e}")
            return False

    return True

def validate_naming(skill_dir):
    """验证命名规范"""
    print("\n" + "=" * 50)
    print("5. 验证命名规范")
    print("=" * 50)

    # 检查目录名称
    dir_name = os.path.basename(skill_dir)
    log_info(f"技能目录名: {dir_name}")

    if not re.match(r'^[a-z0-9-]+$', dir_name):
        log_error("目录名必须使用小写字母、数字和连字符")
        return False

    log_success("目录名格式正确")

    # 检查 SKILL.md 中的 name 是否与目录名匹配
    skill_md_path = os.path.join(skill_dir, 'SKILL.md')
    with open(skill_md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    name_match = re.search(r'^name:\s*(.+)$', content, re.MULTILINE)
    if name_match:
        frontmatter_name = name_match.group(1).strip()
        if frontmatter_name != dir_name:
            log_warning(f"name ({frontmatter_name}) 与目录名 ({dir_name}) 不一致")
        else:
            log_success(f"name 与目录名一致")

    return True

def validate_security(skill_dir):
    """安全检查"""
    print("\n" + "=" * 50)
    print("6. 安全检查")
    print("=" * 50)

    # 检查是否有 secrets 或凭证
    dangerous_patterns = [
        (r'password\s*=\s*["\'][^"\']+["\']', 'password'),
        (r'api[_-]?key\s*=\s*["\'][^"\']+["\']', 'api_key'),
        (r'secret\s*=\s*["\'][^"\']+["\']', 'secret'),
        (r'token\s*=\s*["\'][^"\']+["\']', 'token'),
    ]

    has_secrets = False
    for root, dirs, files in os.walk(skill_dir):
        for file in files:
            if file.endswith(('.py', '.json', '.md', '.txt', '.yaml', '.yml')):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        for pattern, name in dangerous_patterns:
                            if re.search(pattern, content, re.IGNORECASE):
                                rel_path = os.path.relpath(file_path, skill_dir)
                                log_warning(f"{rel_path}: 包含可能的 {name}")
                                has_secrets = True
                except:
                    pass

    if not has_secrets:
        log_success("未发现明显的凭证信息")

    return True

def main():
    """主函数"""
    # 获取技能目录（默认当前目录）
    skill_dir = sys.argv[1] if len(sys.argv) > 1 else '.'

    print("=" * 50)
    print("股票查询技能 - 质量验证")
    print("=" * 50)
    print(f"技能目录: {os.path.abspath(skill_dir)}")

    results = []

    # 运行所有验证
    results.append(("Frontmatter 格式", validate_frontmatter(os.path.join(skill_dir, 'SKILL.md'))))
    results.append(("_meta.json 格式", validate_meta_json(os.path.join(skill_dir, '_meta.json'))))
    results.append(("目录结构", validate_directory_structure(skill_dir)))
    results.append(("代码文件", validate_code_files(skill_dir)))
    results.append(("命名规范", validate_naming(skill_dir)))
    results.append(("安全检查", validate_security(skill_dir)))

    # 输出总结
    print("\n" + "=" * 50)
    print("验证结果汇总")
    print("=" * 50)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = f"{GREEN}PASS{RESET}" if result else f"{RED}FAIL{RESET}"
        print(f"  {name}: {status}")

    print(f"\n通过: {passed}/{total}")

    if passed == total:
        log_success("\n所有验证通过！技能已准备好打包发布。")
        return 0
    else:
        log_error(f"\n有 {total - passed} 项验证失败，请修复后重试。")
        return 1

if __name__ == "__main__":
    sys.exit(main())

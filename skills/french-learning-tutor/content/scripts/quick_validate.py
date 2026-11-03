#!/usr/bin/env python3
"""
French Learning Tutor - 快速验证脚本
验证 SKILL.md 和 _meta.json 的格式和内容
"""

import json
import os
import sys
import re
from pathlib import Path

# 验证规则
VALIDATION_RULES = {
    "SKILL.md": {
        "required_keys": ["name", "description"],
        "frontmatter_only_start": True,
        "max_name_length": 64,
        "name_pattern": r"^[a-z0-9-]+$"
    },
    "_meta.json": {
        "required_keys": ["id", "version"],
        "version_pattern": r"^\d+\.\d+\.\d+$"
    }
}

# 颜色输出
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_success(msg):
    print(f"{Colors.GREEN}✓{Colors.END} {msg}")

def print_error(msg):
    print(f"{Colors.RED}✗{Colors.END} {msg}")

def print_warning(msg):
    print(f"{Colors.YELLOW}⚠{Colors.END} {msg}")

def print_info(msg):
    print(f"{Colors.BLUE}ℹ{Colors.END} {msg}")

def validate_frontmatter(skill_md_path):
    """验证 SKILL.md 的 frontmatter"""
    errors = []
    warnings = []

    try:
        with open(skill_md_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        return [f"文件不存在: {skill_md_path}"], warnings

    # 检查是否以 --- 开头
    if not content.startswith('---'):
        errors.append("SKILL.md 必须以 --- (frontmatter) 开头")
        return errors, warnings

    # 提取 frontmatter
    frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not frontmatter_match:
        errors.append("无法解析 frontmatter，请检查格式")
        return errors, warnings

    frontmatter_text = frontmatter_match.group(1)

    # 解析 YAML
    try:
        import yaml
        frontmatter = yaml.safe_load(frontmatter_text)
    except ImportError:
        # 手动解析简单的 YAML
        frontmatter = {}
        for line in frontmatter_text.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                frontmatter[key.strip()] = value.strip()

    # 验证必需字段
    for key in VALIDATION_RULES["SKILL.md"]["required_keys"]:
        if key not in frontmatter:
            errors.append(f"缺少必需字段: {key}")

    # 验证 name 字段
    if 'name' in frontmatter:
        name = frontmatter['name']
        # 检查长度
        if len(name) > VALIDATION_RULES["SKILL.md"]["max_name_length"]:
            errors.append(f"name 长度超过 {VALIDATION_RULES['SKILL.md']['max_name_length']} 字符")

        # 检查格式
        if not re.match(VALIDATION_RULES["SKILL.md"]["name_pattern"], name):
            errors.append(f"name 格式不正确，应为小写字母、数字、连字符: {name}")

        # 检查与文件夹名一致
        folder_name = os.path.basename(os.path.dirname(skill_md_path))
        if name != folder_name:
            warnings.append(f"name '{name}' 与文件夹名 '{folder_name}' 不一致")

    # 检查 description 字段
    if 'description' in frontmatter:
        desc = frontmatter['description']
        if len(desc) < 10:
            warnings.append("description 太短，建议至少包含触发短语")
        if len(desc) > 500:
            warnings.append("description 可能过长，考虑简化")

    # 检查 markdown 内容在 frontmatter 之后
    after_frontmatter = content.split('---', 2)[2] if content.count('---') >= 2 else ""
    if not after_frontmatter.strip():
        warnings.append("SKILL.md 缺少 markdown 内容部分")

    return errors, warnings


def validate_meta_json(meta_json_path):
    """验证 _meta.json"""
    errors = []
    warnings = []

    try:
        with open(meta_json_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)
    except FileNotFoundError:
        return [f"文件不存在: {meta_json_path}"], warnings
    except json.JSONDecodeError as e:
        return [f"JSON 解析错误: {e}"], warnings

    # 验证必需字段
    for key in VALIDATION_RULES["_meta.json"]["required_keys"]:
        if key not in meta:
            errors.append(f"缺少必需字段: {key}")

    # 验证 id
    if 'id' in meta:
        if not isinstance(meta['id'], int) or meta['id'] <= 0:
            errors.append(f"id 应为正整数: {meta['id']}")

    # 验证 version
    if 'version' in meta:
        if not re.match(VALIDATION_RULES["_meta.json"]["version_pattern"], meta['version']):
            errors.append(f"version 格式不正确，应为 x.y.z: {meta['version']}")

    return errors, warnings


def validate_directory_structure(skill_dir):
    """验证目录结构"""
    errors = []
    warnings = []

    required_files = ['SKILL.md', '_meta.json']

    for file in required_files:
        file_path = os.path.join(skill_dir, file)
        if not os.path.exists(file_path):
            errors.append(f"缺少必需文件: {file}")

    # 检查可选目录
    optional_dirs = ['scripts', 'references', 'assets']
    for dir_name in optional_dirs:
        dir_path = os.path.join(skill_dir, dir_name)
        if os.path.exists(dir_path):
            if not os.listdir(dir_path):
                warnings.append(f"目录 '{dir_name}' 为空")

    return errors, warnings


def validate_scripts(skill_dir):
    """验证脚本"""
    errors = []
    warnings = []

    scripts_dir = os.path.join(skill_dir, 'scripts')
    if not os.path.exists(scripts_dir):
        return errors, warnings

    expected_scripts = ['package_skill.py']
    for script in expected_scripts:
        script_path = os.path.join(scripts_dir, script)
        if not os.path.exists(script_path):
            warnings.append(f"建议包含脚本: {script}")

    # 检查 Python 脚本语法
    for filename in os.listdir(scripts_dir):
        if filename.endswith('.py'):
            script_path = os.path.join(scripts_dir, filename)
            try:
                with open(script_path, 'r', encoding='utf-8') as f:
                    compile(f.read(), script_path, 'exec')
                print_success(f"脚本语法正确: {filename}")
            except SyntaxError as e:
                errors.append(f"脚本语法错误 {filename}: {e}")

    return errors, warnings


def validate_references(skill_dir):
    """验证参考文档"""
    errors = []
    warnings = []

    references_dir = os.path.join(skill_dir, 'references')
    if not os.path.exists(references_dir):
        warnings.append("建议包含 references/ 目录")
        return errors, warnings

    # 检查必要的参考文档
    recommended_refs = [
        'spaced_repetition.md',
        'feishu_integration.md'
    ]

    for ref in recommended_refs:
        ref_path = os.path.join(references_dir, ref)
        if not os.path.exists(ref_path):
            warnings.append(f"建议包含参考文档: {ref}")

    return errors, warnings


def validate_assets(skill_dir):
    """验证资源文件"""
    errors = []
    warnings = []

    assets_dir = os.path.join(skill_dir, 'assets')
    if not os.path.exists(assets_dir):
        warnings.append("建议包含 assets/ 目录")
        return errors, warnings

    # 检查 JSON 资源文件
    json_files = [f for f in os.listdir(assets_dir) if f.endswith('.json')]
    if not json_files:
        warnings.append("建议包含 JSON 资源文件（如 daily_exercises.json）")

    return errors, warnings


def run_validation(skill_dir):
    """运行所有验证"""
    print(f"\n{'='*60}")
    print(f"🎓 法语学习技能验证")
    print(f"{'='*60}\n")

    all_errors = []
    all_warnings = []

    # 验证目录结构
    print_info("检查目录结构...")
    struct_errors, struct_warnings = validate_directory_structure(skill_dir)
    all_errors.extend(struct_errors)
    all_warnings.extend(struct_warnings)

    if struct_errors:
        for err in struct_errors:
            print_error(err)
    else:
        print_success("目录结构正确")

    # 验证 SKILL.md
    print_info("\n验证 SKILL.md...")
    skill_md_path = os.path.join(skill_dir, 'SKILL.md')
    skill_errors, skill_warnings = validate_frontmatter(skill_md_path)
    all_errors.extend(skill_errors)
    all_warnings.extend(skill_warnings)

    if skill_errors:
        for err in skill_errors:
            print_error(err)
    else:
        print_success("SKILL.md 格式正确")

    # 验证 _meta.json
    print_info("\n验证 _meta.json...")
    meta_path = os.path.join(skill_dir, '_meta.json')
    meta_errors, meta_warnings = validate_meta_json(meta_path)
    all_errors.extend(meta_errors)
    all_warnings.extend(meta_warnings)

    if meta_errors:
        for err in meta_errors:
            print_error(err)
    else:
        print_success("_meta.json 格式正确")

    # 验证脚本
    print_info("\n验证脚本...")
    script_errors, script_warnings = validate_scripts(skill_dir)
    all_errors.extend(script_errors)
    all_warnings.extend(script_warnings)

    # 验证参考文档
    print_info("\n验证参考文档...")
    ref_errors, ref_warnings = validate_references(skill_dir)
    all_errors.extend(ref_errors)
    all_warnings.extend(ref_warnings)

    # 验证资源文件
    print_info("\n验证资源文件...")
    asset_errors, asset_warnings = validate_assets(skill_dir)
    all_errors.extend(asset_errors)
    all_warnings.extend(asset_warnings)

    # 输出总结
    print(f"\n{'='*60}")
    print("📊 验证结果总结")
    print(f"{'='*60}")

    if all_warnings:
        print(f"\n{Colors.YELLOW}⚠️  警告 ({len(all_warnings)}):{Colors.END}")
        for warn in all_warnings:
            print_warning(warn)

    if all_errors:
        print(f"\n{Colors.RED}✗ 错误 ({len(all_errors)}):{Colors.END}")
        for err in all_errors:
            print_error(err)
        print(f"\n{Colors.RED}验证失败！请修复错误后重新运行。{Colors.END}")
        return False
    else:
        print(f"\n{Colors.GREEN}✅ 所有验证通过！{Colors.END}")
        print_success("技能结构正确，可以打包")
        return True


if __name__ == "__main__":
    # 获取技能目录（默认当前目录）
    skill_dir = sys.argv[1] if len(sys.argv) > 1 else "."

    success = run_validation(skill_dir)
    sys.exit(0 if success else 1)
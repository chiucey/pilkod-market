#!/usr/bin/env python3
"""
技能验证脚本
验证SKILL.md结构、frontmatter格式和路径正确性
"""

import os
import re
import sys
from pathlib import Path

def validate_frontmatter(skill_md_path: str) -> tuple[bool, list[str]]:
    """验证frontmatter格式"""
    errors = []
    warnings = []

    with open(skill_md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查是否以---开头
    if not content.strip().startswith('---'):
        errors.append("Frontmatter must start with '---' at the very beginning of the file")
        return False, errors

    # 提取frontmatter
    lines = content.split('\n')
    frontmatter_lines = []
    in_frontmatter = False

    for i, line in enumerate(lines):
        if line.strip() == '---':
            if not in_frontmatter:
                in_frontmatter = True
                frontmatter_lines.append((i, line))
            else:
                frontmatter_lines.append((i, line))
                break
        elif in_frontmatter:
            frontmatter_lines.append((i, line))

    if len(frontmatter_lines) < 2:
        errors.append("Frontmatter incomplete - missing closing '---'")
        return False, errors

    # 解析frontmatter内容
    frontmatter_content = '\n'.join([line for _, line in frontmatter_lines[1:-1]])

    # 检查必需字段
    required_fields = ['name', 'description']
    for field in required_fields:
        if not re.search(rf'^{field}:\s*.+', frontmatter_content, re.MULTILINE):
            errors.append(f"Missing required field: '{field}'")

    # 检查name格式
    name_match = re.search(r'^name:\s*(.+)', frontmatter_content, re.MULTILINE)
    if name_match:
        name_value = name_match.group(1).strip()
        if not re.match(r'^[a-z0-9-]+$', name_value):
            errors.append(f"'name' should use hyphen-case (e.g., 'skill-name'): got '{name_value}'")
        if len(name_value) > 64:
            warnings.append(f"'name' exceeds 64 characters: {len(name_value)}")

    # 检查description是否包含触发短语
    desc_match = re.search(r'^description:\s*(.+)', frontmatter_content, re.MULTILINE)
    if desc_match:
        desc_value = desc_match.group(1).strip()
        if len(desc_value) < 20:
            warnings.append("'description' seems too short, should contain trigger phrases")

    return len(errors) == 0, errors + warnings

def validate_file_structure(skill_dir: str) -> tuple[bool, list[str]]:
    """验证技能目录结构"""
    errors = []
    warnings = []

    required_files = ['SKILL.md', '_meta.json']

    for file in required_files:
        file_path = os.path.join(skill_dir, file)
        if not os.path.exists(file_path):
            errors.append(f"Missing required file: {file}")

    # 检查_meta.json格式
    meta_path = os.path.join(skill_dir, '_meta.json')
    if os.path.exists(meta_path):
        try:
            import json
            with open(meta_path, 'r') as f:
                meta = json.load(f)

            if 'id' not in meta:
                errors.append("_meta.json missing 'id' field")
            if 'version' not in meta:
                errors.append("_meta.json missing 'version' field")
        except json.JSONDecodeError as e:
            errors.append(f"_meta.json is not valid JSON: {e}")

    # 检查scripts目录结构
    scripts_dir = os.path.join(skill_dir, 'scripts')
    if os.path.exists(scripts_dir):
        for filename in os.listdir(scripts_dir):
            if filename.endswith('.py'):
                # 检查Python脚本是否有正确的shebang
                file_path = os.path.join(scripts_dir, filename)
                with open(file_path, 'r') as f:
                    first_line = f.readline()
                    if not first_line.startswith('#!'):
                        warnings.append(f"{filename}: Missing shebang line")

    return len(errors) == 0, errors + warnings

def validate_paths_english(skill_dir: str) -> tuple[bool, list[str]]:
    """验证所有路径和名称为英文"""
    errors = []
    warnings = []

    # 检查文件夹名称
    dir_name = os.path.basename(skill_dir)
    if not re.match(r'^[a-z0-9-]+$', dir_name):
        errors.append(f"Directory name should be English-only with hyphens: '{dir_name}'")

    # 检查所有文件名
    for root, dirs, files in os.walk(skill_dir):
        for filename in files:
            if not re.match(r'^[a-zA-Z0-9_.-]+$', filename):
                errors.append(f"Filename should be English-only: '{filename}' in {root}")

    # 检查文件内容中的中文路径引用
    for root, dirs, files in os.walk(skill_dir):
        for filename in files:
            if filename.endswith(('.py', '.md', '.json', '.txt')):
                file_path = os.path.join(root, filename)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        # 检查是否包含非ASCII字符路径（排除注释）
                        lines = content.split('\n')
                        for i, line in enumerate(lines, 1):
                            # 跳过注释行
                            if line.strip().startswith('#') or line.strip().startswith('//'):
                                continue
                            # 检查中文
                            if re.search(r'[\u4e00-\u9fff]', line):
                                # 检查是否是路径引用
                                if '/' in line or '\\' in line:
                                    warnings.append(f"{filename}:{i} - Contains Chinese characters in path-like content")
                except Exception:
                    pass

    return len(errors) == 0, errors + warnings

def run_validation(skill_dir: str) -> bool:
    """运行所有验证"""
    print("=" * 60)
    print("技能验证报告")
    print("=" * 60)
    print(f"\n技能目录: {skill_dir}\n")

    all_passed = True

    # 1. Frontmatter验证
    print("1. Frontmatter格式验证...")
    skill_md = os.path.join(skill_dir, 'SKILL.md')
    if os.path.exists(skill_md):
        passed, messages = validate_frontmatter(skill_md)
        for msg in messages:
            status = "✗ ERROR" if "Missing" in msg or "must" in msg else "⚠ WARNING"
            print(f"   {status}: {msg}")
        if not passed:
            all_passed = False
    else:
        print("   ✗ SKILL.md not found")
        all_passed = False

    # 2. 目录结构验证
    print("\n2. 目录结构验证...")
    passed, messages = validate_file_structure(skill_dir)
    for msg in messages:
        status = "✗ ERROR" if "Missing" in msg else "⚠ WARNING"
        print(f"   {status}: {msg}")
    if not passed:
        all_passed = False

    # 3. 路径英文验证
    print("\n3. 路径英文验证...")
    passed, messages = validate_paths_english(skill_dir)
    for msg in messages:
        status = "✗ ERROR" if "should" in msg else "⚠ WARNING"
        print(f"   {status}: {msg}")
    if not passed:
        all_passed = False

    # 总结
    print("\n" + "=" * 60)
    if all_passed:
        print("✓ 所有验证通过")
    else:
        print("✗ 存在错误，请修复后重试")
    print("=" * 60)

    return all_passed

if __name__ == "__main__":
    # 从命令行参数获取技能目录
    if len(sys.argv) > 1:
        skill_dir = sys.argv[1]
    else:
        # 默认检查当前目录下的技能
        skill_dir = os.path.dirname(os.path.abspath(__file__))
        # 向上两级到达技能根目录
        skill_dir = os.path.dirname(os.path.dirname(skill_dir))

    success = run_validation(skill_dir)
    sys.exit(0 if success else 1)

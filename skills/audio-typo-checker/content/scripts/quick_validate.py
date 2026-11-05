#!/usr/bin/env python3
"""
Audio Typo Checker - Skill Validator
验证技能文件结构和内容的有效性
"""
import json
import os
import re
import sys
from pathlib import Path


def validate_frontmatter(skill_md_path):
    """验证 SKILL.md 的 frontmatter"""
    errors = []
    warnings = []

    with open(skill_md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查是否以 --- 开头
    if not content.startswith('---'):
        errors.append("SKILL.md 必须以 --- 开头")
        return errors, warnings

    # 提取 frontmatter
    lines = content.split('\n')
    if len(lines) < 3:
        errors.append("SKILL.md frontmatter 不完整")
        return errors, warnings

    # 找到 frontmatter 结束
    end_idx = -1
    for i, line in enumerate(lines[1:], 1):
        if line.strip() == '---':
            end_idx = i
            break

    if end_idx == -1:
        errors.append("SKILL.md 缺少 frontmatter 结束标记 ---")
        return errors, warnings

    # 解析 frontmatter
    frontmatter_lines = lines[1:end_idx]
    frontmatter = {}
    for line in frontmatter_lines:
        if ':' in line:
            key, value = line.split(':', 1)
            frontmatter[key.strip()] = value.strip()

    # 必填字段检查
    required_fields = ['name', 'description']
    for field in required_fields:
        if field not in frontmatter:
            errors.append(f"frontmatter 缺少必填字段: {field}")

    # name 检查
    if 'name' in frontmatter:
        name = frontmatter['name']
        # 检查名称格式（连字符）
        if not re.match(r'^[a-z0-9-]+$', name):
            errors.append(f"name 必须使用连字符格式（小写字母、数字、连字符）: {name}")
        # 检查名称长度
        if len(name) > 64:
            errors.append(f"name 不能超过 64 字符: 当前 {len(name)} 字符")

    # description 检查
    if 'description' in frontmatter:
        desc = frontmatter['description']
        # 检查触发短语
        trigger_phrases = ['检测', '配音', '错别字', '音频', '文案']
        has_trigger = any(phrase in desc for phrase in trigger_phrases)
        if not has_trigger:
            warnings.append("description 建议包含触发短语，如'检测错别字'、'配音质检'等")

    return errors, warnings


def validate_meta_json(meta_path):
    """验证 _meta.json"""
    errors = []

    if not os.path.exists(meta_path):
        errors.append("_meta.json 文件不存在")
        return errors

    try:
        with open(meta_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)
    except json.JSONDecodeError as e:
        errors.append(f"_meta.json JSON 格式错误: {e}")
        return errors

    # 必填字段
    required_fields = ['id', 'version']
    for field in required_fields:
        if field not in meta:
            errors.append(f"_meta.json 缺少必填字段: {field}")

    # version 格式检查
    if 'version' in meta:
        version = meta['version']
        if not re.match(r'^\d+\.\d+\.\d+$', version):
            errors.append(f"version 格式错误，应为语义化版本如 1.0.0: {version}")

    return errors


def validate_directory_structure(skill_dir):
    """验证目录结构"""
    errors = []

    # 检查必要文件
    required_files = ['SKILL.md', '_meta.json']
    for file in required_files:
        path = os.path.join(skill_dir, file)
        if not os.path.exists(path):
            errors.append(f"缺少必要文件: {file}")

    # 检查 scripts 目录
    scripts_dir = os.path.join(skill_dir, 'scripts')
    if os.path.exists(scripts_dir):
        # 检查是否为空
        py_files = list(Path(scripts_dir).glob('*.py'))
        if len(py_files) == 0:
            errors.append("scripts 目录存在但没有 Python 文件")

    return errors


def validate_skill_name(skill_dir):
    """验证技能名称与文件夹名称一致"""
    errors = []

    skill_name = os.path.basename(skill_dir)

    # 检查文件夹名称格式
    if not re.match(r'^[a-z0-9-]+$', skill_name):
        errors.append(f"文件夹名称必须使用连字符格式（小写字母、数字、连字符）: {skill_name}")

    # 检查与 SKILL.md 中的 name 是否一致
    skill_md_path = os.path.join(skill_dir, 'SKILL.md')
    if os.path.exists(skill_md_path):
        with open(skill_md_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 提取 name
        match = re.search(r'^name:\s*(.+)$', content, re.MULTILINE)
        if match:
            frontmatter_name = match.group(1).strip()
            if frontmatter_name != skill_name:
                errors.append(f"文件夹名称与 SKILL.md 中的 name 不一致: 文件夹={skill_name}, name={frontmatter_name}")

    return errors


def validate_scripts(skill_dir):
    """验证脚本文件"""
    errors = []
    warnings = []

    scripts_dir = os.path.join(skill_dir, 'scripts')
    if not os.path.exists(scripts_dir):
        warnings.append("scripts 目录不存在（可选）")
        return errors, warnings

    py_files = list(Path(scripts_dir).glob('*.py'))

    for py_file in py_files:
        file_path = py_file.absolute()

        # 检查 shebang
        with open(file_path, 'r', encoding='utf-8') as f:
            first_line = f.readline().strip()
            if not first_line.startswith('#!'):
                warnings.append(f"{py_file.name}: 建议添加 shebang (如 #!/usr/bin/env python3)")

        # 检查文件是否可执行
        if not os.access(file_path, os.X_OK):
            warnings.append(f"{py_file.name}: 建议添加可执行权限 (chmod +x)")

        # 基本语法检查
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                compile(f.read(), file_path, 'exec')
        except SyntaxError as e:
            errors.append(f"{py_file.name}: 语法错误 - {e}")

    return errors, warnings


def validate(skill_dir):
    """执行完整验证"""
    print(f"正在验证技能: {skill_dir}")
    print("=" * 60)

    all_errors = []
    all_warnings = []

    # 1. 目录结构
    print("\n[1/5] 检查目录结构...")
    struct_errors = validate_directory_structure(skill_dir)
    all_errors.extend(struct_errors)
    if struct_errors:
        print(f"  ❌ 发现 {len(struct_errors)} 个错误")
    else:
        print("  ✓ 目录结构正确")

    # 2. Frontmatter
    print("\n[2/5] 检查 frontmatter...")
    skill_md_path = os.path.join(skill_dir, 'SKILL.md')
    if os.path.exists(skill_md_path):
        fm_errors, fm_warnings = validate_frontmatter(skill_md_path)
        all_errors.extend(fm_errors)
        all_warnings.extend(fm_warnings)
        if fm_errors:
            print(f"  ❌ 发现 {len(fm_errors)} 个错误")
            for err in fm_errors:
                print(f"     - {err}")
        else:
            print("  ✓ Frontmatter 正确")
        for warn in fm_warnings:
            print(f"  ⚠️  {warn}")
    else:
        all_errors.append("SKILL.md 不存在")
        print("  ❌ SKILL.md 不存在")

    # 3. _meta.json
    print("\n[3/5] 检查 _meta.json...")
    meta_path = os.path.join(skill_dir, '_meta.json')
    if os.path.exists(meta_path):
        meta_errors = validate_meta_json(meta_path)
        all_errors.extend(meta_errors)
        if meta_errors:
            print(f"  ❌ 发现 {len(meta_errors)} 个错误")
            for err in meta_errors:
                print(f"     - {err}")
        else:
            print("  ✓ _meta.json 正确")

    # 4. 名称一致性
    print("\n[4/5] 检查名称一致性...")
    name_errors = validate_skill_name(skill_dir)
    all_errors.extend(name_errors)
    if name_errors:
        print(f"  ❌ 发现 {len(name_errors)} 个错误")
        for err in name_errors:
            print(f"     - {err}")
    else:
        print("  ✓ 名称一致")

    # 5. 脚本验证
    print("\n[5/5] 检查脚本文件...")
    script_errors, script_warnings = validate_scripts(skill_dir)
    all_errors.extend(script_errors)
    all_warnings.extend(script_warnings)
    if script_errors:
        print(f"  ❌ 发现 {len(script_errors)} 个错误")
        for err in script_errors:
            print(f"     - {err}")
    else:
        print("  ✓ 脚本检查通过")
    for warn in script_warnings:
        print(f"  ⚠️  {warn}")

    # 总结
    print("\n" + "=" * 60)
    print("验证结果:")
    if all_errors:
        print(f"  ❌ 失败: {len(all_errors)} 个错误")
        return False
    else:
        print(f"  ✓ 通过: {len(all_warnings)} 个警告")
        return True


if __name__ == '__main__':
    if len(sys.argv) < 2:
        # 默认验证当前目录
        skill_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    else:
        skill_dir = sys.argv[1]

    success = validate(skill_dir)
    sys.exit(0 if success else 1)

#!/usr/bin/env python3
"""
快速验证脚本 - 检查技能文件结构和格式
"""

import os
import sys
import json
import re

def validate_frontmatter(skill_md_path):
    """验证SKILL.md的frontmatter格式"""
    errors = []

    with open(skill_md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查是否以---开头
    if not content.startswith('---'):
        errors.append("SKILL.md必须以---开头作为frontmatter分隔符")
        return errors

    # 提取frontmatter
    lines = content.split('\n')
    frontmatter_end = -1
    for i, line in enumerate(lines[1:], 1):
        if line.strip() == '---':
            frontmatter_end = i
            break

    if frontmatter_end == -1:
        errors.append("SKILL.md缺少frontmatter结束标记---")
        return errors

    frontmatter_lines = lines[1:frontmatter_end]
    frontmatter_str = '\n'.join(frontmatter_lines)

    # 检查必需字段
    if 'name:' not in frontmatter_str:
        errors.append("frontmatter缺少name字段")
    if 'description:' not in frontmatter_str:
        errors.append("frontmatter缺少description字段")

    # 验证name格式（连字符、小写）
    name_match = re.search(r'^name:\s*(.+)$', frontmatter_str, re.MULTILINE)
    if name_match:
        name = name_match.group(1).strip()
        if not re.match(r'^[a-z0-9-]+$', name):
            errors.append(f"name必须使用小写字母、数字和连字符，当前值：{name}")

    # 检查frontmatter后是否有markdown标题（允许空白行后跟标题）
    after_frontmatter_lines = lines[frontmatter_end+1:]
    # 找到第一个非空行
    first_content_line = ''
    for line in after_frontmatter_lines:
        if line.strip():
            first_content_line = line.strip()
            break

    # 如果第一个非空行直接是标题（无空行间隔），则报错
    # 但允许有1-2个空行后跟标题的情况
    if first_content_line.startswith('#'):
        # 检查是否在frontmatter结束后立即出现标题（无空行）
        content_without_title = '\n'.join(after_frontmatter_lines).strip()
        # 移除开头的空行和标题，检查是否还有内容
        temp = content_without_title.lstrip('#').strip()
        if not temp and len(after_frontmatter_lines) <= 2:
            errors.append("frontmatter后不应直接跟markdown标题，应在空行后开始")

    return errors

def validate_meta_json(meta_path):
    """验证_meta.json格式"""
    errors = []

    if not os.path.exists(meta_path):
        errors.append("_meta.json文件不存在")
        return errors

    try:
        with open(meta_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)

        if 'id' not in meta:
            errors.append("_meta.json缺少id字段")
        if 'version' not in meta:
            errors.append("_meta.json缺少version字段")

        if 'id' in meta and not isinstance(meta['id'], int):
            errors.append("_meta.json的id必须是整数")

        if 'version' in meta:
            version = meta['version']
            if not re.match(r'^\d+\.\d+\.\d+$', version):
                errors.append(f"_meta.json的version格式不正确，应为x.y.z，当前值：{version}")

    except json.JSONDecodeError as e:
        errors.append(f"_meta.json JSON格式错误: {e}")

    return errors

def validate_directory_structure(skill_dir):
    """验证目录结构"""
    errors = []

    required_files = ['SKILL.md', '_meta.json']
    for file in required_files:
        path = os.path.join(skill_dir, file)
        if not os.path.exists(path):
            errors.append(f"缺少必需文件: {file}")

    # 检查可选目录
    optional_dirs = ['scripts', 'references', 'assets']
    for dir_name in optional_dirs:
        dir_path = os.path.join(skill_dir, dir_name)
        if os.path.exists(dir_path) and not os.path.isdir(dir_path):
            errors.append(f"{dir_name}应该是目录而非文件")

    return errors

def validate_naming(skill_dir):
    """验证命名规范"""
    errors = []
    skill_name = os.path.basename(skill_dir)

    if not re.match(r'^[a-z0-9-]+$', skill_name):
        errors.append(f"技能目录名必须使用小写字母、数字和连字符，当前值：{skill_name}")

    return errors

def main():
    skill_dir = sys.argv[1] if len(sys.argv) > 1 else '.'

    all_errors = []

    # 验证各项
    all_errors.extend(validate_frontmatter(os.path.join(skill_dir, 'SKILL.md')))
    all_errors.extend(validate_meta_json(os.path.join(skill_dir, '_meta.json')))
    all_errors.extend(validate_directory_structure(skill_dir))
    all_errors.extend(validate_naming(skill_dir))

    # 输出结果
    if all_errors:
        print("❌ 验证失败:")
        for error in all_errors:
            print(f"  - {error}")
        return 1
    else:
        print("✅ 验证通过!")
        return 0

if __name__ == '__main__':
    sys.exit(main())

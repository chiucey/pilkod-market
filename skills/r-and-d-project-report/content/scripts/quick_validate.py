"""
研发立项报告技能验证脚本
验证SKILL.md的frontmatter和结构是否符合规范
"""

import os
import sys

def validate_skill(skill_path):
    """验证技能结构"""
    errors = []
    warnings = []

    # 检查必需文件
    required_files = ['SKILL.md', '_meta.json']
    for file in required_files:
        file_path = os.path.join(skill_path, file)
        if not os.path.exists(file_path):
            errors.append(f"缺少必需文件: {file}")

    if errors:
        return False, errors, warnings

    # 验证SKILL.md frontmatter
    skill_md_path = os.path.join(skill_path, 'SKILL.md')
    with open(skill_md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查frontmatter格式
    if not content.startswith('---'):
        errors.append("SKILL.md必须以---开头（frontmatter开始）")
    else:
        frontmatter_end = content.find('---', 3)
        if frontmatter_end == -1:
            errors.append("缺少frontmatter结束标记---")
        else:
            frontmatter = content[3:frontmatter_end].strip()
            frontmatter_lines = frontmatter.split('\n')
            found_fields = []
            for line in frontmatter_lines:
                line = line.strip()
                if ':' in line:
                    field_name = line.split(':')[0].strip()
                    found_fields.append(field_name)
            required_fields = ['name', 'description']
            for field in required_fields:
                if field not in found_fields:
                    errors.append(f"缺少必需字段: {field}")

    # 验证_meta.json
    meta_path = os.path.join(skill_path, '_meta.json')
    import json
    with open(meta_path, 'r', encoding='utf-8') as f:
        meta = json.load(f)

    required_meta_fields = ['id', 'version']
    for field in required_meta_fields:
        if field not in meta:
            errors.append(f"_meta.json缺少必需字段: {field}")

    # 检查name是否与目录名一致
    if 'name' in meta:
        expected_name = os.path.basename(skill_path)
        if meta.get('name') != expected_name:
            warnings.append(f"name '{meta.get('name')}' 应与目录名 '{expected_name}' 一致")

    if errors:
        return False, errors, warnings
    return True, [], warnings

if __name__ == '__main__':
    skill_path = sys.argv[1] if len(sys.argv) > 1 else '.'
    success, errors, warnings = validate_skill(skill_path)

    if warnings:
        print("警告:")
        for w in warnings:
            print(f"  - {w}")

    if success:
        print("✓ 验证通过")
        sys.exit(0)
    else:
        print("✗ 验证失败:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
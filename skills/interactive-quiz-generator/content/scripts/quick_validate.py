#!/usr/bin/env python3
"""
Quick Validate Script
验证技能结构和 frontmatter 格式
"""

import json
import sys
from pathlib import Path


def validate_skill(skill_path: Path) -> bool:
    """验证技能目录结构和文件"""
    errors = []
    warnings = []

    # 检查 SKILL.md
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        errors.append("SKILL.md 文件不存在")
        return False

    # 检查 frontmatter
    content = skill_md.read_text(encoding='utf-8')

    # 检查第一行是否是 ---
    lines = content.split('\n')
    if not lines or lines[0].strip() != '---':
        errors.append("SKILL.md 必须以 --- 开头（frontmatter 开始）")
        return False

    # 找到 frontmatter 结束
    try:
        end_idx = lines[1:].index('---') + 1
    except ValueError:
        errors.append("SKILL.md frontmatter 未正确关闭（缺少结束的 ---）")
        return False

    # 解析 frontmatter
    frontmatter_lines = lines[1:end_idx]
    frontmatter = {}
    for line in frontmatter_lines:
        if ':' in line:
            key, value = line.split(':', 1)
            frontmatter[key.strip()] = value.strip()

    # 验证必需字段
    required_fields = ['name', 'description']
    for field in required_fields:
        if field not in frontmatter:
            errors.append(f"frontmatter 缺少必需字段: {field}")

    # 检查 name 格式
    if 'name' in frontmatter:
        name = frontmatter['name']
        if not name.replace('-', '').replace('_', '').isalnum():
            errors.append(f"name 包含非法字符: {name}")
        if ' ' in name:
            warnings.append("name 应该使用连字符格式（kebab-case）")

    # 检查 description
    if 'description' in frontmatter:
        desc = frontmatter['description']
        if len(desc) < 20:
            warnings.append("description 可能太短，建议至少 20 个字符")
        if 'Use when' not in desc and '当用户' not in desc:
            warnings.append("description 建议包含触发短语（如 'Use when...' 或 '当用户...')")

    # 检查 _meta.json
    meta_file = skill_path / "_meta.json"
    if meta_file.exists():
        try:
            meta = json.loads(meta_file.read_text(encoding='utf-8'))
            if 'id' not in meta:
                errors.append("_meta.json 缺少 'id' 字段")
            if 'version' not in meta:
                errors.append("_meta.json 缺少 'version' 字段")
        except json.JSONDecodeError as e:
            errors.append(f"_meta.json 格式错误: {e}")
    else:
        errors.append("_meta.json 文件不存在")

    # 检查模板目录
    templates_dir = skill_path / "templates"
    if templates_dir.exists():
        html_files = list(templates_dir.glob("*.html"))
        if len(html_files) < 1:
            warnings.append("templates 目录为空，建议至少包含一种模板")

    # 输出结果
    print("\n" + "=" * 50)
    print("技能验证结果")
    print("=" * 50)

    if errors:
        print("\n❌ 错误:")
        for error in errors:
            print(f"   - {error}")

    if warnings:
        print("\n⚠️  警告:")
        for warning in warnings:
            print(f"   - {warning}")

    if not errors:
        print("\n✅ 验证通过！")
        print(f"   - frontmatter 格式正确")
        print(f"   - 必需字段完整")
        if templates_dir.exists():
            print(f"   - 找到 {len(html_files)} 个模板文件")
        return True
    else:
        print("\n❌ 验证失败，请修复上述错误")
        return False


def main():
    """主函数"""
    if len(sys.argv) > 1:
        skill_path = Path(sys.argv[1])
    else:
        skill_path = Path(__file__).parent.parent

    if not skill_path.exists():
        print(f"错误: 路径不存在 - {skill_path}")
        sys.exit(1)

    success = validate_skill(skill_path)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()

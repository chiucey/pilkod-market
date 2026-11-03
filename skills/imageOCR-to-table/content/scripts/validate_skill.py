#!/usr/bin/env python3
"""
技能验证脚本 - 检查 SKILL.md 和 _meta.json 的格式正确性
"""
import json
import os
import re
import sys

def validate_skill(skill_path):
    """验证技能结构"""
    errors = []
    warnings = []

    # 检查目录结构
    if not os.path.exists(skill_path):
        errors.append(f"技能目录不存在: {skill_path}")
        return errors, warnings

    # 检查 SKILL.md
    skill_md = os.path.join(skill_path, "SKILL.md")
    if not os.path.exists(skill_md):
        errors.append("缺少 SKILL.md 文件")
    else:
        with open(skill_md, 'r', encoding='utf-8') as f:
            content = f.read()

        # 检查 frontmatter 格式
        if not content.startswith('---'):
            errors.append("SKILL.md 必须以 YAML frontmatter 开头（---）")

        # 提取 frontmatter
        match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
        if not match:
            errors.append("无法解析 YAML frontmatter")
        else:
            try:
                import yaml
                frontmatter = yaml.safe_load(match.group(1))

                # 检查必填字段
                if 'name' not in frontmatter:
                    errors.append("frontmatter 缺少 'name' 字段")
                if 'description' not in frontmatter:
                    errors.append("frontmatter 缺少 'description' 字段")

                # 检查 name 格式（连字符，允许大写缩写词如OCR、API）
                if 'name' in frontmatter:
                    name = frontmatter['name']
                    if not re.match(r'^[a-zA-Z0-9]+(-[a-zA-Z0-9]+)*$', name):
                        errors.append(f"name 格式错误，应使用连字符格式（允许大写缩写词）: {name}")

                # 检查 description 包含触发短语
                if 'description' in frontmatter:
                    desc = frontmatter['description']
                    if 'Use when' not in desc and '当用户' not in desc:
                        warnings.append("description 建议包含触发短语 'Use when...' 或 '当用户...'")
            except Exception as e:
                errors.append(f"YAML 解析错误: {e}")

        # 检查是否在 frontmatter 前有 markdown 标题
        lines = content.split('\n')
        frontmatter_end = content.find('---', 3) + 3
        before_frontmatter = content[:frontmatter_end]
        if '#' in before_frontmatter:
            errors.append("frontmatter 前不能有 markdown 标题（#）")

    # 检查 _meta.json
    meta_json = os.path.join(skill_path, "_meta.json")
    if not os.path.exists(meta_json):
        errors.append("缺少 _meta.json 文件")
    else:
        try:
            with open(meta_json, 'r', encoding='utf-8') as f:
                meta = json.load(f)

            if 'id' not in meta:
                errors.append("_meta.json 缺少 'id' 字段")
            if 'version' not in meta:
                errors.append("_meta.json 缺少 'version' 字段")

            # 检查版本格式
            if 'version' in meta:
                version = meta['version']
                if not re.match(r'^\d+\.\d+\.\d+$', version):
                    errors.append(f"version 格式错误，应为语义化版本如 1.0.0: {version}")
        except json.JSONDecodeError as e:
            errors.append(f"_meta.json JSON 解析错误: {e}")

    return errors, warnings


def main():
    skill_path = sys.argv[1] if len(sys.argv) > 1 else "."
    errors, warnings = validate_skill(skill_path)

    print("=" * 50)
    print("技能验证结果")
    print("=" * 50)

    if warnings:
        print("\n⚠️  警告:")
        for w in warnings:
            print(f"  - {w}")

    if errors:
        print("\n❌ 错误:")
        for e in errors:
            print(f"  - {e}")
        print("\n验证失败！")
        sys.exit(1)
    else:
        print("\n✅ 验证通过！")
        sys.exit(0)


if __name__ == "__main__":
    main()

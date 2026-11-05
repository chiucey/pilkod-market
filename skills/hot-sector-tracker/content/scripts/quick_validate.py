#!/usr/bin/env python3
"""快速验证脚本 - 检查 SKILL.md 和 _meta.json 结构"""
import os
import json
import re
from pathlib import Path

def validate_skill(skill_path):
    """验证技能文件结构和 frontmatter"""
    issues = []
    warnings = []

    # 检查 SKILL.md 存在
    skill_md = Path(skill_path) / "SKILL.md"
    if not skill_md.exists():
        issues.append("SKILL.md 不存在")
        return issues, warnings

    # 读取 SKILL.md 内容
    content = skill_md.read_text(encoding="utf-8")

    # 检查 frontmatter 格式
    if not content.startswith("---"):
        issues.append("SKILL.md 必须以 --- 开头（frontmatter 开始）")
    else:
        # 提取 frontmatter
        fm_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
        if not fm_match:
            issues.append("无法解析 frontmatter，检查 YAML 格式")
        else:
            fm_text = fm_match.group(1)
            fm = {}
            for line in fm_text.split('\n'):
                if ':' in line:
                    key, val = line.split(':', 1)
                    fm[key.strip()] = val.strip()

            # 检查必填字段
            if 'name' not in fm:
                issues.append("frontmatter 缺少 name 字段")
            if 'description' not in fm:
                issues.append("frontmatter 缺少 description 字段")

            # 检查 name 格式
            if 'name' in fm:
                if not re.match(r'^[a-z0-9-]+$', fm['name']):
                    issues.append(f"name 格式错误: {fm['name']}，应使用小写字母和连字符")

    # 检查 _meta.json
    meta_json = Path(skill_path) / "_meta.json"
    if not meta_json.exists():
        issues.append("_meta.json 不存在")
    else:
        try:
            meta = json.loads(meta_json.read_text(encoding="utf-8"))
            if 'id' not in meta:
                issues.append("_meta.json 缺少 id 字段")
            if 'version' not in meta:
                issues.append("_meta.json 缺少 version 字段")
        except json.JSONDecodeError as e:
            issues.append(f"_meta.json JSON 格式错误: {e}")

    return issues, warnings

if __name__ == "__main__":
    import sys
    skill_path = sys.argv[1] if len(sys.argv) > 1 else "/workspace/temp-skills/hot-sector-tracker"
    issues, warnings = validate_skill(skill_path)

    if issues:
        print("❌ 验证失败:")
        for issue in issues:
            print(f"  - {issue}")
        sys.exit(1)
    else:
        print("✅ 验证通过")
        sys.exit(0)
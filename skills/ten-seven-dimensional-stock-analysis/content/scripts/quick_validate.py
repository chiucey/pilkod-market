#!/usr/bin/env python3
"""
快速验证脚本 - 验证技能结构完整性
"""
import os
import re
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).parent.parent
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
RESET = '\033[0m'

def check(name, condition, error_msg=""):
    """检查并输出结果"""
    if condition:
        print(f"{GREEN}✓{RESET} {name}")
        return True
    else:
        print(f"{RED}✗{RESET} {name}")
        if error_msg:
            print(f"  {YELLOW}→{RESET} {error_msg}")
        return False

def main():
    print("=" * 60)
    print("技能验证检查")
    print("=" * 60)

    all_passed = True

    # 1. 检查 SKILL.md 存在性
    skill_md = SKILL_DIR / "SKILL.md"
    all_passed &= check("SKILL.md 存在", skill_md.exists())

    if skill_md.exists():
        content = skill_md.read_text(encoding='utf-8')

        # 2. 检查 frontmatter 格式
        has_frontmatter_start = content.startswith('---')
        all_passed &= check("Frontmatter 以 --- 开头", has_frontmatter_start)

        # 3. 检查 frontmatter 必填字段
        has_name = bool(re.search(r'^name:\s*\S+', content, re.MULTILINE))
        has_desc = bool(re.search(r'^description:', content, re.MULTILINE))
        all_passed &= check("Frontmatter 包含 name", has_name)
        all_passed &= check("Frontmatter 包含 description", has_desc)

        # 4. 检查 frontmatter 在 markdown 内容之前
        lines = content.split('\n')
        frontmatter_end = -1
        for i, line in enumerate(lines):
            if i > 0 and line == '---':
                frontmatter_end = i
                break
        markdown_after_frontmatter = frontmatter_end > 0 and not lines[frontmatter_end + 1].startswith('#')
        all_passed &= check("Frontmatter 在 markdown 内容之前", markdown_after_frontmatter,
                          "Frontmatter 结束后不应该是 markdown 标题")

        # 5. 检查 name 字段格式（连字符）
        name_match = re.search(r'^name:\s*(.+)', content, re.MULTILINE)
        if name_match:
            name_value = name_match.group(1).strip()
            is_hyphen_case = '-' in name_value or name_value.islower()
            all_passed &= check("name 格式正确（连字符/小写）", is_hyphen_case, f"name='{name_value}'")

        # 6. 检查 description 长度
        desc_match = re.search(r'^description:\s*(.+)', content, re.MULTILINE)
        if desc_match:
            desc_value = desc_match.group(1).strip()
            desc_length_ok = len(desc_value) >= 20
            all_passed &= check("description 长度足够（≥20字符）", desc_length_ok,
                              f"当前长度: {len(desc_value)}")

    # 7. 检查 _meta.json 存在性
    meta_json = SKILL_DIR / "_meta.json"
    all_passed &= check("_meta.json 存在", meta_json.exists())

    if meta_json.exists():
        import json
        try:
            meta = json.loads(meta_json.read_text(encoding='utf-8'))
            has_id = 'id' in meta
            has_version = 'version' in meta
            all_passed &= check("_meta.json 包含 id", has_id)
            all_passed &= check("_meta.json 包含 version", has_version)
        except json.JSONDecodeError as e:
            all_passed = False
            print(f"  {YELLOW}→{RESET} JSON 解析错误: {e}")

    # 8. 检查 references 目录结构
    references_dir = SKILL_DIR / "references"
    if references_dir.exists():
        ref_files = list(references_dir.glob("*.md"))
        all_passed &= check("references 目录包含 markdown 文件", len(ref_files) > 0,
                          f"找到 {len(ref_files)} 个文件")

    # 9. 检查目录名称与 name 一致
    if skill_md.exists():
        name_match = re.search(r'^name:\s*(.+)', content, re.MULTILINE)
        if name_match:
            expected_name = name_match.group(1).strip()
            actual_name = SKILL_DIR.name
            all_passed &= check("目录名称与 frontmatter name 一致",
                              actual_name == expected_name,
                              f"目录='{actual_name}', name='{expected_name}'")

    # 10. 检查路径只包含英文（使用更简单的检查）
    has_chinese = bool(re.search(r'[\u4e00-\u9fff]', SKILL_DIR.name))
    path_ok = not has_chinese
    all_passed &= check("目录路径只包含英文字符", path_ok)

    print("=" * 60)
    if all_passed:
        print(f"{GREEN}✓ 所有检查通过！{RESET}")
        return 0
    else:
        print(f"{RED}✗ 部分检查未通过，请修复后重试！{RESET}")
        return 1

if __name__ == "__main__":
    sys.exit(main())

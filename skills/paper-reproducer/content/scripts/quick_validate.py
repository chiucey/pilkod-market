"""
论文复现技能验证脚本

验证SKILL.md的frontmatter和结构是否符合规范
"""

import os
import sys
import re
import json
from pathlib import Path


def validate_frontmatter(skill_path: str) -> tuple[bool, list[str]]:
    """验证frontmatter格式和必填字段"""
    errors = []
    skill_md = Path(skill_path) / "SKILL.md"
    
    if not skill_md.exists():
        return False, ["SKILL.md not found"]
    
    content = skill_md.read_text(encoding='utf-8')
    
    # 检查第一行是否为frontmatter开始
    lines = content.split('\n')
    if not lines or lines[0].strip() != '---':
        errors.append("Frontmatter must start at the first line with '---'")
        return False, errors
    
    # 找到frontmatter结束标记
    try:
        end_idx = lines[1:].index('---') + 1
    except ValueError:
        errors.append("Frontmatter closing '---' not found")
        return False, errors
    
    # 提取frontmatter内容
    fm_content = '\n'.join(lines[1:end_idx])
    
    # 检查必填字段
    if not re.search(r'^name:\s*.+$', fm_content, re.MULTILINE):
        errors.append("Missing required field: name")
    
    if not re.search(r'^description:\s*.+$', fm_content, re.MULTILINE):
        errors.append("Missing required field: description")
    
    # 检查name格式（连字符格式）
    name_match = re.search(r'^name:\s*(.+)$', fm_content, re.MULTILINE)
    if name_match:
        name = name_match.group(1).strip()
        if not re.match(r'^[a-z0-9-]+$', name):
            errors.append(f"Name must be lowercase with hyphens: '{name}'")
    
    return len(errors) == 0, errors


def validate_meta_json(skill_path: str) -> tuple[bool, list[str]]:
    """验证_meta.json格式"""
    errors = []
    meta_path = Path(skill_path) / "_meta.json"
    
    if not meta_path.exists():
        return False, ["_meta.json not found"]
    
    try:
        meta = json.loads(meta_path.read_text(encoding='utf-8'))
    except json.JSONDecodeError as e:
        return False, [f"Invalid JSON: {e}"]
    
    if 'id' not in meta:
        errors.append("Missing required field: id")
    
    if 'version' not in meta:
        errors.append("Missing required field: version")
    
    return len(errors) == 0, errors


def validate_structure(skill_path: str) -> tuple[bool, list[str]]:
    """验证目录结构"""
    errors = []
    path = Path(skill_path)
    
    # 检查基本结构
    required_files = ['SKILL.md', '_meta.json']
    for f in required_files:
        if not (path / f).exists():
            errors.append(f"Missing required file: {f}")
    
    # 检查可选目录
    optional_dirs = ['scripts', 'references', 'assets']
    for d in optional_dirs:
        dir_path = path / d
        if dir_path.exists() and not dir_path.is_dir():
            errors.append(f"{d} should be a directory")
    
    return len(errors) == 0, errors


def main():
    """主验证流程"""
    if len(sys.argv) < 2:
        print("Usage: python quick_validate.py <skill_path>")
        sys.exit(1)
    
    skill_path = sys.argv[1]
    all_errors = []
    
    # 运行所有验证
    validators = [
        ("Frontmatter", validate_frontmatter),
        ("Meta JSON", validate_meta_json),
        ("Structure", validate_structure),
    ]
    
    all_passed = True
    for name, validator in validators:
        passed, errors = validator(skill_path)
        if not passed:
            all_passed = False
            all_errors.append(f"\n[{name}]")
            for err in errors:
                all_errors.append(f"  - {err}")
    
    # 输出结果
    if all_passed:
        print("✓ All validations passed")
        sys.exit(0)
    else:
        print("✗ Validation failed:")
        for err in all_errors:
            print(err)
        sys.exit(1)


if __name__ == "__main__":
    main()

"""
快速验证脚本 - 检查SKILL.md结构和frontmatter格式
"""

import json
import os
import re
import sys
from pathlib import Path


def validate_frontmatter(skill_path: Path) -> dict:
    """验证SKILL.md的frontmatter格式"""
    skill_md = skill_path / "SKILL.md"

    if not skill_md.exists():
        return {"status": "FAIL", "error": "SKILL.md 不存在"}

    with open(skill_md, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查是否以 --- 开头
    if not content.strip().startswith('---'):
        return {
            "status": "FAIL",
            "error": "SKILL.md 必须以 YAML frontmatter 开头 (---)",
            "line": 1
        }

    # 提取 frontmatter
    parts = content.split('---', 2)
    if len(parts) < 3:
        return {"status": "FAIL", "error": "frontmatter 格式不完整"}

    frontmatter = parts[1]

    # 检查必需字段
    required_fields = ['name', 'description']
    missing = []

    for field in required_fields:
        if not re.search(rf'^{field}:\s*', frontmatter, re.MULTILINE):
            missing.append(field)

    if missing:
        return {"status": "FAIL", "error": f"缺少必需字段: {', '.join(missing)}"}

    # 提取 name 和 description
    name_match = re.search(r'^name:\s*(.+)', frontmatter, re.MULTILINE)
    desc_match = re.search(r'^description:\s*(.+)', frontmatter, re.MULTILINE)

    name = name_match.group(1).strip() if name_match else None
    desc = desc_match.group(1).strip() if desc_match else None

    # 验证 name 格式 (连字符, 英文)
    if name and not re.match(r'^[a-z][a-z0-9-]*$', name):
        return {"status": "WARN", "error": f"name 应使用连字符格式: {name}"}

    return {
        "status": "PASS",
        "name": name,
        "description": desc[:80] + "..." if desc and len(desc) > 80 else desc
    }


def validate_meta_json(skill_path: Path) -> dict:
    """验证 _meta.json 格式"""
    meta_file = skill_path / "_meta.json"

    if not meta_file.exists():
        return {"status": "FAIL", "error": "_meta.json 不存在"}

    try:
        with open(meta_file, 'r', encoding='utf-8') as f:
            meta = json.load(f)
    except json.JSONDecodeError as e:
        return {"status": "FAIL", "error": f"_meta.json JSON格式错误: {e}"}

    required = ['id', 'version']
    missing = [k for k in required if k not in meta]

    if missing:
        return {"status": "FAIL", "error": f"缺少字段: {', '.join(missing)}"}

    # 验证 id 是整数
    if not isinstance(meta['id'], int):
        return {"status": "FAIL", "error": "id 必须是整数"}

    # 验证 version 格式
    if not re.match(r'^\d+\.\d+\.\d+$', meta.get('version', '')):
        return {"status": "WARN", "error": "version 应为语义化版本 (x.y.z)"}

    return {
        "status": "PASS",
        "id": meta['id'],
        "version": meta['version']
    }


def validate_directory_structure(skill_path: Path) -> dict:
    """验证目录结构"""
    required = ['SKILL.md', '_meta.json']
    missing = [f for f in required if not (skill_path / f).exists()]

    if missing:
        return {"status": "FAIL", "error": f"缺少文件: {', '.join(missing)}"}

    # 检查 scripts 目录
    scripts_dir = skill_path / "scripts"
    if scripts_dir.exists():
        scripts = list(scripts_dir.glob("*.py"))
        return {
            "status": "PASS",
            "has_scripts": True,
            "script_count": len(scripts),
            "scripts": [s.name for s in scripts]
        }

    return {"status": "PASS", "has_scripts": False}


def validate_skill(skill_path: str) -> dict:
    """完整验证技能"""
    skill_path = Path(skill_path)

    if not skill_path.exists():
        return {"status": "FAIL", "error": "技能目录不存在"}

    results = {
        "path": str(skill_path),
        "name": skill_path.name,
        "checks": {}
    }

    # 执行各项验证
    results["checks"]["frontmatter"] = validate_frontmatter(skill_path)
    results["checks"]["meta_json"] = validate_meta_json(skill_path)
    results["checks"]["structure"] = validate_directory_structure(skill_path)

    # 综合结果
    all_passed = all(
        check["status"] == "PASS"
        for check in results["checks"].values()
    )

    results["status"] = "PASS" if all_passed else "FAIL"
    return results


def main():
    """主函数"""
    if len(sys.argv) > 1:
        skill_path = sys.argv[1]
    else:
        # 默认检查当前目录下的 temp-skills
        skill_path = "/workspace/temp-skills/sgpjbg-reporter"

    print(f"验证技能: {skill_path}\n")

    results = validate_skill(skill_path)

    print(f"技能名称: {results['name']}")
    print(f"验证结果: {results['status']}\n")

    print("检查项:")
    for check_name, result in results["checks"].items():
        status = result.get("status", "UNKNOWN")
        icon = "✅" if status == "PASS" else ("⚠️" if status == "WARN" else "❌")
        print(f"  {icon} {check_name}: {result.get('error', '通过')}")

    print()
    if results["status"] == "PASS":
        print("✅ 所有验证通过!")
        sys.exit(0)
    else:
        print("❌ 存在验证失败项，请修复后重试")
        sys.exit(1)


if __name__ == "__main__":
    main()
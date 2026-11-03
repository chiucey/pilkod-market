"""
技能验证脚本
检查技能结构和文件完整性
"""

import os
import json
from pathlib import Path


def validate_skill(skill_path: str) -> dict:
    """
    验证技能结构和完整性
    返回验证结果
    """
    results = {
        "passed": True,
        "errors": [],
        "warnings": [],
        "checks": []
    }

    skill_path = Path(skill_path)

    # 检查1: SKILL.md 存在
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        results["passed"] = False
        results["errors"].append("SKILL.md 文件不存在")
    else:
        results["checks"].append("✓ SKILL.md 存在")

        # 检查frontmatter
        with open(skill_md, 'r', encoding='utf-8') as f:
            content = f.read()

        # 检查是否以---开头
        if not content.startswith('---'):
            results["passed"] = False
            results["errors"].append("SKILL.md 必须以 YAML frontmatter 开头（---）")
        else:
            results["checks"].append("✓ SKILL.md frontmatter 格式正确")

        # 提取frontmatter
        import re
        match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
        if match:
            fm_text = match.group(1)
            fm = {}
            for line in fm_text.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    fm[key.strip()] = value.strip()

            # 检查必填字段
            if 'name' not in fm:
                results["passed"] = False
                results["errors"].append("frontmatter 缺少 'name' 字段")
            else:
                results["checks"].append(f"✓ name: {fm['name']}")

                # 检查名称一致性
                if fm['name'] != skill_path.name:
                    results["warnings"].append(f"name 字段 '{fm['name']}' 应与文件夹名称 '{skill_path.name}' 一致")

            if 'description' not in fm:
                results["passed"] = False
                results["errors"].append("frontmatter 缺少 'description' 字段")
            else:
                desc = fm['description']
                if len(desc) < 10:
                    results["warnings"].append("description 过短，建议提供更详细的描述")
                results["checks"].append(f"✓ description: {desc[:50]}...")
        else:
            results["passed"] = False
            results["errors"].append("无法解析 YAML frontmatter")

    # 检查2: _meta.json 存在
    meta_json = skill_path / "_meta.json"
    if not meta_json.exists():
        results["passed"] = False
        results["errors"].append("_meta.json 文件不存在")
    else:
        results["checks"].append("✓ _meta.json 存在")

        try:
            with open(meta_json, 'r', encoding='utf-8') as f:
                meta = json.load(f)

            if 'id' not in meta:
                results["passed"] = False
                results["errors"].append("_meta.json 缺少 'id' 字段")
            else:
                results["checks"].append(f"✓ id: {meta['id']}")

            if 'version' not in meta:
                results["passed"] = False
                results["errors"].append("_meta.json 缺少 'version' 字段")
            else:
                results["checks"].append(f"✓ version: {meta['version']}")
        except json.JSONDecodeError as e:
            results["passed"] = False
            results["errors"].append(f"_meta.json JSON 格式错误: {e}")

    # 检查3: scripts 目录
    scripts_dir = skill_path / "scripts"
    if scripts_dir.exists():
        results["checks"].append("✓ scripts/ 目录存在")
        py_files = list(scripts_dir.glob("*.py"))
        results["checks"].append(f"  - 包含 {len(py_files)} 个 Python 脚本")
    else:
        results["warnings"].append("scripts/ 目录不存在（非必需）")

    # 检查4: references 目录
    refs_dir = skill_path / "references"
    if refs_dir.exists():
        results["checks"].append("✓ references/ 目录存在")
        md_files = list(refs_dir.glob("*.md"))
        results["checks"].append(f"  - 包含 {len(md_files)} 个参考文档")
    else:
        results["warnings"].append("references/ 目录不存在（非必需）")

    # 检查5: 文件命名规范
    for item in skill_path.iterdir():
        if item.is_file():
            if not item.name.startswith('_') and not item.suffix in ['.md', '.json', '.py']:
                results["warnings"].append(f"发现非常规文件: {item.name}")

    return results


def main():
    """主函数"""
    skill_path = "/workspace/temp-skills/a-stock-sector-emotion"

    print("=" * 50)
    print("技能验证报告")
    print("=" * 50)
    print(f"验证路径: {skill_path}\n")

    results = validate_skill(skill_path)

    print("【检查项】")
    for check in results["checks"]:
        print(f"  {check}")

    if results["warnings"]:
        print("\n【警告】")
        for warning in results["warnings"]:
            print(f"  ⚠ {warning}")

    if results["errors"]:
        print("\n【错误】")
        for error in results["errors"]:
            print(f"  ✗ {error}")

    print("\n" + "=" * 50)
    if results["passed"]:
        print("✓ 验证通过")
    else:
        print("✗ 验证失败")
    print("=" * 50)

    return 0 if results["passed"] else 1


if __name__ == "__main__":
    exit(main())

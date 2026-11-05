#!/usr/bin/env python3
"""打包考研调剂技能为 .skill 文件"""

import zipfile
import os
import json
from pathlib import Path

SKILL_DIR = Path(__file__).parent.parent
OUTPUT_DIR = Path("/workspace/temp-skills/dist")

def validate_skill():
    """验证技能结构"""
    errors = []

    # 检查 SKILL.md
    skill_md = SKILL_DIR / "SKILL.md"
    if not skill_md.exists():
        errors.append("SKILL.md 不存在")
    else:
        content = skill_md.read_text(encoding="utf-8")
        if not content.startswith("---"):
            errors.append("SKILL.md 必须以 YAML frontmatter 开头")
        if "name:" not in content:
            errors.append("SKILL.md 缺少 name 字段")
        if "description:" not in content:
            errors.append("SKILL.md 缺少 description 字段")

    # 检查 _meta.json
    meta = SKILL_DIR / "_meta.json"
    if not meta.exists():
        errors.append("_meta.json 不存在")
    else:
        try:
            meta_data = json.loads(meta.read_text(encoding="utf-8"))
            if "id" not in meta_data:
                errors.append("_meta.json 缺少 id 字段")
            if "version" not in meta_data:
                errors.append("_meta.json 缺少 version 字段")
        except json.JSONDecodeError:
            errors.append("_meta.json 格式错误")

    return errors

def package_skill():
    """打包技能"""
    errors = validate_skill()
    if errors:
        print("❌ 验证失败:")
        for e in errors:
            print(f"  - {e}")
        return False

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    skill_name = SKILL_DIR.name
    output_file = OUTPUT_DIR / f"{skill_name}.skill"

    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(SKILL_DIR):
            # 排除 __pycache__ 等
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']

            for file in files:
                if file.startswith('.'):
                    continue
                file_path = Path(root) / file
                arcname = file_path.relative_to(SKILL_DIR)
                zf.write(file_path, arcname)

    print(f"✅ 技能打包成功: {output_file}")
    return str(output_file)

if __name__ == "__main__":
    result = package_skill()
    print(f"\n打包文件路径: {result}")

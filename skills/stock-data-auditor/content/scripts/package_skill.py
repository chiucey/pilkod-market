#!/usr/bin/env python3
"""
股票数据审计技能打包脚本
将技能打包为可发布的.skill文件
"""

import json
import os
import shutil
from pathlib import Path
from datetime import datetime

def package_skill(skill_path: str, output_path: str = None) -> dict:
    """打包技能为.skill文件"""

    skill_name = os.path.basename(skill_path)

    if output_path is None:
        output_path = f"/workspace/temp-skills/{skill_name}.skill"

    # 读取_meta.json
    meta_path = os.path.join(skill_path, '_meta.json')
    with open(meta_path, 'r', encoding='utf-8') as f:
        meta = json.load(f)

    # 读取SKILL.md
    skill_md_path = os.path.join(skill_path, 'SKILL.md')
    with open(skill_md_path, 'r', encoding='utf-8') as f:
        skill_content = f.read()

    # 准备打包内容
    package_data = {
        "meta": meta,
        "skill_content": skill_content,
        "package_info": {
            "name": skill_name,
            "packaged_at": datetime.now().isoformat(),
            "packaged_by": "MiniMax Agent"
        }
    }

    # 添加references（如果存在）
    references_path = os.path.join(skill_path, 'references')
    if os.path.exists(references_path):
        references = {}
        for filename in os.listdir(references_path):
            file_path = os.path.join(references_path, filename)
            if os.path.isfile(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    references[filename] = f.read()
        package_data['references'] = references

    # 添加scripts元数据（不包含实际脚本内容，仅记录）
    scripts_path = os.path.join(skill_path, 'scripts')
    if os.path.exists(scripts_path):
        scripts_meta = []
        for filename in os.listdir(scripts_path):
            if filename.endswith('.py'):
                scripts_meta.append(filename)
        package_data['scripts'] = scripts_meta

    # 保存为.skill文件
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(package_data, f, ensure_ascii=False, indent=2)

    return {
        "success": True,
        "output_path": output_path,
        "skill_id": meta['id'],
        "version": meta['version']
    }

def main():
    skill_path = "/workspace/temp-skills/stock-data-auditor"
    output_path = "/workspace/temp-skills/stock-data-auditor.skill"

    print("=" * 50)
    print("股票数据审计技能 - 打包")
    print("=" * 50)

    result = package_skill(skill_path, output_path)

    if result['success']:
        print(f"\n✓ 技能打包成功！")
        print(f"  技能ID: {result['skill_id']}")
        print(f"  版本: {result['version']}")
        print(f"  输出文件: {result['output_path']}")

        # 显示文件大小
        file_size = os.path.getsize(result['output_path'])
        print(f"  文件大小: {file_size} bytes")
    else:
        print(f"\n✗ 打包失败: {result.get('error', '未知错误')}")
        return 1

    return 0

if __name__ == "__main__":
    exit(main())

#!/usr/bin/env python3
"""
简历优化专家技能打包脚本
生成.skill文件用于分发部署
"""

import os
import json
import zipfile
from pathlib import Path
from datetime import datetime

SKILL_ROOT = Path("/workspace/temp-skills/ji-si-2026-resume-optimizer-v25")
OUTPUT_DIR = Path("/workspace/temp-skills")

def validate_before_pack():
    """打包前验证"""
    # 读取_meta.json验证
    meta_path = SKILL_ROOT / "_meta.json"
    with open(meta_path, 'r', encoding='utf-8') as f:
        meta = json.load(f)

    # 验证必需字段
    if 'id' not in meta:
        raise ValueError("缺少id字段")
    if 'version' not in meta:
        raise ValueError("缺少version字段")

    # 验证SKILL.md存在
    skill_path = SKILL_ROOT / "SKILL.md"
    if not skill_path.exists():
        raise ValueError("SKILL.md不存在")

    print(f"✓ 技能ID: {meta['id']}")
    print(f"✓ 技能版本: {meta['version']}")
    print(f"✓ 技能名称: {meta.get('name', '未定义')}")

    return meta

def package_skill():
    """打包技能"""
    print("=" * 50)
    print("简历优化专家技能打包")
    print("=" * 50)

    # 验证
    print("\n[1] 验证技能配置...")
    meta = validate_before_pack()

    # 生成输出文件名
    skill_name = meta.get('name', 'unnamed-skill')
    version = meta.get('version', '1.0.0')
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    output_file = OUTPUT_DIR / f"{skill_name}_v{version}_{timestamp}.skill"

    # 创建zip包
    print(f"\n[2] 创建技能包...")
    print(f"    输出: {output_file}")

    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(SKILL_ROOT):
            # 排除__pycache__等
            dirs[:] = [d for d in dirs if not d.startswith('.')]

            for file in files:
                if file.startswith('.'):
                    continue

                file_path = Path(root) / file
                arcname = file_path.relative_to(SKILL_ROOT)
                zf.write(file_path, arcname)
                print(f"    + {arcname}")

    # 验证包内容
    print(f"\n[3] 验证包内容...")
    with zipfile.ZipFile(output_file, 'r') as zf:
        file_count = len(zf.namelist())
        print(f"    ✓ 包含 {file_count} 个文件")

    print("\n" + "=" * 50)
    print(f"✓ 打包完成: {output_file.name}")
    print("=" * 50)

    return output_file

if __name__ == "__main__":
    package_skill()

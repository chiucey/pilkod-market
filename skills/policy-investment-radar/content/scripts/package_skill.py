#!/usr/bin/env python3
"""
政策投资机会雷达技能打包脚本
将技能打包为可分发的 .skill 文件
"""

import os
import json
import shutil
import zipfile
from datetime import datetime

def package_skill(skill_path: str, output_dir: str = "/workspace/temp-skills/dist"):
    """打包技能为 .skill 文件"""

    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)

    # 读取元数据
    meta_path = os.path.join(skill_path, "_meta.json")
    with open(meta_path, "r", encoding="utf-8") as f:
        meta = json.load(f)

    skill_id = meta.get("id", "unknown")
    version = meta.get("version", "1.0.0")
    skill_name = os.path.basename(skill_path)

    # 生成打包文件名
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    output_file = os.path.join(output_dir, f"{skill_name}_{version}.skill")

    # 创建 zip 文件
    with zipfile.ZipFile(output_file, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(skill_path):
            # 跳过空目录
            if not files and not dirs:
                continue

            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, os.path.dirname(skill_path))
                zipf.write(file_path, arcname)
                print(f"  + {arcname}")

    print(f"\n✅ 技能打包完成: {output_file}")
    return output_file


def main():
    skill_path = "/workspace/temp-skills/policy-investment-radar"

    print("=" * 50)
    print("政策投资机会雷达 - 技能打包")
    print("=" * 50)

    output = package_skill(skill_path)

    print("\n打包摘要:")
    print(f"  技能名称: policy-investment-radar")
    print(f"  技能 ID: policy-investment-radar-001")
    print(f"  版本: 1.0.0")
    print(f"  输出文件: {output}")

    return output


if __name__ == "__main__":
    main()

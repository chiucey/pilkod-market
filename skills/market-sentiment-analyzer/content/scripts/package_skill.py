#!/usr/bin/env python3
"""
市场情绪分析技能 - 打包脚本
将技能打包为 .skill 文件用于分发
"""

import os
import zipfile
import json
from pathlib import Path
from datetime import datetime

SKILL_DIR = Path(__file__).parent.parent
OUTPUT_DIR = Path(__file__).parent.parent.parent / "skill_packages"

def validate_before_pack():
    """打包前验证"""
    # 检查必需文件
    required_files = ["SKILL.md", "_meta.json"]
    for filename in required_files:
        file_path = SKILL_DIR / filename
        if not file_path.exists():
            print(f"❌ 缺少必需文件: {filename}")
            return False

    # 检查 _meta.json
    meta = json.loads((SKILL_DIR / "_meta.json").read_text(encoding="utf-8"))
    if "id" not in meta or "version" not in meta:
        print("❌ _meta.json 必须包含 id 和 version")
        return False

    return True

def get_package_name():
    """生成包名"""
    meta = json.loads((SKILL_DIR / "_meta.json").read_text(encoding="utf-8"))
    name = meta.get("name", SKILL_DIR.name)
    version = meta.get("version", "1.0.0")
    return f"{name}_{version}.skill"

def create_package():
    """创建 .skill 包"""
    global OUTPUT_DIR

    if not validate_before_pack():
        print("❌ 打包前验证失败")
        return False

    # 创建输出目录
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # 生成包名
    package_name = get_package_name()
    package_path = OUTPUT_DIR / package_name

    # 创建 zip 包
    with zipfile.ZipFile(package_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for file_path in SKILL_DIR.rglob("*"):
            if file_path.is_file():
                # 排除临时文件和隐藏文件
                if file_path.name.startswith("."):
                    continue
                arcname = file_path.relative_to(SKILL_DIR)
                zf.write(file_path, arcname)
                print(f"  📦 添加: {arcname}")

    print(f"✅ 技能包已创建: {package_path}")
    print(f"   路径: {package_path.absolute()}")
    return True

def main():
    print(f"📦 打包技能: {SKILL_DIR.name}")
    print("=" * 50)

    if create_package():
        print("=" * 50)
        print("✅ 打包成功！")
        return 0
    else:
        print("=" * 50)
        print("❌ 打包失败")
        return 1

if __name__ == "__main__":
    exit(main())

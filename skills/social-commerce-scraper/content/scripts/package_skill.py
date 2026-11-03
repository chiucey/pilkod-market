#!/usr/bin/env python3
"""
社交电商热销商品抓取技能 - 打包脚本
将技能打包为可分发的.skill文件
"""

import os
import json
import shutil
import sys
from pathlib import Path
from datetime import datetime

SKILL_DIR = Path(__file__).parent.parent
OUTPUT_DIR = Path("/workspace/temp-skills/output")
RED = '\033[91m'
GREEN = '\033[92m'
RESET = '\033[0m'

def log_error(msg):
    print(f"{RED}✗ {msg}{RESET}")

def log_success(msg):
    print(f"{GREEN}✓ {msg}{RESET}")

def validate_before_pack():
    """打包前验证"""
    # 验证SKILL.md
    skill_md = SKILL_DIR / "SKILL.md"
    if not skill_md.exists():
        log_error("SKILL.md 不存在")
        return False

    # 验证_meta.json
    meta_json = SKILL_DIR / "_meta.json"
    if not meta_json.exists():
        log_error("_meta.json 不存在")
        return False

    return True

def get_skill_info():
    """获取技能信息"""
    meta_file = SKILL_DIR / "_meta.json"
    with open(meta_file, 'r', encoding='utf-8') as f:
        meta = json.load(f)

    skill_md = SKILL_DIR / "SKILL.md"
    with open(skill_md, 'r', encoding='utf-8') as f:
        content = f.read()

    import re
    name_match = re.search(r'^name:\s*(.+)', content, re.MULTILINE)
    name = name_match.group(1).strip() if name_match else "unknown"

    return {
        "name": name,
        "id": meta.get("id", "unknown"),
        "version": meta.get("version", "1.0.0")
    }

def create_package():
    """创建技能包"""
    if not validate_before_pack():
        return False

    # 创建输出目录
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # 获取技能信息
    skill_info = get_skill_info()
    output_name = f"{skill_info['name']}.skill"
    output_path = OUTPUT_DIR / output_name

    # 清理旧文件
    if output_path.exists():
        output_path.unlink()

    # 打包文件
    import zipfile
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(SKILL_DIR):
            # 排除output目录
            if 'output' in root:
                continue

            for file in files:
                # 排除Python缓存文件
                if file.endswith('.pyc') or file == '__pycache__':
                    continue

                file_path = Path(root) / file
                arcname = file_path.relative_to(SKILL_DIR)
                zipf.write(file_path, arcname)

    log_success(f"技能包已创建: {output_path}")

    # 显示包内容
    print("\n打包内容:")
    with zipfile.ZipFile(output_path, 'r') as zipf:
        for name in sorted(zipf.namelist()):
            info = zipf.getinfo(name)
            size = info.file_size
            print(f"  - {name} ({size} bytes)")

    print(f"\n技能信息:")
    print(f"  名称: {skill_info['name']}")
    print(f"  ID: {skill_info['id']}")
    print(f"  版本: {skill_info['version']}")
    print(f"  路径: {output_path}")

    return True

def main():
    print("=" * 50)
    print("社交电商热销商品抓取技能 - 打包工具")
    print("=" * 50)
    print()

    if create_package():
        log_success("打包完成！")
        return 0
    else:
        log_error("打包失败")
        return 1

if __name__ == "__main__":
    sys.exit(main())

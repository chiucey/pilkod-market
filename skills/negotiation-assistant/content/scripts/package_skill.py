#!/usr/bin/env python3
"""
打包谈判助手技能为 .skill 文件
"""

import os
import zipfile
import json
import time
from pathlib import Path
from datetime import datetime

SKILL_DIR = Path("/workspace/temp-skills/negotiation-assistant")
OUTPUT_DIR = Path("/workspace/temp-skills")

# 最小有效时间戳 (1980-01-01 00:00:00)
MIN_TIMESTAMP = 315532800

def safe_add_to_zip(zf, file_path, arcname):
    """安全添加到zip，处理旧时间戳问题"""
    # 确保arcname是字符串
    arcname_str = str(arcname)
    # 获取文件时间戳
    mtime = os.path.getmtime(file_path)
    # 如果时间戳在1980年之前，使用最小有效时间戳
    if mtime < MIN_TIMESTAMP:
        # 创建带有效时间戳的ZipInfo
        info = zipfile.ZipInfo(arcname_str)
        info.date_time = (1980, 1, 1, 0, 0, 0)
        with open(file_path, 'rb') as f:
            zf.writestr(info, f.read())
    else:
        zf.write(file_path, arcname_str)

def package_skill():
    print("=== 打包谈判助手技能 ===\n")

    # 确保输出目录存在
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # 生成打包文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = OUTPUT_DIR / f"negotiation-assistant_{timestamp}.skill"

    # 创建 zip 包
    print("1. 创建技能包...")
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(SKILL_DIR):
            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(SKILL_DIR)
                # 跳过 scripts 目录（内部工具）
                if not str(arcname).startswith('scripts/'):
                    safe_add_to_zip(zf, file_path, arcname)
                    print(f"   + {arcname}")

    print(f"\n2. 技能包已创建: {output_file}")

    # 验证包内容
    print("\n3. 验证包内容...")
    with zipfile.ZipFile(output_file, 'r') as zf:
        files = zf.namelist()
        print(f"   包含 {len(files)} 个文件:")
        for f in files:
            print(f"   - {f}")

    # 检查必需文件
    required = ['SKILL.md', '_meta.json']
    for req in required:
        if req not in files:
            print(f"\n❌ 错误: 缺少必需文件 {req}")
            return False

    print("\n✅ 打包完成!")
    print(f"\n技能包路径: {output_file}")
    return True

if __name__ == "__main__":
    import sys
    success = package_skill()
    sys.exit(0 if success else 1)
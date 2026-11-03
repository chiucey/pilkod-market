#!/usr/bin/env python3
"""
初中生试卷分析技能 - 打包脚本
将技能打包为可分发的 .skill 文件
"""

import os
import shutil
import json
from pathlib import Path
from datetime import datetime

def package_skill():
    """打包技能为 .skill 文件"""
    skill_dir = Path("/workspace/temp-skills/middle-school-paper-analyzer")
    output_dir = Path("/workspace/temp-skills")

    # 读取meta信息
    meta_file = skill_dir / "_meta.json"
    with open(meta_file, "r", encoding="utf-8") as f:
        meta = json.load(f)

    # 生成输出文件名
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    output_name = f"middle-school-paper-analyzer_v{meta['version']}_{timestamp}.skill"
    output_path = output_dir / output_name

    # 创建临时打包目录
    temp_dir = output_dir / f"_temp_{timestamp}"
    temp_dir.mkdir(exist_ok=True)

    # 复制文件（排除隐藏文件和临时文件）
    skip_patterns = [".DS_Store", "__pycache__", "*.pyc", ".git"]

    for item in skill_dir.rglob("*"):
        if item.is_file():
            # 检查是否应该跳过
            should_skip = False
            for pattern in skip_patterns:
                if pattern.startswith("*"):
                    if item.name.endswith(pattern[1:]):
                        should_skip = True
                        break
                else:
                    if pattern in str(item):
                        should_skip = True
                        break

            if not should_skip:
                # 保持相对路径结构
                relative = item.relative_to(skill_dir)
                dest = temp_dir / relative
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(item, dest)

    # 创建打包文件（使用zip格式）
    shutil.make_archive(
        str(temp_dir),
        'zip',
        root_dir=temp_dir
    )

    # 重命名为.skill文件
    zip_path = output_dir / f"{temp_dir.name}.zip"
    shutil.move(str(zip_path), str(output_path))

    # 清理临时目录
    shutil.rmtree(temp_dir)

    print("=" * 50)
    print("初中生试卷分析技能 - 打包完成")
    print("=" * 50)
    print(f"📦 打包文件: {output_path}")
    print(f"📄 版本: {meta['version']}")
    print(f"🆔 技能ID: {meta['id']}")
    print("=" * 50)

    return str(output_path)

if __name__ == "__main__":
    package_skill()

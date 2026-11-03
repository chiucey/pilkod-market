#!/usr/bin/env python3
"""
股票量化资金参与度分析技能 - 打包脚本
生成 .skill 分发包
"""

import os
import shutil
import zipfile
from pathlib import Path
from datetime import datetime

def package_skill(skill_path):
    """打包技能为 .skill 文件"""
    skill_path = Path(skill_path)

    # 创建打包输出目录
    output_dir = Path("/workspace/temp-skills/dist")
    output_dir.mkdir(parents=True, exist_ok=True)

    # 生成输出文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    skill_name = skill_path.name
    output_file = output_dir / f"{skill_name}_{timestamp}.skill"

    # 创建 zip 包
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(skill_path):
            # 跳过 __pycache__ 和 .git
            dirs[:] = [d for d in dirs if d not in ['__pycache__', '.git', '.pytest_cache']]

            for file in files:
                if file.endswith('.pyc'):
                    continue

                file_path = Path(root) / file
                arcname = file_path.relative_to(skill_path.parent)
                zipf.write(file_path, arcname)

    print(f"✅ 技能打包成功: {output_file}")
    print(f"📦 包大小: {output_file.stat().st_size / 1024:.2f} KB")

    # 显示包含的文件
    print("\n📁 打包内容:")
    with zipfile.ZipFile(output_file, 'r') as zipf:
        for name in sorted(zipf.namelist()):
            info = zipf.getinfo(name)
            print(f"   - {name} ({info.file_size} bytes)")

    return str(output_file)

def main():
    skill_path = Path(__file__).parent.parent
    output_path = package_skill(skill_path)
    print(f"\n✨ 打包完成！")
    print(f"📍 技能文件位置: {output_path}")

if __name__ == "__main__":
    main()

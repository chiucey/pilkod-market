#!/usr/bin/env python3
"""股票自动盯盘技能打包脚本"""

import os
import json
import shutil
from pathlib import Path
from datetime import datetime

def package_skill():
    """打包技能为.skill文件"""

    skill_dir = Path("/workspace/temp-skills/stock-auto-monitor")
    output_dir = Path("/workspace/temp-skills")

    # 1. 读取meta信息
    meta_file = skill_dir / "_meta.json"
    if not meta_file.exists():
        print("❌ _meta.json不存在")
        return False

    meta = json.loads(meta_file.read_text(encoding="utf-8"))
    skill_name = meta.get('id', skill_dir.name)
    version = meta.get('version', '1.0.0')

    # 2. 创建打包输出目录
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    package_name = f"{skill_name}_v{version}_{timestamp}.skill"
    package_path = output_dir / package_name

    # 3. 创建临时打包目录
    temp_dir = output_dir / f"_temp_package_{timestamp}"
    temp_skill_dir = temp_dir / skill_dir.name
    temp_skill_dir.mkdir(parents=True)

    try:
        # 4. 复制文件（排除临时文件和隐藏文件）
        for item in skill_dir.iterdir():
            if item.name.startswith('.') or item.name.startswith('_'):
                continue
            if item.is_file():
                shutil.copy2(item, temp_skill_dir / item.name)
            elif item.is_dir():
                shutil.copytree(item, temp_skill_dir / item.name)

        # 5. 创建.zip归档
        shutil.make_archive(str(temp_dir), 'zip', str(temp_dir))

        # 6. 重命名为.skill
        zip_file = str(temp_dir) + '.zip'
        shutil.move(zip_file, str(package_path))

        # 7. 清理临时目录
        shutil.rmtree(temp_dir)

        print(f"✅ 技能打包成功: {package_path}")
        print(f"📦 打包文件: {package_path.name}")
        return True

    except Exception as e:
        print(f"❌ 打包失败: {e}")
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
        return False

if __name__ == "__main__":
    package_skill()

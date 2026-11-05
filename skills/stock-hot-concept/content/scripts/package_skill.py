#!/usr/bin/env python3
"""
股票热点概念技能打包脚本
将技能打包为可分发的.skill文件
"""

import os
import json
import shutil
import zipfile
from pathlib import Path
from datetime import datetime


class SkillPackager:
    def __init__(self, skill_path: str):
        self.skill_path = Path(skill_path)
        self.output_dir = Path('/workspace/temp-skills')
        self.exclude_patterns = [
            '__pycache__',
            '*.pyc',
            '.git',
            '.DS_Store',
            '*.log'
        ]

    def package(self) -> str:
        """打包技能并返回产物路径"""
        skill_name = self.skill_path.name

        # 创建打包目录
        package_dir = self.output_dir / 'package_temp'
        if package_dir.exists():
            shutil.rmtree(package_dir)
        package_dir.mkdir(parents=True)

        # 复制技能文件
        for item in self.skill_path.rglob('*'):
            if item.is_file():
                # 检查是否应该排除
                if any(pattern in str(item) for pattern in self.exclude_patterns):
                    continue

                # 计算相对路径
                rel_path = item.relative_to(self.skill_path)
                dest_path = package_dir / rel_path

                # 确保目录存在
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(item, dest_path)

        # 读取meta信息
        meta_path = self.skill_path / '_meta.json'
        with open(meta_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)

        # 创建.skill文件（本质上是zip）
        skill_file = self.output_dir / f"{skill_name}.skill"
        if skill_file.exists():
            skill_file.unlink()

        with zipfile.ZipFile(skill_file, 'w', zipfile.ZIP_DEFLATED) as zf:
            for item in package_dir.rglob('*'):
                if item.is_file():
                    arcname = item.relative_to(package_dir)
                    zf.write(item, arcname)

        # 清理临时目录
        shutil.rmtree(package_dir)

        # 生成打包报告
        report = f"""
{'='*50}
技能打包完成
{'='*50}
技能名称: {skill_name}
技能ID: {meta.get('id', 'N/A')}
版本: {meta.get('version', '1.0.0')}
打包时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
产物路径: {skill_file}
{'='*50}
"""
        print(report)
        return str(skill_file)


def main():
    import sys

    if len(sys.argv) > 1:
        skill_path = sys.argv[1]
    else:
        skill_path = os.path.dirname(os.path.abspath(__file__))
        skill_path = os.path.dirname(skill_path)

    packager = SkillPackager(skill_path)
    output_path = packager.package()
    print(f"\n打包成功: {output_path}")


if __name__ == '__main__':
    main()

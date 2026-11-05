"""
技能打包器 - 将技能打包为 .skill 文件
Skill Packager - Package skill as .skill file
"""

import os
import sys
import json
import shutil
import zipfile
from pathlib import Path
from datetime import datetime
from typing import List, Optional


class SkillPackager:
    """技能打包器"""

    def __init__(self, skill_path: str, output_dir: Optional[str] = None):
        """
        初始化打包器

        Args:
            skill_path: 技能目录路径
            output_dir: 输出目录，默认为 skill_path 的父目录
        """
        self.skill_path = Path(skill_path).resolve()
        self.output_dir = Path(output_dir) if output_dir else self.skill_path.parent

        if not self.skill_path.exists():
            raise FileNotFoundError(f"技能目录不存在: {skill_path}")

        if not self.skill_path.is_dir():
            raise NotADirectoryError(f"路径不是目录: {skill_path}")

    def get_skill_metadata(self) -> dict:
        """
        获取技能元数据

        Returns:
            元数据字典
        """
        meta_path = self.skill_path / '_meta.json'

        if not meta_path.exists():
            raise FileNotFoundError("_meta.json 文件不存在")

        with open(meta_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def get_skill_name(self) -> str:
        """
        获取技能名称

        Returns:
            技能名称
        """
        skill_md = self.skill_path / 'SKILL.md'

        if not skill_md.exists():
            raise FileNotFoundError("SKILL.md 文件不存在")

        with open(skill_md, 'r', encoding='utf-8') as f:
            content = f.read()

        # 提取 name
        import re
        name_match = re.search(r'^name:\s*(.+)$', content, re.MULTILINE)

        if name_match:
            return name_match.group(1).strip()

        raise ValueError("无法从 SKILL.md 提取 name")

    def collect_files(self) -> List[Path]:
        """
        收集需要打包的文件

        Returns:
            文件路径列表
        """
        files = []

        # 收集所有文件
        exclude_patterns = [
            '__pycache__',
            '*.pyc',
            '.git',
            '.DS_Store',
            '*.egg-info'
        ]

        for item in self.skill_path.rglob('*'):
            if item.is_file():
                # 检查是否应该排除
                should_exclude = False
                for pattern in exclude_patterns:
                    if pattern in str(item):
                        should_exclude = True
                        break

                if not should_exclude:
                    # 计算相对路径
                    rel_path = item.relative_to(self.skill_path)
                    files.append((item, rel_path))

        return files

    def validate_package_content(self, files: List) -> bool:
        """
        验证打包内容

        Args:
            files: 文件列表

        Returns:
            是否有效
        """
        file_names = [f[1].name for f in files]

        # 必须包含的文件
        required = ['SKILL.md', '_meta.json']
        for req in required:
            if req not in file_names:
                print(f"错误: 缺少必需文件: {req}")
                return False

        return True

    def package(self) -> str:
        """
        执行打包

        Returns:
            输出文件路径
        """
        print(f"开始打包技能: {self.skill_path}")
        print()

        # 获取元数据
        try:
            meta = self.get_skill_metadata()
            skill_name = self.get_skill_name()
        except Exception as e:
            print(f"错误: {e}")
            raise

        # 收集文件
        files = self.collect_files()
        print(f"收集到 {len(files)} 个文件/目录")

        # 验证内容
        if not self.validate_package_content(files):
            raise ValueError("打包内容验证失败")

        # 生成输出文件名
        version = meta.get('version', '1.0.0')
        output_name = f"{skill_name}_{version}.skill"
        output_path = self.output_dir / output_name

        # 如果文件已存在，先删除
        if output_path.exists():
            output_path.unlink()

        # 创建 ZIP 包
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for abs_path, rel_path in files:
                zf.write(abs_path, rel_path)
                print(f"  + {rel_path}")

        print()
        print(f"打包完成: {output_path}")
        print(f"文件大小: {output_path.stat().st_size / 1024:.2f} KB")

        return str(output_path)

    def verify_package(self, package_path: str) -> bool:
        """
        验证包内容

        Args:
            package_path: 包文件路径

        Returns:
            是否有效
        """
        print()
        print("验证包内容...")

        try:
            with zipfile.ZipFile(package_path, 'r') as zf:
                file_list = zf.namelist()

                # 检查必需文件
                required = ['SKILL.md', '_meta.json']
                for req in required:
                    if req not in file_list:
                        print(f"错误: 包内缺少 {req}")
                        return False

                # 检查脚本文件
                scripts_dir = 'scripts/'
                has_scripts = any(f.startswith(scripts_dir) for f in file_list)
                if not has_scripts:
                    print("警告: 包内没有 scripts 目录")

                print(f"包内文件数: {len(file_list)}")
                print("验证通过")

            return True

        except zipfile.BadZipFile:
            print("错误: 无效的 ZIP 文件")
            return False


def main():
    """主函数"""
    if len(sys.argv) < 2:
        skill_path = os.getcwd()
    else:
        skill_path = sys.argv[1]

    print("=" * 60)
    print("技能打包器")
    print("=" * 60)
    print()

    try:
        packager = SkillPackager(skill_path)
        output_path = packager.package()
        packager.verify_package(output_path)

        print()
        print("=" * 60)
        print("打包成功!")
        print("=" * 60)

    except Exception as e:
        print()
        print("=" * 60)
        print(f"打包失败: {e}")
        print("=" * 60)
        sys.exit(1)


if __name__ == "__main__":
    main()

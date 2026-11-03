"""
技能打包脚本 - 将足球评测技能打包为可分发的 .skill 文件

此脚本将技能目录打包为标准的 .skill 归档文件。
"""

import os
import json
import zipfile
import sys
from pathlib import Path
from datetime import datetime
from typing import Tuple, List, Dict
import sys
from pathlib import Path
from datetime import datetime


class SkillPackager:
    """技能打包器"""

    def __init__(self, skill_dir: str):
        self.skill_dir = Path(skill_dir)
        self.skill_name = self.skill_dir.name
        self.output_file = None

    def validate_structure(self) -> Tuple[bool, List[str]]:
        """
        验证技能目录结构

        Returns:
            (是否有效, 错误列表)
        """
        errors = []

        # 检查基本文件
        required_files = ['SKILL.md', '_meta.json']
        for filename in required_files:
            filepath = self.skill_dir / filename
            if not filepath.exists():
                errors.append(f"缺少必需文件: {filename}")

        # 验证 SKILL.md frontmatter
        skill_md = self.skill_dir / 'SKILL.md'
        if skill_md.exists():
            with open(skill_md, 'r', encoding='utf-8') as f:
                content = f.read()

            # 检查是否以 --- 开头
            if not content.strip().startswith('---'):
                errors.append("SKILL.md 必须以 YAML frontmatter 开头（第一行为 ---）")

            # 检查必需字段
            if 'name:' not in content:
                errors.append("SKILL.md frontmatter 缺少 name 字段")
            if 'description:' not in content:
                errors.append("SKILL.md frontmatter 缺少 description 字段")

        # 验证 _meta.json
        meta_json = self.skill_dir / '_meta.json'
        if meta_json.exists():
            try:
                with open(meta_json, 'r', encoding='utf-8') as f:
                    meta = json.load(f)

                if 'id' not in meta:
                    errors.append("_meta.json 缺少 id 字段")
                if 'version' not in meta:
                    errors.append("_meta.json 缺少 version 字段")
            except json.JSONDecodeError as e:
                errors.append(f"_meta.json 格式错误: {e}")

        return len(errors) == 0, errors

    def create_package(self) -> str:
        """
        创建技能包

        Returns:
            输出文件路径
        """
        # 验证结构
        valid, errors = self.validate_structure()
        if not valid:
            raise ValueError(f"技能目录结构无效:\n" + "\n".join(f"  - {e}" for e in errors))

        # 生成输出文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = self.skill_dir.parent / f"{self.skill_name}_{timestamp}.skill"

        # 创建 ZIP 包
        with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
            for root, dirs, files in os.walk(self.skill_dir):
                # 排除隐藏文件和目录
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                files = [f for f in files if not f.startswith('.')]

                for file in files:
                    file_path = Path(root) / file
                    arcname = file_path.relative_to(self.skill_dir)
                    zf.write(file_path, arcname)

        self.output_file = str(output_file)
        return self.output_file

    def get_package_info(self) -> Dict:
        """
        获取包信息

        Returns:
            包信息字典
        """
        meta_json = self.skill_dir / '_meta.json'
        with open(meta_json, 'r', encoding='utf-8') as f:
            meta = json.load(f)

        # 统计文件
        file_count = sum(1 for root, dirs, files in os.walk(self.skill_dir)
                        for f in files if not f.startswith('.'))

        return {
            'name': self.skill_name,
            'id': meta.get('id'),
            'version': meta.get('version'),
            'files_count': file_count,
            'output': self.output_file
        }


def main():
    """主函数 - 命令行入口"""
    if len(sys.argv) < 2:
        print("使用方法: python package_skill.py <skill_directory>")
        sys.exit(1)

    skill_dir = sys.argv[1]

    if not os.path.isdir(skill_dir):
        print(f"错误: 目录不存在 - {skill_dir}")
        sys.exit(1)

    try:
        packager = SkillPackager(skill_dir)
        output_file = packager.create_package()
        info = packager.get_package_info()

        print("\n=== 打包成功 ===")
        print(f"技能名称: {info['name']}")
        print(f"技能 ID: {info['id']}")
        print(f"版本: {info['version']}")
        print(f"文件数量: {info['files_count']}")
        print(f"输出文件: {output_file}")

    except ValueError as e:
        print(f"\n错误: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n打包失败: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()

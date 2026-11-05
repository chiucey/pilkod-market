#!/usr/bin/env python3
"""
技能打包器 (Skill Packager)
将技能打包为 .skill 文件用于分发
"""

import os
import sys
import json
import shutil
import zipfile
from pathlib import Path
from datetime import datetime


class SkillPackager:
    def __init__(self, skill_path: str):
        self.skill_path = Path(skill_path)
        self.skill_name = self.skill_path.name
        self.output_dir = Path("/workspace/temp-skills/packages")
        self.exclude_patterns = [
            '__pycache__',
            '*.pyc',
            '.git',
            '.DS_Store',
            '*.log',
            '.env',
            'node_modules',
        ]

    def package(self) -> str:
        """打包技能"""
        print(f"📦 正在打包技能: {self.skill_name}\n")

        # 验证技能结构
        if not self.validate():
            raise Exception("技能验证失败")

        # 创建输出目录
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # 生成输出文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.output_dir / f"{self.skill_name}_{timestamp}.skill"

        # 创建zip包
        with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
            for root, dirs, files in os.walk(self.skill_path):
                # 过滤目录
                dirs[:] = [d for d in dirs if not self.should_exclude(d)]

                for file in files:
                    if self.should_exclude(file):
                        continue

                    file_path = Path(root) / file
                    arcname = file_path.relative_to(self.skill_path.parent)
                    zf.write(file_path, arcname)
                    print(f"  + {arcname}")

        print(f"\n✅ 打包完成: {output_file}")
        return str(output_file)

    def validate(self) -> bool:
        """验证技能"""
        print("🔍 验证技能结构...")

        # 检查SKILL.md
        skill_md = self.skill_path / "SKILL.md"
        if not skill_md.exists():
            print(f"  ❌ SKILL.md 不存在")
            return False
        print("  ✅ SKILL.md 存在")

        # 检查_meta.json
        meta_json = self.skill_path / "_meta.json"
        if not meta_json.exists():
            print(f"  ⚠️ _meta.json 不存在 (建议添加)")
        else:
            print("  ✅ _meta.json 存在")

        # 验证frontmatter
        with open(skill_md, 'r', encoding='utf-8') as f:
            content = f.read()

        if not content.startswith('---'):
            print("  ❌ SKILL.md 必须以 frontmatter 开头")
            return False

        print("  ✅ Frontmatter 格式正确")

        return True

    def should_exclude(self, name: str) -> bool:
        """检查是否应该排除"""
        for pattern in self.exclude_patterns:
            if pattern.startswith('*'):
                if name.endswith(pattern[1:]):
                    return True
            elif pattern in name:
                return True
        return False


def main():
    """主函数"""
    if len(sys.argv) < 2:
        # 默认打包当前技能
        skill_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    else:
        skill_path = sys.argv[1]

    try:
        packager = SkillPackager(skill_path)
        output_file = packager.package()
        print(f"\n📦 输出文件: {output_file}")
    except Exception as e:
        print(f"\n❌ 打包失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

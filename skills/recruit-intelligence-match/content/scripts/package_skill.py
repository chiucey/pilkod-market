#!/usr/bin/env python3
"""
技能打包脚本 - 生成可分发的 .skill 文件
"""

import os
import sys
import zipfile
import json
import tarfile
from pathlib import Path
from datetime import datetime


class SkillPackager:
    """技能打包器"""

    def __init__(self, skill_path: str):
        self.skill_path = Path(skill_path)
        self.skill_name = self.skill_path.name

    def validate_for_packaging(self) -> bool:
        """打包前验证"""
        # 检查必需文件
        required = ["SKILL.md", "_meta.json"]
        for file in required:
            if not (self.skill_path / file).exists():
                print(f"❌ 缺少必需文件: {file}")
                return False

        # 检查 meta.json 有效性
        try:
            meta = json.loads((self.skill_path / "_meta.json").read_text())
            if "id" not in meta or "version" not in meta:
                print("❌ _meta.json 必须包含 id 和 version")
                return False
        except Exception as e:
            print(f"❌ _meta.json 解析失败: {e}")
            return False

        return True

    def package(self, output_dir: str = None) -> str:
        """
        打包技能

        Args:
            output_dir: 输出目录，默认与技能同目录

        Returns:
            打包文件路径
        """
        if not self.validate_for_packaging():
            raise ValueError("打包验证失败")

        output_dir = Path(output_dir) if output_dir else self.skill_path.parent
        output_dir.mkdir(parents=True, exist_ok=True)

        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        skill_id = json.loads((self.skill_path / "_meta.json").read_text()).get("id", "unknown")
        output_file = output_dir / f"{self.skill_name}_{skill_id}_{timestamp}.skill"

        # 创建 tar.gz 归档
        print(f"📦 打包技能: {self.skill_name}")

        with tarfile.open(output_file, "w:gz") as tar:
            # 添加技能目录中的所有文件
            for root, dirs, files in os.walk(self.skill_path):
                for file in files:
                    file_path = Path(root) / file
                    # 跳过临时文件和隐藏文件
                    if file.startswith('.') or file.endswith('.pyc'):
                        continue

                    arcname = file_path.relative_to(self.skill_path.parent)
                    tar.add(file_path, arcname=arcname)
                    print(f"  + {arcname}")

        print(f"\n✅ 打包完成: {output_file}")
        print(f"   文件大小: {output_file.stat().st_size / 1024:.1f} KB")

        return str(output_file)

    def extract(self, package_path: str, output_dir: str = None) -> str:
        """
        解包技能

        Args:
            package_path: 打包文件路径
            output_dir: 输出目录

        Returns:
            解压后的技能目录
        """
        package_path = Path(package_path)
        output_dir = Path(output_dir) if output_dir else Path.cwd()

        print(f"📂 解包技能: {package_path}")

        with tarfile.open(package_path, "r:gz") as tar:
            tar.extractall(output_dir)

        # 找到解压后的技能目录
        for item in output_dir.iterdir():
            if item.is_dir() and (item / "SKILL.md").exists():
                print(f"✅ 解压完成: {item}")
                return str(item)

        raise ValueError("解包失败，未找到 SKILL.md")


def main():
    if len(sys.argv) < 2:
        print("用法: python package_skill.py <skill_path> [output_dir]")
        print("示例: python package_skill.py /workspace/temp-skills/recruit-intelligence-match")
        sys.exit(1)

    skill_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None

    packager = SkillPackager(skill_path)

    try:
        output_file = packager.package(output_dir)
        print(f"\n📤 技能已打包，可分发给用户")
    except Exception as e:
        print(f"\n❌ 打包失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
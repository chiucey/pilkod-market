#!/usr/bin/env python3
"""
A股主力博弈分析系统 - 技能打包脚本
将技能目录打包为 .skill 文件用于发布
"""

import json
import os
import zipfile
import sys
from pathlib import Path


class SkillPacker:
    def __init__(self, skill_dir: str):
        self.skill_dir = Path(skill_dir)
        self.skill_name = self.skill_dir.name

    def validate_before_pack(self) -> bool:
        """打包前验证"""
        # 检查 SKILL.md
        if not (self.skill_dir / "SKILL.md").exists():
            print("❌ Error: SKILL.md not found")
            return False

        # 检查 _meta.json
        if not (self.skill_dir / "_meta.json").exists():
            print("❌ Error: _meta.json not found")
            return False

        # 验证 _meta.json 格式
        try:
            with open(self.skill_dir / "_meta.json", 'r', encoding='utf-8') as f:
                meta = json.load(f)
            if 'id' not in meta or 'version' not in meta:
                print("❌ Error: _meta.json must contain 'id' and 'version'")
                return False
        except Exception as e:
            print(f"❌ Error: Invalid _meta.json: {e}")
            return False

        return True

    def pack(self, output_dir: str = None) -> str:
        """打包技能为 .skill 文件"""
        if not self.validate_before_pack():
            sys.exit(1)

        # 获取版本号
        with open(self.skill_dir / "_meta.json", 'r', encoding='utf-8') as f:
            meta = json.load(f)
        version = meta.get('version', '1.0.0')

        # 确定输出目录
        if output_dir:
            output_path = Path(output_dir)
        else:
            output_path = self.skill_dir.parent

        output_path.mkdir(parents=True, exist_ok=True)

        # 生成输出文件名
        output_file = output_path / f"{self.skill_name}.skill"

        # 创建 .clawhub 目录和 origin.json
        clawhub_dir = self.skill_dir / ".clawhub"
        clawhub_dir.mkdir(exist_ok=True)

        origin_data = {
            "version": 1,
            "registry": "https://clawhub.ai",
            "slug": self.skill_name,
            "installedVersion": version,
            "installedAt": 0
        }
        with open(clawhub_dir / "origin.json", 'w', encoding='utf-8') as f:
            json.dump(origin_data, f, indent=2, ensure_ascii=False)

        # 打包为 .skill 文件
        with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
            for file_path in self.skill_dir.rglob('*'):
                if file_path.is_file():
                    # 排除隐藏文件和临时文件
                    if any(part.startswith('.') for part in file_path.parts):
                        continue
                    arcname = file_path.relative_to(self.skill_dir)
                    # 设置合理的修改时间，避免1980年前时间戳导致ZIP错误
                    info = zipfile.ZipInfo(str(arcname), date_time=(2024, 1, 1, 0, 0, 0))
                    with open(file_path, 'rb') as f:
                        zf.writestr(info, f.read())

        print("=" * 60)
        print("SKILL PACKAGE REPORT")
        print("=" * 60)
        print(f"Skill name: {self.skill_name}")
        print(f"Version: {version}")
        print(f"Output file: {output_file}")
        print(f"File size: {output_file.stat().st_size:,} bytes")
        print()

        # 列出打包内容
        print("Package contents:")
        with zipfile.ZipFile(output_file, 'r') as zf:
            for name in sorted(zf.namelist()):
                info = zf.getinfo(name)
                print(f"  {name} ({info.file_size:,} bytes)")

        print("=" * 60)
        print("✅ Package created successfully!")
        print("=" * 60)

        return str(output_file)


def main():
    if len(sys.argv) < 2:
        print("Usage: python package_skill.py <skill-directory> [output-directory]")
        sys.exit(1)

    skill_dir = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None

    packer = SkillPacker(skill_dir)
    output_file = packer.pack(output_dir)

    print(f"\n📦 Skill package: {output_file}")


if __name__ == "__main__":
    main()
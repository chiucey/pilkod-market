#!/usr/bin/env python3
"""
简历优化技能打包脚本

将技能文件夹打包为可分发的 .skill 文件。
"""

import os
import sys
import json
import shutil
import zipfile
from pathlib import Path
from datetime import datetime


class SkillPacker:
    """技能打包器"""

    def __init__(self, skill_dir: str, output_dir: str = None):
        self.skill_dir = Path(skill_dir)
        self.output_dir = Path(output_dir) if output_dir else self.skill_dir.parent

        if not self.skill_dir.exists():
            raise ValueError(f"技能目录不存在: {skill_dir}")

        self.skill_name = self.skill_dir.name

    def validate(self) -> bool:
        """
        验证技能包是否符合打包要求

        Returns:
            验证是否通过
        """
        errors = []

        # 检查必需文件
        required_files = ["SKILL.md", "_meta.json"]
        for filename in required_files:
            filepath = self.skill_dir / filename
            if not filepath.exists():
                errors.append(f"缺少必需文件: {filename}")

        # 检查 _meta.json 格式
        meta_path = self.skill_dir / "_meta.json"
        if meta_path.exists():
            try:
                with open(meta_path, "r", encoding="utf-8") as f:
                    meta = json.load(f)

                if "id" not in meta:
                    errors.append("_meta.json 缺少 id 字段")
                if "version" not in meta:
                    errors.append("_meta.json 缺少 version 字段")

            except json.JSONDecodeError as e:
                errors.append(f"_meta.json 格式错误: {e}")

        # 检查 SKILL.md frontmatter
        skill_md_path = self.skill_dir / "SKILL.md"
        if skill_md_path.exists():
            content = skill_md_path.read_text(encoding="utf-8")
            if not content.startswith("---"):
                errors.append("SKILL.md 必须以 YAML frontmatter 开头")

        if errors:
            print("❌ 验证失败:")
            for error in errors:
                print(f"  - {error}")
            return False

        print("✅ 验证通过")
        return True

    def pack(self, output_filename: str = None) -> str:
        """
        打包技能为 .skill 文件

        Args:
            output_filename: 输出文件名，默认使用 技能名-版本.skill

        Returns:
            输出文件路径
        """
        if not self.validate():
            raise ValueError("技能验证失败，无法打包")

        # 获取版本号
        meta_path = self.skill_dir / "_meta.json"
        with open(meta_path, "r", encoding="utf-8") as f:
            meta = json.load(f)

        version = meta.get("version", "1.0.0")

        # 生成输出文件名
        if not output_filename:
            timestamp = datetime.now().strftime("%Y%m%d")
            output_filename = f"{self.skill_name}-v{version}-{timestamp}.skill"

        output_path = self.output_dir / output_filename

        # 创建 .skill 文件（本质是 zip）
        with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for root, dirs, files in os.walk(self.skill_dir):
                # 跳过隐藏文件和目录
                dirs[:] = [d for d in dirs if not d.startswith('.')]

                for file in files:
                    if file.startswith('.'):
                        continue

                    file_path = Path(root) / file
                    arcname = file_path.relative_to(self.skill_dir)

                    # 记录打包内容
                    print(f"  📦 添加: {arcname}")
                    zf.write(file_path, arcname)

        print(f"\n✅ 技能包已生成: {output_path}")
        print(f"   文件大小: {output_path.stat().st_size / 1024:.1f} KB")

        return str(output_path)

    def unpack(self, skill_file: str, output_dir: str = None):
        """
        解包 .skill 文件

        Args:
            skill_file: .skill 文件路径
            output_dir: 输出目录，默认解压到 .skill 文件同目录下
        """
        skill_file = Path(skill_file)

        if not skill_file.exists():
            raise ValueError(f"技能包文件不存在: {skill_file}")

        if output_dir:
            target_dir = Path(output_dir)
        else:
            # 解压到同目录下的 skill_name 文件夹
            target_dir = skill_file.parent / skill_file.stem

        # 解压
        with zipfile.ZipFile(skill_file, "r") as zf:
            zf.extractall(target_dir)

        print(f"✅ 技能已解压到: {target_dir}")
        return str(target_dir)

    def list_contents(self, skill_file: str = None):
        """
        列出技能包内容

        Args:
            skill_file: .skill 文件路径，如果为None则列出目录内容
        """
        if skill_file:
            # 列出 .skill 文件内容
            skill_file = Path(skill_file)
            if not skill_file.exists():
                print(f"文件不存在: {skill_file}")
                return

            print(f"📦 技能包: {skill_file.name}\n")

            with zipfile.ZipFile(skill_file, "r") as zf:
                for info in zf.infolist():
                    size = info.file_size / 1024
                    print(f"  {info.filename:<40} {size:>8.1f} KB")

        else:
            # 列出目录内容
            print(f"📁 技能目录: {self.skill_dir}\n")

            for root, dirs, files in os.walk(self.skill_dir):
                level = root.replace(str(self.skill_dir), "").count(os.sep)
                indent = "  " * level

                dir_name = Path(root).name
                if level > 0:  # 不显示根目录
                    print(f"{indent}📂 {dir_name}/")

                subindent = "  " * (level + 1)
                for file in files:
                    if not file.startswith('.'):
                        file_path = Path(root) / file
                        size = file_path.stat().st_size / 1024
                        print(f"{subindent}📄 {file:<30} {size:>8.1f} KB")


def main():
    if len(sys.argv) < 2:
        print("""
简历优化技能打包工具

用法:
  python package_skill.py <skill-dir>           # 打包技能
  python package_skill.py <skill-dir> --unpack   # 解包示例
  python package_skill.py <skill-dir> --list      # 列出内容

示例:
  python package_skill.py /workspace/temp-skills/resume-optimizer
  python package_skill.py /workspace/temp-skills/resume-optimizer --list
        """)
        sys.exit(1)

    skill_dir = sys.argv[1]
    packer = SkillPacker(skill_dir)

    # 检查命令
    if len(sys.argv) >= 3:
        command = sys.argv[2]
        if command == "--list":
            packer.list_contents()
        elif command == "--unpack":
            packer.unpack(packer.output_dir / f"{packer.skill_name}.skill")
        else:
            print(f"未知命令: {command}")
            sys.exit(1)
    else:
        # 默认打包
        output_path = packer.pack()
        print(f"\n📦 技能包已准备就绪，可以分发了。")


if __name__ == "__main__":
    main()

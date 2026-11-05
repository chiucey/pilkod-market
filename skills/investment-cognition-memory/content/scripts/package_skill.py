#!/usr/bin/env python3
"""
投资认知记忆系统 - 打包脚本
将技能打包为 .skill 文件
"""

import os
import json
import shutil
import zipfile
from datetime import datetime
from pathlib import Path

# 技能目录
SKILL_DIR = "/workspace/temp-skills/investment-cognition-memory"

# 输出目录
OUTPUT_DIR = "/workspace/temp-skills/output"

# 打包文件
PACKAGE_NAME = "investment-cognition-memory-1.0.0.skill"

class SkillPacker:
    """技能打包器"""

    def __init__(self):
        self.skill_dir = Path(SKILL_DIR)
        self.output_dir = Path(OUTPUT_DIR)
        self.errors = []
        self.warnings = []

    def validate_structure(self) -> bool:
        """验证技能目录结构"""
        print("检查技能目录结构...")

        # 检查必需文件
        required_files = [
            "SKILL.md",
            "_meta.json"
        ]

        for file in required_files:
            file_path = self.skill_dir / file
            if not file_path.exists():
                self.errors.append(f"缺少必需文件: {file}")
            else:
                print(f"  ✓ {file}")

        # 检查目录结构
        expected_dirs = ["references", "scripts"]
        for dir_name in expected_dirs:
            dir_path = self.skill_dir / dir_name
            if not dir_path.exists():
                self.warnings.append(f"缺少目录: {dir_name}")
            else:
                print(f"  ✓ {dir_name}/")

        return len(self.errors) == 0

    def validate_meta(self) -> bool:
        """验证元数据文件"""
        print("\n验证 _meta.json...")

        meta_path = self.skill_dir / "_meta.json"
        if not meta_path.exists():
            return False

        try:
            with open(meta_path, 'r', encoding='utf-8') as f:
                meta = json.load(f)

            # 检查必需字段
            required_fields = ["id", "version", "name", "description"]
            for field in required_fields:
                if field not in meta:
                    self.errors.append(f"_meta.json 缺少字段: {field}")
                else:
                    print(f"  ✓ {field}: {meta[field]}")

            # 验证字段类型
            if not isinstance(meta.get("id"), (int, str)):
                self.errors.append("_meta.json 的 id 必须是数字或字符串")

            if not isinstance(meta.get("version"), str):
                self.errors.append("_meta.json 的 version 必须是字符串")

            if len(meta.get("name", "")) > 64:
                self.warnings.append("name 字段超过64字符限制")

            return len(self.errors) == 0

        except json.JSONDecodeError as e:
            self.errors.append(f"_meta.json 格式错误: {e}")
            return False

    def validate_frontmatter(self) -> bool:
        """验证 SKILL.md frontmatter"""
        print("\n验证 SKILL.md frontmatter...")

        skill_path = self.skill_dir / "SKILL.md"
        if not skill_path.exists():
            self.errors.append("SKILL.md 不存在")
            return False

        with open(skill_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 检查是否以 frontmatter 开头
        if not content.startswith('---'):
            self.errors.append("SKILL.md 必须以 YAML frontmatter 开头（---）")
            return False

        # 提取 frontmatter
        lines = content.split('\n')
        frontmatter_lines = []
        in_frontmatter = False

        for i, line in enumerate(lines):
            if line.strip() == '---' and not in_frontmatter:
                in_frontmatter = True
                continue
            elif line.strip() == '---' and in_frontmatter:
                frontmatter_lines = lines[1:i]
                break

        if not frontmatter_lines:
            self.errors.append("无法解析 YAML frontmatter")
            return False

        # 解析 frontmatter 内容
        frontmatter = {}
        for line in frontmatter_lines:
            if ':' in line:
                key, value = line.split(':', 1)
                frontmatter[key.strip()] = value.strip()

        # 检查必需字段
        required_fields = ["name", "description"]
        for field in required_fields:
            if field not in frontmatter:
                self.errors.append(f"SKILL.md frontmatter 缺少字段: {field}")
            else:
                print(f"  ✓ {field}: {frontmatter[field][:50]}...")

        # 验证 frontmatter 位置（在任何标题之前）
        first_title = content.find('#')
        first_frontmatter_end = content.find('---', 4) + 3

        if first_title < first_frontmatter_end and first_title != -1:
            self.errors.append("SKILL.md frontmatter 后不应紧跟标题")

        return len(self.errors) == 0

    def create_package(self) -> str:
        """创建技能包"""
        print("\n创建技能包...")

        # 确保输出目录存在
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # 打包文件路径
        package_path = self.output_dir / PACKAGE_NAME

        # 创建 zip 文件
        with zipfile.ZipFile(package_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for root, dirs, files in os.walk(self.skill_dir):
                # 排除 __pycache__ 等目录
                dirs[:] = [d for d in dirs if not d.startswith('__')]

                for file in files:
                    if file.endswith('.pyc'):
                        continue

                    file_path = Path(root) / file
                    arcname = file_path.relative_to(self.skill_dir)
                    zf.write(file_path, arcname)
                    print(f"  + {arcname}")

        print(f"\n✓ 技能包已创建: {package_path}")
        return str(package_path)

    def generate_report(self) -> str:
        """生成打包报告"""
        report = []
        report.append("=" * 60)
        report.append("投资认知记忆系统 - 打包报告")
        report.append("=" * 60)
        report.append(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"技能目录: {self.skill_dir}")
        report.append(f"打包状态: {'成功' if not self.errors else '失败'}")
        report.append("")

        if self.errors:
            report.append("错误:")
            for error in self.errors:
                report.append(f"  ✗ {error}")
            report.append("")

        if self.warnings:
            report.append("警告:")
            for warning in self.warnings:
                report.append(f"  ⚠ {warning}")
            report.append("")

        return "\n".join(report)

    def run(self) -> bool:
        """执行打包流程"""
        print("=" * 60)
        print("投资认知记忆系统 - 打包工具")
        print("=" * 60)
        print()

        # 验证
        self.validate_structure()
        self.validate_meta()
        self.validate_frontmatter()

        if self.errors:
            print("\n" + self.generate_report())
            return False

        # 打包
        package_path = self.create_package()

        # 完成
        print("\n" + "=" * 60)
        print("打包完成！")
        print("=" * 60)
        print(f"技能包: {package_path}")

        return True


def main():
    """命令行入口"""
    packer = SkillPacker()
    success = packer.run()
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())

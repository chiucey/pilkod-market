#!/usr/bin/env python3
"""
技能打包脚本 - PRD 生成器技能
Skill Packaging Script - PRD Generator Skill
"""

import os
import sys
import json
import zipfile
import re
from pathlib import Path
from datetime import datetime


class SkillValidator:
    """技能验证器"""

    def __init__(self, skill_path):
        self.skill_path = Path(skill_path)
        self.errors = []
        self.warnings = []
        self.skill_name = self.skill_path.name

    def validate_frontmatter(self):
        """验证 SKILL.md frontmatter"""
        skill_md = self.skill_path / "SKILL.md"
        if not skill_md.exists():
            self.errors.append("SKILL.md 文件不存在")
            return False

        with open(skill_md, 'r', encoding='utf-8') as f:
            content = f.read()

        if not content.startswith('---'):
            self.errors.append("SKILL.md 必须以 --- 开头 (frontmatter 必须在第一行)")
            return False

        lines = content.split('\n')
        if len(lines) < 3:
            self.errors.append("SKILL.md 文件过短")
            return False

        # 查找 frontmatter 边界
        frontmatter_start = -1
        frontmatter_end = -1
        for i, line in enumerate(lines):
            if line.strip() == '---' and frontmatter_start == -1:
                frontmatter_start = i
            elif line.strip() == '---' and frontmatter_start >= 0 and frontmatter_end == -1:
                frontmatter_end = i
                break

        if frontmatter_start == -1 or frontmatter_end == -1:
            self.errors.append("SKILL.md 缺少 frontmatter 分隔符 ---")
            return False

        frontmatter_lines = lines[frontmatter_start + 1:frontmatter_end]
        frontmatter_text = '\n'.join(frontmatter_lines)

        # 检查必需字段
        if not re.search(r'^name:\s*.+', frontmatter_text, re.MULTILINE):
            self.errors.append("frontmatter 缺少 'name' 字段")

        if not re.search(r'^description:\s*.+', frontmatter_text, re.MULTILINE):
            self.errors.append("frontmatter 缺少 'description' 字段")

        # 检查 name 字段值是否与文件夹名匹配
        name_match = re.search(r'^name:\s*(.+)', frontmatter_text, re.MULTILINE)
        if name_match:
            frontmatter_name = name_match.group(1).strip()
            if frontmatter_name != self.skill_name:
                self.errors.append(f"name 字段值 '{frontmatter_name}' 与文件夹名 '{self.skill_name}' 不匹配")

        return len(self.errors) == 0

    def validate_meta_json(self):
        """验证 _meta.json"""
        meta_json = self.skill_path / "_meta.json"
        if not meta_json.exists():
            self.errors.append("_meta.json 文件不存在")
            return False

        try:
            with open(meta_json, 'r', encoding='utf-8') as f:
                meta = json.load(f)
        except json.JSONDecodeError as e:
            self.errors.append(f"_meta.json 格式错误: {e}")
            return False

        if 'id' not in meta:
            self.errors.append("_meta.json 缺少 'id' 字段")
        if 'version' not in meta:
            self.errors.append("_meta.json 缺少 'version' 字段")

        if 'id' in meta and not isinstance(meta['id'], int):
            self.errors.append("_meta.json 中 'id' 必须是整数")

        return len(self.errors) == 0

    def validate_structure(self):
        """验证目录结构"""
        required_files = ['SKILL.md', '_meta.json']
        for f in required_files:
            if not (self.skill_path / f).exists():
                self.errors.append(f"缺少必需文件: {f}")

        scripts_dir = self.skill_path / "scripts"
        if scripts_dir.exists():
            for f in scripts_dir.iterdir():
                if f.is_file() and not f.name.startswith('.'):
                    self.warnings.append(f"发现脚本: {f.name}")

        return len(self.errors) == 0

    def validate_all(self):
        """执行所有验证"""
        print(f"🔍 开始验证技能: {self.skill_name}")
        print("-" * 50)

        self.validate_structure()
        self.validate_frontmatter()
        self.validate_meta_json()

        if self.errors:
            print("❌ 验证失败:")
            for err in self.errors:
                print(f"   - {err}")
            return False

        print("✅ 验证通过!")
        if self.warnings:
            print("📋 提示:")
            for warn in self.warnings:
                print(f"   - {warn}")
        return True


class SkillPackager:
    """技能打包器"""

    def __init__(self, skill_path, output_dir=None):
        self.skill_path = Path(skill_path)
        self.output_dir = Path(output_dir) if output_dir else Path(".")
        self.skill_name = self.skill_path.name

    def check_dangerous_files(self, archive_path):
        """检查归档中是否有危险文件"""
        dangerous_patterns = [
            r'\.env$',
            r'\.pem$',
            r'\.key$',
            r'id_rsa',
            r'password',
            r'secret',
            r'\.git/'
        ]

        with zipfile.ZipFile(archive_path, 'r') as zf:
            for name in zf.namelist():
                for pattern in dangerous_patterns:
                    if re.search(pattern, name, re.IGNORECASE):
                        print(f"⚠️  警告: 发现可能敏感的文件: {name}")

    def package(self):
        """打包技能"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = self.output_dir / f"{self.skill_name}_{timestamp}.skill"

        print(f"\n📦 开始打包技能: {self.skill_name}")
        print("-" * 50)

        try:
            with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
                for root, dirs, files in os.walk(self.skill_path):
                    dirs[:] = [d for d in dirs if not d.startswith('.')]
                    files = [f for f in files if not f.startswith('.')]

                    for file in files:
                        file_path = Path(root) / file
                        arcname = file_path.relative_to(self.skill_path)
                        zf.write(file_path, arcname)
                        print(f"   + {arcname}")

            print("-" * 50)
            self.check_dangerous_files(output_file)

            with zipfile.ZipFile(output_file, 'r') as zf:
                print(f"\n📁 归档内容 ({len(zf.namelist())} 个文件):")
                for name in sorted(zf.namelist()):
                    print(f"   - {name}")

            print(f"\n✅ 打包完成!")
            print(f"   输出文件: {output_file.absolute()}")
            print(f"   文件大小: {output_file.stat().st_size / 1024:.2f} KB")

            return str(output_file.absolute())

        except Exception as e:
            print(f"❌ 打包失败: {e}")
            return None


def main():
    if len(sys.argv) < 2:
        print("用法: python package_skill.py <skill_path> [output_dir]")
        print("示例: python package_skill.py /workspace/temp-skills/prd-generator")
        sys.exit(1)

    skill_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None

    validator = SkillValidator(skill_path)
    if not validator.validate_all():
        sys.exit(1)

    packager = SkillPackager(skill_path, output_dir)
    output_file = packager.package()

    if output_file:
        print(f"\n🎉 技能打包成功!")
        print(f"\n下一步:")
        print(f"   1. 测试技能功能")
        print(f"   2. 发布到社区")


if __name__ == "__main__":
    main()

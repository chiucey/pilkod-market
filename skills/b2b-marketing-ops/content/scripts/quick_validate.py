#!/usr/bin/env python3
"""
B2B市场营销技能验证脚本
验证技能结构、frontmatter、命名规范等
"""

import os
import sys
import json
import re
from pathlib import Path


class SkillValidator:
    def __init__(self, skill_path: str):
        self.skill_path = Path(skill_path)
        self.errors = []
        self.warnings = []

    def validate_all(self) -> bool:
        """执行所有验证检查"""
        print(f"🔍 开始验证技能: {self.skill_path.name}")
        print("=" * 50)

        # 1. 验证目录结构
        self.validate_structure()

        # 2. 验证SKILL.md
        self.validate_skill_md()

        # 3. 验证_meta.json
        self.validate_meta_json()

        # 4. 验证命名规范
        self.validate_naming()

        # 5. 验证路径安全
        self.validate_security()

        # 输出结果
        self.print_results()

        return len(self.errors) == 0

    def validate_structure(self):
        """验证目录结构"""
        print("\n📁 检查目录结构...")

        required_files = ['SKILL.md', '_meta.json']
        for file in required_files:
            file_path = self.skill_path / file
            if file_path.exists():
                print(f"  ✅ {file} 存在")
            else:
                self.errors.append(f"缺少必需文件: {file}")
                print(f"  ❌ {file} 缺失")

    def validate_skill_md(self):
        """验证SKILL.md"""
        print("\n📄 检查 SKILL.md...")

        skill_md = self.skill_path / 'SKILL.md'
        if not skill_md.exists():
            self.errors.append("SKILL.md 文件不存在")
            return

        content = skill_md.read_text(encoding='utf-8')

        # 检查frontmatter必须在第一行
        if not content.startswith('---'):
            self.errors.append("SKILL.md 必须以 YAML frontmatter 开始")
            print("  ❌ frontmatter 未在第一行")
        else:
            print("  ✅ frontmatter 在第一行")

        # 解析frontmatter
        if content.startswith('---'):
            end_match = re.search(r'^---', content[3:], re.MULTILINE)
            if end_match:
                frontmatter = content[3:3 + end_match.start()]
                self.validate_frontmatter(frontmatter)
            else:
                self.errors.append("无法解析 YAML frontmatter")

    def validate_frontmatter(self, frontmatter: str):
        """验证frontmatter内容"""
        required_fields = ['name', 'description']

        for field in required_fields:
            pattern = rf'^{field}:\s*'
            if re.search(pattern, frontmatter, re.MULTILINE):
                print(f"  ✅ {field} 字段存在")
            else:
                self.errors.append(f"缺少必需字段: {field}")
                print(f"  ❌ {field} 字段缺失")

        # 检查name格式
        name_match = re.search(r'^name:\s*(.+)', frontmatter, re.MULTILINE)
        if name_match:
            name = name_match.group(1).strip()
            if len(name) > 64:
                self.warnings.append(f"name 长度 ({len(name)}) 超过64字符限制")
            if not re.match(r'^[a-z0-9-]+$', name):
                self.errors.append(f"name 必须使用小写字母、数字和连字符: {name}")

    def validate_meta_json(self):
        """验证_meta.json"""
        print("\n📋 检查 _meta.json...")

        meta_json = self.skill_path / '_meta.json'
        if not meta_json.exists():
            self.errors.append("_meta.json 文件不存在")
            return

        try:
            data = json.loads(meta_json.read_text(encoding='utf-8'))

            required_fields = ['id', 'version']
            for field in required_fields:
                if field in data:
                    print(f"  ✅ {field} 字段存在")
                else:
                    self.errors.append(f"缺少必需字段: {field}")
                    print(f"  ❌ {field} 字段缺失")

            # 验证id类型
            if 'id' in data and isinstance(data['id'], int):
                print(f"  ✅ id 为整数: {data['id']}")
            elif 'id' in data:
                self.warnings.append(f"id 建议使用整数类型")

            # 验证version格式
            if 'version' in data:
                version = data['version']
                if re.match(r'^\d+\.\d+\.\d+$', version):
                    print(f"  ✅ version 格式正确: {version}")
                else:
                    self.warnings.append(f"version 建议使用语义化版本格式: x.y.z")

        except json.JSONDecodeError as e:
            self.errors.append(f"_meta.json JSON解析失败: {e}")
        except Exception as e:
            self.errors.append(f"_meta.json 读取失败: {e}")

    def validate_naming(self):
        """验证命名规范"""
        print("\n🏷️ 检查命名规范...")

        skill_name = self.skill_path.name

        # 检查文件夹名称
        if re.match(r'^[a-z0-9-]+$', skill_name):
            print(f"  ✅ 文件夹名称规范: {skill_name}")
        else:
            self.errors.append(f"文件夹名称必须使用小写字母、数字和连字符: {skill_name}")
            print(f"  ❌ 文件夹名称不规范: {skill_name}")

        # 检查文件路径中是否有非ASCII字符
        for root, dirs, files in os.walk(self.skill_path):
            for d in dirs:
                if not re.match(r'^[a-zA-Z0-9_-]+$', d):
                    self.errors.append(f"目录名称包含非ASCII字符: {d}")
            for f in files:
                if not re.match(r'^[a-zA-Z0-9_.-]+$', f):
                    self.errors.append(f"文件名称包含非ASCII字符: {f}")

    def validate_security(self):
        """验证安全性"""
        print("\n🔒 检查安全规范...")

        # 检查是否有符号链接逃逸
        for root, dirs, files in os.walk(self.skill_path, followlinks=False):
            for name in dirs + files:
                path = Path(root) / name
                if path.is_symlink():
                    target = path.resolve()
                    if not str(target).startswith(str(self.skill_path)):
                        self.errors.append(f"符号链接逃逸: {path} -> {target}")
                        print(f"  ❌ 符号链接逃逸: {path}")

        # 检查是否有敏感文件
        sensitive_patterns = ['.env', '.pem', '.key', 'credentials', 'secrets']
        for root, dirs, files in os.walk(self.skill_path):
            for f in files:
                if any(pattern in f.lower() for pattern in sensitive_patterns):
                    self.warnings.append(f"发现潜在敏感文件: {f}")
                    print(f"  ⚠️ 敏感文件: {f}")

        print("  ✅ 安全检查完成")

    def print_results(self):
        """输出验证结果"""
        print("\n" + "=" * 50)
        print("📊 验证结果汇总")
        print("=" * 50)

        if self.errors:
            print(f"\n❌ 错误 ({len(self.errors)}):")
            for error in self.errors:
                print(f"   • {error}")

        if self.warnings:
            print(f"\n⚠️ 警告 ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"   • {warning}")

        if not self.errors and not self.warnings:
            print("\n✅ 所有检查通过!")
        elif not self.errors:
            print("\n✅ 无阻塞错误，但有警告需要关注")
        else:
            print("\n❌ 存在错误，请修复后重试")


def main():
    if len(sys.argv) < 2:
        # 默认检查当前目录下的技能
        skill_path = Path(__file__).parent.parent
    else:
        skill_path = Path(sys.argv[1])

    validator = SkillValidator(skill_path)
    success = validator.validate_all()

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()

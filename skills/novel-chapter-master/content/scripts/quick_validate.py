#!/usr/bin/env python3
"""
快速验证脚本 - 验证技能结构和质量门槛
Quick validation script for skill quality gates
"""

import os
import re
import json
import sys
from pathlib import Path


class SkillValidator:
    """技能验证器"""

    def __init__(self, skill_path: str):
        self.skill_path = Path(skill_path)
        self.errors = []
        self.warnings = []
        self.passed = []

    def validate_all(self) -> bool:
        """运行所有验证"""
        print(f"\n{'='*60}")
        print(f"技能验证开始: {self.skill_path.name}")
        print(f"{'='*60}\n")

        # 执行各项验证
        self.check_structure()
        self.check_frontmatter()
        self.check_meta_json()
        self.check_naming()
        self.check_content_quality()

        # 输出结果
        self.print_results()

        return len(self.errors) == 0

    def check_structure(self):
        """检查目录结构"""
        print("📁 检查目录结构...")

        required_files = ['SKILL.md', '_meta.json']
        required_dirs = []

        for f in required_files:
            if not (self.skill_path / f).exists():
                self.errors.append(f"缺少必需文件: {f}")
            else:
                self.passed.append(f"✓ {f} 存在")

        for d in required_dirs:
            if not (self.skill_path / d).is_dir():
                self.warnings.append(f"建议添加目录: {d}")
            else:
                self.passed.append(f"✓ {d}/ 目录存在")

    def check_frontmatter(self):
        """检查Frontmatter格式"""
        print("\n📋 检查Frontmatter...")

        skill_md = self.skill_path / 'SKILL.md'
        if not skill_md.exists():
            self.errors.append("SKILL.md 不存在")
            return

        content = skill_md.read_text(encoding='utf-8')

        # 检查是否以 --- 开头
        if not content.startswith('---'):
            self.errors.append("SKILL.md 必须以 --- 开头（Frontmatter）")
            return

        # 提取frontmatter
        lines = content.split('\n')
        if len(lines) < 3:
            self.errors.append("Frontmatter 格式不正确")
            return

        # 找到结束标记
        end_idx = -1
        for i, line in enumerate(lines[1:], 1):
            if line.strip() == '---':
                end_idx = i
                break

        if end_idx == -1:
            self.errors.append("缺少 Frontmatter 结束标记 ---")
            return

        frontmatter_text = '\n'.join(lines[1:end_idx])

        # 检查必需字段
        required_fields = ['name', 'description']
        for field in required_fields:
            pattern = rf'^{field}:\s*.+$'
            if not re.search(pattern, frontmatter_text, re.MULTILINE):
                self.errors.append(f"Frontmatter 缺少必需字段: {field}")
            else:
                self.passed.append(f"✓ {field} 字段存在")

        # 检查name格式
        name_match = re.search(r'^name:\s*(.+)$', frontmatter_text, re.MULTILINE)
        if name_match:
            name = name_match.group(1).strip()
            if not re.match(r'^[a-z0-9\-]+$', name):
                self.errors.append(f"name 必须使用连字符格式: {name}")
            elif len(name) > 64:
                self.errors.append(f"name 长度不能超过64字符: {len(name)}")
            else:
                self.passed.append(f"✓ name 格式正确: {name}")

    def check_meta_json(self):
        """检查_meta.json"""
        print("\n⚙️ 检查 _meta.json...")

        meta_file = self.skill_path / '_meta.json'
        if not meta_file.exists():
            self.errors.append("_meta.json 不存在")
            return

        try:
            meta = json.loads(meta_file.read_text(encoding='utf-8'))
        except json.JSONDecodeError as e:
            self.errors.append(f"_meta.json JSON格式错误: {e}")
            return

        # 检查必需字段
        required_fields = ['id', 'version']
        for field in required_fields:
            if field not in meta:
                self.errors.append(f"_meta.json 缺少字段: {field}")
            else:
                self.passed.append(f"✓ {field}: {meta[field]}")

        # 验证version格式
        if 'version' in meta:
            if not re.match(r'^\d+\.\d+\.\d+$', meta['version']):
                self.errors.append(f"version 格式不正确，应为语义化版本: {meta['version']}")

    def check_naming(self):
        """检查命名规范"""
        print("\n🏷️ 检查命名规范...")

        # 文件夹名称
        folder_name = self.skill_path.name
        if not re.match(r'^[a-z0-9\-]+$', folder_name):
            self.errors.append(f"文件夹名称必须使用英文连字符格式: {folder_name}")
        else:
            self.passed.append(f"✓ 文件夹名称正确: {folder_name}")

        # SKILL.md中的name应与文件夹一致
        skill_md = self.skill_path / 'SKILL.md'
        if skill_md.exists():
            content = skill_md.read_text(encoding='utf-8')
            name_match = re.search(r'^name:\s*(.+)$', content, re.MULTILINE)
            if name_match:
                frontmatter_name = name_match.group(1).strip()
                if frontmatter_name != folder_name:
                    self.warnings.append(f"name 与文件夹名称不一致: {frontmatter_name} vs {folder_name}")

    def check_content_quality(self):
        """检查内容质量"""
        print("\n📝 检查内容质量...")

        skill_md = self.skill_path / 'SKILL.md'
        if not skill_md.exists():
            return

        content = skill_md.read_text(encoding='utf-8')

        # 检查是否有有效内容
        if len(content) < 500:
            self.warnings.append("SKILL.md 内容较少，建议增加更多详细信息")
        else:
            self.passed.append(f"✓ 内容长度: {len(content)} 字符")

        # 检查description质量
        desc_match = re.search(r'^description:\s*(.+)$', content, re.MULTILINE)
        if desc_match:
            desc = desc_match.group(1).strip()
            if len(desc) < 20:
                self.warnings.append("description 过短，建议提供更详细的描述")
            elif '当用户' in desc or 'Use when' in desc:
                self.passed.append("✓ description 包含触发短语")

    def print_results(self):
        """打印验证结果"""
        print(f"\n{'='*60}")
        print("验证结果")
        print(f"{'='*60}")

        # 通过项
        if self.passed:
            print(f"\n✅ 通过 ({len(self.passed)})")
            for p in self.passed[:10]:  # 只显示前10项
                print(f"  {p}")
            if len(self.passed) > 10:
                print(f"  ... 还有 {len(self.passed) - 10} 项")

        # 警告
        if self.warnings:
            print(f"\n⚠️ 警告 ({len(self.warnings)})")
            for w in self.warnings:
                print(f"  {w}")

        # 错误
        if self.errors:
            print(f"\n❌ 错误 ({len(self.errors)})")
            for e in self.errors:
                print(f"  {e}")
            print(f"\n❌ 验证失败: {len(self.errors)} 个错误")
        else:
            print(f"\n✅✅✅ 验证全部通过！✅✅✅")


def main():
    if len(sys.argv) < 2:
        # 默认验证当前目录
        skill_path = '.'
    else:
        skill_path = sys.argv[1]

    validator = SkillValidator(skill_path)
    success = validator.validate_all()

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()

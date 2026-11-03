#!/usr/bin/env python3
"""
HermesAgent 技能验证脚本

此脚本验证技能的结构完整性和内容质量，确保符合技能创建规范。
"""

import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Any


class HermesValidator:
    """HermesAgent 技能验证器"""

    def __init__(self, skill_path: str):
        self.skill_path = Path(skill_path)
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.info: List[str] = []

    def validate_all(self) -> bool:
        """执行所有验证检查"""
        print(f"开始验证技能: {self.skill_path}")
        print("=" * 60)

        # 1. 检查目录结构
        self._validate_structure()

        # 2. 验证 SKILL.md
        self._validate_skill_md()

        # 3. 验证 _meta.json
        self._validate_meta_json()

        # 4. 验证脚本
        self._validate_scripts()

        # 5. 验证参考文档
        self._validate_references()

        # 输出验证结果
        self._print_results()

        return len(self.errors) == 0

    def _validate_structure(self) -> None:
        """验证目录结构"""
        print("\n[1/5] 验证目录结构...")

        required_dirs = ['scripts', 'references', 'assets']
        for dir_name in required_dirs:
            dir_path = self.skill_path / dir_name
            if not dir_path.exists():
                self.warnings.append(f"缺少目录: {dir_name}")
                dir_path.mkdir(parents=True, exist_ok=True)
                self.info.append(f"已创建目录: {dir_name}")

        # 检查必需文件
        if not (self.skill_path / 'SKILL.md').exists():
            self.errors.append("缺少必需文件: SKILL.md")
        if not (self.skill_path / '_meta.json').exists():
            self.errors.append("缺少必需文件: _meta.json")

    def _validate_skill_md(self) -> None:
        """验证 SKILL.md 文件"""
        print("\n[2/5] 验证 SKILL.md...")

        skill_md = self.skill_path / 'SKILL.md'
        if not skill_md.exists():
            return

        content = skill_md.read_text(encoding='utf-8')

        # 检查 frontmatter 位置
        if not content.startswith('---'):
            self.errors.append("SKILL.md 必须以 YAML frontmatter 开头")
            return

        # 提取 frontmatter
        frontmatter_end = content.find('---', 3)
        if frontmatter_end == -1:
            self.errors.append("SKILL.md 的 YAML frontmatter 未正确闭合")
            return

        frontmatter_str = content[3:frontmatter_end].strip()
        try:
            import yaml
            frontmatter = yaml.safe_load(frontmatter_str)
        except ImportError:
            # 手动解析基本字段
            frontmatter = {}
            for line in frontmatter_str.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    frontmatter[key.strip()] = value.strip()

        # 验证必需字段
        required_fields = ['name', 'description']
        for field in required_fields:
            if field not in frontmatter:
                self.errors.append(f"Frontmatter 缺少必需字段: {field}")

        # 验证 name 字段格式
        if 'name' in frontmatter:
            name = frontmatter['name']
            if not re.match(r'^[a-z0-9-]+$', name):
                self.errors.append(f"name 字段格式不正确，应使用小写字母、数字和连字符: {name}")
            if self.skill_path.name != name:
                self.warnings.append(f"name 字段 ({name}) 与目录名称 ({self.skill_path.name}) 不一致")

        # 验证 description 字段
        if 'description' in frontmatter:
            desc = frontmatter['description']
            if len(desc) < 10:
                self.warnings.append("description 字段过于简短，建议提供更详细的描述")
            if not any(keyword in desc for keyword in ['使用', '触发', '当用户']):
                self.warnings.append("description 应包含触发短语（如 '使用当...' 或 '触发：'）")

        # 检查是否在 frontmatter 之前有 markdown 标题（文件开头不应以 # 开头）
        if content.strip().startswith('#'):
            self.errors.append("SKILL.md 必须以 YAML frontmatter (---) 开头，而非 markdown 标题")

        self.info.append(f"SKILL.md 行数: {len(content.splitlines())}")

    def _validate_meta_json(self) -> None:
        """验证 _meta.json 文件"""
        print("\n[3/5] 验证 _meta.json...")

        meta_json = self.skill_path / '_meta.json'
        if not meta_json.exists():
            return

        try:
            meta = json.loads(meta_json.read_text(encoding='utf-8'))
        except json.JSONDecodeError as e:
            self.errors.append(f"_meta.json 格式错误: {e}")
            return

        # 验证必需字段
        required_fields = ['id', 'version']
        for field in required_fields:
            if field not in meta:
                self.errors.append(f"_meta.json 缺少必需字段: {field}")

        # 验证 id 字段
        if 'id' in meta:
            if not isinstance(meta['id'], int) or meta['id'] <= 0:
                self.errors.append(f"id 必须是正整数: {meta['id']}")

        # 验证 version 字段
        if 'version' in meta:
            if not re.match(r'^\d+\.\d+\.\d+$', meta['version']):
                self.warnings.append(f"version 应遵循语义化版本格式: {meta['version']}")

    def _validate_scripts(self) -> None:
        """验证脚本文件"""
        print("\n[4/5] 验证脚本文件...")

        scripts_dir = self.skill_path / 'scripts'
        if not scripts_dir.exists():
            return

        script_files = list(scripts_dir.glob('*.py'))
        self.info.append(f"找到 {len(script_files)} 个脚本文件")

        for script in script_files:
            content = script.read_text(encoding='utf-8')

            # 检查是否可执行
            if not os.access(script, os.X_OK):
                self.warnings.append(f"脚本缺少执行权限: {script.name}")

            # 检查基本结构
            if not content.strip().startswith('#!'):
                self.warnings.append(f"脚本应包含 shebang: {script.name}")

            # 检查是否包含必要的函数
            if 'def ' not in content:
                self.warnings.append(f"脚本应包含函数定义: {script.name}")

    def _validate_references(self) -> None:
        """验证参考文档"""
        print("\n[5/5] 验证参考文档...")

        references_dir = self.skill_path / 'references'
        if not references_dir.exists():
            self.warnings.append("缺少 references 目录")
            return

        ref_files = list(references_dir.glob('*'))
        if not ref_files:
            self.warnings.append("references 目录为空")
        else:
            self.info.append(f"找到 {len(ref_files)} 个参考文件")

    def _print_results(self) -> None:
        """打印验证结果"""
        print("\n" + "=" * 60)
        print("验证结果")
        print("=" * 60)

        if self.errors:
            print(f"\n❌ 错误 ({len(self.errors)}):")
            for error in self.errors:
                print(f"   - {error}")

        if self.warnings:
            print(f"\n⚠️  警告 ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"   - {warning}")

        if self.info:
            print(f"\nℹ️  信息 ({len(self.info)}):")
            for info in self.info:
                print(f"   - {info}")

        print("\n" + "-" * 60)
        if not self.errors:
            print("✅ 验证通过！")
        else:
            print(f"❌ 验证失败！发现 {len(self.errors)} 个错误。")


def main():
    """主函数"""
    if len(sys.argv) < 2:
        # 默认验证当前目录
        skill_path = Path(__file__).parent.parent
    else:
        skill_path = Path(sys.argv[1])

    if not skill_path.exists():
        print(f"错误: 路径不存在 - {skill_path}")
        sys.exit(1)

    validator = HermesValidator(skill_path)
    success = validator.validate_all()

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()

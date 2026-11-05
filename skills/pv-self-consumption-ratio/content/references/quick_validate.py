"""
技能验证器 - 快速检查技能结构和质量
Quick Validator for Skill Structure and Quality
"""

import os
import sys
import json
import re
from pathlib import Path
from typing import Dict, List, Tuple, Any


class SkillValidator:
    """技能验证器"""

    def __init__(self, skill_path: str):
        """
        初始化验证器

        Args:
            skill_path: 技能目录路径
        """
        self.skill_path = Path(skill_path)
        self.errors = []
        self.warnings = []
        self.passed = []

    def validate_all(self) -> bool:
        """
        执行所有验证

        Returns:
            是否全部通过
        """
        self._validate_structure()
        self._validate_frontmatter()
        self._validate_meta()
        self._validate_naming()
        self._validate_scripts()

        return len(self.errors) == 0

    def _validate_structure(self):
        """验证目录结构"""
        required_dirs = ['scripts', 'references']
        required_files = ['SKILL.md', '_meta.json']

        for d in required_dirs:
            path = self.skill_path / d
            if not path.exists():
                self.errors.append(f"缺少必需目录: {d}")
            elif not path.is_dir():
                self.errors.append(f"{d} 不是目录")

        for f in required_files:
            path = self.skill_path / f
            if not path.exists():
                self.errors.append(f"缺少必需文件: {f}")
            elif not path.is_file():
                self.errors.append(f"{f} 不是文件")

        if len(self.errors) == 0:
            self.passed.append("目录结构验证通过")

    def _validate_frontmatter(self):
        """验证 SKILL.md frontmatter"""
        skill_md = self.skill_path / 'SKILL.md'

        if not skill_md.exists():
            self.errors.append("SKILL.md 文件不存在")
            return

        with open(skill_md, 'r', encoding='utf-8') as f:
            content = f.read()

        # 检查是否以 frontmatter 开头
        if not content.startswith('---'):
            self.errors.append("SKILL.md 必须以 YAML frontmatter 开头 (---)")
            return

        # 提取 frontmatter
        lines = content.split('\n')
        frontmatter_end = -1
        for i, line in enumerate(lines[1:], 1):
            if line.strip() == '---':
                frontmatter_end = i
                break

        if frontmatter_end == -1:
            self.errors.append("SKILL.md frontmatter 未正确闭合 (---)")
            return

        frontmatter_text = '\n'.join(lines[1:frontmatter_end])

        # 检查必需字段
        if 'name:' not in frontmatter_text:
            self.errors.append("frontmatter 缺少 'name' 字段")

        if 'description:' not in frontmatter_text:
            self.errors.append("frontmatter 缺少 'description' 字段")

        # 检查 name 格式
        name_match = re.search(r'^name:\s*(.+)$', frontmatter_text, re.MULTILINE)
        if name_match:
            name = name_match.group(1).strip()
            if not re.match(r'^[a-z0-9-]+$', name):
                self.errors.append(f"name 格式不正确，应使用小写字母、数字和连字符: {name}")
            if len(name) > 64:
                self.errors.append(f"name 长度超过64字符: {len(name)}")

        # 检查 description 是否包含触发短语
        desc_match = re.search(r'^description:\s*(.+)$', frontmatter_text, re.MULTILINE)
        if desc_match:
            desc = desc_match.group(1).strip()
            if 'Use when' not in desc and '当用户' not in desc:
                self.warnings.append("description 建议包含触发短语（如 'Use when...' 或 '当用户...'）")

        if len(self.errors) == 0:
            self.passed.append("Frontmatter 验证通过")

    def _validate_meta(self):
        """验证 _meta.json"""
        meta_path = self.skill_path / '_meta.json'

        if not meta_path.exists():
            self.errors.append("_meta.json 文件不存在")
            return

        try:
            with open(meta_path, 'r', encoding='utf-8') as f:
                meta = json.load(f)

            # 检查必需字段
            if 'id' not in meta:
                self.errors.append("_meta.json 缺少 'id' 字段")

            if 'version' not in meta:
                self.errors.append("_meta.json 缺少 'version' 字段")

            # 验证 id 格式
            if 'id' in meta:
                if not isinstance(meta['id'], (str, int)):
                    self.errors.append(f"id 应为字符串或整数: {type(meta['id'])}")

            # 验证 version 格式
            if 'version' in meta:
                version = meta['version']
                if not re.match(r'^\d+\.\d+\.\d+$', version):
                    self.warnings.append(f"version 建议使用语义化版本格式 (x.y.z): {version}")

            if len(self.errors) == 0:
                self.passed.append("_meta.json 验证通过")

        except json.JSONDecodeError as e:
            self.errors.append(f"_meta.json 解析失败: {e}")

    def _validate_naming(self):
        """验证命名规范"""
        # 检查技能名称与文件夹名称一致
        folder_name = self.skill_path.name

        skill_md = self.skill_path / 'SKILL.md'
        if skill_md.exists():
            with open(skill_md, 'r', encoding='utf-8') as f:
                content = f.read()

            name_match = re.search(r'^name:\s*(.+)$', content, re.MULTILINE)
            if name_match:
                skill_name = name_match.group(1).strip()
                if folder_name != skill_name:
                    self.warnings.append(
                        f"文件夹名称与 skill name 不一致: "
                        f"文件夹='{folder_name}', name='{skill_name}'"
                    )

        # 检查路径中是否有非英文字符
        path_str = str(self.skill_path)
        if re.search(r'[^\x00-\x7F]', path_str):
            self.errors.append(f"路径包含非英文字符: {path_str}")

        if len(self.errors) == 0 and len(self.warnings) == 0:
            self.passed.append("命名规范验证通过")

    def _validate_scripts(self):
        """验证脚本"""
        scripts_dir = self.skill_path / 'scripts'

        if not scripts_dir.exists():
            self.warnings.append("缺少 scripts 目录")
            return

        # 检查 Python 脚本语法
        for py_file in scripts_dir.glob('*.py'):
            if py_file.name.startswith('test_') or py_file.name.startswith('__'):
                continue

            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    code = f.read()
                compile(code, py_file.name, 'exec')
            except SyntaxError as e:
                self.errors.append(f"脚本语法错误 {py_file.name}: {e}")

        if len(self.errors) == 0:
            self.passed.append("脚本验证通过")

    def get_report(self) -> str:
        """
        获取验证报告

        Returns:
            报告文本
        """
        lines = []
        lines.append("=" * 60)
        lines.append("技能验证报告")
        lines.append("=" * 60)
        lines.append(f"技能路径: {self.skill_path}")
        lines.append("")

        if self.passed:
            lines.append("✅ 通过项:")
            for p in self.passed:
                lines.append(f"  ✓ {p}")
            lines.append("")

        if self.warnings:
            lines.append("⚠️ 警告项:")
            for w in self.warnings:
                lines.append(f"  ⚠ {w}")
            lines.append("")

        if self.errors:
            lines.append("❌ 错误项:")
            for e in self.errors:
                lines.append(f"  ✗ {e}")
            lines.append("")

        lines.append("-" * 60)
        if len(self.errors) == 0:
            lines.append("验证结果: ✅ 全部通过")
        else:
            lines.append(f"验证结果: ❌ 存在 {len(self.errors)} 个错误")
        lines.append("=" * 60)

        return "\n".join(lines)


def main():
    """主函数"""
    if len(sys.argv) < 2:
        skill_path = os.getcwd()
    else:
        skill_path = sys.argv[1]

    print(f"验证技能: {skill_path}")
    print()

    validator = SkillValidator(skill_path)
    validator.validate_all()

    print(validator.get_report())

    # 返回退出码
    sys.exit(0 if len(validator.errors) == 0 else 1)


if __name__ == "__main__":
    main()

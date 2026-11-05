#!/usr/bin/env python3
"""
名片扫描导入技能验证脚本
Business Card Importer Skill Validation Script

验证技能结构和内容是否符合规范。
"""

import os
import re
import json
import sys
from pathlib import Path
from typing import List, Dict, Tuple


class SkillValidator:
    """技能验证器"""

    def __init__(self, skill_path: str):
        self.skill_path = Path(skill_path)
        self.errors = []
        self.warnings = []

    def validate(self) -> bool:
        """执行所有验证"""
        print(f"\n{'='*60}")
        print(f"开始验证技能: {self.skill_path.name}")
        print(f"{'='*60}\n")

        checks = [
            ("目录结构检查", self.check_directory_structure),
            ("SKILL.md 检查", self.check_skill_md),
            ("Frontmatter 检查", self.check_frontmatter),
            ("_meta.json 检查", self.check_meta_json),
            ("脚本文件检查", self.check_scripts),
            ("引用文档检查", self.check_references),
        ]

        all_passed = True
        for name, check_func in checks:
            print(f"\n▶ {name}...")
            try:
                result = check_func()
                if result:
                    print(f"  ✓ 通过")
                else:
                    print(f"  ✗ 失败")
                    all_passed = False
            except Exception as e:
                print(f"  ✗ 错误: {e}")
                all_passed = False

        # 输出汇总
        print(f"\n{'='*60}")
        print("验证结果汇总")
        print(f"{'='*60}")

        if self.errors:
            print(f"\n错误 ({len(self.errors)}):")
            for err in self.errors:
                print(f"  • {err}")

        if self.warnings:
            print(f"\n警告 ({len(self.warnings)}):")
            for warn in self.warnings:
                print(f"  • {warn}")

        if all_passed:
            print(f"\n✓ 所有检查通过！")
        else:
            print(f"\n✗ 存在错误，请修复后重试。")

        return all_passed

    def check_directory_structure(self) -> bool:
        """检查目录结构"""
        required_items = [
            "SKILL.md",
            "_meta.json",
        ]

        required_dirs = [
            "scripts",
            "references",
            "assets",
        ]

        passed = True

        # 检查必需文件
        for item in required_items:
            path = self.skill_path / item
            if not path.exists():
                self.errors.append(f"缺少必需文件: {item}")
                passed = False

        # 检查目录
        for dir_name in required_dirs:
            path = self.skill_path / dir_name
            if not path.exists():
                self.warnings.append(f"建议添加目录: {dir_name}")
            elif not path.is_dir():
                self.errors.append(f"{dir_name} 不是目录")
                passed = False

        return passed

    def check_skill_md(self) -> bool:
        """检查SKILL.md文件"""
        skill_md = self.skill_path / "SKILL.md"

        if not skill_md.exists():
            self.errors.append("SKILL.md 文件不存在")
            return False

        content = skill_md.read_text(encoding="utf-8")

        # 检查frontmatter位置（必须在文件开头）
        if not content.startswith("---"):
            self.errors.append("SKILL.md 必须以 YAML frontmatter (---) 开头")
            return False

        # 检查文件不为空
        if len(content.strip()) < 100:
            self.errors.append("SKILL.md 内容过短")
            return False

        # 检查必需部分
        required_sections = [
            "name:",
            "description:",
            "# 名片扫描导入技能"
        ]

        for section in required_sections:
            if section not in content:
                if ":" in section:
                    # frontmatter字段
                    self.errors.append(f"缺少 frontmatter 字段: {section}")
                else:
                    self.warnings.append(f"建议添加: {section}")

        return len(self.errors) == 0

    def check_frontmatter(self) -> bool:
        """检查frontmatter内容"""
        skill_md = self.skill_path / "SKILL.md"
        content = skill_md.read_text(encoding="utf-8")

        # 提取frontmatter
        lines = content.split("\n")
        in_frontmatter = False
        frontmatter_lines = []
        frontmatter_end = -1

        for i, line in enumerate(lines):
            if line.strip() == "---":
                if not in_frontmatter:
                    in_frontmatter = True
                    continue
                else:
                    frontmatter_end = i
                    break

        if frontmatter_end == -1:
            self.errors.append("Frontmatter 未正确关闭")
            return False

        frontmatter_text = "\n".join(lines[:frontmatter_end])
        after_frontmatter = "\n".join(lines[frontmatter_end+1:])

        # 检查frontmatter前没有markdown标题
        if after_frontmatter.startswith("#"):
            self.errors.append("Frontmatter 后不能直接跟 markdown 标题")
            return False

        # 检查必需字段
        required_fields = ["name:", "description:"]
        for field in required_fields:
            if field not in frontmatter_text:
                self.errors.append(f"Frontmatter 缺少字段: {field}")

        # 检查name格式（连字符）
        name_match = re.search(r'^name:\s*(.+)$', frontmatter_text, re.MULTILINE)
        if name_match:
            name_value = name_match.group(1).strip()
            if not re.match(r'^[a-z0-9]+(-[a-z0-9]+)*$', name_value):
                self.errors.append(f"name 格式错误，应使用连字符格式: {name_value}")
            # 检查name长度
            if len(name_value) > 64:
                self.errors.append(f"name 长度超过64字符限制")
            # 检查name与目录名一致
            expected_name = self.skill_path.name
            if name_value != expected_name:
                self.errors.append(f"name ({name_value}) 与目录名 ({expected_name}) 不一致")

        # 检查description
        desc_match = re.search(r'^description:\s*(.+)$', frontmatter_text, re.MULTILINE)
        if desc_match:
            desc_value = desc_match.group(1).strip()
            if len(desc_value) < 20:
                self.errors.append("description 内容过短（建议至少20字符）")
            # 检查触发短语
            trigger_keywords = ["导入名片", "扫描名片", "名片识别", "批量导入"]
            if not any(kw in desc_value for kw in trigger_keywords):
                self.warnings.append("description 建议包含触发关键词")

        return len(self.errors) == 0

    def check_meta_json(self) -> bool:
        """检查_meta.json"""
        meta_path = self.skill_path / "_meta.json"

        if not meta_path.exists():
            self.errors.append("_meta.json 文件不存在")
            return False

        try:
            with open(meta_path, "r", encoding="utf-8") as f:
                meta = json.load(f)
        except json.JSONDecodeError as e:
            self.errors.append(f"_meta.json JSON格式错误: {e}")
            return False

        # 检查必需字段
        if "id" not in meta:
            self.errors.append("_meta.json 缺少 'id' 字段")
        elif not isinstance(meta["id"], int):
            self.errors.append("_meta.json 'id' 必须是整数")

        if "version" not in meta:
            self.errors.append("_meta.json 缺少 'version' 字段")
        elif not re.match(r'^\d+\.\d+\.\d+$', meta["version"]):
            self.errors.append("_meta.json 'version' 格式错误，应为 x.y.z")

        return len(self.errors) == 0

    def check_scripts(self) -> bool:
        """检查脚本文件"""
        scripts_dir = self.skill_path / "scripts"

        if not scripts_dir.exists():
            self.warnings.append("scripts 目录不存在（建议添加处理脚本）")
            return True

        py_files = list(scripts_dir.glob("*.py"))
        if not py_files:
            self.warnings.append("scripts 目录中没有 Python 文件")

        # 检查Python语法
        for py_file in py_files:
            try:
                compile(py_file.read_text(encoding="utf-8"), py_file.name, "exec")
            except SyntaxError as e:
                self.errors.append(f"Python 语法错误 {py_file.name}:{e.lineno}: {e.msg}")

        return len(self.errors) == 0

    def check_references(self) -> bool:
        """检查引用文档"""
        ref_dir = self.skill_path / "references"

        if not ref_dir.exists():
            self.warnings.append("references 目录不存在（建议添加详细文档）")
            return True

        return True


def main():
    """主函数"""
    if len(sys.argv) < 2:
        # 默认检查当前目录
        skill_path = "."
    else:
        skill_path = sys.argv[1]

    validator = SkillValidator(skill_path)
    success = validator.validate()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

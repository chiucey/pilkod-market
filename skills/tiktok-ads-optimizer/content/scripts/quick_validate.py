#!/usr/bin/env python3
"""
技能验证脚本 - 验证TikTok广告优化技能的结构和内容
"""

import os
import sys
import json
import re
from pathlib import Path
from typing import Dict, List, Tuple


class SkillValidator:
    """技能验证器"""

    def __init__(self, skill_path: str):
        self.skill_path = Path(skill_path)
        self.errors = []
        self.warnings = []
        self.passed = []

    def validate_all(self) -> bool:
        """执行所有验证"""
        print("=" * 60)
        print("TikTok广告优化技能 - 结构验证")
        print("=" * 60)
        print()

        checks = [
            ("目录结构", self.check_directory_structure),
            ("SKILL.md存在性", self.check_skill_md_exists),
            ("Frontmatter格式", self.check_frontmatter),
            ("_meta.json格式", self.check_meta_json),
            ("脚本语法", self.check_scripts),
            ("触发词检查", self.check_trigger_phrases),
        ]

        all_passed = True
        for name, check_func in checks:
            print(f"检查 {name}...", end=" ")
            result, message = check_func()
            if result:
                print(f"✅ {message}")
                self.passed.append(name)
            else:
                print(f"❌ {message}")
                self.errors.append(f"{name}: {message}")
                all_passed = False
            print()

        self.print_summary()
        return all_passed

    def check_directory_structure(self) -> Tuple[bool, str]:
        """检查目录结构"""
        required_dirs = ["scripts", "references"]
        required_files = ["SKILL.md", "_meta.json"]

        # 检查目录
        for dir_name in required_dirs:
            dir_path = self.skill_path / dir_name
            if not dir_path.exists():
                return False, f"缺少目录: {dir_name}"

        # 检查文件
        for file_name in required_files:
            file_path = self.skill_path / file_name
            if not file_path.exists():
                return False, f"缺少文件: {file_name}"

        # 检查子目录
        scripts_dir = self.skill_path / "scripts"
        scripts_files = list(scripts_dir.glob("*.py"))
        if not scripts_files:
            self.warnings.append("scripts目录为空，建议添加自动化脚本")

        references_dir = self.skill_path / "references"
        references_files = list(references_dir.glob("*.md"))
        if not references_files:
            self.warnings.append("references目录为空，建议添加参考文档")

        return True, "目录结构完整"

    def check_skill_md_exists(self) -> Tuple[bool, str]:
        """检查SKILL.md存在性"""
        skill_md = self.skill_path / "SKILL.md"
        if not skill_md.exists():
            return False, "SKILL.md不存在"

        content = skill_md.read_text(encoding="utf-8")
        if len(content) < 100:
            return False, "SKILL.md内容过少"

        return True, f"SKILL.md存在 ({len(content)} 字符)"

    def check_frontmatter(self) -> Tuple[bool, str]:
        """检查Frontmatter格式"""
        skill_md = self.skill_path / "SKILL.md"
        content = skill_md.read_text(encoding="utf-8")

        # 检查是否以---开头
        if not content.strip().startswith("---"):
            return False, "Frontmatter必须以---开头"

        # 提取frontmatter
        lines = content.split("\n")
        frontmatter_end = -1
        for i, line in enumerate(lines[1:], 1):
            if line.strip() == "---":
                frontmatter_end = i
                break

        if frontmatter_end == -1:
            return False, "Frontmatter缺少结束标记---"

        frontmatter_text = "\n".join(lines[1:frontmatter_end])

        # 检查必需字段
        required_fields = ["name", "description"]
        for field in required_fields:
            pattern = rf"^{field}:\s*.+$"
            if not re.search(pattern, frontmatter_text, re.MULTILINE):
                return False, f"Frontmatter缺少必需字段: {field}"

        # 验证name格式
        name_match = re.search(r"^name:\s*(.+)$", frontmatter_text, re.MULTILINE)
        if name_match:
            name = name_match.group(1).strip()
            if not re.match(r"^[a-z0-9-]+$", name):
                return False, f"name字段格式错误: {name} (应为小写字母、数字、连字符)"

        # 验证description不为空
        desc_match = re.search(r"^description:\s*(.+)$", frontmatter_text, re.MULTILINE)
        if desc_match:
            desc = desc_match.group(1).strip()
            if len(desc) < 20:
                return False, "description内容过短，应详细描述技能功能和触发词"

        return True, "Frontmatter格式正确"

    def check_meta_json(self) -> Tuple[bool, str]:
        """检查_meta.json格式"""
        meta_json = self.skill_path / "_meta.json"
        if not meta_json.exists():
            return False, "_meta.json不存在"

        try:
            with open(meta_json, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # 检查必需字段
            required_fields = ["id", "version"]
            for field in required_fields:
                if field not in data:
                    return False, f"_meta.json缺少字段: {field}"

            # 验证version格式
            version = data.get("version", "")
            if not re.match(r"^\d+\.\d+\.\d+$", version):
                return False, f"version格式错误: {version} (应为x.y.z)"

            return True, "_meta.json格式正确"

        except json.JSONDecodeError as e:
            return False, f"_meta.json JSON格式错误: {e}"
        except Exception as e:
            return False, f"读取_meta.json失败: {e}"

    def check_scripts(self) -> Tuple[bool, str]:
        """检查脚本语法"""
        scripts_dir = self.skill_path / "scripts"
        if not scripts_dir.exists():
            return True, "无scripts目录"

        python_files = list(scripts_dir.glob("*.py"))
        if not python_files:
            return True, "无Python脚本"

        syntax_errors = []
        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                compile(content, py_file.name, 'exec')
            except SyntaxError as e:
                syntax_errors.append(f"{py_file.name}: {e}")

        if syntax_errors:
            return False, f"语法错误: {', '.join(syntax_errors)}"

        return True, f"所有脚本语法正确 ({len(python_files)}个)"

    def check_trigger_phrases(self) -> Tuple[bool, str]:
        """检查触发词"""
        skill_md = self.skill_path / "SKILL.md"
        content = skill_md.read_text(encoding="utf-8")

        # 检查是否有TikTok相关关键词
        required_keywords = [
            "TikTok", "广告", "优化"
        ]

        missing = []
        for keyword in required_keywords:
            if keyword not in content:
                missing.append(keyword)

        if missing:
            return False, f"缺少关键词: {', '.join(missing)}"

        return True, "触发词完整"

    def print_summary(self) -> None:
        """打印验证摘要"""
        print("=" * 60)
        print("验证结果摘要")
        print("=" * 60)
        print(f"✅ 通过: {len(self.passed)} 项")
        print(f"❌ 失败: {len(self.errors)} 项")
        print(f"⚠️ 警告: {len(self.warnings)} 项")
        print()

        if self.errors:
            print("错误详情:")
            for error in self.errors:
                print(f"  • {error}")
            print()

        if self.warnings:
            print("警告详情:")
            for warning in self.warnings:
                print(f"  • {warning}")
            print()

        if not self.errors:
            print("🎉 验证全部通过！")
        else:
            print("❌ 存在错误，请修复后重试。")


def main():
    """主函数"""
    # 默认路径
    default_path = "/workspace/temp-skills/tiktok-ads-optimizer"

    # 获取路径参数
    if len(sys.argv) > 1:
        skill_path = sys.argv[1]
    else:
        skill_path = default_path

    print(f"验证路径: {skill_path}\n")

    validator = SkillValidator(skill_path)
    success = validator.validate_all()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

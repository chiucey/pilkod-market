#!/usr/bin/env python3
"""
简历优化技能验证脚本

验证技能文件的结构和内容是否符合规范。
"""

import os
import sys
import re
from pathlib import Path
from typing import List, Tuple, Dict


class SkillValidator:
    """技能验证器"""

    def __init__(self, skill_dir: str):
        self.skill_dir = Path(skill_dir)
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.passed: List[str] = []

    def validate_all(self) -> bool:
        """执行所有验证"""
        print(f"正在验证技能: {self.skill_dir.name}\n")

        self._check_directory_structure()
        self._check_skill_md()
        self._check_meta_json()
        self._check_scripts()

        # 打印结果
        self._print_results()

        return len(self.errors) == 0

    def _check_directory_structure(self):
        """检查目录结构"""
        required_dirs = ["scripts", "references", "assets"]

        for dir_name in required_dirs:
            dir_path = self.skill_dir / dir_name
            if not dir_path.exists():
                self.warnings.append(f"建议目录 {dir_name}/ 不存在")
            elif not dir_path.is_dir():
                self.errors.append(f"{dir_name}/ 不是目录")
            else:
                self.passed.append(f"目录 {dir_name}/ 存在")

    def _check_skill_md(self):
        """检查SKILL.md"""
        skill_md = self.skill_dir / "SKILL.md"

        if not skill_md.exists():
            self.errors.append("SKILL.md 不存在")
            return

        content = skill_md.read_text(encoding="utf-8")

        # 检查frontmatter
        if not content.startswith("---"):
            self.errors.append("SKILL.md 必须以 YAML frontmatter 开头（---）")
        else:
            self.passed.append("SKILL.md frontmatter 格式正确")

        # 提取frontmatter
        frontmatter = self._extract_frontmatter(content)

        # 检查必需字段
        if "name" not in frontmatter:
            self.errors.append("Frontmatter 缺少 'name' 字段")
        else:
            name = frontmatter["name"]
            if not re.match(r'^[a-z0-9-]+$', name):
                self.errors.append(f"name '{name}' 必须使用小写字母、数字和连字符")
            else:
                self.passed.append(f"Frontmatter name '{name}' 格式正确")

        if "description" not in frontmatter:
            self.errors.append("Frontmatter 缺少 'description' 字段")
        else:
            desc = frontmatter["description"]
            if len(desc) < 20:
                self.warnings.append("description 可能过于简短，建议提供更详细的描述")
            else:
                self.passed.append("Frontmatter description 存在且完整")

        # 检查文件大小
        if len(content) < 1000:
            self.warnings.append("SKILL.md 内容可能过于简短")

    def _check_meta_json(self):
        """检查_meta.json"""
        meta_json = self.skill_dir / "_meta.json"

        if not meta_json.exists():
            self.errors.append("_meta.json 不存在")
            return

        try:
            import json
            content = meta_json.read_text(encoding="utf-8")
            data = json.loads(content)

            # 检查必需字段
            required_fields = ["id", "version"]
            for field in required_fields:
                if field not in data:
                    self.errors.append(f"_meta.json 缺少 '{field}' 字段")
                else:
                    self.passed.append(f"_meta.json '{field}' 字段存在")

            # 检查版本格式
            if "version" in data:
                if not re.match(r'^\d+\.\d+\.\d+$', data["version"]):
                    self.errors.append(f"version '{data['version']}' 必须符合语义化版本格式 (如 1.0.0)")
                else:
                    self.passed.append(f"版本号格式正确: {data['version']}")

        except json.JSONDecodeError as e:
            self.errors.append(f"_meta.json JSON 格式错误: {e}")
        except Exception as e:
            self.errors.append(f"读取 _meta.json 时出错: {e}")

    def _check_scripts(self):
        """检查脚本文件"""
        scripts_dir = self.skill_dir / "scripts"

        if not scripts_dir.exists():
            return

        for script_file in scripts_dir.glob("*.py"):
            if script_file.name.startswith("test_"):
                continue

            # 检查脚本是否有执行权限设置提示
            content = script_file.read_text(encoding="utf-8")

            if "#!/usr/bin/env python" in content or "#!/usr/bin/python" in content:
                self.passed.append(f"脚本 {script_file.name} 有 shebang")
            else:
                self.warnings.append(f"脚本 {script_file.name} 建议添加 shebang")

            # 检查是否有错误处理
            if "try:" in content and "except" in content:
                self.passed.append(f"脚本 {script_file.name} 有错误处理")
            else:
                self.warnings.append(f"脚本 {script_file.name} 建议添加错误处理")

    def _extract_frontmatter(self, content: str) -> Dict[str, str]:
        """提取YAML frontmatter"""
        if not content.startswith("---"):
            return {}

        # 找到第二个 ---
        match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
        if not match:
            return {}

        frontmatter = {}
        for line in match.group(1).split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                frontmatter[key.strip()] = value.strip()

        return frontmatter

    def _print_results(self):
        """打印验证结果"""
        print("=" * 50)

        if self.passed:
            print(f"\n✅ 通过 ({len(self.passed)})")
            for item in self.passed:
                print(f"  ✓ {item}")

        if self.warnings:
            print(f"\n⚠️ 警告 ({len(self.warnings)})")
            for item in self.warnings:
                print(f"  ⚠ {item}")

        if self.errors:
            print(f"\n❌ 错误 ({len(self.errors)})")
            for item in self.errors:
                print(f"  ✗ {item}")

        print("\n" + "=" * 50)

        if len(self.errors) == 0:
            print("✅ 验证通过！技能文件符合规范。")
        else:
            print(f"❌ 验证失败！发现 {len(self.errors)} 个错误需要修复。")


def main():
    if len(sys.argv) < 2:
        print("用法: python quick_validate.py <skill-directory>")
        print("示例: python quick_validate.py /workspace/temp-skills/resume-optimizer")
        sys.exit(1)

    skill_dir = sys.argv[1]

    if not os.path.isdir(skill_dir):
        print(f"错误: 目录 {skill_dir} 不存在")
        sys.exit(1)

    validator = SkillValidator(skill_dir)
    success = validator.validate_all()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

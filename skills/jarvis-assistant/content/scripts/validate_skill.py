#!/usr/bin/env python3
"""
贾维斯技能验证脚本
验证技能是否符合质量门槛要求
"""

import os
import re
import json
from pathlib import Path

class SkillValidator:
    def __init__(self, skill_path: str):
        self.skill_path = Path(skill_path)
        self.errors = []
        self.warnings = []
        self.passed = []

    def validate_all(self) -> bool:
        """执行所有验证"""
        print("=" * 50)
        print("贾维斯技能验证")
        print("=" * 50)

        checks = [
            ("目录结构检查", self.check_directory_structure),
            ("SKILL.md检查", self.check_skill_md),
            ("_meta.json检查", self.check_meta_json),
            ("Frontmatter格式检查", self.check_frontmatter),
            ("文件内容检查", self.check_file_contents),
        ]

        all_passed = True
        for name, check_func in checks:
            print(f"\n📋 {name}...")
            try:
                result = check_func()
                if result:
                    self.passed.append(name)
                    print(f"   ✅ 通过")
                else:
                    all_passed = False
            except Exception as e:
                self.errors.append(f"{name} 执行失败: {str(e)}")
                print(f"   ❌ 失败: {str(e)}")
                all_passed = False

        self.print_summary()
        return all_passed

    def check_directory_structure(self) -> bool:
        """检查目录结构"""
        required = ["SKILL.md", "_meta.json"]
        for item in required:
            if not (self.skill_path / item).exists():
                self.errors.append(f"缺少必需文件: {item}")
                return False
        return True

    def check_skill_md(self) -> bool:
        """检查SKILL.md"""
        skill_md = self.skill_path / "SKILL.md"
        if not skill_md.exists():
            self.errors.append("SKILL.md 文件不存在")
            return False

        content = skill_md.read_text(encoding="utf-8")

        # 检查frontmatter开始
        if not content.startswith("---"):
            self.errors.append("SKILL.md 必须以 frontmatter --- 开头")
            return False

        return True

    def check_meta_json(self) -> bool:
        """检查_meta.json"""
        meta = self.skill_path / "_meta.json"
        if not meta.exists():
            self.errors.append("_meta.json 文件不存在")
            return False

        try:
            data = json.loads(meta.read_text(encoding="utf-8"))

            # 检查必需字段
            required_fields = ["id", "version", "name"]
            for field in required_fields:
                if field not in data:
                    self.errors.append(f"_meta.json 缺少必需字段: {field}")
                    return False

            # 检查name是否为英文
            name = data.get("name", "")
            if not re.match(r'^[a-zA-Z0-9\-_]+$', name):
                self.errors.append(f"_meta.json name 字段必须为英文: {name}")
                return False

            return True
        except json.JSONDecodeError as e:
            self.errors.append(f"_meta.json JSON格式错误: {str(e)}")
            return False

    def check_frontmatter(self) -> bool:
        """检查frontmatter格式"""
        skill_md = self.skill_path / "SKILL.md"
        content = skill_md.read_text(encoding="utf-8")

        # 提取frontmatter
        frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
        if not frontmatter_match:
            self.errors.append("无法解析 frontmatter")
            return False

        frontmatter_text = frontmatter_match.group(1)

        # 检查必需字段
        if 'name:' not in frontmatter_text:
            self.errors.append("frontmatter 缺少 name 字段")
            return False

        if 'description:' not in frontmatter_text:
            self.errors.append("frontmatter 缺少 description 字段")
            return False

        # 检查name格式
        name_match = re.search(r'^name:\s*(.+)$', frontmatter_text, re.MULTILINE)
        if name_match:
            name_value = name_match.group(1).strip()
            if not re.match(r'^[a-zA-Z0-9\-_]+$', name_value):
                self.errors.append(f"frontmatter name 必须为英文: {name_value}")
                return False

        # 检查是否有markdown标题在frontmatter之前
        lines = content.split('\n')
        frontmatter_end = -1
        for i, line in enumerate(lines):
            if line.strip() == '---':
                if frontmatter_end == -1:
                    frontmatter_end = i
                else:
                    break

        # 检查frontmatter之后是否有markdown标题
        content_after = '\n'.join(lines[frontmatter_end+1:]).strip()
        if content_after.startswith('#'):
            pass  # 正确：标题在frontmatter之后

        return True

    def check_file_contents(self) -> bool:
        """检查文件内容质量"""
        # 检查references目录是否存在
        references = self.skill_path / "references"
        if references.exists():
            ref_files = list(references.glob("*.md"))
            if len(ref_files) < 2:
                self.warnings.append("references 目录内容较少，建议添加更多参考文档")

        return True

    def print_summary(self):
        """打印验证摘要"""
        print("\n" + "=" * 50)
        print("验证摘要")
        print("=" * 50)

        print(f"\n✅ 通过: {len(self.passed)} 项")
        for item in self.passed:
            print(f"   - {item}")

        if self.warnings:
            print(f"\n⚠️ 警告: {len(self.warnings)} 项")
            for item in self.warnings:
                print(f"   - {item}")

        if self.errors:
            print(f"\n❌ 错误: {len(self.errors)} 项")
            for item in self.errors:
                print(f"   - {item}")
            print("\n🔴 验证失败")
        else:
            print("\n🟢 所有验证通过！")


def main():
    import sys

    if len(sys.argv) > 1:
        skill_path = sys.argv[1]
    else:
        # 默认当前目录
        skill_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    print(f"验证技能: {skill_path}")

    validator = SkillValidator(skill_path)
    success = validator.validate_all()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

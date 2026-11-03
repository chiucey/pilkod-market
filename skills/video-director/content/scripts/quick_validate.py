"""
视频导演Skill验证脚本
Quick Validator for Video Director Skill

验证skill结构和frontmatter是否符合规范。
"""

import os
import json
import re
import sys
from pathlib import Path


class ValidationError:
    """验证错误"""

    def __init__(self, error_type: str, message: str, file_path: str = ""):
        self.error_type = error_type
        self.message = message
        self.file_path = file_path

    def __str__(self):
        if self.file_path:
            return f"[{self.error_type}] {self.file_path}: {self.message}"
        return f"[{self.error_type}] {self.message}"


class SkillValidator:
    """Skill验证器"""

    def __init__(self, skill_path: str):
        self.skill_path = Path(skill_path)
        self.errors: list[ValidationError] = []
        self.warnings: list[ValidationError] = []

    def validate(self) -> bool:
        """执行所有验证"""
        print(f"开始验证 skill: {self.skill_path}")
        print("=" * 60)

        # 1. 检查目录结构
        self._check_directory_structure()

        # 2. 验证SKILL.md
        self._validate_skill_md()

        # 3. 验证_meta.json
        self._validate_meta_json()

        # 4. 检查文件命名规范
        self._check_naming_conventions()

        # 5. 验证references目录
        self._validate_references()

        # 6. 验证scripts目录
        self._validate_scripts()

        # 输出结果
        self._print_results()

        return len(self.errors) == 0

    def _check_directory_structure(self) -> None:
        """检查目录结构"""
        print("\n[1/6] 检查目录结构...")

        required_dirs = ["scripts", "references"]
        for dir_name in required_dirs:
            dir_path = self.skill_path / dir_name
            if not dir_path.exists():
                self.warnings.append(
                    ValidationError("WARNING", f"建议目录不存在: {dir_name}", str(self.skill_path))
                )
            else:
                print(f"  ✓ {dir_name}/ 目录存在")

    def _validate_skill_md(self) -> None:
        """验证SKILL.md"""
        print("\n[2/6] 验证 SKILL.md...")

        skill_md = self.skill_path / "SKILL.md"
        if not skill_md.exists():
            self.errors.append(
                ValidationError("ERROR", "SKILL.md 文件不存在", str(skill_md))
            )
            return

        with open(skill_md, "r", encoding="utf-8") as f:
            content = f.read()

        # 检查frontmatter是否存在
        if not content.startswith("---"):
            self.errors.append(
                ValidationError("ERROR", "SKILL.md 必须以 frontmatter (---) 开头", str(skill_md))
            )
            return

        # 提取frontmatter
        frontmatter_match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
        if not frontmatter_match:
            self.errors.append(
                ValidationError("ERROR", "无法解析 frontmatter", str(skill_md))
            )
            return

        frontmatter = frontmatter_match.group(1)

        # 检查必需字段
        required_fields = ["name", "description"]
        for field in required_fields:
            if not re.search(rf"^{field}:\s*.+", frontmatter, re.MULTILINE):
                self.errors.append(
                    ValidationError("ERROR", f"frontmatter 缺少必需字段: {field}", str(skill_md))
                )
            else:
                print(f"  ✓ {field} 字段存在")

        # 检查name格式
        name_match = re.search(r"^name:\s*(.+)", frontmatter, re.MULTILINE)
        if name_match:
            name = name_match.group(1).strip()
            if not re.match(r"^[a-z0-9-]+$", name):
                self.errors.append(
                    ValidationError("ERROR", f"name 必须使用连字符格式 (kebab-case): {name}", str(skill_md))
                )
            elif name != self.skill_path.name:
                self.errors.append(
                    ValidationError("ERROR", f"name ({name}) 必须与文件夹名称 ({self.skill_path.name}) 一致", str(skill_md))
                )

        # 检查description格式
        desc_match = re.search(r"^description:\s*(.+)", frontmatter, re.MULTILINE)
        if desc_match:
            desc = desc_match.group(1).strip()
            if len(desc) < 10:
                self.warnings.append(
                    ValidationError("WARNING", "description 可能过短，建议提供更详细的描述", str(skill_md))
                )
            if "Use when" not in desc and "适用于" not in desc:
                self.warnings.append(
                    ValidationError("WARNING", "description 建议包含触发短语 (Use when / 适用于)", str(skill_md))
                )

        print("  ✓ SKILL.md 结构正确")

    def _validate_meta_json(self) -> None:
        """验证_meta.json"""
        print("\n[3/6] 验证 _meta.json...")

        meta_json = self.skill_path / "_meta.json"
        if not meta_json.exists():
            self.errors.append(
                ValidationError("ERROR", "_meta.json 文件不存在", str(meta_json))
            )
            return

        try:
            with open(meta_json, "r", encoding="utf-8") as f:
                meta = json.load(f)
        except json.JSONDecodeError as e:
            self.errors.append(
                ValidationError("ERROR", f"_meta.json JSON格式错误: {e}", str(meta_json))
            )
            return

        # 检查必需字段
        required_fields = ["id", "version"]
        for field in required_fields:
            if field not in meta:
                self.errors.append(
                    ValidationError("ERROR", f"_meta.json 缺少必需字段: {field}", str(meta_json))
                )
            else:
                print(f"  ✓ {field} 字段存在")

        # 验证id类型
        if "id" in meta and not isinstance(meta["id"], int):
            self.errors.append(
                ValidationError("ERROR", "_meta.json 的 id 必须是整数", str(meta_json))
            )

        # 验证version格式
        if "version" in meta:
            version = meta["version"]
            if not re.match(r"^\d+\.\d+\.\d+$", version):
                self.errors.append(
                    ValidationError("ERROR", f"_meta.json 的 version 格式错误 (应为 semver): {version}", str(meta_json))
                )

        print("  ✓ _meta.json 结构正确")

    def _check_naming_conventions(self) -> None:
        """检查文件命名规范"""
        print("\n[4/6] 检查文件命名规范...")

        # 检查所有文件是否使用英文命名
        for root, dirs, files in os.walk(self.skill_path):
            for file in files:
                file_path = Path(root) / file

                # 跳过 __pycache__ 等
                if "__pycache__" in str(file_path):
                    continue

                # 检查是否包含非ASCII字符
                if not file.encode("utf-8").decode("ascii").isascii():
                    self.warnings.append(
                        ValidationError("WARNING", f"文件名包含非ASCII字符: {file}", str(file_path))
                    )

        print("  ✓ 文件命名规范检查完成")

    def _validate_references(self) -> None:
        """验证references目录"""
        print("\n[5/6] 验证 references 目录...")

        refs_dir = self.skill_path / "references"
        if not refs_dir.exists():
            print("  ⚠ references 目录不存在（可选）")
            return

        md_files = list(refs_dir.glob("*.md"))
        if md_files:
            print(f"  ✓ 找到 {len(md_files)} 个参考文档")
        else:
            print("  ⚠ references 目录为空")

    def _validate_scripts(self) -> None:
        """验证scripts目录"""
        print("\n[6/6] 验证 scripts 目录...")

        scripts_dir = self.skill_path / "scripts"
        if not scripts_dir.exists():
            print("  ⚠ scripts 目录不存在（可选）")
            return

        py_files = list(scripts_dir.glob("*.py"))
        if py_files:
            print(f"  ✓ 找到 {len(py_files)} 个脚本文件")

            # 检查脚本是否可执行
            for py_file in py_files:
                try:
                    with open(py_file, "r", encoding="utf-8") as f:
                        content = f.read()
                    if "__main__" in content or "def main" in content:
                        print(f"  ✓ {py_file.name} 包含可执行入口")
                except Exception as e:
                    self.warnings.append(
                        ValidationError("WARNING", f"脚本 {py_file.name} 读取失败: {e}", str(py_file))
                    )
        else:
            print("  ⚠ scripts 目录为空")

    def _print_results(self) -> None:
        """打印验证结果"""
        print("\n" + "=" * 60)
        print("验证结果:")
        print("=" * 60)

        if self.warnings:
            print(f"\n⚠ 警告 ({len(self.warnings)}):")
            for w in self.warnings:
                print(f"  {w}")

        if self.errors:
            print(f"\n✗ 错误 ({len(self.errors)}):")
            for e in self.errors:
                print(f"  {e}")
            print("\n❌ 验证失败！请修复上述错误。")
        else:
            print("\n✅ 所有验证通过！")


def main():
    """主函数"""
    # 获取skill路径
    if len(sys.argv) > 1:
        skill_path = sys.argv[1]
    else:
        skill_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    validator = SkillValidator(skill_path)
    success = validator.validate()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

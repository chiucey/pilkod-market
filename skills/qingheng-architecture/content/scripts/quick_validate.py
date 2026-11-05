#!/usr/bin/env python3
"""
青衡架构技能验证器
验证技能的结构、frontmatter格式和命名规范
"""

import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Any


class QinghengValidator:
    """青衡架构技能验证器"""

    def __init__(self, skill_path: str):
        self.skill_path = Path(skill_path)
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def validate_all(self) -> bool:
        """执行所有验证检查"""
        checks = [
            ("目录结构", self.check_directory_structure),
            ("Frontmatter格式", self.check_frontmatter),
            ("Meta文件", self.check_meta_file),
            ("命名规范", self.check_naming_conventions),
            ("内容完整性", self.check_content_completeness),
        ]

        all_passed = True
        for check_name, check_func in checks:
            print(f"检查 {check_name}...", end=" ")
            try:
                if not check_func():
                    all_passed = False
                    print("❌ 失败")
                else:
                    print("✅ 通过")
            except Exception as e:
                all_passed = False
                self.errors.append(f"{check_name}检查异常: {str(e)}")
                print(f"❌ 异常: {str(e)}")

        return all_passed

    def check_directory_structure(self) -> bool:
        """检查目录结构是否符合规范"""
        required_files = ["SKILL.md", "_meta.json"]

        for file_name in required_files:
            file_path = self.skill_path / file_name
            if not file_path.exists():
                self.errors.append(f"缺少必需文件: {file_name}")
                return False

        # 检查可选目录
        optional_dirs = ["scripts", "references", "assets"]
        for dir_name in optional_dirs:
            dir_path = self.skill_path / dir_name
            if dir_path.exists() and not dir_path.is_dir():
                self.errors.append(f"{dir_name} 应该是目录")
                return False

        return True

    def check_frontmatter(self) -> bool:
        """检查SKILL.md的frontmatter格式"""
        skill_md = self.skill_path / "SKILL.md"
        if not skill_md.exists():
            self.errors.append("SKILL.md 文件不存在")
            return False

        content = skill_md.read_text(encoding="utf-8")

        # 检查frontmatter是否在文件开头
        if not content.startswith("---"):
            self.errors.append("SKILL.md 必须以 --- 开头（frontmatter）")
            return False

        # 提取frontmatter内容（不包含---分隔符）
        lines = content.split("\n")
        frontmatter_lines = []
        in_frontmatter = False
        frontmatter_end_found = False

        for line in lines:
            stripped = line.strip()
            if stripped == "---" and not in_frontmatter:
                in_frontmatter = True
                continue
            elif stripped == "---" and in_frontmatter:
                frontmatter_end_found = True
                break
            elif in_frontmatter:
                frontmatter_lines.append(line)

        if not frontmatter_end_found:
            self.errors.append("Frontmatter 未正确关闭（缺少结束 ---）")
            return False

        frontmatter_text = "\n".join(frontmatter_lines)

        # 检查必需的frontmatter字段
        required_fields = ["name", "description"]
        for field in required_fields:
            if not re.search(rf"^{field}\s*:", frontmatter_text, re.MULTILINE):
                self.errors.append(f"Frontmatter 缺少必需字段: {field}")
                return False

        # 解析frontmatter为YAML
        try:
            import yaml
            frontmatter = yaml.safe_load(frontmatter_text)
            if not isinstance(frontmatter, dict):
                self.errors.append("Frontmatter 格式无效，应为YAML字典")
                return False
        except ImportError:
            # 如果没有yaml库，使用正则表达式解析
            for field in required_fields:
                if not re.search(rf"^{field}\s*:", frontmatter_text, re.MULTILINE):
                    self.errors.append(f"Frontmatter 缺少必需字段: {field}")
                    return False
        except Exception as e:
            self.errors.append(f"Frontmatter YAML解析失败: {str(e)}")
            return False

        # 检查name格式（连字符格式）
        if "name" in frontmatter:
            name = frontmatter["name"]
            if not re.match(r'^[a-z0-9]+(-[a-z0-9]+)*$', name):
                self.errors.append(f"name字段格式错误，应使用连字符格式: {name}")
                return False

        # 检查description不为空
        if "description" in frontmatter:
            desc = frontmatter["description"]
            if not desc or len(str(desc).strip()) < 10:
                self.warnings.append("description字段过短，建议至少10个字符")

        return True

    def check_meta_file(self) -> bool:
        """检查_meta.json文件"""
        meta_file = self.skill_path / "_meta.json"
        if not meta_file.exists():
            self.errors.append("_meta.json 文件不存在")
            return False

        try:
            meta = json.loads(meta_file.read_text(encoding="utf-8"))

            # 检查必需字段
            required_fields = ["id", "version"]
            for field in required_fields:
                if field not in meta:
                    self.errors.append(f"_meta.json 缺少必需字段: {field}")
                    return False

            # 验证version格式（语义化版本）
            version = meta.get("version", "")
            if not re.match(r'^\d+\.\d+\.\d+$', version):
                self.errors.append(f"version格式无效，应为语义化版本（如1.0.0）: {version}")
                return False

            return True
        except json.JSONDecodeError as e:
            self.errors.append(f"_meta.json JSON解析失败: {str(e)}")
            return False

    def check_naming_conventions(self) -> bool:
        """检查命名规范"""
        skill_name = self.skill_path.name

        # 文件夹名称应使用连字符格式
        if not re.match(r'^[a-z0-9]+(-[a-z0-9]+)*$', skill_name):
            self.warnings.append(
                f"技能文件夹名称建议使用连字符格式: 当前 '{skill_name}'"
            )

        # 检查SKILL.md中的name字段与文件夹名称一致
        skill_md = self.skill_path / "SKILL.md"
        if skill_md.exists():
            content = skill_md.read_text(encoding="utf-8")
            match = re.search(r'^name\s*:\s*(.+)$', content, re.MULTILINE)
            if match:
                frontmatter_name = match.group(1).strip()
                if frontmatter_name != skill_name:
                    self.warnings.append(
                        f"SKILL.md中name字段与文件夹名称不一致: "
                        f"文件夹='{skill_name}', name='{frontmatter_name}'"
                    )

        return True

    def check_content_completeness(self) -> bool:
        """检查内容完整性"""
        skill_md = self.skill_path / "SKILL.md"
        if not skill_md.exists():
            return False

        content = skill_md.read_text(encoding="utf-8")

        # 检查是否包含核心内容章节
        essential_sections = [
            "核心定位",
            "三位一体理论框架",
            "技术选型",
            "实施路线",
        ]

        missing_sections = []
        for section in essential_sections:
            if section not in content:
                missing_sections.append(section)

        if missing_sections:
            self.warnings.append(
                f"建议包含以下章节: {', '.join(missing_sections)}"
            )

        # 检查内容长度
        lines = [line for line in content.split("\n") if line.strip()]
        if len(lines) < 50:
            self.warnings.append(
                f"技能内容较短（{len(lines)}行），建议增加更多详细内容"
            )

        return True

    def get_report(self) -> str:
        """生成验证报告"""
        report_lines = ["=" * 50, "验证报告", "=" * 50, ""]

        if self.errors:
            report_lines.append(f"❌ 错误 ({len(self.errors)}个):")
            for error in self.errors:
                report_lines.append(f"  - {error}")
            report_lines.append("")

        if self.warnings:
            report_lines.append(f"⚠️  警告 ({len(self.warnings)}个):")
            for warning in self.warnings:
                report_lines.append(f"  - {warning}")
            report_lines.append("")

        if not self.errors and not self.warnings:
            report_lines.append("✅ 所有检查通过！")
        elif not self.errors:
            report_lines.append("✅ 核心检查通过，存在可优化的警告项")
        else:
            report_lines.append("❌ 存在错误，需要修复后重新验证")

        return "\n".join(report_lines)


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python quick_validate.py <技能路径>")
        print("示例: python quick_validate.py /workspace/temp-skills/qingheng-architecture")
        sys.exit(1)

    skill_path = sys.argv[1]
    print(f"开始验证技能: {skill_path}")
    print("-" * 50)

    validator = QinghengValidator(skill_path)
    passed = validator.validate_all()

    print("-" * 50)
    print(validator.get_report())

    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()

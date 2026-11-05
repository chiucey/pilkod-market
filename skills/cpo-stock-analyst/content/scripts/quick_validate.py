"""
技能验证脚本
验证SKILL.md的结构和frontmatter是否符合规范
"""

import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple

# 颜色定义
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'

def print_success(msg):
    print(f"{GREEN}✓ {msg}{RESET}")

def print_error(msg):
    print(f"{RED}✗ {msg}{RESET}")

def print_warning(msg):
    print(f"{YELLOW}⚠ {msg}{RESET}")

def print_info(msg):
    print(f"  {msg}")

class SkillValidator:
    """技能验证器"""

    def __init__(self, skill_path: str):
        self.skill_path = Path(skill_path)
        self.errors = []
        self.warnings = []
        self.passed = []

    def validate_all(self) -> bool:
        """执行所有验证"""
        print(f"\n{'='*60}")
        print(f"验证技能: {self.skill_path.name}")
        print(f"{'='*60}\n")

        # 1. 检查目录结构
        self.validate_structure()

        # 2. 验证SKILL.md
        self.validate_skill_md()

        # 3. 验证_meta.json
        self.validate_meta_json()

        # 4. 检查命名规范
        self.validate_naming()

        # 输出结果
        self.print_summary()

        return len(self.errors) == 0

    def validate_structure(self):
        """验证目录结构"""
        print_info("检查目录结构...")

        # 检查必要文件
        required_files = ["SKILL.md", "_meta.json"]

        for file in required_files:
            file_path = self.skill_path / file
            if file_path.exists():
                print_success(f"存在必要文件: {file}")
                self.passed.append(file)
            else:
                print_error(f"缺少必要文件: {file}")
                self.errors.append(f"Missing required file: {file}")

    def validate_skill_md(self):
        """验证SKILL.md"""
        print_info("验证SKILL.md...")

        skill_md = self.skill_path / "SKILL.md"

        if not skill_md.exists():
            print_error("SKILL.md不存在")
            return

        content = skill_md.read_text(encoding='utf-8')

        # 检查frontmatter位置
        lines = content.split('\n')

        if lines[0].strip() != '---':
            print_error("SKILL.md第一行必须是--- (frontmatter开始)")
            self.errors.append("Frontmatter must start at line 1")
            return

        # 找到frontmatter结束
        frontmatter_end = -1
        for i, line in enumerate(lines[1:], 1):
            if line.strip() == '---':
                frontmatter_end = i
                break

        if frontmatter_end == -1:
            print_error("SKILL.md缺少frontmatter结束标记 ---")
            self.errors.append("Missing frontmatter end marker")
            return

        # 解析frontmatter
        frontmatter_lines = lines[1:frontmatter_end]
        frontmatter_text = '\n'.join(frontmatter_lines)

        # 检查必需字段
        required_fields = ['name', 'description']
        for field in required_fields:
            pattern = rf'^{field}:'
            if re.search(pattern, frontmatter_text, re.MULTILINE):
                print_success(f"Frontmatter包含必需字段: {field}")
                self.passed.append(f"field:{field}")
            else:
                print_error(f"Frontmatter缺少必需字段: {field}")
                self.errors.append(f"Missing required frontmatter field: {field}")

        # 检查name格式
        name_match = re.search(r'^name:\s*(.+)$', frontmatter_text, re.MULTILINE)
        if name_match:
            name = name_match.group(1).strip()
            if re.match(r'^[a-z0-9-]+$', name):
                print_success(f"name格式正确: {name}")
                self.passed.append(f"name format")
            else:
                print_error(f"name格式错误(应使用小写字母、数字、连字符): {name}")
                self.errors.append(f"Invalid name format: {name}")

            # 检查name是否与目录名匹配
            expected_name = self.skill_path.name
            if name == expected_name:
                print_success("name与目录名匹配")
            else:
                print_warning(f"name({name})与目录名({expected_name})不匹配")
                self.warnings.append(f"name mismatch: {name} vs {expected_name}")

        # 检查description
        desc_match = re.search(r'^description:\s*(.+)$', frontmatter_text, re.MULTILINE)
        if desc_match:
            desc = desc_match.group(1).strip()
            if len(desc) >= 20:
                print_success(f"description长度充足: {len(desc)}字符")
            else:
                print_warning(f"description较短({len(desc)}字符),建议至少20字符")
                self.warnings.append(f"Short description: {len(desc)} chars")

    def validate_meta_json(self):
        """验证_meta.json"""
        print_info("验证_meta.json...")

        meta_json = self.skill_path / "_meta.json"

        if not meta_json.exists():
            print_error("_meta.json不存在")
            return

        import json

        try:
            content = meta_json.read_text(encoding='utf-8')
            data = json.loads(content)

            # 检查必需字段
            required_fields = ['id', 'version']
            for field in required_fields:
                if field in data:
                    print_success(f"_meta.json包含必需字段: {field}")
                    self.passed.append(f"meta:{field}")
                else:
                    print_error(f"_meta.json缺少必需字段: {field}")
                    self.errors.append(f"Missing meta field: {field}")

            # 验证id格式
            if 'id' in data:
                if isinstance(data['id'], int) or str(data['id']).isdigit():
                    print_success(f"id格式正确: {data['id']}")
                else:
                    print_error(f"id必须是数字: {data['id']}")
                    self.errors.append(f"Invalid id format: {data['id']}")

            # 验证version格式
            if 'version' in data:
                if re.match(r'^\d+\.\d+\.\d+$', data['version']):
                    print_success(f"version格式正确: {data['version']}")
                else:
                    print_warning(f"version格式建议使用semver: {data['version']}")

        except json.JSONDecodeError as e:
            print_error(f"_meta.json JSON格式错误: {e}")
            self.errors.append(f"Invalid JSON: {e}")
        except Exception as e:
            print_error(f"验证_meta.json时出错: {e}")
            self.errors.append(f"Meta validation error: {e}")

    def validate_naming(self):
        """验证命名规范"""
        print_info("检查路径命名...")

        # 检查目录名是否为英文
        dir_name = self.skill_path.name
        if re.match(r'^[a-z0-9-]+$', dir_name):
            print_success(f"目录名使用英文: {dir_name}")
            self.passed.append("dir name")
        else:
            print_error(f"目录名必须使用英文(小写字母、数字、连字符): {dir_name}")
            self.errors.append(f"Invalid directory name: {dir_name}")

        # 检查references目录中的文件
        references_dir = self.skill_path / "references"
        if references_dir.exists():
            for f in references_dir.iterdir():
                if f.is_file():
                    if not re.match(r'^[a-z0-9_.-]+$', f.name):
                        print_warning(f"references文件命名建议使用英文: {f.name}")

    def print_summary(self):
        """打印验证摘要"""
        print(f"\n{'='*60}")
        print("验证结果摘要")
        print(f"{'='*60}")

        print(f"\n{GREEN}通过: {len(self.passed)}{RESET}")
        print(f"{YELLOW}警告: {len(self.warnings)}{RESET}")
        print(f"{RED}错误: {len(self.errors)}{RESET}")

        if self.warnings:
            print(f"\n警告详情:")
            for w in self.warnings:
                print_warning(w)

        if self.errors:
            print(f"\n错误详情:")
            for e in self.errors:
                print_error(e)

        print(f"\n{'='*60}")

        if len(self.errors) == 0:
            print_success("验证通过!")
        else:
            print_error(f"验证失败，发现 {len(self.errors)} 个错误")
        print(f"{'='*60}\n")


def main():
    """主函数"""
    # 获取技能路径
    if len(sys.argv) > 1:
        skill_path = sys.argv[1]
    else:
        skill_path = "/workspace/temp-skills/a-share-analysis-system"

    validator = SkillValidator(skill_path)
    success = validator.validate_all()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Roundtable Skill 验证脚本
验证 SKILL.md 结构、frontmatter 和 _meta.json 的有效性
"""

import os
import re
import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple

# ANSI 颜色代码
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'
BOLD = '\033[1m'


class SkillValidator:
    """技能验证器"""

    def __init__(self, skill_path: str):
        self.skill_path = Path(skill_path)
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.passed: List[str] = []

    def log_pass(self, msg: str):
        self.passed.append(msg)
        print(f"{GREEN}✓{RESET} {msg}")

    def log_error(self, msg: str):
        self.errors.append(msg)
        print(f"{RED}✗{RESET} {msg}")

    def log_warning(self, msg: str):
        self.warnings.append(msg)
        print(f"{YELLOW}⚠{RESET} {msg}")

    def validate_all(self) -> bool:
        """运行所有验证"""
        print(f"\n{BOLD}验证 Roundtable 技能：{self.skill_path}{RESET}\n")

        # 1. 验证目录结构
        self.validate_structure()

        # 2. 验证 SKILL.md
        self.validate_skill_md()

        # 3. 验证 _meta.json
        self.validate_meta_json()

        # 4. 验证命名规范
        self.validate_naming()

        # 5. 验证内容质量
        self.validate_content()

        # 输出总结
        self.print_summary()

        return len(self.errors) == 0

    def validate_structure(self):
        """验证目录结构"""
        print(f"\n{BOLD}检查目录结构...{RESET}")

        if not self.skill_path.exists():
            self.log_error(f"技能目录不存在: {self.skill_path}")
            return

        skill_md = self.skill_path / "SKILL.md"
        if not skill_md.exists():
            self.log_error("缺少 SKILL.md 文件")
        else:
            self.log_pass("SKILL.md 文件存在")

        meta_json = self.skill_path / "_meta.json"
        if not meta_json.exists():
            self.log_error("缺少 _meta.json 文件")
        else:
            self.log_pass("_meta.json 文件存在")

    def validate_skill_md(self):
        """验证 SKILL.md 内容"""
        print(f"\n{BOLD}检查 SKILL.md...{RESET}")

        skill_md = self.skill_path / "SKILL.md"
        if not skill_md.exists():
            return

        content = skill_md.read_text(encoding='utf-8')
        lines = content.split('\n')

        # 检查 frontmatter 是否在最前面
        if not content.startswith('---'):
            self.log_error("SKILL.md 必须以 frontmatter (---) 开头")
            return
        else:
            self.log_pass("Frontmatter 正确位于文件开头")

        # 解析 frontmatter
        try:
            frontmatter_end = -1
            for i, line in enumerate(lines[1:], 1):
                if line.strip() == '---':
                    frontmatter_end = i
                    break

            if frontmatter_end == -1:
                self.log_error("Frontmatter 缺少闭合标记 ---")
                return

            frontmatter_text = '\n'.join(lines[1:frontmatter_end])
            frontmatter = {}

            for line in frontmatter_text.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    frontmatter[key.strip()] = value.strip()

            # 验证必填字段
            required_fields = ['name', 'description']
            for field in required_fields:
                if field not in frontmatter:
                    self.log_error(f"Frontmatter 缺少必填字段: {field}")
                else:
                    self.log_pass(f"Frontmatter 包含 {field} 字段")

            # 验证 name 格式
            if 'name' in frontmatter:
                name = frontmatter['name']
                if not re.match(r'^[a-z0-9-]+$', name):
                    self.log_error(f"name 字段格式错误: '{name}' (应使用小写字母、数字和连字符)")
                elif len(name) > 64:
                    self.log_error(f"name 字段长度超过64字符: {len(name)}")
                else:
                    self.log_pass(f"name 字段格式正确: {name}")

            # 验证 description 长度
            if 'description' in frontmatter:
                desc = frontmatter['description']
                if len(desc) < 10:
                    self.log_warning(f"description 可能太短 ({len(desc)} 字符)")
                elif len(desc) > 500:
                    self.log_warning(f"description 可能太长 ({len(desc)} 字符)")
                else:
                    self.log_pass(f"description 长度合理 ({len(desc)} 字符)")

        except Exception as e:
            self.log_error(f"解析 frontmatter 失败: {e}")

    def validate_meta_json(self):
        """验证 _meta.json 内容"""
        print(f"\n{BOLD}检查 _meta.json...{RESET}")

        meta_json = self.skill_path / "_meta.json"
        if not meta_json.exists():
            return

        try:
            meta = json.loads(meta_json.read_text(encoding='utf-8'))

            # 验证必填字段
            required_fields = ['id', 'version']
            for field in required_fields:
                if field not in meta:
                    self.log_error(f"_meta.json 缺少必填字段: {field}")
                else:
                    self.log_pass(f"_meta.json 包含 {field} 字段")

            # 验证 id 类型
            if 'id' in meta:
                if not isinstance(meta['id'], (int, str)):
                    self.log_error(f"id 字段类型错误: 应为数字或字符串")
                else:
                    self.log_pass(f"id 值有效: {meta['id']}")

            # 验证 version 格式
            if 'version' in meta:
                version = meta['version']
                if not re.match(r'^\d+\.\d+\.\d+$', str(version)):
                    self.log_warning(f"version 格式不是标准语义化版本: {version}")
                else:
                    self.log_pass(f"version 格式正确: {version}")

        except json.JSONDecodeError as e:
            self.log_error(f"_meta.json JSON 格式错误: {e}")
        except Exception as e:
            self.log_error(f"解析 _meta.json 失败: {e}")

    def validate_naming(self):
        """验证命名规范"""
        print(f"\n{BOLD}检查命名规范...{RESET}")

        folder_name = self.skill_path.name
        if not re.match(r'^[a-z0-9-]+$', folder_name):
            self.log_error(f"文件夹名称格式错误: '{folder_name}'")
        else:
            self.log_pass(f"文件夹名称格式正确: {folder_name}")

        # 检查 SKILL.md 中的 name 与文件夹名称是否匹配
        skill_md = self.skill_path / "SKILL.md"
        if skill_md.exists():
            content = skill_md.read_text(encoding='utf-8')
            match = re.search(r'^name:\s*(.+)$', content, re.MULTILINE)
            if match:
                frontmatter_name = match.group(1).strip()
                if frontmatter_name != folder_name:
                    self.log_error(f"name 不匹配: frontmatter='{frontmatter_name}', 文件夹='{folder_name}'")
                else:
                    self.log_pass("SKILL.md name 与文件夹名称匹配")

    def validate_content(self):
        """验证内容质量"""
        print(f"\n{BOLD}检查内容质量...{RESET}")

        skill_md = self.skill_path / "SKILL.md"
        if not skill_md.exists():
            return

        content = skill_md.read_text(encoding='utf-8')

        # 检查是否包含必要的章节
        required_sections = [
            (r'##\s*\d+\.?\s*总规则', '总规则章节'),
            (r'##\s*\d+\.?\s*固定专家角色', '专家角色章节'),
            (r'##\s*\d+\.?\s*工作流程', '工作流程章节'),
            (r'##\s*\d+\.?\s*输出格式', '输出格式章节'),
        ]

        for pattern, name in required_sections:
            if re.search(pattern, content, re.IGNORECASE):
                self.log_pass(f"包含 {name}")
            else:
                self.log_warning(f"可能缺少 {name}")

        # 检查是否有足够的角色定义
        role_count = len(re.findall(r'###\s*角色[A-E]', content))
        if role_count >= 5:
            self.log_pass(f"包含 {role_count} 个角色定义")
        else:
            self.log_warning(f"角色定义可能不足: {role_count}/5")

        # 检查触发短语
        if '触发' in content or 'trigger' in content.lower():
            self.log_pass("包含触发说明")

    def print_summary(self):
        """打印验证总结"""
        print(f"\n{BOLD}{'='*50}{RESET}")
        print(f"{BOLD}验证总结{RESET}")
        print(f"{'='*50}")
        print(f"{GREEN}通过: {len(self.passed)}{RESET}")
        print(f"{YELLOW}警告: {len(self.warnings)}{RESET}")
        print(f"{RED}错误: {len(self.errors)}{RESET}")

        if self.errors:
            print(f"\n{RED}验证失败！请修复上述错误。{RESET}")
            return False
        elif self.warnings:
            print(f"\n{YELLOW}验证通过（有警告）{RESET}")
            return True
        else:
            print(f"\n{GREEN}验证通过！{RESET}")
            return True


def main():
    if len(sys.argv) < 2:
        print(f"用法: python quick_validate.py <skill_path>")
        print(f"示例: python quick_validate.py /workspace/temp-skills/roundtable")
        sys.exit(1)

    skill_path = sys.argv[1]
    validator = SkillValidator(skill_path)
    success = validator.validate_all()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

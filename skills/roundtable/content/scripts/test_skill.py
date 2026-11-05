#!/usr/bin/env python3
"""
Roundtable Skill 测试脚本
测试技能的核心功能和输出格式
"""

import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple

# ANSI 颜色代码
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
CYAN = '\033[96m'
RESET = '\033[0m'
BOLD = '\033[1m'


class SkillTester:
    """技能测试器"""

    def __init__(self, skill_path: str):
        self.skill_path = Path(skill_path)
        self.tests_passed = 0
        self.tests_failed = 0
        self.tests_skipped = 0
        self.errors: List[str] = []

    def log_pass(self, test_name: str, msg: str = ""):
        self.tests_passed += 1
        indicator = f"{GREEN}✓{RESET}"
        detail = f" - {msg}" if msg else ""
        print(f"{indicator} {test_name}{detail}")

    def log_fail(self, test_name: str, msg: str = ""):
        self.tests_failed += 1
        self.errors.append(f"{test_name}: {msg}")
        indicator = f"{RED}✗{RESET}"
        detail = f" - {msg}" if msg else ""
        print(f"{indicator} {test_name}{detail}")

    def log_skip(self, test_name: str, reason: str = ""):
        self.tests_skipped += 1
        indicator = f"{YELLOW}⊘{RESET}"
        reason_text = f" ({reason})" if reason else ""
        print(f"{indicator} {test_name} - 跳过{reason_text}")

    def test_skill_structure(self) -> bool:
        """测试技能结构"""
        print(f"\n{BOLD}测试技能结构...{RESET}")

        # 检查必需文件
        required_files = ['SKILL.md', '_meta.json']
        all_exist = True

        for file in required_files:
            file_path = self.skill_path / file
            if file_path.exists():
                self.log_pass(f"文件存在: {file}")
            else:
                self.log_fail(f"文件存在: {file}", "文件不存在")
                all_exist = False

        # 检查目录结构
        scripts_dir = self.skill_path / 'scripts'
        if scripts_dir.exists():
            self.log_pass("scripts 目录存在")
        else:
            self.log_fail("scripts 目录存在", "目录不存在")

        return all_exist

    def test_frontmatter(self) -> bool:
        """测试 frontmatter 格式"""
        print(f"\n{BOLD}测试 Frontmatter...{RESET}")

        skill_md = self.skill_path / "SKILL.md"
        if not skill_md.exists():
            self.log_fail("Frontmatter 测试", "SKILL.md 不存在")
            return False

        content = skill_md.read_text(encoding='utf-8')
        lines = content.split('\n')

        # 检查开头
        if content.startswith('---'):
            self.log_pass("Frontmatter 格式正确")
        else:
            self.log_fail("Frontmatter 格式正确", "未以 --- 开头")
            return False

        # 解析 frontmatter
        frontmatter_end = -1
        for i, line in enumerate(lines[1:], 1):
            if line.strip() == '---':
                frontmatter_end = i
                break

        if frontmatter_end == -1:
            self.log_fail("Frontmatter 闭合标记", "未找到闭合 ---")
            return False

        frontmatter_text = '\n'.join(lines[1:frontmatter_end])
        frontmatter = {}

        for line in frontmatter_text.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                frontmatter[key.strip()] = value.strip()

        # 验证必填字段
        required = ['name', 'description']
        for field in required:
            if field in frontmatter:
                self.log_pass(f"包含字段: {field}")
            else:
                self.log_fail(f"包含字段: {field}", f"缺少 {field} 字段")

        return all(field in frontmatter for field in required)

    def test_meta_json(self) -> bool:
        """测试 _meta.json"""
        print(f"\n{BOLD}测试 _meta.json...{RESET}")

        meta_json = self.skill_path / "_meta.json"
        if not meta_json.exists():
            self.log_fail("_meta.json 测试", "文件不存在")
            return False

        try:
            import json
            meta = json.loads(meta_json.read_text(encoding='utf-8'))

            # 验证必填字段
            required = ['id', 'version']
            for field in required:
                if field in meta:
                    self.log_pass(f"包含字段: {field}", f"值为 {meta[field]}")
                else:
                    self.log_fail(f"包含字段: {field}", f"缺少 {field} 字段")

            return all(field in meta for field in required)

        except json.JSONDecodeError as e:
            self.log_fail("_meta.json JSON 格式", str(e))
            return False
        except Exception as e:
            self.log_fail("_meta.json 测试", str(e))
            return False

    def test_content_completeness(self) -> bool:
        """测试内容完整性"""
        print(f"\n{BOLD}测试内容完整性...{RESET}")

        skill_md = self.skill_path / "SKILL.md"
        if not skill_md.exists():
            self.log_fail("内容完整性测试", "SKILL.md 不存在")
            return False

        content = skill_md.read_text(encoding='utf-8')

        # 检查必要章节
        required_sections = [
            (r'##.*总规则', '总规则'),
            (r'##.*角色', '角色定义'),
            (r'##.*工作流程', '工作流程'),
            (r'##.*输出格式', '输出格式'),
        ]

        all_present = True
        for pattern, name in required_sections:
            if re.search(pattern, content, re.IGNORECASE):
                self.log_pass(f"包含章节: {name}")
            else:
                self.log_fail(f"包含章节: {name}", "章节不存在")
                all_present = False

        # 检查角色定义
        role_count = len(re.findall(r'###.*角色[A-E]', content))
        if role_count >= 5:
            self.log_pass(f"角色定义完整", f"{role_count}/5 个角色")
        else:
            self.log_fail(f"角色定义完整", f"只有 {role_count}/5 个角色")
            all_present = False

        # 检查触发说明
        if '触发' in content or 'trigger' in content.lower():
            self.log_pass("包含触发说明")
        else:
            self.log_skip("包含触发说明", "可能不需要")

        return all_present

    def test_workflow_logic(self) -> bool:
        """测试工作流程逻辑"""
        print(f"\n{BOLD}测试工作流程逻辑...{RESET}")

        skill_md = self.skill_path / "SKILL.md"
        if not skill_md.exists():
            self.log_fail("工作流程测试", "SKILL.md 不存在")
            return False

        content = skill_md.read_text(encoding='utf-8')

        # 检查步骤定义
        steps = ['Step 1', 'Step 2', 'Step 3', 'Step 4']
        all_steps_present = True

        for step in steps:
            if step in content:
                self.log_pass(f"包含步骤: {step}")
            else:
                self.log_fail(f"包含步骤: {step}", "步骤不存在")
                all_steps_present = False

        # 检查关键概念
        concepts = [
            (r'独立思考|独立输出', '独立思考/输出'),
            (r'交叉质询|互相.*质询', '交叉质询'),
            (r'共识|汇总', '共识汇总'),
            (r'分歧', '分歧处理'),
        ]

        for pattern, name in concepts:
            if re.search(pattern, content, re.IGNORECASE):
                self.log_pass(f"包含概念: {name}")
            else:
                self.log_skip(f"包含概念: {name}", "可能不需要")

        return all_steps_present

    def test_output_format(self) -> bool:
        """测试输出格式定义"""
        print(f"\n{BOLD}测试输出格式...{RESET}")

        skill_md = self.skill_path / "SKILL.md"
        if not skill_md.exists():
            self.log_fail("输出格式测试", "SKILL.md 不存在")
            return False

        content = skill_md.read_text(encoding='utf-8')

        # 检查输出格式章节
        if '输出格式' in content:
            self.log_pass("包含输出格式定义")
        else:
            self.log_fail("包含输出格式定义", "未找到输出格式章节")
            return False

        # 检查格式标记
        format_markers = ['【', '】', '━', '━━', '✅', '⚠️']
        found_markers = [m for m in format_markers if m in content]

        if found_markers:
            self.log_pass(f"包含格式标记", f"找到 {len(found_markers)} 种标记")
        else:
            self.log_skip("包含格式标记", "可能使用其他格式")

        return True

    def run_all_tests(self) -> bool:
        """运行所有测试"""
        print(f"\n{BOLD}{'='*60}{RESET}")
        print(f"{BOLD}运行 Roundtable 技能测试{RESET}")
        print(f"{BOLD}{'='*60}{RESET}")
        print(f"技能路径: {self.skill_path}")

        # 执行所有测试
        results = [
            ("结构测试", self.test_skill_structure),
            ("Frontmatter 测试", self.test_frontmatter),
            ("_meta.json 测试", self.test_meta_json),
            ("内容完整性测试", self.test_content_completeness),
            ("工作流程测试", self.test_workflow_logic),
            ("输出格式测试", self.test_output_format),
        ]

        all_passed = True
        for name, test_func in results:
            try:
                result = test_func()
                if not result:
                    all_passed = False
            except Exception as e:
                self.log_fail(f"{name} 执行", str(e))
                all_passed = False

        # 打印总结
        self.print_summary()

        return all_passed

    def print_summary(self):
        """打印测试总结"""
        total = self.tests_passed + self.tests_failed + self.tests_skipped

        print(f"\n{BOLD}{'='*60}{RESET}")
        print(f"{BOLD}测试总结{RESET}")
        print(f"{'='*60}")
        print(f"总测试数: {total}")
        print(f"{GREEN}通过: {self.tests_passed}{RESET}")
        print(f"{RED}失败: {self.tests_failed}{RESET}")
        print(f"{YELLOW}跳过: {self.tests_skipped}{RESET}")

        if self.errors:
            print(f"\n{RED}失败详情:{RESET}")
            for error in self.errors:
                print(f"  - {error}")

        if self.tests_failed == 0:
            print(f"\n{GREEN}所有测试通过！{RESET}")
        else:
            print(f"\n{RED}有测试失败，请检查。{RESET}")


def main():
    if len(sys.argv) < 2:
        print(f"用法: python test_skill.py <skill_path>")
        print(f"示例: python test_skill.py /workspace/temp-skills/roundtable")
        sys.exit(1)

    skill_path = sys.argv[1]
    tester = SkillTester(skill_path)
    success = tester.run_all_tests()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

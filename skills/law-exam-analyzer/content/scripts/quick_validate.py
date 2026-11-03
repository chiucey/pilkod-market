#!/usr/bin/env python3
"""
法考错题分析技能 - 快速验证脚本

验证以下内容：
1. SKILL.md frontmatter 格式正确（必须在第一行，name/description必填）
2. _meta.json 格式正确（id/version必填）
3. 目录结构符合规范
4. 无非英文路径
"""

import os
import re
import json
import sys
from pathlib import Path


class SkillValidator:
    def __init__(self, skill_path: str):
        self.skill_path = Path(skill_path)
        self.errors = []
        self.warnings = []
        self.success = True

    def validate_all(self) -> bool:
        """执行所有验证检查"""
        print(f"=" * 60)
        print(f"技能验证：{self.skill_path.name}")
        print(f"=" * 60)

        self.check_meta_json()
        self.check_skill_md()
        self.check_naming()
        self.check_directory_structure()
        self.check_forbidden_content()

        self.print_results()
        return self.success

    def check_meta_json(self):
        """验证 _meta.json"""
        print("\n[1/5] 检查 _meta.json...")

        meta_path = self.skill_path / "_meta.json"
        if not meta_path.exists():
            self.errors.append("缺少 _meta.json 文件")
            self.success = False
            return

        try:
            with open(meta_path, 'r', encoding='utf-8') as f:
                meta = json.load(f)

            required_keys = ['id', 'version']
            for key in required_keys:
                if key not in meta:
                    self.errors.append(f"_meta.json 缺少必填字段: {key}")
                    self.success = False

            if 'id' in meta:
                print(f"  - 技能ID: {meta['id']}")
            if 'version' in meta:
                print(f"  - 版本: {meta['version']}")

        except json.JSONDecodeError as e:
            self.errors.append(f"_meta.json 格式错误: {e}")
            self.success = False
        except Exception as e:
            self.errors.append(f"读取 _meta.json 失败: {e}")
            self.success = False

    def check_skill_md(self):
        """验证 SKILL.md"""
        print("\n[2/5] 检查 SKILL.md...")

        skill_path = self.skill_path / "SKILL.md"
        if not skill_path.exists():
            self.errors.append("缺少 SKILL.md 文件")
            self.success = False
            return

        with open(skill_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 检查frontmatter是否在第一行
        if not content.startswith('---'):
            self.errors.append("SKILL.md 必须以 frontmatter (---) 开头，不能有markdown标题")
            self.success = False
        else:
            print("  - Frontmatter 格式正确")

        # 提取frontmatter
        frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
        if not frontmatter_match:
            self.errors.append("无法解析 frontmatter")
            self.success = False
            return

        frontmatter_text = frontmatter_match.group(1)

        # 检查必填字段
        required_fields = ['name', 'description']
        for field in required_fields:
            if not re.search(rf'^{field}:', frontmatter_text, re.MULTILINE):
                self.errors.append(f"Frontmatter 缺少必填字段: {field}")
                self.success = False

        # 提取name字段值
        name_match = re.search(r'^name:\s*(.+)$', frontmatter_text, re.MULTILINE)
        if name_match:
            name_value = name_match.group(1).strip()
            print(f"  - 技能名称: {name_value}")

            # 检查name是否与文件夹名匹配
            expected_name = self.skill_path.name
            if name_value != expected_name:
                self.warnings.append(f"name字段值 '{name_value}' 与文件夹名 '{expected_name}' 不一致")

    def check_naming(self):
        """检查路径和命名是否为英文"""
        print("\n[3/5] 检查路径命名...")

        # 检查文件夹名
        folder_name = self.skill_path.name
        if not folder_name.isascii():
            self.errors.append(f"文件夹名包含非ASCII字符: {folder_name}")
            self.success = False
        else:
            print(f"  - 文件夹名: {folder_name} ✓")

        # 检查所有文件
        for root, dirs, files in os.walk(self.skill_path):
            for d in dirs:
                if not d.isascii():
                    self.errors.append(f"目录名包含非ASCII字符: {os.path.join(root, d)}")
                    self.success = False

            for f in files:
                if not f.isascii():
                    self.errors.append(f"文件名包含非ASCII字符: {os.path.join(root, f)}")
                    self.success = False

        print("  - 所有路径均为英文 ✓")

    def check_directory_structure(self):
        """检查目录结构"""
        print("\n[4/5] 检查目录结构...")

        required_files = ['SKILL.md', '_meta.json']
        for f in required_files:
            path = self.skill_path / f
            if path.exists():
                print(f"  - {f} ✓")
            else:
                self.errors.append(f"缺少必填文件: {f}")
                self.success = False

        # 检查可选目录
        optional_dirs = ['scripts', 'references', 'assets']
        for d in optional_dirs:
            path = self.skill_path / d
            if path.exists() and path.is_dir():
                print(f"  - {d}/ (可选) ✓")

    def check_forbidden_content(self):
        """检查禁止的内容"""
        print("\n[5/5] 检查安全合规性...")

        # 检查是否有secrets或敏感信息
        forbidden_patterns = [
            (r'password\s*=', '密码硬编码'),
            (r'api[_-]?key\s*=', 'API密钥'),
            (r'secret\s*=', '密钥'),
            (r'-----BEGIN.*PRIVATE KEY-----', '私钥'),
        ]

        for root, dirs, files in os.walk(self.skill_path):
            for f in files:
                if f.endswith(('.md', '.json', '.py', '.txt')):
                    path = os.path.join(root, f)
                    try:
                        with open(path, 'r', encoding='utf-8') as file:
                            content = file.read()
                            for pattern, desc in forbidden_patterns:
                                if re.search(pattern, content, re.IGNORECASE):
                                    self.warnings.append(f"文件 {f} 可能包含敏感信息: {desc}")
                    except:
                        pass

        print("  - 安全检查完成 ✓")

    def print_results(self):
        """打印验证结果"""
        print("\n" + "=" * 60)
        if self.success and not self.warnings:
            print("✓ 所有验证通过！")
        elif self.success and self.warnings:
            print("⚠ 验证通过，但有警告:")
        else:
            print("✗ 验证失败:")

        if self.errors:
            print("\n错误:")
            for e in self.errors:
                print(f"  - {e}")

        if self.warnings:
            print("\n警告:")
            for w in self.warnings:
                print(f"  - {w}")

        print("=" * 60)


def main():
    if len(sys.argv) < 2:
        # 默认检查当前目录
        skill_path = "."
    else:
        skill_path = sys.argv[1]

    validator = SkillValidator(skill_path)
    success = validator.validate_all()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

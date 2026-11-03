#!/usr/bin/env python3
"""
WBS Generator Skill Test Suite
测试WBS技能的各个组件
"""

import unittest
import os
import sys
from pathlib import Path

# 添加scripts目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from validate_skill import SkillValidator

class TestSkillValidator(unittest.TestCase):
    """测试技能验证器"""

    def setUp(self):
        """设置测试环境"""
        self.skill_path = Path(__file__).parent.parent
        self.validator = SkillValidator(self.skill_path)

    def test_skill_md_exists(self):
        """测试SKILL.md是否存在"""
        skill_md = self.skill_path / "SKILL.md"
        self.assertTrue(skill_md.exists(), "SKILL.md应该存在")

    def test_meta_json_exists(self):
        """测试_meta.json是否存在"""
        meta_json = self.skill_path / "_meta.json"
        self.assertTrue(meta_json.exists(), "_meta.json应该存在")

    def test_frontmatter_format(self):
        """测试frontmatter格式"""
        skill_md = self.skill_path / "SKILL.md"
        content = skill_md.read_text(encoding='utf-8')
        self.assertTrue(content.startswith('---'), "SKILL.md应该以---开头")

    def test_meta_json_format(self):
        """测试_meta.json格式"""
        import json
        meta_json = self.skill_path / "_meta.json"
        with open(meta_json, 'r', encoding='utf-8') as f:
            meta = json.load(f)
        self.assertIn('id', meta, "_meta.json应该包含id字段")
        self.assertIn('version', meta, "_meta.json应该包含version字段")

    def test_references_exist(self):
        """测试references目录是否存在"""
        ref_dir = self.skill_path / "references"
        self.assertTrue(ref_dir.exists(), "references目录应该存在")

def run_tests():
    """运行测试"""
    suite = unittest.TestLoader().loadTestsFromTestCase(TestSkillValidator)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)

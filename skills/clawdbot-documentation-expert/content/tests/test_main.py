import unittest
import sys
import os

# 导入主模块
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from main import run


class TestClawdbotDocSkill(unittest.TestCase):
    """测试Clawdbot文档专家技能主逻辑"""

    def test_run_with_valid_input(self):
        """测试正常输入场景"""
        input_data = {"user_input": "Clawdbot怎么安装？"}
        result = run(input_data)
        self.assertEqual(result["status"], "success")
        self.assertTrue(result["data"]["processed"])

    def test_run_with_empty_input(self):
        """测试空输入场景"""
        result = run({})
        self.assertEqual(result["status"], "success")

    def test_run_with_none_input(self):
        """测试异常输入场景"""
        result = run(None)
        self.assertEqual(result["status"], "success")


if __name__ == "__main__":
    unittest.main()

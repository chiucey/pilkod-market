import unittest
import sys
import os

# 导入src核心模块
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))
from main import run


class TestAcademicDeepResearch(unittest.TestCase):
    def test_normal_research_success(self):
        """正常学术主题调研测试"""
        input_params = {"research_topic": "大模型学术应用研究", "research_depth": 2}
        res = run(input_params)
        self.assertEqual(res["status"], "success")
        self.assertIn("data", res)
        self.assertIn("research_title", res["data"])

    def test_empty_topic_error(self):
        """空研究主题异常测试"""
        input_params = {"research_topic": ""}
        res = run(input_params)
        self.assertEqual(res["status"], "error")

    def test_no_input_error(self):
        """无入参兜底测试"""
        res = run(None)
        self.assertEqual(res["status"], "error")


if __name__ == "__main__":
    unittest.main()

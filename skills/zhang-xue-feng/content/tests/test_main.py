#!/usr/bin/env python3
"""
张雪峰技能单元测试
"""

import unittest
import sys
import os

# 添加src目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from main import run, _detect_intent


class TestZhangXueFengSkill(unittest.TestCase):
    """测试用例"""

    def test_empty_query(self):
        """测试空查询"""
        res = run({})
        self.assertEqual(res["status"], "success")
        # 空查询会触发general回复
        self.assertIsNotNone(res["message_for_user"])

    def test_college_query(self):
        """测试院校查询"""
        res = run({
            "query": "清华大学怎么样",
            "params": {"school": "清华大学"}
        })
        self.assertEqual(res["status"], "success")
        self.assertIn("清华大学", res["message_for_user"])
        self.assertIn("C9", res["message_for_user"])

    def test_major_analysis_biology(self):
        """测试专业分析-生物（天坑专业）"""
        res = run({
            "query": "生物专业好吗",
            "params": {"major": "生物"}
        })
        self.assertEqual(res["status"], "success")
        self.assertIn("家里有矿", res["message_for_user"])
        self.assertIn("天坑", res["message_for_user"])

    def test_major_analysis_computer(self):
        """测试专业分析-计算机"""
        res = run({
            "query": "计算机专业怎么样",
            "params": {"major": "计算机"}
        })
        self.assertEqual(res["status"], "success")
        self.assertIn("996", res["message_for_user"])

    def test_volunteer_fill_complete(self):
        """测试志愿填报-完整信息"""
        res = run({
            "query": "志愿填报",
            "params": {
                "province": "河南",
                "type": "理科",
                "rank": 25000,
                "major": "计算机"
            }
        })
        self.assertEqual(res["status"], "success")
        # 位次25000应该能找到郑州大学
        self.assertIn("郑州大学", res["message_for_user"])
        self.assertIn("稳", res["message_for_user"])

    def test_volunteer_fill_with_rank(self):
        """测试志愿填报-基于位次"""
        res = run({
            "query": "冲稳保",
            "params": {
                "province": "北京",
                "type": "文科",
                "rank": 500
            }
        })
        self.assertEqual(res["status"], "success")
        # 应该有推荐结果
        self.assertTrue(len(res.get("data", {}).get("recommendations", [])) > 0)

    def test_missing_params_error(self):
        """测试参数缺失错误处理"""
        res = run({
            "query": "志愿填报",
            "params": {"province": "北京"}  # 缺少type和rank
        })
        self.assertEqual(res["status"], "error")
        self.assertIn("缺一不可", res["message_for_user"])

    def test_intent_detection_college(self):
        """测试意图识别-院校"""
        self.assertEqual(_detect_intent("清华大学怎么样"), "college")
        self.assertEqual(_detect_intent("推荐大学"), "college")

    def test_intent_detection_major(self):
        """测试意图识别-专业"""
        self.assertEqual(_detect_intent("生物专业好吗"), "major")
        self.assertEqual(_detect_intent("就业前景"), "major")

    def test_intent_detection_volunteer(self):
        """测试意图识别-志愿"""
        self.assertEqual(_detect_intent("志愿填报"), "volunteer")
        self.assertEqual(_detect_intent("冲稳保"), "volunteer")
        self.assertEqual(_detect_intent("位次"), "volunteer")

    def test_intent_detection_plan(self):
        """测试意图识别-规划"""
        self.assertEqual(_detect_intent("考研规划"), "plan")
        self.assertEqual(_detect_intent("要不要复读"), "plan")

    def test_unsupported_province(self):
        """测试不支持的省份"""
        res = run({
            "query": "志愿填报",
            "params": {
                "province": "新疆",
                "type": "理科",
                "rank": 5000
            }
        })
        self.assertEqual(res["status"], "success")
        self.assertIn("数据", res["message_for_user"])

    def test_law_major(self):
        """测试法学专业"""
        res = run({
            "query": "法学专业怎么样",
            "params": {"major": "法学"}
        })
        self.assertEqual(res["status"], "success")
        self.assertIn("五院四系", res["message_for_user"])

    def test_medicine_major(self):
        """测试医学专业"""
        res = run({
            "query": "临床医学怎么样",
            "params": {"major": "临床医学"}
        })
        self.assertEqual(res["status"], "success")
        self.assertIn("35岁", res["message_for_user"])


class TestZhangQuotes(unittest.TestCase):
    """测试张雪峰语录库"""

    def test_biology_quote(self):
        """测试生物专业语录"""
        res = run({
            "query": "生物怎么样",
            "params": {"major": "生物"}
        })
        self.assertIn("家里有矿", res["message_for_user"])

    def test_chemistry_quote(self):
        """测试化学专业语录"""
        res = run({
            "query": "化学怎么样",
            "params": {"major": "化学"}
        })
        self.assertEqual(res["status"], "success")
        self.assertIn("天坑", res["message_for_user"])

    def test_material_quote(self):
        """测试材料专业语录"""
        res = run({
            "query": "材料怎么样",
            "params": {"major": "材料"}
        })
        self.assertEqual(res["status"], "success")
        self.assertIn("新能源", res["message_for_user"])


if __name__ == "__main__":
    unittest.main(verbosity=2)

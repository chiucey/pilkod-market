#!/usr/bin/env python3
"""
测试脚本 - 验证技能各项功能
"""

import sys
import unittest
from pathlib import Path

# 添加脚本目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.auto_optimizer import TikTokAdOptimizer, AdGroupMetrics, OptimizationRule
from scripts.report_generator import TikTokReportGenerator, DailyMetrics


class TestAutoOptimizer(unittest.TestCase):
    """自动优化器测试"""

    def setUp(self):
        """测试前准备"""
        self.optimizer = TikTokAdOptimizer()

    def test_roas_expand_rule(self):
        """测试ROAS扩量规则"""
        # 创建高ROAS的广告组
        metrics = AdGroupMetrics(
            adgroup_id="test001",
            adgroup_name="测试广告组",
            campaign_id="camp001",
            spend=1000.0,
            impressions=50000,
            clicks=1000,
            conversions=50,
            ctr=2.0,
            cvr=5.0,
            cpc=1.0,
            cpa=20.0,
            roas=5.0,  # 高ROAS
            status="ENABLE"
        )

        analysis = self.optimizer.analyze_adgroup(metrics)

        # 验证触发了扩量规则
        self.assertEqual(analysis["decision"], "expand")
        self.assertTrue(len(analysis["applicable_rules"]) > 0)

    def test_high_cpa_reduce_rule(self):
        """测试超成本降价规则"""
        self.optimizer.config["target_cpa"] = 50.0
        self.optimizer.config["min_conversions_for_optimization"] = 10  # 降低阈值以便测试

        metrics = AdGroupMetrics(
            adgroup_id="test002",
            adgroup_name="高成本广告组",
            campaign_id="camp001",
            spend=2000.0,
            impressions=40000,
            clicks=400,
            conversions=50,  # 满足最小转化阈值
            ctr=1.0,
            cvr=5.0,
            cpc=5.0,
            cpa=100.0,  # 超目标 (100 > 50 * 1.5 = 75)
            roas=1.0,
            status="ENABLE"
        )

        analysis = self.optimizer.analyze_adgroup(metrics)

        # 验证触发了降价规则
        self.assertEqual(analysis["decision"], "reduce")

    def test_no_conversion_pause_rule(self):
        """测试无转化暂停规则"""
        metrics = AdGroupMetrics(
            adgroup_id="test003",
            adgroup_name="无效广告组",
            campaign_id="camp001",
            spend=600.0,  # 超过阈值
            impressions=10000,
            clicks=50,
            conversions=0,  # 无转化
            ctr=0.5,
            cvr=0.0,
            cpc=12.0,
            cpa=0,
            roas=0,
            status="ENABLE"
        )

        analysis = self.optimizer.analyze_adgroup(metrics)

        # 验证触发了暂停规则
        self.assertEqual(analysis["decision"], "pause")

    def test_batch_optimization(self):
        """测试批量优化"""
        adgroups = [
            AdGroupMetrics(
                adgroup_id=f"ag{i}",
                adgroup_name=f"广告组{i}",
                campaign_id="camp001",
                spend=1000.0,
                impressions=50000,
                clicks=800,
                conversions=50,
                ctr=1.6,
                cvr=6.25,
                cpc=1.25,
                cpa=20.0,
                roas=5.0 if i % 2 == 0 else 1.0,
                status="ENABLE"
            )
            for i in range(10)
        ]

        report = self.optimizer.optimize_batch(adgroups)

        # 验证报告结构
        self.assertIn("summary", report)
        self.assertIn("expand_count", report["summary"])
        self.assertIn("reduce_count", report["summary"])

        # 验证结果分类
        self.assertEqual(
            report["summary"]["expand_count"] + report["summary"]["reduce_count"] + report["summary"]["hold_count"],
            len(adgroups)
        )


class TestReportGenerator(unittest.TestCase):
    """报告生成器测试"""

    def setUp(self):
        """测试前准备"""
        self.generator = TikTokReportGenerator()

    def test_daily_report_generation(self):
        """测试日报生成"""
        today = DailyMetrics(
            date="2026-04-01",
            spend=5000.0,
            impressions=200000,
            clicks=3500,
            conversions=150,
            video_views=50000,
            ctr=1.75,
            cvr=4.3,
            cpm=25.0,
            cpc=1.43,
            cpa=33.33,
            roas=3.5
        )

        yesterday = DailyMetrics(
            date="2026-03-31",
            spend=4500.0,
            impressions=180000,
            clicks=3000,
            conversions=130,
            video_views=45000,
            ctr=1.67,
            cvr=4.3,
            cpm=25.0,
            cpc=1.5,
            cpa=34.62,
            roas=3.2
        )

        report = self.generator.generate_daily_report(
            today_data=today,
            yesterday_data=yesterday,
            top_campaigns=[
                {"name": "测试系列", "spend": 3000, "conversions": 100, "cpa": 30, "roas": 4.0}
            ],
            top_adgroups=[
                {"name": "测试组A", "spend": 1000, "conversions": 50, "roas": 5.0}
            ],
            alerts=[],
            recommendations=["提升预算"]
        )

        # 验证报告内容
        self.assertIn("TikTok广告日报", report)
        self.assertIn("2026-04-01", report)
        self.assertIn("¥5,000", report)
        self.assertIn("测试系列", report)

    def test_calculate_change(self):
        """测试变化计算"""
        change, pct = self.generator.calculate_change(100, 80)
        self.assertEqual(change, "+20.00")
        self.assertEqual(pct, "+25.0%")

        change, pct = self.generator.calculate_change(80, 100)
        self.assertEqual(change, "-20.00")
        self.assertEqual(pct, "-20.0%")

        change, pct = self.generator.calculate_change(100, 0)
        self.assertEqual(pct, "+∞")


def run_tests():
    """运行所有测试"""
    print("=" * 60)
    print("运行技能单元测试")
    print("=" * 60)
    print()

    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # 添加测试类
    suite.addTests(loader.loadTestsFromTestCase(TestAutoOptimizer))
    suite.addTests(loader.loadTestsFromTestCase(TestReportGenerator))

    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print()
    print("=" * 60)
    print("测试结果摘要")
    print("=" * 60)
    print(f"运行: {result.testsRun} 个测试")
    print(f"成功: {result.testsRun - len(result.failures) - len(result.errors)} 个")
    print(f"失败: {len(result.failures)} 个")
    print(f"错误: {len(result.errors)} 个")

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)

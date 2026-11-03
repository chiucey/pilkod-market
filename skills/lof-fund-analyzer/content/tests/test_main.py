import unittest
import sys
import os
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from main import load_config, get_trade_date, run


class TestLOFAnalyzer(unittest.TestCase):
    def test_load_config(self):
        """测试配置文件加载"""
        config = load_config()
        self.assertIn("arbitrage", config)
        self.assertIn("filter", config)
        self.assertIn("output", config)

    def test_get_trade_date(self):
        """测试交易日计算"""
        trade_date = get_trade_date()
        self.assertEqual(len(trade_date), 10)
        self.assertIn("-", trade_date)

    def test_run_basic_execution(self):
        """测试核心执行流程"""
        result = run({"max_analyze_funds": 10})
        self.assertIn("status", result)
        self.assertIn("message_for_user", result)
        self.assertIn("data", result)

    def test_run_custom_params(self):
        """测试自定义参数覆盖"""
        custom_premium_rate = 2.0
        result = run({
            "min_premium_rate": custom_premium_rate,
            "max_analyze_funds": 10
        })
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["data"]["filter_config_used"]["min_premium_rate"], custom_premium_rate)


if __name__ == "__main__":
    unittest.main()

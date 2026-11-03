#!/usr/bin/env python3
"""Unit tests for Stock Market Pro"""

import unittest
import sys
import os
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from main import run, StockMarketPro


class TestMultiSource(unittest.TestCase):
    """Multi-source stock data tests"""

    def test_run_with_empty_input(self):
        """Test run function with empty input"""
        result = run({})
        self.assertIn("status", result)

    def test_run_price_action(self):
        """Test price action"""
        result = run({"action": "price", "ticker": "AAPL"})
        self.assertIn("status", result)

    def test_run_price_with_source(self):
        """Test price with specific source"""
        result = run({"action": "price", "ticker": "000001", "data_source": "dfcf"})
        self.assertIn("status", result)

    def test_invalid_action(self):
        """Test invalid action"""
        result = run({"action": "invalid_action", "ticker": "AAPL"})
        self.assertEqual(result["status"], "error")
        self.assertIn("message_for_user", result)

    def test_stockmarketpro_initialization(self):
        """Test StockMarketPro class initialization"""
        smp = StockMarketPro()
        self.assertIsNotNone(smp)

    def test_is_cn_stock(self):
        """Test Chinese stock detection"""
        smp = StockMarketPro()
        self.assertTrue(smp._is_cn_stock("600519"))
        self.assertTrue(smp._is_cn_stock("000001"))
        self.assertTrue(smp._is_cn_stock("00700"))
        self.assertFalse(smp._is_cn_stock("AAPL"))


class TestTickerValidation(unittest.TestCase):
    """Ticker validation tests"""

    def test_us_stock_format(self):
        """Test US stock format detection"""
        import re
        pattern = r'^[A-Z]{1,5}$'
        self.assertTrue(bool(re.match(pattern, "AAPL")))
        self.assertTrue(bool(re.match(pattern, "TSLA")))
        self.assertFalse(bool(re.match(pattern, "600519")))

    def test_cn_stock_format(self):
        """Test Chinese stock format detection"""
        import re
        pattern = r'^[0-9]{6}$'
        self.assertTrue(bool(re.match(pattern, "600519")))
        self.assertTrue(bool(re.match(pattern, "000001")))
        self.assertFalse(bool(re.match(pattern, "AAPL")))

    def test_hk_stock_format(self):
        """Test HK stock format detection"""
        import re
        pattern = r'^[0-9]{4,5}$|^[0-9]{4,5}\.HK$'
        self.assertTrue(bool(re.match(pattern, "00700")))
        self.assertTrue(bool(re.match(pattern, "00700.HK")))


class TestTechnicalIndicators(unittest.TestCase):
    """Technical indicators calculation tests"""

    def test_indicator_imports(self):
        """Test that indicator modules can be imported"""
        try:
            import pandas as pd
            import numpy as np
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"Failed to import required modules: {e}")

    def test_dataframe_operations(self):
        """Test basic pandas operations for indicators"""
        try:
            import pandas as pd
            import numpy as np
            from datetime import datetime, timedelta

            # Create sample data
            dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
            data = pd.DataFrame({
                'Open': np.random.randn(30).cumsum() + 100,
                'High': np.random.randn(30).cumsum() + 103,
                'Low': np.random.randn(30).cumsum() + 97,
                'Close': np.random.randn(30).cumsum() + 100,
                'Volume': np.random.randint(1000000, 10000000, 30)
            }, index=dates)

            # Test RSI calculation logic
            delta = data['Close'].diff()
            gain = delta.where(delta > 0, 0).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))

            self.assertFalse(rsi.isna().all())
        except Exception as e:
            self.fail(f"Indicator calculation test failed: {e}")


if __name__ == "__main__":
    unittest.main()

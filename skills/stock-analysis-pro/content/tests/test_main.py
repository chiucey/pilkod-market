#!/usr/bin/env python3
"""
stock-analysis-pro 单元测试
"""

import unittest
import sys
import os
from datetime import datetime
from unittest.mock import patch, MagicMock

# 添加src目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from main import (
    StockDataFetcher,
    TechnicalAnalyzer,
    FundamentalAnalyzer,
    RiskAnalyzer,
    ReportGenerator,
    run
)


class TestStockDataFetcher(unittest.TestCase):
    """测试股票数据获取"""

    def test_normalize_symbol_us(self):
        """测试美股代码标准化"""
        symbol = StockDataFetcher.normalize_symbol('AAPL', 'us')
        self.assertEqual(symbol, 'AAPL')

    def test_normalize_symbol_hk(self):
        """测试港股代码标准化"""
        symbol = StockDataFetcher.normalize_symbol('0700', 'hk')
        self.assertEqual(symbol, '0700.HK')

    def test_normalize_symbol_a_sh(self):
        """测试A股上海代码标准化"""
        symbol = StockDataFetcher.normalize_symbol('600519', 'a_sh')
        self.assertEqual(symbol, '600519.SS')

    def test_normalize_symbol_a_sz(self):
        """测试A股深圳代码标准化"""
        symbol = StockDataFetcher.normalize_symbol('000001', 'a_sz')
        self.assertEqual(symbol, '000001.SZ')

    def test_normalize_symbol_with_suffix(self):
        """测试已有后缀的代码"""
        symbol = StockDataFetcher.normalize_symbol('AAPL', 'hk')
        self.assertEqual(symbol, 'AAPL')  # 不应添加后缀

    @patch('yfinance.Ticker')
    def test_get_stock_info(self, mock_ticker):
        """测试获取股票信息"""
        mock_info = {
            'shortName': 'Apple Inc.',
            'exchange': 'NASDAQ',
            'industry': 'Technology',
            'sector': 'Consumer Electronics',
            'marketCap': 3000000000000,
            'trailingPE': 30.5,
            'priceToBook': 50.0,
            'beta': 1.2,
            'fiftyTwoWeekHigh': 200.0,
            'fiftyTwoWeekLow': 100.0,
        }
        mock_ticker.return_value.info = mock_info

        info = StockDataFetcher.get_stock_info('AAPL', 'us')
        self.assertEqual(info['name'], 'Apple Inc.')
        self.assertEqual(info['pe_ratio'], 30.5)
        self.assertIn('market_cap_fmt', info)


class TestTechnicalAnalyzer(unittest.TestCase):
    """测试技术分析"""

    def setUp(self):
        """创建测试数据"""
        np = __import__('numpy')
        dates = pd.date_range(start='2024-01-01', periods=100)
        np.random.seed(42)

        self.test_data = pd.DataFrame({
            'Open': 100 + np.random.randn(100).cumsum() * 2,
            'High': 105 + np.random.randn(100).cumsum() * 2,
            'Low': 95 + np.random.randn(100).cumsum() * 2,
            'Close': 100 + np.random.randn(100).cumsum() * 2,
            'Volume': np.random.randint(1000000, 10000000, 100),
        }, index=dates)

        # 确保High >= Open, Close, Low
        self.test_data['High'] = self.test_data[['Open', 'Close', 'High']].max(axis=1) * 1.01
        self.test_data['Low'] = self.test_data[['Open', 'Close', 'Low']].min(axis=1) * 0.99

    def test_calculate_indicators(self):
        """测试指标计算"""
        result = TechnicalAnalyzer.calculate_indicators(self.test_data.copy())
        self.assertIn('MA5', result.columns)
        self.assertIn('MA20', result.columns)
        self.assertIn('MACD', result.columns)
        self.assertIn('RSI6', result.columns)
        self.assertIn('BOLL_Upper', result.columns)

    def test_analyze_trend(self):
        """测试趋势分析"""
        data = TechnicalAnalyzer.calculate_indicators(self.test_data.copy())
        trend = TechnicalAnalyzer.analyze_trend(data)
        self.assertIn('trend', trend)
        self.assertIn('price', trend)
        self.assertIn('ma5', trend)

    def test_analyze_momentum(self):
        """测试动量分析"""
        data = TechnicalAnalyzer.calculate_indicators(self.test_data.copy())
        momentum = TechnicalAnalyzer.analyze_momentum(data)
        self.assertIn('rsi6', momentum)
        self.assertIn('macd', momentum)
        self.assertIn('rsi_signal', momentum)

    def test_analyze_bollinger(self):
        """测试布林带分析"""
        data = TechnicalAnalyzer.calculate_indicators(self.test_data.copy())
        boll = TechnicalAnalyzer.analyze_bollinger(data)
        self.assertIn('upper', boll)
        self.assertIn('lower', boll)
        self.assertIn('signal', boll)

    def test_generate_technical_signal(self):
        """测试综合信号生成"""
        data = TechnicalAnalyzer.calculate_indicators(self.test_data.copy())
        signal = TechnicalAnalyzer.generate_technical_signal(data)
        self.assertIn('signals', signal)
        self.assertIn('score', signal)
        self.assertIn('overall', signal)


class TestRiskAnalyzer(unittest.TestCase):
    """测试风险分析"""

    def setUp(self):
        """创建测试数据"""
        np = __import__('numpy')
        dates = pd.date_range(start='2024-01-01', periods=100)
        np.random.seed(42)

        self.test_data = pd.DataFrame({
            'Close': 100 + np.random.randn(100).cumsum() * 2,
            'Open': 100 + np.random.randn(100).cumsum() * 2,
            'High': 105 + np.random.randn(100).cumsum() * 2,
            'Low': 95 + np.random.randn(100).cumsum() * 2,
            'Volume': np.random.randint(1000000, 10000000, 100),
        }, index=dates)

    def test_calculate_risk_metrics(self):
        """测试风险指标计算"""
        metrics = RiskAnalyzer.calculate_risk_metrics(self.test_data)
        self.assertIn('annual_volatility', metrics)
        self.assertIn('max_drawdown', metrics)
        self.assertIn('var_95', metrics)
        self.assertIsInstance(metrics['annual_volatility'], float)

    def test_assess_risk_level(self):
        """测试风险等级评估"""
        metrics = {
            'annual_volatility': 25.0,
            'max_drawdown': -15.0,
            'var_95': -3.0,
        }
        info = {'beta': 1.2}

        assessment = RiskAnalyzer.assess_risk_level(metrics, info)
        self.assertIn('level', assessment)
        self.assertIn('score', assessment)
        self.assertIn('factors', assessment)


class TestReportGenerator(unittest.TestCase):
    """测试报告生成"""

    def test_generate_report_structure(self):
        """测试报告结构"""
        np = __import__('numpy')
        dates = pd.date_range(start='2024-01-01', periods=100)
        np.random.seed(42)

        test_data = pd.DataFrame({
            'Close': 100 + np.random.randn(100).cumsum() * 2,
            'Open': 100 + np.random.randn(100).cumsum() * 2,
            'High': 105 + np.random.randn(100).cumsum() * 2,
            'Low': 95 + np.random.randn(100).cumsum() * 2,
            'Volume': np.random.randint(1000000, 10000000, 100),
        }, index=dates)

        tech_data = TechnicalAnalyzer.calculate_indicators(test_data)

        info = {
            'name': 'Test Corp',
            'industry': 'Technology',
            'market_cap_fmt': '1.5万亿',
            'dividend_yield': 0.02,
            '52w_high': 150.0,
            '52w_low': 80.0,
            'beta': 1.2,
        }

        fundamentals = {'valuations': {'pe': '25.0 (合理)', 'pb': '3.0 (合理)'}}
        trend = TechnicalAnalyzer.analyze_trend(tech_data)
        momentum = TechnicalAnalyzer.analyze_momentum(tech_data)
        boll = TechnicalAnalyzer.analyze_bollinger(tech_data)
        signal = TechnicalAnalyzer.generate_technical_signal(tech_data)
        risk_metrics = RiskAnalyzer.calculate_risk_metrics(test_data)
        risk_assessment = RiskAnalyzer.assess_risk_level(risk_metrics, info)

        report = ReportGenerator.generate_report(
            symbol='TEST',
            market='us',
            period='1y',
            technical_data=tech_data,
            info=info,
            fundamentals=fundamentals,
            technical_trend=trend,
            technical_momentum=momentum,
            technical_bollinger=boll,
            technical_signal=signal,
            risk_metrics=risk_metrics,
            risk_assessment=risk_assessment,
        )

        self.assertIn('# 📊 股票深度分析报告', report)
        self.assertIn('TEST', report)
        self.assertIn('技术面分析', report)
        self.assertIn('风险评估', report)
        self.assertIn('⚠️ 风险提示', report)


class TestRunFunction(unittest.TestCase):
    """测试主函数"""

    @patch('yfinance.Ticker')
    def test_run_success(self, mock_ticker):
        """测试正常执行"""
        # Mock数据
        mock_history = MagicMock()
        mock_history.history.return_value = pd.DataFrame({
            'Open': [100, 101, 102],
            'High': [105, 106, 107],
            'Low': [95, 96, 97],
            'Close': [100, 102, 103],
            'Volume': [1000000, 1100000, 1200000],
        })

        mock_info = {
            'shortName': 'Test Inc.',
            'exchange': 'NYSE',
            'industry': 'Tech',
            'sector': 'Software',
            'marketCap': 1000000000,
            'trailingPE': 25.0,
            'priceToBook': 5.0,
            'dividendYield': 0.01,
            'beta': 1.0,
            'fiftyTwoWeekHigh': 110.0,
            'fiftyTwoWeekLow': 90.0,
        }

        mock_ticker.return_value = MagicMock(
            history=mock_history,
            info=mock_info
        )

        result = run({'symbol': 'TEST', 'period': '1mo'})

        self.assertEqual(result['status'], 'success')
        self.assertIn('data', result)
        self.assertIn('report', result['data'])

    def test_run_with_minimal_params(self):
        """测试最小参数"""
        result = run({})
        # 默认参数应该有返回值（即使数据获取失败）
        self.assertIn('status', result)


if __name__ == '__main__':
    # 需要先导入pandas
    import pandas as pd

    unittest.main(verbosity=2)

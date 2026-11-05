#!/usr/bin/env python3
"""
个股K线分析脚本
计算风险指标、流动性指标、估值指标并生成分析报告
"""

import json
import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

# 简化版数据分析（实际使用stocks_price API获取数据后进行计算）
class StockAnalyzer:
    """股票K线分析器"""

    def __init__(self, symbol: str, kline_data: List[Dict]):
        self.symbol = symbol
        self.kline_data = kline_data  # [{date, open, high, low, close, volume}]
        self.returns = []
        self.market_returns = []  # 用于Beta计算

    def calculate_daily_returns(self) -> List[float]:
        """计算日收益率"""
        if len(self.kline_data) < 2:
            return []

        self.returns = []
        for i in range(1, len(self.kline_data)):
            prev_close = self.kline_data[i-1]['close']
            curr_close = self.kline_data[i]['close']
            daily_return = (curr_close - prev_close) / prev_close
            self.returns.append(daily_return)

        return self.returns

    def mean(self, values: List[float]) -> float:
        """计算均值"""
        if not values:
            return 0
        return sum(values) / len(values)

    def std(self, values: List[float]) -> float:
        """计算标准差"""
        if len(values) < 2:
            return 0
        mean_val = self.mean(values)
        variance = sum((x - mean_val) ** 2 for x in values) / (len(values) - 1)
        return math.sqrt(variance)

    def cov(self, x: List[float], y: List[float]) -> float:
        """计算协方差"""
        if len(x) != len(y) or len(x) < 2:
            return 0
        mean_x = self.mean(x)
        mean_y = self.mean(y)
        return sum((x[i] - mean_x) * (y[i] - mean_y) for i in range(len(x))) / (len(x) - 1)

    def calculate_volatility(self) -> float:
        """计算年化波动率 = STD(日收益率) × √252"""
        returns = self.calculate_daily_returns()
        if not returns:
            return 0
        daily_std = self.std(returns)
        annualized_volatility = daily_std * math.sqrt(252)
        return annualized_volatility

    def calculate_beta(self, market_returns: List[float]) -> float:
        """计算Beta = COV(个股, 市场) / VAR(市场)"""
        returns = self.calculate_daily_returns()
        if len(returns) != len(market_returns) or len(returns) < 2:
            return 1.0  # 默认Beta

        covariance = self.cov(returns, market_returns)
        market_variance = self.std(market_returns) ** 2

        if market_variance == 0:
            return 1.0

        return covariance / market_variance

    def calculate_var(self, confidence: float = 0.95) -> float:
        """计算VaR = 均值 - Z × STD（日收益率）"""
        returns = self.calculate_daily_returns()
        if not returns:
            return 0

        z_score = 1.65 if confidence == 0.95 else 2.33 if confidence == 0.99 else 1.65
        mean_return = self.mean(returns)
        std_return = self.std(returns)

        var = mean_return - z_score * std_return
        return var

    def calculate_turnover_rate(self, volume: float, circulating_shares: float) -> float:
        """计算换手率 = 成交股数/流通股本 × 100%"""
        if circulating_shares == 0:
            return 0
        return (volume / circulating_shares) * 100

    def calculate_turnover_change(self, current_amount: float, prev_amount: float) -> float:
        """计算成交额变化率 = (当日 - 前日) / 前日 × 100%"""
        if prev_amount == 0:
            return 0
        return ((current_amount - prev_amount) / prev_amount) * 100

    def calculate_fund_flow(self, volume: float, avg_price: float, buy_ratio: float = 0.5) -> float:
        """估算资金流向 = 成交量 × 成交均价 × (买入比例 - 卖出比例)"""
        # 假设buy_ratio为估算的主动买入比例，>0.5表示净流入
        turnover_ratio = buy_ratio - 0.5
        return volume * avg_price * turnover_ratio

    def get_risk_score(self) -> Tuple[float, str]:
        """
        风险评分（0-100，分数越低风险越高）
        综合波动率、Beta、VaR三个指标
        """
        volatility = self.calculate_volatility()
        var_95 = self.calculate_var(0.95)

        # 假设Beta已知或设为1
        beta = 1.0

        # 波动率评分 (25%)
        if volatility < 0.20:
            vol_score = 100
        elif volatility < 0.35:
            vol_score = 75
        elif volatility < 0.50:
            vol_score = 50
        else:
            vol_score = 25

        # Beta评分 (25%)
        if 0.8 <= beta <= 1.2:
            beta_score = 100
        elif 0.5 <= beta < 0.8 or 1.2 < beta <= 1.5:
            beta_score = 75
        elif 0.3 <= beta < 0.5 or 1.5 < beta <= 2.0:
            beta_score = 50
        else:
            beta_score = 25

        # VaR评分 (25%)
        if var_95 > -0.02:
            var_score = 100
        elif var_95 > -0.035:
            var_score = 75
        elif var_95 > -0.05:
            var_score = 50
        else:
            var_score = 25

        # 换手率评分 (25%) - 需要外部数据
        turnover_score = 75  # 默认中等

        total_score = vol_score * 0.25 + beta_score * 0.25 + var_score * 0.25 + turnover_score * 0.25

        if total_score >= 75:
            assessment = "低风险"
        elif total_score >= 50:
            assessment = "中等风险"
        else:
            assessment = "高风险"

        return total_score, assessment

    def get_liquidity_score(self, turnover_rate: float, turnover_change: float, fund_flow: float) -> Tuple[float, str]:
        """
        流动性评分（0-100）
        """
        # 换手率评分 (40%)
        if 2 <= turnover_rate <= 8:
            turnover_score = 100
        elif 1 <= turnover_rate < 2 or 8 < turnover_rate <= 15:
            turnover_score = 75
        elif 0.5 <= turnover_rate < 1 or 15 < turnover_rate <= 25:
            turnover_score = 50
        else:
            turnover_score = 25

        # 成交额变化评分 (30%)
        if abs(turnover_change) < 10:
            change_score = 100
        elif abs(turnover_change) < 30:
            change_score = 75
        elif abs(turnover_change) < 50:
            change_score = 50
        else:
            change_score = 25

        # 资金流向评分 (30%)
        if abs(fund_flow) < 100000000:  # 1亿以下
            flow_score = 75
        elif abs(fund_flow) < 500000000:  # 5亿以下
            flow_score = 100
        else:
            flow_score = 50 if fund_flow > 0 else 25

        total_score = turnover_score * 0.4 + change_score * 0.3 + flow_score * 0.3

        if total_score >= 75:
            assessment = "流动性良好"
        elif total_score >= 50:
            assessment = "流动性中等"
        else:
            assessment = "流动性较差"

        return total_score, assessment

    def get_valuation_score(self, pe: float, pb: float, dividend_yield: float) -> Tuple[float, str]:
        """
        估值评分（0-100）
        """
        # PE评分 (40%) - PE越低越好，但需考虑行业差异
        if pe < 10:
            pe_score = 100
        elif pe < 20:
            pe_score = 80
        elif pe < 30:
            pe_score = 60
        elif pe < 50:
            pe_score = 40
        else:
            pe_score = 20

        # PB评分 (30%) - PB < 1 通常表示低估
        if pb < 1:
            pb_score = 100
        elif pb < 2:
            pb_score = 80
        elif pb < 3:
            pb_score = 60
        elif pb < 5:
            pb_score = 40
        else:
            pb_score = 20

        # 股息率评分 (30%) - 股息率越高越好
        if dividend_yield > 5:
            div_score = 100
        elif dividend_yield > 3:
            div_score = 80
        elif dividend_yield > 2:
            div_score = 60
        elif dividend_yield > 1:
            div_score = 40
        else:
            div_score = 20

        total_score = pe_score * 0.4 + pb_score * 0.3 + div_score * 0.3

        if total_score >= 75:
            assessment = "估值偏低（值得关注）"
        elif total_score >= 50:
            assessment = "估值合理"
        else:
            assessment = "估值偏高（谨慎）"

        return total_score, assessment

    def get_comprehensive_score(self, risk_score: float, liquidity_score: float, valuation_score: float) -> Tuple[float, str]:
        """
        综合评分与建议
        综合评分 = 风险评分 × 0.4 + 流动性评分 × 0.3 + 估值评分 × 0.3
        """
        comprehensive = risk_score * 0.4 + liquidity_score * 0.3 + valuation_score * 0.3

        if comprehensive >= 75:
            suggestion = "强烈建议买入"
            reason = "各项指标表现优秀，风险可控，流动性良好，估值合理偏低"
        elif comprehensive >= 60:
            suggestion = "建议买入"
            reason = "整体指标良好，可考虑布局"
        elif comprehensive >= 45:
            suggestion = "持有观望"
            reason = "指标表现一般，建议等待更好的买入时机"
        elif comprehensive >= 30:
            suggestion = "建议减仓"
            reason = "风险因素增加，建议降低持仓"
        else:
            suggestion = "建议卖出"
            reason = "风险较高，流动性或估值存在较大问题"

        return comprehensive, suggestion, reason

    def generate_report(self, stock_info: Dict, risk_metrics: Dict, liquidity_metrics: Dict, valuation_metrics: Dict) -> str:
        """生成分析报告"""
        risk_score, risk_assessment = self.get_risk_score()
        liquidity_score, liquidity_assessment = self.get_liquidity_score(
            liquidity_metrics.get('turnover_rate', 5),
            liquidity_metrics.get('turnover_change', 0),
            liquidity_metrics.get('fund_flow', 0)
        )
        valuation_score, valuation_assessment = self.get_valuation_score(
            valuation_metrics.get('pe', 20),
            valuation_metrics.get('pb', 2),
            valuation_metrics.get('dividend_yield', 2)
        )

        comprehensive_score, suggestion, reason = self.get_comprehensive_score(
            risk_score, liquidity_score, valuation_score
        )

        report = f"""# 📊 个股K线分析报告

## 基本信息
- **股票代码**: {self.symbol}
- **股票名称**: {stock_info.get('name', 'N/A')}
- **分析日期**: {datetime.now().strftime('%Y-%m-%d')}
- **数据周期**: {self.kline_data[0]['date'] if self.kline_data else 'N/A'} 至 {self.kline_data[-1]['date'] if self.kline_data else 'N/A'}

---

## 一、风险指标分析

| 指标 | 数值 | 评估 |
|------|------|------|
| 年化波动率 | {risk_metrics.get('volatility', 0)*100:.2f}% | {'偏高' if risk_metrics.get('volatility', 0) > 0.35 else '正常' if risk_metrics.get('volatility', 0) < 0.35 else '中等'} |
| Beta | {risk_metrics.get('beta', 1.0):.2f} | {'高波动' if risk_metrics.get('beta', 1.0) > 1.5 else '低波动' if risk_metrics.get('beta', 1.0) < 0.8 else '匹配市场'} |
| VaR(95%) | {risk_metrics.get('var_95', 0)*100:.2f}% | {'高风险' if risk_metrics.get('var_95', 0) < -0.05 else '中风险' if risk_metrics.get('var_95', 0) < -0.02 else '低风险'} |
| **风险评分** | **{risk_score:.0f}/100** | {risk_assessment} |

---

## 二、流动性分析

| 指标 | 数值 | 评估 |
|------|------|------|
| 换手率 | {liquidity_metrics.get('turnover_rate', 0):.2f}% | {'活跃' if liquidity_metrics.get('turnover_rate', 0) > 10 else '低迷' if liquidity_metrics.get('turnover_rate', 0) < 2 else '正常'} |
| 成交额变化 | {liquidity_metrics.get('turnover_change', 0):+.2f}% | {'上升' if liquidity_metrics.get('turnover_change', 0) > 0 else '下降'} |
| 资金流向 | {self._format_amount(liquidity_metrics.get('fund_flow', 0))} | {'净流入' if liquidity_metrics.get('fund_flow', 0) > 0 else '净流出'} |
| **流动性评分** | **{liquidity_score:.0f}/100** | {liquidity_assessment} |

---

## 三、估值分析

| 指标 | 数值 | 评估 |
|------|------|------|
| 市盈率(PE) | {valuation_metrics.get('pe', 0):.2f} | {'偏低' if valuation_metrics.get('pe', 0) < 20 else '偏高' if valuation_metrics.get('pe', 0) > 40 else '合理'} |
| 市净率(PB) | {valuation_metrics.get('pb', 0):.2f} | {'低估' if valuation_metrics.get('pb', 0) < 1 else '合理' if valuation_metrics.get('pb', 0) < 3 else '高估'} |
| 股息率 | {valuation_metrics.get('dividend_yield', 0):.2f}% | {'高' if valuation_metrics.get('dividend_yield', 0) > 3 else '中等' if valuation_metrics.get('dividend_yield', 0) > 1 else '低'} |
| **估值评分** | **{valuation_score:.0f}/100** | {valuation_assessment} |

---

## 四、综合评分与建议

| 评分维度 | 数值 | 权重 |
|----------|------|------|
| 风险评分 | {risk_score:.0f}/100 | 40% |
| 流动性评分 | {liquidity_score:.0f}/100 | 30% |
| 估值评分 | {valuation_score:.0f}/100 | 30% |
| **综合评分** | **{comprehensive_score:.0f}/100** | 100% |

---

## 五、投资建议

### 🎯 建议操作: **{suggestion}**

### 📝 理由说明:
{reason}

### 综合评估详情:
- 风险控制能力: {risk_assessment}（得分 {risk_score:.0f}）
- 交易活跃程度: {liquidity_assessment}（得分 {liquidity_score:.0f}）
- 估值合理程度: {valuation_assessment}（得分 {valuation_score:.0f}）

---

## 六、⚠️ 风险提示

1. 本报告仅供参考，不构成投资建议
2. 股票投资有风险，入市需谨慎
3. 建议结合基本面分析和市场环境综合判断
4. 以上分析基于历史数据，未来表现可能与历史趋势不同

---
*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        return report

    @staticmethod
    def _format_amount(amount: float) -> str:
        """格式化金额显示"""
        if abs(amount) >= 100000000:
            return f"{amount/100000000:.2f}亿"
        elif abs(amount) >= 10000:
            return f"{amount/10000:.2f}万"
        else:
            return f"{amount:.2f}"


def analyze_stock(symbol: str, kline_data: List[Dict], stock_info: Dict, market_returns: List[float] = None) -> str:
    """
    分析单只股票并生成报告

    Args:
        symbol: 股票代码
        kline_data: K线数据列表
        stock_info: 股票基本信息
        market_returns: 市场收益率列表（用于Beta计算）

    Returns:
        分析报告字符串
    """
    analyzer = StockAnalyzer(symbol, kline_data)

    # 计算风险指标
    risk_metrics = {
        'volatility': analyzer.calculate_volatility(),
        'beta': analyzer.calculate_beta(market_returns or [0.01] * len(analyzer.returns)) if market_returns else 1.0,
        'var_95': analyzer.calculate_var(0.95)
    }

    # 计算流动性指标
    latest_data = kline_data[-1] if kline_data else {}
    prev_data = kline_data[-2] if len(kline_data) > 1 else latest_data

    turnover_rate = 5.0  # 默认值，需要从stock_info获取
    turnover_change = 0.0
    fund_flow = 0.0

    if latest_data and prev_data:
        curr_amount = latest_data.get('close', 0) * latest_data.get('volume', 0)
        prev_amount = prev_data.get('close', 0) * prev_data.get('volume', 0)
        turnover_change = analyzer.calculate_turnover_change(curr_amount, prev_amount)
        avg_price = (latest_data.get('high', 0) + latest_data.get('low', 0)) / 2
        fund_flow = analyzer.calculate_fund_flow(latest_data.get('volume', 0), avg_price)

    liquidity_metrics = {
        'turnover_rate': turnover_rate,
        'turnover_change': turnover_change,
        'fund_flow': fund_flow
    }

    # 估值指标（从stock_info获取）
    valuation_metrics = {
        'pe': stock_info.get('trailingPE', 20) or 20,
        'pb': stock_info.get('priceToBook', 2) or 2,
        'dividend_yield': stock_info.get('dividendYield', 0) or 0
    }
    if valuation_metrics['dividend_yield'] > 1:
        valuation_metrics['dividend_yield'] = valuation_metrics['dividend_yield'] * 100

    # 生成报告
    report = analyzer.generate_report(stock_info, risk_metrics, liquidity_metrics, valuation_metrics)

    return report


if __name__ == "__main__":
    # 测试数据
    import random

    test_symbol = "600519.SS"  # 贵州茅台
    test_kline = [
        {"date": "2024-01-01", "open": 1700, "high": 1750, "low": 1680, "close": 1720, "volume": 2000000},
        {"date": "2024-01-02", "open": 1720, "high": 1740, "low": 1710, "close": 1730, "volume": 2100000},
    ]
    test_info = {
        "name": "贵州茅台",
        "trailingPE": 30.5,
        "priceToBook": 12.5,
        "dividendYield": 0.015  # 1.5%
    }

    report = analyze_stock(test_symbol, test_kline, test_info)
    print(report)

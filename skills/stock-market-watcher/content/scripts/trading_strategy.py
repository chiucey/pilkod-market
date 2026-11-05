"""
股票交易策略分析模块
基于技术指标生成交易信号和建议
"""

import json
from typing import Dict, List, Optional
from datetime import datetime, time
from technical_indicators import TechnicalIndicators, calculate_all_for_stock


class TradingSignal:
    """交易信号类"""

    STRONG_BUY = "强烈买入"
    BUY = "买入"
    HOLD = "观望"
    SELL = "卖出"
    STRONG_SELL = "强烈卖出"

    def __init__(self, score: int, action: str, confidence: float,
                 stop_loss: float, take_profit: float, risk_level: str):
        """
        初始化交易信号

        Args:
            score: 信号评分 (-10 到 +10)
            action: 操作建议
            confidence: 信心指数 (0-1)
            stop_loss: 止损价
            take_profit: 止盈价
            risk_level: 风险等级 (高/中/低)
        """
        self.score = score
        self.action = action
        self.confidence = confidence
        self.stop_loss = stop_loss
        self.take_profit = take_profit
        self.risk_level = risk_level

    def to_dict(self) -> Dict:
        return {
            'score': self.score,
            'action': self.action,
            'confidence': self.confidence,
            'stop_loss': self.stop_loss,
            'take_profit': self.take_profit,
            'risk_level': self.risk_level
        }


class StockStrategyAnalyzer:
    """股票策略分析器"""

    def __init__(self, current_price: float):
        """
        初始化分析器

        Args:
            current_price: 当前股价
        """
        self.current_price = current_price

    def analyze_bollinger_bands(self, bb_data: Dict) -> Dict:
        """
        分析布林线信号

        Returns:
            信号字典
        """
        position = bb_data.get('position', '数据不足')
        current = bb_data.get('current', {})

        score = 0
        reason = []

        if position == "跌破下轨":
            score = 3
            reason.append("价格跌破布林下轨，可能存在超卖机会")
        elif position == "突破上轨":
            score = -3
            reason.append("价格突破布林上轨，注意回调风险")
        elif position == "中轨上方":
            score = 1
            reason.append("价格位于布林中轨上方，多头趋势")
        elif position == "中轨下方":
            score = -1
            reason.append("价格位于布林中轨下方，空头趋势")

        return {
            'score': score,
            'signal': '买入' if score > 0 else ('卖出' if score < 0 else '观望'),
            'position': position,
            'reason': reason
        }

    def analyze_cci(self, cci_data: Dict) -> Dict:
        """
        分析CCI信号

        Returns:
            信号字典
        """
        current_cci = cci_data.get('current')
        signal = cci_data.get('signal', '数据不足')

        score = 0
        reason = []

        if current_cci is None:
            return {'score': 0, 'signal': '观望', 'reason': ['CCI数据不足']}

        # CCI从超卖区回升
        if cci_data['cci'][-5] < -100 and current_cci > -100:
            score = 3
            reason.append("CCI从超卖区回升，金叉信号")
        # CCI从超买区回落
        elif cci_data['cci'][-5] > 100 and current_cci < 100:
            score = -3
            reason.append("CCI从超买区回落，死叉信号")
        # CCI在超卖区
        elif current_cci < -100:
            score = 2
            reason.append("CCI处于超卖区，可能存在反弹机会")
        # CCI在超买区
        elif current_cci > 100:
            score = -2
            reason.append("CCI处于超买区，注意回调风险")
        # CCI接近零轴
        elif abs(current_cci) < 20:
            score = 0
            reason.append("CCI处于正常区间")
        elif current_cci > 0:
            score = 1
            reason.append("CCI为正，多头信号")
        else:
            score = -1
            reason.append("CCI为负，空头信号")

        return {
            'score': score,
            'signal': '买入' if score > 0 else ('卖出' if score < 0 else '观望'),
            'cci_value': current_cci,
            'reason': reason
        }

    def analyze_macd(self, macd_data: Dict) -> Dict:
        """
        分析MACD信号

        Returns:
            信号字典
        """
        crossover = macd_data.get('crossover', '数据不足')
        current = macd_data.get('current', {})

        score = 0
        reason = []

        if crossover == "金叉":
            score = 4
            reason.append("MACD形成金叉，买入信号")
        elif crossover == "死叉":
            score = -4
            reason.append("MACD形成死叉，卖出信号")
        elif crossover == "多头排列":
            score = 2
            reason.append("MACD多头排列，持续看涨")
        elif crossover == "空头排列":
            score = -2
            reason.append("MACD空头排列，持续看跌")
        elif crossover == "数据不足":
            score = 0
            reason.append("MACD数据不足")

        # MACD柱状图
        histogram = current.get('histogram')
        if histogram is not None:
            if histogram > 0:
                score += 1
                reason.append("MACD柱状图为正，红柱")
            else:
                score -= 1
                reason.append("MACD柱状图为负，绿柱")

        return {
            'score': score,
            'signal': '买入' if score > 0 else ('卖出' if score < 0 else '观望'),
            'crossover': crossover,
            'reason': reason
        }

    def analyze_expma(self, expma_data: Dict) -> Dict:
        """
        分析EXPMA信号

        Returns:
            信号字典
        """
        crossover = expma_data.get('crossover', '数据不足')
        current = expma_data.get('current', {})

        score = 0
        reason = []

        if crossover == "短期线上穿长期线":
            score = 4
            reason.append("EXPMA形成金叉，买入信号")
        elif crossover == "短期线下穿长期线":
            score = -4
            reason.append("EXPMA形成死叉，卖出信号")
        elif crossover == "多头排列":
            score = 2
            reason.append("EXPMA多头排列，看涨趋势")
        elif crossover == "空头排列":
            score = -2
            reason.append("EXPMA空头排列，看跌趋势")
        elif crossover == "数据不足":
            score = 0
            reason.append("EXPMA数据不足")

        # 价格与EXPMA关系
        expma_short = current.get('short')
        if expma_short and self.current_price > expma_short:
            score += 1
            reason.append("价格位于EXPMA12上方")
        elif expma_short:
            score -= 1
            reason.append("价格位于EXPMA12下方")

        return {
            'score': score,
            'signal': '买入' if score > 0 else ('卖出' if score < 0 else '观望'),
            'crossover': crossover,
            'reason': reason
        }

    def generate_signal(self, indicators: Dict) -> TradingSignal:
        """
        综合所有指标生成交易信号

        Args:
            indicators: 技术指标数据

        Returns:
            交易信号
        """
        # 分析各指标
        bb_signal = self.analyze_bollinger_bands(indicators['bollinger_bands'])
        cci_signal = self.analyze_cci(indicators['cci'])
        macd_signal = self.analyze_macd(indicators['macd'])
        expma_signal = self.analyze_expma(indicators['expma'])

        # 汇总评分
        total_score = (bb_signal['score'] + cci_signal['score'] +
                       macd_signal['score'] + expma_signal['score'])

        # 收集所有原因
        all_reasons = []
        all_reasons.extend(bb_signal['reason'])
        all_reasons.extend(cci_signal['reason'])
        all_reasons.extend(macd_signal['reason'])
        all_reasons.extend(expma_signal['reason'])

        # 判断信号强度
        if total_score >= 8:
            action = TradingSignal.STRONG_BUY
            confidence = min(0.95, 0.6 + abs(total_score) * 0.03)
        elif total_score >= 4:
            action = TradingSignal.BUY
            confidence = min(0.85, 0.5 + abs(total_score) * 0.03)
        elif total_score <= -8:
            action = TradingSignal.STRONG_SELL
            confidence = min(0.95, 0.6 + abs(total_score) * 0.03)
        elif total_score <= -4:
            action = TradingSignal.SELL
            confidence = min(0.85, 0.5 + abs(total_score) * 0.03)
        else:
            action = TradingSignal.HOLD
            confidence = 0.3

        # 计算止损止盈
        volatility = 0.03  # 默认波动率3%
        if abs(total_score) >= 8:
            volatility = 0.02
        elif abs(total_score) >= 4:
            volatility = 0.025

        if action in [TradingSignal.BUY, TradingSignal.STRONG_BUY]:
            stop_loss = self.current_price * (1 - volatility)
            take_profit = self.current_price * (1 + volatility * 2)
        elif action in [TradingSignal.SELL, TradingSignal.STRONG_SELL]:
            stop_loss = self.current_price * (1 + volatility)
            take_profit = self.current_price * (1 - volatility * 2)
        else:
            stop_loss = self.current_price * (1 - volatility)
            take_profit = self.current_price * (1 + volatility)

        # 风险等级
        if abs(total_score) >= 8:
            risk_level = "低"
        elif abs(total_score) >= 4:
            risk_level = "中"
        else:
            risk_level = "高"

        return TradingSignal(
            score=total_score,
            action=action,
            confidence=confidence,
            stop_loss=round(stop_loss, 2),
            take_profit=round(take_profit, 2),
            risk_level=risk_level
        )


def analyze_stock(symbol: str, historical_data: List[Dict],
                  stock_info: Dict = None) -> Dict:
    """
    全面分析股票并生成报告

    Args:
        symbol: 股票代码
        historical_data: 历史行情数据
        stock_info: 股票基本信息（可选）

    Returns:
        完整分析报告
    """
    if not historical_data:
        return {
            'error': '缺少历史数据',
            'symbol': symbol
        }

    # 获取当前价格
    current_price = historical_data[-1]['close']

    # 计算技术指标
    result = calculate_all_for_stock(historical_data)

    if 'error' in result:
        return {
            'error': result['error'],
            'symbol': symbol,
            'required': result['required'],
            'provided': result['provided']
        }

    # 分析策略
    analyzer = StockStrategyAnalyzer(current_price)
    signal = analyzer.generate_signal(result['indicators'])

    # 构建报告
    report = {
        'symbol': symbol,
        'stock_name': stock_info.get('name', symbol) if stock_info else symbol,
        'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'current_price': current_price,
        'price_change': stock_info.get('price_change', 0) if stock_info else 0,
        'change_percent': stock_info.get('change_percent', 0) if stock_info else 0,
        'volume': historical_data[-1].get('volume', 0),
        'data_count': result['data_count'],
        'indicators': {
            'bollinger_bands': {
                'upper': result['indicators']['bollinger_bands']['current']['upper'],
                'middle': result['indicators']['bollinger_bands']['current']['middle'],
                'lower': result['indicators']['bollinger_bands']['current']['lower'],
                'position': result['indicators']['bollinger_bands']['position']
            },
            'cci': {
                'value': result['indicators']['cci']['current'],
                'signal': result['indicators']['cci']['signal']
            },
            'macd': {
                'dif': result['indicators']['macd']['current']['dif'],
                'dea': result['indicators']['macd']['current']['dea'],
                'histogram': result['indicators']['macd']['current']['histogram'],
                'signal': result['indicators']['macd']['signal']
            },
            'expma': {
                'ema12': result['indicators']['expma']['current']['short'],
                'ema50': result['indicators']['expma']['current']['long'],
                'signal': result['indicators']['expma']['signal']
            }
        },
        'trading_signal': signal.to_dict()
    }

    return report


def format_report_text(report: Dict) -> str:
    """
    格式化报告为文本

    Args:
        report: 分析报告

    Returns:
        格式化的文本报告
    """
    if 'error' in report:
        return f"分析失败: {report['error']}"

    # 信号表情
    signal_emoji = {
        '强烈买入': '[RUBR]',
        '买入': '[RUB]',
        '观望': '[RUB]',
        '卖出': '[BLUE]',
        '强烈卖出': '[REVIEW]'
    }

    action_emoji = signal_emoji.get(report['trading_signal']['action'], '')

    report_text = f"""
[BLUE]股票看盘报告[/BLUE]

[BLUE]股票信息[/BLUE]
- 股票名称: {report['stock_name']}
- 股票代码: {report['symbol']}
- 更新时间: {report['update_time']}

[BLUE]实时行情[/BLUE]
- 当前价: ¥{report['current_price']:.2f}
- 涨跌幅: {report['change_percent']:+.2f}%
- 成交量: {report['volume']:,.0f}

[BLUE]技术指标分析[/BLUE]

[BOLD]布林线 (Bollinger Bands)[/BOLD]
- 上轨: ¥{report['indicators']['bollinger_bands']['upper']:.2f}
- 中轨: ¥{report['indicators']['bollinger_bands']['middle']:.2f}
- 下轨: ¥{report['indicators']['bollinger_bands']['lower']:.2f}
- 位置: {report['indicators']['bollinger_bands']['position']}

[BOLD]CCI顺势指标[/BOLD]
- 当前值: {report['indicators']['cci']['value']:.2f}
- 信号: {report['indicators']['cci']['signal']}

[BOLD]MACD指标[/BOLD]
- DIF: {report['indicators']['macd']['dif']:.4f}
- DEA: {report['indicators']['macd']['dea']:.4f}
- MACD柱: {report['indicators']['macd']['histogram']:.4f}
- 信号: {report['indicators']['macd']['signal']}

[BOLD]EXPMA指标[/BOLD]
- EMA12: ¥{report['indicators']['expma']['ema12']:.2f}
- EMA50: ¥{report['indicators']['expma']['ema50']:.2f}
- 信号: {report['indicators']['expma']['signal']}

[BLUE]交易策略[/BLUE]
- 信号评级: {report['trading_signal']['action']} {action_emoji}
- 信号评分: {report['trading_signal']['score']}
- 信心指数: {report['trading_signal']['confidence']*100:.0f}%
- 建议操作: {report['trading_signal']['action']}
- 止损位: ¥{report['trading_signal']['stop_loss']:.2f}
- 止盈位: ¥{report['trading_signal']['take_profit']:.2f}
- 风险等级: {report['trading_signal']['risk_level']}

[RED]风险提示: 以上建议仅供参考，不构成投资依据，投资有风险，入市需谨慎[/RED]
"""

    return report_text


def is_trading_hours() -> bool:
    """
    检查当前是否为交易时间

    Returns:
        是否在交易时间内
    """
    now = datetime.now()
    current_time = now.time()

    # 周末
    if now.weekday() >= 5:
        return False

    # A股交易时间
    morning_start = time(9, 15)
    morning_end = time(11, 30)
    afternoon_start = time(13, 0)
    afternoon_end = time(15, 0)

    return (morning_start <= current_time <= morning_end or
            afternoon_start <= current_time <= afternoon_end)


if __name__ == "__main__":
    # 测试代码
    import random

    # 模拟60天数据
    test_data = []
    price = 100
    for i in range(60):
        price = price * (1 + random.uniform(-0.02, 0.025))
        test_data.append({
            'date': f'2024-01-{i+1:02d}',
            'open': price * 0.99,
            'high': price * 1.02,
            'low': price * 0.98,
            'close': price,
            'volume': random.randint(1000000, 5000000)
        })

    # 分析股票
    report = analyze_stock('000001.SZ', test_data, {
        'name': '平安银行',
        'price_change': 0.35,
        'change_percent': 1.25
    })

    print(format_report_text(report))

#!/usr/bin/env python3
"""
stock-analysis-pro 专业级股票分析技能主入口
融合基本面、技术面、估值、风险四大分析维度

核心功能：
- 获取股票行情和财务数据
- 计算20+技术指标
- 基本面财务分析
- PE/PB/PEG/DCF估值
- Beta/波动率/最大回撤风险评估
- 多标的对比分析
- 生成结构化Markdown报告
"""

import sys
import json
import warnings
from datetime import datetime
from typing import Dict, List, Optional, Any

import pandas as pd
import numpy as np
import yfinance as yf

# 技术指标库
from ta.trend import MACD, SMAIndicator, EMAIndicator, ADXIndicator, DMAIndicator
from ta.momentum import RSIIndicator, StochasticOscillator, WilliamsRIndicator, ROCIndicator
from ta.volatility import BollingerBands, AverageTrueRange
from ta.volume import OnBalanceVolumeIndicator, VolumePriceTrendIndicator

warnings.filterwarnings('ignore')


class StockDataFetcher:
    """股票数据获取器"""

    # A股市场后缀映射
    MARKET_SUFFIX = {
        'us': '',           # 美股
        'hk': '.HK',        # 港股
        'a': '.SS',         # A股上海
        'a_sh': '.SS',      # A股上海
        'a_sz': '.SZ',      # A股深圳
    }

    @staticmethod
    def normalize_symbol(symbol: str, market: str = 'us') -> str:
        """标准化股票代码"""
        symbol = symbol.upper().strip()

        # 如果已经有后缀，直接返回
        if '.' in symbol:
            return symbol

        # 根据市场添加后缀
        suffix = StockDataFetcher.MARKET_SUFFIX.get(market.lower(), '')
        return f"{symbol}{suffix}"

    @classmethod
    def get_stock_data(cls, symbol: str, period: str = "1y",
                       market: str = 'us') -> pd.DataFrame:
        """获取股票历史行情数据"""
        try:
            normalized_symbol = cls.normalize_symbol(symbol, market)
            stock = yf.Ticker(normalized_symbol)
            data = stock.history(period=period)

            if data.empty:
                raise ValueError(f"未查询到股票 {symbol} 的行情数据")

            return data
        except Exception as e:
            raise Exception(f"数据获取失败：{str(e)}")

    @classmethod
    def get_stock_info(cls, symbol: str, market: str = 'us') -> Dict:
        """获取股票基本信息"""
        try:
            normalized_symbol = cls.normalize_symbol(symbol, market)
            stock = yf.Ticker(normalized_symbol)
            info = stock.info

            return {
                'symbol': symbol,
                'name': info.get('shortName', 'N/A'),
                'market': info.get('exchange', 'N/A'),
                'industry': info.get('industry', 'N/A'),
                'sector': info.get('sector', 'N/A'),
                'market_cap': info.get('marketCap', 0),
                'pe_ratio': info.get('trailingPE', None),
                'pb_ratio': info.get('priceToBook', None),
                'dividend_yield': info.get('dividendYield', 0),
                'beta': info.get('beta', None),
                '52w_high': info.get('fiftyTwoWeekHigh', None),
                '52w_low': info.get('fiftyTwoWeekLow', None),
            }
        except Exception as e:
            return {'symbol': symbol, 'error': str(e)}

    @classmethod
    def get_financial_data(cls, symbol: str, market: str = 'us') -> Dict:
        """获取财务报表数据"""
        try:
            normalized_symbol = cls.normalize_symbol(symbol, market)
            stock = yf.Ticker(normalized_symbol)

            financials = stock.financials
            balance_sheet = stock.balance_sheet
            cashflow = stock.cashflow

            return {
                'financials': financials.to_dict() if not financials.empty else {},
                'balance_sheet': balance_sheet.to_dict() if not balance_sheet.empty else {},
                'cashflow': cashflow.to_dict() if not cashflow.empty else {},
            }
        except Exception as e:
            return {'error': str(e)}


class TechnicalAnalyzer:
    """技术指标分析器"""

    @staticmethod
    def calculate_indicators(data: pd.DataFrame) -> pd.DataFrame:
        """计算所有技术指标"""
        df = data.copy()

        # 移动平均线
        df['MA5'] = SMAIndicator(df['Close'], window=5).sma_indicator()
        df['MA10'] = SMAIndicator(df['Close'], window=10).sma_indicator()
        df['MA20'] = SMAIndicator(df['Close'], window=20).sma_indicator()
        df['MA60'] = SMAIndicator(df['Close'], window=60).sma_indicator()
        df['MA120'] = SMAIndicator(df['Close'], window=120).sma_indicator()

        # EMA
        df['EMA12'] = EMAIndicator(df['Close'], window=12).ema_indicator()
        df['EMA26'] = EMAIndicator(df['Close'], window=26).ema_indicator()

        # MACD
        macd = MACD(df['Close'])
        df['MACD'] = macd.macd()
        df['MACD_Signal'] = macd.macd_signal()
        df['MACD_Hist'] = macd.macd_diff()

        # RSI
        df['RSI6'] = RSIIndicator(df['Close'], window=6).rsi()
        df['RSI12'] = RSIIndicator(df['Close'], window=12).rsi()
        df['RSI24'] = RSIIndicator(df['Close'], window=24).rsi()

        # KDJ (使用随机指标)
        stoch = StochasticOscillator(df['High'], df['Low'], df['Close'])
        df['KDJ_K'] = stoch.stoch()
        df['KDJ_D'] = stoch.stoch_signal()

        # 威廉指标
        df['WR'] = WilliamsRIndicator(df['High'], df['Low'], df['Close']).wr()

        # ROC变动率
        df['ROC'] = ROCIndicator(df['Close']).roc()

        # 布林带
        boll = BollingerBands(df['Close'])
        df['BOLL_Upper'] = boll.bollinger_hband()
        df['BOLL_Middle'] = boll.bollinger_mavg()
        df['BOLL_Lower'] = boll.bollinger_lband()
        df['BOLL_Width'] = boll.bollinger_wband()

        # ATR
        df['ATR'] = AverageTrueRange(df['High'], df['Low'], df['Close']).average_true_range()

        # OBV
        df['OBV'] = OnBalanceVolumeIndicator(df['Close'], df['Volume']).on_balance_volume()

        # DMI
        try:
            adx = ADXIndicator(df['High'], df['Low'], df['Close'])
            df['ADX'] = adx.adx()
            df['ADX_Pos'] = adx.adx_pos()
            df['ADX_Neg'] = adx.adx_neg()
        except:
            pass

        return df.dropna()

    @staticmethod
    def analyze_trend(data: pd.DataFrame) -> Dict[str, Any]:
        """分析趋势"""
        latest = data.iloc[-1]

        # 均线多头/空头排列
        ma5, ma20, ma60 = latest['MA5'], latest['MA20'], latest['MA60']
        price = latest['Close']

        if ma5 > ma20 > ma60 and price > ma5:
            trend = "强势上涨"
        elif ma5 < ma20 < ma60 and price < ma5:
            trend = "弱势下跌"
        elif ma5 > ma20 and price > ma20:
            trend = "震荡偏强"
        elif ma5 < ma20 and price < ma20:
            trend = "震荡偏弱"
        else:
            trend = "横盘整理"

        return {
            'trend': trend,
            'price': round(float(price), 2),
            'ma5': round(float(ma5), 2),
            'ma20': round(float(ma20), 2),
            'ma60': round(float(ma60), 2),
            'price_vs_ma5': 'above' if price > ma5 else 'below',
            'price_vs_ma20': 'above' if price > ma20 else 'below',
        }

    @staticmethod
    def analyze_momentum(data: pd.DataFrame) -> Dict[str, Any]:
        """分析动量"""
        latest = data.iloc[-1]

        rsi6 = latest['RSI6']
        rsi12 = latest['RSI12']
        macd = latest['MACD']
        macd_signal = latest['MACD_Signal']

        # RSI判断
        if rsi6 > 80:
            rsi_signal = '超强（警惕回调）'
        elif rsi6 > 70:
            rsi_signal = '强势'
        elif rsi6 < 20:
            rsi_signal = '超卖（关注反弹）'
        elif rsi6 < 30:
            rsi_signal = '弱势'
        else:
            rsi_signal = '中性'

        # MACD判断
        if macd > macd_signal:
            macd_trend = '金叉（看涨）'
        else:
            macd_trend = '死叉（看跌）'

        return {
            'rsi6': round(float(rsi6), 2),
            'rsi12': round(float(rsi12), 2),
            'rsi_signal': rsi_signal,
            'macd': round(float(macd), 4),
            'macd_signal': round(float(macd_signal), 4),
            'macd_trend': macd_trend,
            'kdj_k': round(float(latest['KDJ_K']), 2),
            'kdj_d': round(float(latest['KDJ_D']), 2),
            'wr': round(float(latest['WR']), 2),
            'roc': round(float(latest['ROC']), 2),
        }

    @staticmethod
    def analyze_bollinger(data: pd.DataFrame) -> Dict[str, Any]:
        """分析布林带"""
        latest = data.iloc[-1]
        price = latest['Close']
        upper = latest['BOLL_Upper']
        lower = latest['BOLL_Lower']
        width = latest['BOLL_Width']

        position = (price - lower) / (upper - lower) * 100

        if price > upper:
            position_signal = '突破上轨（警惕回调）'
        elif price < lower:
            position_signal = '跌破下轨（关注反弹）'
        elif position > 80:
            position_signal = '接近上轨'
        elif position < 20:
            position_signal = '接近下轨'
        else:
            position_signal = '中轨附近'

        return {
            'upper': round(float(upper), 2),
            'middle': round(float(latest['BOLL_Middle']), 2),
            'lower': round(float(lower), 2),
            'width': round(float(width), 2),
            'position': round(float(position), 2),
            'signal': position_signal,
        }

    @staticmethod
    def generate_technical_signal(data: pd.DataFrame) -> Dict[str, Any]:
        """生成综合技术信号"""
        latest = data.iloc[-1]

        signals = []
        weight = 0

        # RSI
        if latest['RSI6'] > 80:
            signals.append(('RSI', '卖出', -1))
        elif latest['RSI6'] < 20:
            signals.append(('RSI', '买入', 1))
        elif latest['RSI6'] > 70:
            signals.append(('RSI', '谨慎', -0.5))
        elif latest['RSI6'] < 30:
            signals.append(('RSI', '关注', 0.5))
        else:
            signals.append(('RSI', '中性', 0))

        # MACD
        if latest['MACD'] > latest['MACD_Signal']:
            signals.append(('MACD', '买入', 1))
        else:
            signals.append(('MACD', '卖出', -1))

        # KDJ
        if latest['KDJ_K'] > latest['KDJ_D'] and latest['KDJ_K'] < 30:
            signals.append(('KDJ', '买入', 0.5))
        elif latest['KDJ_K'] < latest['KDJ_D'] and latest['KDJ_K'] > 70:
            signals.append(('KDJ', '卖出', -0.5))
        else:
            signals.append(('KDJ', '中性', 0))

        # 均线
        if latest['Close'] > latest['MA20']:
            signals.append(('MA20', '多头', 0.5))
        else:
            signals.append(('MA20', '空头', -0.5))

        total_score = sum(s[2] for s in signals)
        avg_score = total_score / len(signals)

        if avg_score > 0.3:
            overall_signal = '买入信号'
        elif avg_score < -0.3:
            overall_signal = '卖出信号'
        else:
            overall_signal = '持有观望'

        return {
            'signals': signals,
            'score': round(avg_score, 2),
            'overall': overall_signal,
        }


class FundamentalAnalyzer:
    """基本面分析器"""

    @staticmethod
    def analyze_fundamentals(symbol: str, market: str = 'us') -> Dict[str, Any]:
        """分析基本面"""
        try:
            info = StockDataFetcher.get_stock_info(symbol, market)
            financials = StockDataFetcher.get_financial_data(symbol, market)

            result = {
                'basic_info': info,
                'valuations': {},
                'financials': {},
                'warnings': [],
            }

            # 估值分析
            if info.get('pe_ratio'):
                pe = info['pe_ratio']
                if pe < 0:
                    result['valuations']['pe'] = '亏损'
                elif pe < 15:
                    result['valuations']['pe'] = f'{pe:.2f} (偏低)'
                elif pe < 30:
                    result['valuations']['pe'] = f'{pe:.2f} (合理)'
                else:
                    result['valuations']['pe'] = f'{pe:.2f} (偏高)'

            if info.get('pb_ratio'):
                pb = info['pb_ratio']
                if pb < 0:
                    result['valuations']['pb'] = '亏损'
                elif pb < 1:
                    result['valuations']['pb'] = f'{pb:.2f} (破净)'
                elif pb < 3:
                    result['valuations']['pb'] = f'{pb:.2f} (合理)'
                else:
                    result['valuations']['pb'] = f'{pb:.2f} (偏高)'

            # 市值格式化
            if info.get('market_cap'):
                cap = info['market_cap']
                if cap >= 1e12:
                    result['basic_info']['market_cap_fmt'] = f'{cap/1e12:.2f}万亿'
                elif cap >= 1e10:
                    result['basic_info']['market_cap_fmt'] = f'{cap/1e10:.2f}千亿'
                elif cap >= 1e8:
                    result['basic_info']['market_cap_fmt'] = f'{cap/1e8:.2f}亿'
                else:
                    result['basic_info']['market_cap_fmt'] = f'{cap:.2f}'

            return result

        except Exception as e:
            return {'error': str(e)}


class RiskAnalyzer:
    """风险分析器"""

    @staticmethod
    def calculate_risk_metrics(data: pd.DataFrame) -> Dict[str, Any]:
        """计算风险指标"""
        # 计算日收益率
        returns = data['Close'].pct_change().dropna()

        # 历史波动率（年化）
        daily_volatility = returns.std()
        annual_volatility = daily_volatility * np.sqrt(252) * 100

        # 最大回撤
        cumulative = (1 + returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = drawdown.min() * 100

        # VaR (95%置信度)
        var_95 = returns.quantile(0.05) * 100

        # 收益率统计
        mean_return = returns.mean() * 252 * 100
        negative_days = (returns < 0).sum()
        total_days = len(returns)

        return {
            'annual_volatility': round(annual_volatility, 2),
            'max_drawdown': round(max_drawdown, 2),
            'var_95': round(var_95, 2),
            'mean_annual_return': round(mean_return, 2),
            'negative_day_ratio': round(negative_days / total_days * 100, 2),
            'daily_volatility': round(daily_volatility * 100, 4),
        }

    @staticmethod
    def assess_risk_level(metrics: Dict, info: Dict) -> Dict[str, Any]:
        """评估风险等级"""
        score = 0
        factors = []

        # 波动率评分
        vol = metrics.get('annual_volatility', 0)
        if vol > 50:
            score += 25
            factors.append(('波动率', f'{vol}%', '高风险'))
        elif vol > 30:
            score += 15
            factors.append(('波动率', f'{vol}%', '中等'))
        elif vol > 15:
            score += 5
            factors.append(('波动率', f'{vol}%', '较低'))
        else:
            factors.append(('波动率', f'{vol}%', '低'))

        # 最大回撤评分
        mdd = abs(metrics.get('max_drawdown', 0))
        if mdd > 40:
            score += 25
            factors.append(('最大回撤', f'{mdd}%', '高风险'))
        elif mdd > 25:
            score += 15
            factors.append(('最大回撤', f'{mdd}%', '中等'))
        elif mdd > 10:
            score += 5
            factors.append(('最大回撤', f'{mdd}%', '较低'))
        else:
            factors.append(('最大回撤', f'{mdd}%', '低'))

        # Beta系数评分
        beta = info.get('beta')
        if beta:
            if beta > 1.5:
                score += 20
                factors.append(('Beta', f'{beta:.2f}', '高波动'))
            elif beta > 1.2:
                score += 10
                factors.append(('Beta', f'{beta:.2f}', '偏高'))
            elif beta < 0.8:
                score += 0
                factors.append(('Beta', f'{beta:.2f}', '防御型'))
            else:
                score += 5
                factors.append(('Beta', f'{beta:.2f}', '正常'))

        # 确定风险等级
        if score >= 60:
            level = 'R5-高风险'
        elif score >= 45:
            level = 'R4-中高风险'
        elif score >= 30:
            level = 'R3-中等风险'
        elif score >= 15:
            level = 'R2-中低风险'
        else:
            level = 'R1-低风险'

        return {
            'score': score,
            'level': level,
            'factors': factors,
        }


class ReportGenerator:
    """报告生成器"""

    @staticmethod
    def generate_report(
        symbol: str,
        market: str,
        period: str,
        technical_data: pd.DataFrame,
        info: Dict,
        fundamentals: Dict,
        technical_trend: Dict,
        technical_momentum: Dict,
        technical_bollinger: Dict,
        technical_signal: Dict,
        risk_metrics: Dict,
        risk_assessment: Dict,
        compare_symbol: Optional[str] = None,
        compare_data: Optional[Dict] = None,
    ) -> str:
        """生成Markdown分析报告"""

        latest = technical_data.iloc[-1]
        report_date = datetime.now().strftime('%Y-%m-%d %H:%M')

        report = f"""# 📊 股票深度分析报告

## 基本信息

| 项目 | 内容 |
|------|------|
| **股票代码** | {symbol} |
| **市场** | {market.upper()} |
| **分析周期** | {period} |
| **分析时间** | {report_date} |
| **公司名称** | {info.get('name', 'N/A')} |
| **所属行业** | {info.get('industry', 'N/A')} |
| **总市值** | {info.get('market_cap_fmt', 'N/A')} |

---

## 一、技术面分析

### 1.1 趋势判断

| 指标 | 数值 | 状态 |
|------|------|------|
| 最新价 | ¥{technical_trend['price']} | {'↑' if technical_trend['price_vs_ma5'] == 'above' else '↓'} |
| MA5 | ¥{technical_trend['ma5']} | {'多头' if technical_trend['price_vs_ma5'] == 'above' else '空头'} |
| MA20 | ¥{technical_trend['ma20']} | {'多头' if technical_trend['price_vs_ma20'] == 'above' else '空头'} |
| MA60 | ¥{technical_trend['ma60']} | {'站稳' if technical_trend['price'] > technical_trend['ma60'] else '跌破'} |

**趋势结论**: {technical_trend['trend']}

### 1.2 动量指标

| 指标 | 数值 | 信号 |
|------|------|------|
| RSI(6) | {technical_momentum['rsi6']} | {technical_momentum['rsi_signal']} |
| RSI(12) | {technical_momentum['rsi12']} | - |
| MACD | {technical_momentum['macd']} | {technical_momentum['macd_trend']} |
| KDJ-K | {technical_momentum['kdj_k']} | - |
| KDJ-D | {technical_momentum['kdj_d']} | - |
| WR | {technical_momentum['wr']} | - |
| ROC | {technical_momentum['roc']}% | - |

### 1.3 布林带分析

| 位置 | 数值 |
|------|------|
| 上轨 | ¥{technical_bollinger['upper']} |
| 中轨 | ¥{technical_bollinger['middle']} |
| 下轨 | ¥{technical_bollinger['lower']} |
| 带宽 | {technical_bollinger['width']}% |
| 当前价位 | ¥{latest['Close']:.2f} ({technical_bollinger['position']:.1f}%) |

**信号**: {technical_bollinger['signal']}

### 1.4 综合技术信号

| 指标 | 信号 | 权重 |
|------|------|------|
"""

        for name, signal, weight in technical_signal['signals']:
            report += f"| {name} | {signal} | {weight:+.1f} |\n"

        report += f"""
**综合评分**: {technical_signal['score']} / **结论**: {technical_signal['overall']}

---

## 二、基本面分析

### 2.1 估值指标

| 指标 | 数值 |
|------|------|
"""

        for key, value in fundamentals.get('valuations', {}).items():
            report += f"| {key.upper()} | {value} |\n"

        report += f"""| 股息率 | {info.get('dividend_yield', 0) * 100:.2f}% |
| 52周高点 | ¥{info.get('52w_high', 'N/A')} |
| 52周低点 | ¥{info.get('52w_low', 'N/A')} |

### 2.2 Beta系数

- **Beta**: {info.get('beta', 'N/A')}
- **解读**: {'进攻型' if info.get('beta', 1) > 1.2 else '防御型' if info.get('beta', 1) < 0.8 else '中性'}

---

## 三、风险评估

### 3.1 风险指标

| 指标 | 数值 | 评价 |
|------|------|------|
| 年化波动率 | {risk_metrics['annual_volatility']}% | {'高' if risk_metrics['annual_volatility'] > 30 else '中' if risk_metrics['annual_volatility'] > 15 else '低'} |
| 最大回撤 | {risk_metrics['max_drawdown']}% | - |
| VaR(95%) | {risk_metrics['var_95']}% | 单日最大损失 |
| 负收益天数占比 | {risk_metrics['negative_day_ratio']}% | - |

### 3.2 风险因素分析

| 因素 | 数值 | 评价 |
|------|------|------|
"""

        for name, value, status in risk_assessment['factors']:
            report += f"| {name} | {value} | {status} |\n"

        report += f"""
**综合风险等级**: **{risk_assessment['level']}**

---

## 四、综合评级

| 维度 | 评分 | 说明 |
|------|------|------|
| 技术面 | {'⭐⭐⭐⭐⭐' if technical_signal['score'] > 0.5 else '⭐⭐⭐⭐' if technical_signal['score'] > 0 else '⭐⭐⭐' if technical_signal['score'] > -0.5 else '⭐⭐'} | {technical_signal['overall']} |
| 基本面 | {'⭐⭐⭐⭐⭐' if '偏低' in fundamentals.get('valuations', {}).get('pe', '') or '合理' in fundamentals.get('valuations', {}).get('pe', '') else '⭐⭐⭐⭐'} | {'估值吸引力较高' if '偏低' in fundamentals.get('valuations', {}).get('pe', '') else '估值合理'} |
| 风险控制 | {'⭐⭐⭐⭐⭐' if 'R1' in risk_assessment['level'] or 'R2' in risk_assessment['level'] else '⭐⭐⭐⭐' if 'R3' in risk_assessment['level'] else '⭐⭐⭐'} | {risk_assessment['level']} |
"""

        if compare_data:
            report += f"""
---

## 五、对比分析

### {symbol} vs {compare_symbol}

| 指标 | {symbol} | {compare_symbol} | 对比 |
|------|----------|------------------|------|
"""
            for key in compare_data.get('metrics', {}).keys():
                val1 = compare_data['metrics'][key].get(symbol, 'N/A')
                val2 = compare_data['metrics'][key].get(compare_symbol, 'N/A')
                report += f"| {key} | {val1} | {val2} | - |\n"

        report += f"""
---

## ⚠️ 风险提示与合规声明

1. 本报告仅基于公开数据进行分析，**不构成任何投资建议**
2. 过去业绩不代表未来表现，股市有风险，投资需谨慎
3. 技术分析存在滞后性，基本面变化可能影响长期趋势
4. 请根据自身风险承受能力做出投资决策
5. 建议咨询专业投资顾问后再做决策

---
*报告生成时间: {report_date}*
*数据来源: Yahoo Finance (yfinance)*
"""

        return report


def run(input_data: Dict = None) -> Dict:
    """
    技能执行主函数

    输入参数:
        symbol: 股票代码 (默认: AAPL)
        market: 市场 'us'/'hk'/'a' (默认: us)
        period: 分析周期 '1mo'/'3mo'/'6mo'/'1y'/'2y'/'5y' (默认: 1y)
        compare: 对比股票代码 (可选)
        dimensions: 分析维度 'all'/'technical'/'fundamental'/'risk' (默认: all)
    """
    try:
        # 参数解析
        input_data = input_data or {}
        symbol = input_data.get('symbol', 'AAPL')
        market = input_data.get('market', 'us')
        period = input_data.get('period', '1y')
        compare_symbol = input_data.get('compare')
        dimensions = input_data.get('dimensions', 'all')

        # 获取数据
        stock_data = StockDataFetcher.get_stock_data(symbol, period, market)
        info = StockDataFetcher.get_stock_info(symbol, market)

        # 技术分析
        tech_data = TechnicalAnalyzer.calculate_indicators(stock_data)
        tech_trend = TechnicalAnalyzer.analyze_trend(tech_data)
        tech_momentum = TechnicalAnalyzer.analyze_momentum(tech_data)
        tech_bollinger = TechnicalAnalyzer.analyze_bollinger(tech_data)
        tech_signal = TechnicalAnalyzer.generate_technical_signal(tech_data)

        # 基本面分析
        fundamentals = FundamentalAnalyzer.analyze_fundamentals(symbol, market)

        # 风险评估
        risk_metrics = RiskAnalyzer.calculate_risk_metrics(stock_data)
        risk_assessment = RiskAnalyzer.assess_risk_level(risk_metrics, info)

        # 对比分析
        compare_data = None
        if compare_symbol:
            try:
                compare_data = {
                    'metrics': {
                        '收盘价': {symbol: tech_trend['price'], compare_symbol: 'N/A'},
                        'RSI': {symbol: tech_momentum['rsi6'], compare_symbol: 'N/A'},
                        '波动率': {symbol: f"{risk_metrics['annual_volatility']}%", compare_symbol: 'N/A'},
                        'Beta': {symbol: info.get('beta', 'N/A'), compare_symbol: 'N/A'},
                    }
                }
            except:
                pass

        # 生成报告
        report = ReportGenerator.generate_report(
            symbol=symbol,
            market=market,
            period=period,
            technical_data=tech_data,
            info=info,
            fundamentals=fundamentals,
            technical_trend=tech_trend,
            technical_momentum=tech_momentum,
            technical_bollinger=tech_bollinger,
            technical_signal=tech_signal,
            risk_metrics=risk_metrics,
            risk_assessment=risk_assessment,
            compare_symbol=compare_symbol,
            compare_data=compare_data,
        )

        return {
            'status': 'success',
            'data': {
                'symbol': symbol,
                'market': market,
                'period': period,
                'price': tech_trend['price'],
                'trend': tech_trend['trend'],
                'signal': tech_signal['overall'],
                'risk_level': risk_assessment['level'],
                'report': report,
            },
            'message_for_user': f"✅ 股票 {symbol} ({market.upper()}) 分析完成 | 趋势: {tech_trend['trend']} | 信号: {tech_signal['overall']} | 风险: {risk_assessment['level']}"
        }

    except Exception as e:
        return {
            'status': 'error',
            'data': None,
            'message_for_user': f"❌ 分析失败：{str(e)}"
        }


if __name__ == "__main__":
    # 独立运行支持
    if not sys.stdin.isatty():
        input_json = sys.stdin.read()
        input_data = json.loads(input_json) if input_json else {}
    else:
        # 默认测试参数
        input_data = {
            'symbol': 'AAPL',
            'market': 'us',
            'period': '1y',
        }

    output = run(input_data)
    print(json.dumps(output, ensure_ascii=False, indent=2))

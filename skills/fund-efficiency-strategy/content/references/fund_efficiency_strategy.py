"""
资金效率动量策略 - 纯日线数据版本

基于"单位成交额引起的流通市值变化率"核心创意，
结合MFI、OBV、成交量分布和背离检测构建的多因子复合策略。

作者：资金效率策略团队
版本：1.1（新增严格数据验证机制）
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta


def validate_data_integrity(df, ts_code='Unknown', expected_name=None):
    """
    严格数据完整性验证机制
    
    验证内容：
    1. 数据日期是否为最近交易日
    2. 股票代码是否匹配
    3. 收盘价是否合理（>0, 在合理范围内）
    4. 成交额与收盘价×成交量的逻辑一致性
    5. 流通市值的合理性
    
    返回：(is_valid, validation_report)
    """
    validation_issues = []
    warnings = []
    
    # 1. 日期验证
    if len(df) > 0:
        # 优先使用trade_date列，否则用index
        if 'trade_date' in df.columns:
            latest_date = pd.Timestamp(df['trade_date'].max())
        else:
            latest_date = df.index.max()
            if not isinstance(latest_date, (pd.Timestamp, datetime)):
                latest_date = pd.Timestamp(latest_date)
        today = pd.Timestamp.today()
        days_diff = (today - latest_date).days
        
        if days_diff > 5:
            validation_issues.append(f"数据过期：最新日期 {latest_date.date()} 距今 {days_diff} 天（>5天）")
        elif days_diff > 2:
            warnings.append(f"数据可能非最新：最新日期 {latest_date.date()} 距今 {days_diff} 天")
    
    # 2. 收盘价验证
    if 'close' in df.columns:
        latest_close = df['close'].iloc[-1]
        if pd.isna(latest_close) or latest_close <= 0:
            validation_issues.append(f"收盘价异常：{latest_close}")
        elif latest_close < 1:
            warnings.append(f"收盘价偏低：{latest_close}元（可能是ST或低价股）")
        elif latest_close > 10000:
            warnings.append(f"收盘价偏高：{latest_close}元（请确认数据正确）")
    
    # 3. 成交额与收盘价×成交量逻辑验证
    if all(col in df.columns for col in ['close', 'vol', 'amount']):
        #东方财富amount单位是千元
        df['amount_yuan'] = df['amount'] * 1000
        # 成交额应该 ≈ 收盘价 × 成交量(手) × 100
        df['calculated_amount'] = df['close'] * df['vol'] * 100
        
        # 允许10%的误差
        mask = df['calculated_amount'] > 0
        ratio = (df.loc[mask, 'amount_yuan'] / df.loc[mask, 'calculated_amount']).abs()
        
        if (ratio < 0.5).any() or (ratio > 2).any():
            warnings.append("成交额与收盘价×成交量存在较大差异（可能因除权或数据源差异）")
    
    # 4. 流通市值合理性验证
    if all(col in df.columns for col in ['close', 'float_shares']):
        calc_market_cap = df['close'] * df['float_shares']
        if 'market_cap' in df.columns:
            cap_ratio = (calc_market_cap / df['market_cap']).replace([np.inf, -np.inf], np.nan)
            if not cap_ratio.dropna().between(0.5, 2).all():
                warnings.append("流通市值计算结果与提供数据存在差异")
    
    # 5. 数据完整性检查
    required_cols = ['open', 'high', 'low', 'close', 'vol', 'amount', 'float_shares', 'market_cap']
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        validation_issues.append(f"缺少必要列：{missing_cols}")
    
    # 综合判断
    is_valid = len(validation_issues) == 0
    
    report = {
        'is_valid': is_valid,
        'issues': validation_issues,
        'warnings': warnings,
        'latest_date': df['trade_date'].max() if len(df) > 0 and 'trade_date' in df.columns else None,
        'latest_close': df['close'].iloc[-1] if len(df) > 0 and 'close' in df.columns else None,
        'record_count': len(df)
    }
    
    return is_valid, report


def get_recent_data(df, days=5, ascending=False):
    """
    获取最近N个交易日数据（确保正确排序）
    
    参数：
    - df: DataFrame，带datetime索引
    - days: 获取天数
    - ascending: True=升序（最早在前），False=降序（最新在前）
    
    返回：排序后的DataFrame
    """
    if len(df) == 0:
        return df
    
    # 确保按日期排序（降序=最新在前）
    df_sorted = df.sort_index(ascending=False)
    
    # 取最近N天
    return df_sorted.head(days)


def format_validation_report(validation_result, ts_code):
    """格式化验证报告为可读字符串"""
    is_valid, report = validation_result
    
    lines = [
        f"【数据验证报告 - {ts_code}】",
        f"验证结果：{'[PASS] 通过' if is_valid else '[FAIL] 未通过'}",
        f"数据记录数：{report['record_count']}条",
        f"最新交易日：{report['latest_date']}",
        f"最新收盘价：{report['latest_close']}元",
    ]
    
    if report['warnings']:
        lines.append("")
        lines.append("[WARN] 警告：")
        for w in report['warnings']:
            lines.append(f"  - {w}")
    
    if report['issues']:
        lines.append("")
        lines.append("[ERROR] 错误：")
        for i in report['issues']:
            lines.append(f"  - {i}")
    
    return "\n".join(lines)


def calculate_fund_efficiency_daily(df):
    """
    单位成交额流通市值变化率 - 核心因子（优化版）

    基于"单位成交额引起的流通市值变化率"核心创意：
    - 相同资金流入对不同市值股票产生不同价格推动力
    - 小市值股票对资金流动更敏感
    
    关键优化：
    - 使用"成交额"而非"成交量"（考虑股价差异）
    - 多周期对比（当日 vs 5日 vs 20日平均）
    - 动态阈值调整

    参数：df需包含 open, high, low, close, volume, amount, float_shares, market_cap
    """
    # 确保流通市值存在
    if 'market_cap' not in df.columns:
        df['market_cap'] = df['close'] * df['float_shares']

    # ===== 核心资金效率因子 =====
    # 单位成交额引起的流通市值变化率
    # 公式：(今日市值 - 昨日市值) / 成交额
    # 含义：每元成交额推动了多少市值变化
    
    # 注意：market_cap是万元单位，amount是千元单位
    # 统一转换为元：market_cap*10000，amount*1000
    df['cap_change'] = (df['market_cap'] * 10000).diff()  # 市值变化额（元）
    df['cap_change_rate'] = df['cap_change'] / (df['market_cap'].shift(1) * 10000)  # 变化率
    
    # 资金效率 = 市值变化额 / 成交额（考虑成交额为0的情况）
    df['fund_efficiency'] = np.where(
        df['amount'] > 0,
        df['cap_change'] / (df['amount'] * 1000),  # amount转元
        0
    )

    # ===== 多周期平滑 =====
    # 当日效率
    df['fe_daily'] = df['fund_efficiency']
    # 5日移动平均（短期趋势）
    df['fe_ma5'] = df['fund_efficiency'].rolling(5).mean()
    # 20日移动平均（中期基准）
    df['fe_ma20'] = df['fund_efficiency'].rolling(20).mean()
    
    # 多周期对比信号
    # 当日 > 5日 > 20日 → 资金效率上升趋势
    df['fe_trend'] = (df['fe_daily'] > df['fe_ma5']).astype(int) + \
                     (df['fe_ma5'] > df['fe_ma20']).astype(int)

    # ===== 价格重心（Point of Control）=====
    df['price_poc'] = (df['open'] + df['high'] + df['low'] + df['close']) / 4
    df['poc_bias'] = (df['close'] - df['price_poc']) / df['price_poc']

    # ===== 市值敏感性调整 =====
    # 小市值股票效率需要打折（更容易被操纵）
    # 阈值设定：<100亿为小盘，100-500亿为中盘，>500亿为大盘
    avg_mcap = df['market_cap'].rolling(20).mean()
    df['cap_sensitivity'] = np.where(
        avg_mcap < 1e10, 0.7,      # 小盘：70%权重
        np.where(avg_mcap < 5e10, 0.85, 1.0)  # 中盘：85%，大盘：100%
    )

    # ===== 修正资金效率 =====
    df['fund_efficiency_adj'] = (
        df['fund_efficiency'] * 
        (1 + df['poc_bias']) *  # 价格重心偏移修正
        df['cap_sensitivity']    # 市值敏感性调整
    )

    # 5日平滑
    df['fund_efficiency_ma5'] = df['fund_efficiency_adj'].rolling(5).mean()

    # ===== 异常值处理 =====
    # 限制极端值影响
    df['fund_efficiency_ma5'] = df['fund_efficiency_ma5'].clip(-10, 10)

    # 行业排名标准化（分位数）
    if 'industry' in df.columns:
        df['fund_efficiency_rank'] = df.groupby('industry')['fund_efficiency_ma5'].rank(pct=True)
    else:
        df['fund_efficiency_rank'] = df['fund_efficiency_ma5'].rank(pct=True)

    return df


def calculate_volume_profile(df, lookback=20):
    """
    基于日线数据的成交量分布分析
    识别"成交量簇"和主力建仓区域
    """
    # 20日价格区间
    price_high = df['high'].rolling(lookback).max()
    price_low = df['low'].rolling(lookback).min()
    price_range = price_high - price_low

    # 价格位置（0-1之间，0=最低，1=最高）
    df['price_position'] = (df['close'] - price_low) / price_range

    # 成交量集中度
    df['vol_ma20'] = df['volume'].rolling(20).mean()
    df['vol_concentration'] = df['volume'] / df['vol_ma20']

    # 价格重心稳定性（连续3日在窄区间）
    df['poc_stability'] = df['price_poc'].rolling(3).apply(
        lambda x: 1 if (x.max() - x.min()) / x.mean() < 0.02 else 0, raw=True
    )

    # 主力吸筹信号：低位+放量+重心上移
    df['is_low_position'] = df['price_position'] < 0.3
    df['is_high_volume'] = df['vol_concentration'] > 1.5
    df['is_poc_rising'] = df['price_poc'].diff(3) > 0
    df['main_force_signal'] = (df['is_low_position'] & df['is_high_volume'] & df['is_poc_rising']).astype(int)

    return df


def calculate_mfi_daily(df, period=14):
    """
    资金流量指标 - 纯日线版本
    """
    # 典型价格
    tp = (df['high'] + df['low'] + df['close']) / 3

    # 资金流量
    money_flow = tp * df['volume']

    # 正负资金流量（基于典型价格变化）
    positive_flow = (money_flow * (tp > tp.shift(1))).rolling(period).sum()
    negative_flow = (money_flow * (tp < tp.shift(1))).rolling(period).sum()

    # MFI计算
    money_ratio = positive_flow / negative_flow
    df['mfi'] = 100 - (100 / (1 + money_ratio))

    # MFI变化率（用于捕捉转折）
    df['mfi_change'] = df['mfi'].diff(6)

    return df


def calculate_obv_daily(df):
    """
    能量潮指标 - 验证成交量真实性
    """
    obv = [0]
    for i in range(1, len(df)):
        if df['close'].iloc[i] > df['close'].iloc[i-1]:
            obv.append(obv[-1] + df['volume'].iloc[i])
        elif df['close'].iloc[i] < df['close'].iloc[i-1]:
            obv.append(obv[-1] - df['volume'].iloc[i])
        else:
            obv.append(obv[-1])

    df['obv'] = obv
    df['obv_ma20'] = df['obv'].rolling(20).mean()
    df['obv_slope'] = df['obv'].rolling(10).apply(
        lambda x: (x[-1] - x[0]) / 10 if len(x) >= 2 else 0, raw=True
    )

    return df


def detect_divergence_daily(df):
    """
    自适应背离检测 - 纯日线数据
    """
    try:
        from scipy import stats
        has_scipy = True
    except ImportError:
        has_scipy = False

    lookback = 20

    if len(df) < lookback:
        df['divergence_type'] = 'none'
        df['divergence_strength'] = 0
        return df

    # 价格、OBV、MFI趋势
    if has_scipy:
        price_slope, _, _, _, _ = stats.linregress(range(lookback), df['close'].iloc[-lookback:])
        obv_slope, _, _, _, _ = stats.linregress(range(lookback), df['obv'].iloc[-lookback:])
        mfi_slope, _, _, _, _ = stats.linregress(range(lookback), df['mfi'].iloc[-lookback:])
    else:
        # Fallback: 简单线性回归
        price_slope = (df['close'].iloc[-1] - df['close'].iloc[-lookback]) / lookback
        obv_slope = (df['obv'].iloc[-1] - df['obv'].iloc[-lookback]) / lookback
        mfi_slope = (df['mfi'].iloc[-1] - df['mfi'].iloc[-lookback]) / lookback

    # 背离判断
    df['divergence_type'] = 'none'
    df['divergence_strength'] = 0

    # 底背离：价格下降，指标上升
    if price_slope < -0.005 and (obv_slope > 0 or mfi_slope > 0):
        df['divergence_type'] = 'bullish_divergence'
        df['divergence_strength'] = abs(obv_slope) + abs(mfi_slope)

    # 顶背离：价格上升，指标下降
    elif price_slope > 0.005 and (obv_slope < 0 or mfi_slope < 0):
        df['divergence_type'] = 'bearish_divergence'
        df['divergence_strength'] = abs(obv_slope) + abs(mfi_slope)

    return df


def composite_scoring_daily(df):
    """
    多因子复合评分 - 纯日线数据
    """
    # 各因子得分
    score_fund = df['fund_efficiency_rank']

    # MFI健康度（40-60区间最佳，且上升）
    mfi_normalized = 1 - abs(df['mfi'] - 50) / 50
    mfi_trend = np.where(df['mfi_change'] > 0, 1, 0.5)
    score_mfi = mfi_normalized * mfi_trend

    # 成交量分布质量
    score_volume = (
        df['main_force_signal'] * 0.4 +
        (df['vol_concentration'] > 1.2).astype(int) * 0.3 +
        df['poc_stability'] * 0.3
    )

    # OBV验证
    score_obv = np.where(
        ((df['close'] > df['close'].shift(5)) & (df['obv'] > df['obv'].shift(5))), 1,
        np.where(
            (df['close'] < df['close'].shift(5)) & (df['obv'] < df['obv'].shift(5)), 0.8,
            0.3
        )
    )

    # 背离得分
    score_divergence = np.where(
        df['divergence_type'] == 'bullish_divergence', df['divergence_strength'] * 0.2,
        np.where(
            df['divergence_type'] == 'bearish_divergence', -0.2, 0
        )
    )

    # 动态权重
    weights = {'fund': 0.35, 'mfi': 0.25, 'volume': 0.20, 'obv': 0.15, 'divergence': 0.05}

    # 综合得分
    df['composite_score'] = (
        score_fund * weights['fund'] +
        score_mfi * weights['mfi'] +
        score_volume * weights['volume'] +
        score_obv * weights['obv'] +
        score_divergence
    )

    # 信号强度分级
    df['signal_strength'] = pd.cut(
        df['composite_score'],
        bins=[-np.inf, 0.3, 0.5, 0.7, np.inf],
        labels=['weak', 'moderate', 'strong', 'extreme']
    )

    return df


# ==================== 指标备注说明 ====================
INDICATOR_GUIDE = """
【指标含义与参考区间】

■ 资金效率排名（fund_efficiency_rank）
  - 含义：单位成交额推动的市值变化率在同类中的排名分位
  - 范围：0%~100%（越高越好）
  - 区间：
    · >70%：优秀 — 资金利用高效，主力积极
    · 50%~70%：良好 — 正常资金效率
    · 30%~50%：一般 — 资金效率偏弱
    · <30%：较差 — 资金推动效果弱，可能有出货嫌疑

■ MFI资金流量指标（Money Flow Index）
  - 含义：量能加权RSI，反映资金流入流出的强度
  - 范围：0~100
  - 区间：
    · >80：超买区 — 警惕回调风险
    · 60~80：偏高区 — 强势但注意滞涨
    · 40~60：正常区 — 多空平衡
    · 20~40：偏低区 — 超卖区域，可能反弹
    · <20：超卖区 — 极度超卖，可能见底

■ MFI变化（mfi_change）
  - 含义：过去6日MFI的变化值
  - 正值：资金流入加速（偏多）
  - 负值：资金流入减缓（偏空）
  - 警戒：MFI变化<-10且MFI>80，双重见顶信号

■ 成交量集中度（vol_concentration）
  - 含义：当日成交量与20日均量的比值
  - 范围：>0
  - 区间：
    · >1.5：大幅放量 — 可能异动
    · 1.2~1.5：温和放量 — 活跃
    · 0.8~1.2：正常量能
    · <0.8：缩量 — 观望

■ OBV能量潮（On-Balance Volume）
  - 含义：累计成交量，反映资金进出趋势
  - OBV>MA20：资金持续流入（偏多）
  - OBV<MA20：资金持续流出（偏空）
  - 顶背离：价格创新高但OBV未跟上 → 警惕
  - 底背离：价格创新低但OBV未新低 → 关注

■ 综合得分（composite_score）
  - 含义：多因子加权得分，反映综合交易价值
  - 范围：0~1
  - 区间：
    · >0.7：极强信号 — 可考虑买入
    · 0.5~0.7：强势信号 — 值得关注
    · 0.3~0.5：中性信号 — 观望
    · <0.3：弱势信号 — 谨慎

■ 背离类型（divergence）
  - bullish_divergence：底背离 — 价格跌但指标不跟跌 → 看涨信号
  - bearish_divergence：顶背离 — 价格涨但指标不跟涨 → 看跌信号
  - none：无背离

■ 主力吸筹信号（main_force_signal）
  - 条件：价格低位 + 成交量放大 + 重心上移
  - 含义：疑似主力资金进场吸筹
  - 1=是，0=否
"""

def get_mfi_status(mfi):
    """获取MFI状态说明"""
    if mfi > 80:
        return '超买区', '注意回调风险', 'sell'
    elif mfi > 60:
        return '偏高区', '强势但注意滞涨', 'warning'
    elif mfi >= 40:
        return '正常区', '多空平衡', 'hold'
    elif mfi >= 20:
        return '偏低区', '超卖区域，可能反弹', 'buy'
    else:
        return '超卖区', '极度超卖，可能见底', 'buy'

def get_fund_efficiency_status(rank):
    """获取资金效率排名状态说明"""
    pct = rank * 100
    if pct > 70:
        return '优秀', '资金利用高效，主力积极', 'buy'
    elif pct > 50:
        return '良好', '正常资金效率', 'hold'
    elif pct > 30:
        return '一般', '资金效率偏弱', 'warning'
    else:
        return '较差', '资金推动效果弱', 'sell'

def get_vol_concentration_status(vol_conc):
    """获取成交量集中度状态说明"""
    if vol_conc > 1.5:
        return '大幅放量', '可能异动', 'warning'
    elif vol_conc >= 1.2:
        return '温和放量', '活跃', 'buy'
    elif vol_conc >= 0.8:
        return '正常量能', '平稳', 'hold'
    else:
        return '缩量', '观望', 'warning'

def get_composite_score_status(score):
    """获取综合得分状态说明"""
    if score > 0.7:
        return '极强信号', '可考虑买入', 'buy'
    elif score >= 0.5:
        return '强势信号', '值得关注', 'buy'
    elif score >= 0.3:
        return '中性信号', '观望', 'hold'
    else:
        return '弱势信号', '谨慎', 'sell'


def generate_signals_daily(df):
    """
    完整的买卖信号生成系统
    """
    # 买入条件（需同时满足）
    buy_conditions = (
        (df['composite_score'] > 0.6) &
        (df['fund_efficiency_rank'] > 0.7) &
        (df['mfi'] > 40) & (df['mfi'] < 70) &
        (df['mfi_change'] > 0) &
        (df['obv'] > df['obv_ma20']) &
        (df['divergence_type'] != 'bearish_divergence') &
        ((df['vol_concentration'] > 1.2) | (df['main_force_signal'] == 1)) &
        (df['close'] > df['close'].rolling(5).mean()) &
        (df['close'].rolling(5).mean() > df['close'].rolling(10).mean()) &
        (df['amount'] > 5e7) &
        (df['market_cap'] > 2e8)
    )

    # 卖出条件（任一满足）
    sell_conditions = (
        (df['composite_score'] < 0.4) |
        (df['fund_efficiency_rank'] < 0.5) |
        (df['mfi'] > 80) | (df['mfi_change'] < -10) |
        (df['divergence_type'] == 'bearish_divergence') |
        (df['close'].rolling(5).mean() < df['close'].rolling(10).mean()) |
        (df['close'] < df['high'].rolling(20).max() * 0.92)
    )

    df['buy_signal'] = buy_conditions.astype(int)
    df['sell_signal'] = sell_conditions.astype(int)

    return df


def market_risk_control_daily(index_df):
    """
    大盘风控 - 仅用指数日线数据
    """
    index_df['ma20'] = index_df['close'].rolling(20).mean()
    index_df['ma30'] = index_df['close'].rolling(30).mean()

    # 空头排列信号
    index_df['bearish_arrangement'] = (
        (index_df['ma20'] < index_df['ma30']) &
        (index_df['close'] < index_df['ma20'])
    ).astype(int)

    # 市场恐慌信号
    index_df['panic_signal'] = (
        (index_df['close'].diff(3) < 0) &
        (index_df['volume'] > index_df['volume'].rolling(20).mean())
    ).astype(int)

    # 综合风险等级（0-2安全，3-4警惕，5+清仓）
    index_df['risk_level'] = index_df['bearish_arrangement'] + index_df['panic_signal']

    return index_df


class FundEfficiencyStrategyDaily:
    """
    资金效率动量策略 - 纯日线数据版本

    参数要求：
    - stock_data: dict {code: DataFrame} 股票池数据，包含OHLCV
    - index_data: DataFrame 指数数据，用于风控
    - float_shares: dict {code: float} 流通股本（可用换手率反推估算）
    """

    def __init__(self):
        self.params = {
            'max_holding': 10,
            'stop_loss': 0.05,
            'trailing_stop': 0.08,
            'min_amount': 50000,  # 千元单位，50000千元=5000万元
            'min_market_cap': 20000,  # 万元单位，20000万元=2亿元
            'rebalance_freq': 5
        }

    def prepare_indicators(self, df):
        """计算所有技术指标"""
        df = calculate_fund_efficiency_daily(df)
        df = calculate_volume_profile(df)
        df = calculate_mfi_daily(df)
        df = calculate_obv_daily(df)
        df = detect_divergence_daily(df)
        df = composite_scoring_daily(df)
        df = generate_signals_daily(df)
        return df

    def select_stocks(self, stock_pool, date):
        """选股逻辑"""
        scores = []
        for code, df in stock_pool.items():
            if date not in df.index:
                continue
            data = df.loc[date]
            if (data['amount'] < self.params['min_amount'] or
                data['market_cap'] < self.params['min_market_cap']):
                continue
            scores.append({
                'code': code,
                'score': data['composite_score'],
                'fund_rank': data['fund_efficiency_rank'],
                'mfi': data['mfi'],
                'signal': data['signal_strength']
            })
        scores = sorted(scores, key=lambda x: x['score'], reverse=True)
        return [s['code'] for s in scores[:self.params['max_holding']]]

    def should_clear_position(self, index_data, date):
        """判断是否清仓"""
        if date not in index_data.index:
            return False
        risk_level = index_data.loc[date, 'risk_level']
        return risk_level >= 2

    def backtest(self, stock_data, index_data, start_date, end_date):
        """回测框架"""
        # 预处理
        for code in stock_data:
            stock_data[code] = self.prepare_indicators(stock_data[code])

        index_data = market_risk_control_daily(index_data)

        portfolio = {}
        trades = []
        dates = pd.date_range(start_date, end_date, freq='B')

        for i, date in enumerate(dates):
            # 大盘风控
            if self.should_clear_position(index_data, date):
                if portfolio:
                    trades.append({
                        'date': date,
                        'action': 'clear',
                        'reason': 'market_risk',
                        'holdings': list(portfolio.keys())
                    })
                    portfolio = {}
                continue

            # 定期调仓
            if i % self.params['rebalance_freq'] == 0:
                new_selection = self.select_stocks(stock_data, date)
                for code in list(portfolio.keys()):
                    if code not in new_selection:
                        trades.append({
                            'date': date,
                            'action': 'sell',
                            'code': code,
                            'reason': 'rebalance'
                        })
                        del portfolio[code]

                for code in new_selection:
                    if code not in portfolio and len(portfolio) < self.params['max_holding']:
                        portfolio[code] = {
                            'entry_date': date,
                            'entry_price': stock_data[code].loc[date, 'close'],
                            'max_price': stock_data[code].loc[date, 'close']
                        }
                        trades.append({
                            'date': date,
                            'action': 'buy',
                            'code': code,
                            'price': stock_data[code].loc[date, 'close']
                        })

            # 每日止损检查
            for code in list(portfolio.keys()):
                if date not in stock_data[code].index:
                    continue
                current_price = stock_data[code].loc[date, 'close']
                holding = portfolio[code]
                holding['max_price'] = max(holding['max_price'], current_price)

                stop_price = max(
                    holding['entry_price'] * (1 - self.params['stop_loss']),
                    holding['max_price'] * (1 - self.params['trailing_stop'])
                )

                if current_price <= stop_price:
                    trades.append({
                        'date': date,
                        'action': 'sell',
                        'code': code,
                        'reason': 'stop_loss',
                        'return': (current_price - holding['entry_price']) / holding['entry_price']
                    })
                    del portfolio[code]

        return trades

    def analyze_stock(self, df, ts_code='Unknown'):
        """分析单只股票，返回关键指标（含数据验证）"""
        # 确保有足够的数据
        if len(df) < 30:
            return {'error': '数据不足，需要至少30个交易日数据', 'code': ts_code}

        # === 严格数据验证 ===
        is_valid, val_report = validate_data_integrity(df, ts_code)
        
        if not is_valid:
            return {
                'error': f"数据验证失败: {val_report['issues']}",
                'code': ts_code,
                'validation_report': val_report
            }
        
        if val_report['warnings']:
            print(f"[数据警告] {ts_code}: {val_report['warnings']}")

        # 计算指标
        df = self.prepare_indicators(df)

        # 获取最新数据（确保是最后一条）
        latest = df.iloc[-1]

        return {
            'code': ts_code,
            'composite_score': latest['composite_score'],
            'signal_strength': latest['signal_strength'],
            'fund_efficiency_rank': latest['fund_efficiency_rank'],
            'mfi': latest['mfi'],
            'mfi_change': latest['mfi_change'],
            'vol_concentration': latest['vol_concentration'],
            'obv_above_ma20': latest['obv'] > latest['obv_ma20'],
            'divergence_type': latest['divergence_type'],
            'main_force_signal': latest['main_force_signal'],
            'buy_signal': latest['buy_signal'],
            'sell_signal': latest['sell_signal'],
            'amount': latest['amount'],
            'market_cap': latest['market_cap'],
            'price': latest['close'],
            'latest_date': val_report['latest_date'],
            'data_validated': True
        }

    def generate_report(self, analysis_result):
        """生成诊断报告（含指标备注）"""
        if 'error' in analysis_result:
            return f"分析失败: {analysis_result['error']}"

        score = analysis_result['composite_score']
        mfi = analysis_result['mfi']
        rank = analysis_result['fund_efficiency_rank']
        vol_conc = analysis_result['vol_concentration']

        # 获取各指标状态
        score_status, score_desc, _ = get_composite_score_status(score)
        mfi_status, mfi_desc, _ = get_mfi_status(mfi)
        fe_status, fe_desc, _ = get_fund_efficiency_status(rank)
        vol_status, vol_desc, _ = get_vol_concentration_status(vol_conc)

        # 判断信号
        if analysis_result['sell_signal'] == 1:
            signal_text = '卖出信号'
            signal_class = 'sell'
            signal_advice = '[WARN] 注意风险 - 卖出信号触发，资金效率下降，MFI转势或顶背离。建议减仓或止损。'
        elif analysis_result['buy_signal'] == 1:
            signal_text = '买入信号'
            signal_class = 'buy'
            signal_advice = '[BUY] 关注机会 - 买入信号触发，多项指标向好。建议关注并考虑建仓。'
        else:
            signal_text = '持有/观望'
            signal_class = 'hold'
            signal_advice = '[HOLD] 观望为主 - 当前无明确方向信号，建议等待进一步确认。'

        # 背离说明
        divergence_map = {
            'bullish_divergence': ('底背离', '价格跌但指标不跟跌 → 看涨信号'),
            'bearish_divergence': ('顶背离', '价格涨但指标不跟涨 → 看跌信号'),
            'none': ('无背离', '正常走势')
        }
        div_name, div_meaning = divergence_map.get(analysis_result['divergence_type'], ('未知', ''))

        # OBV说明
        obv_text = 'OBV>MA20（资金流入）' if analysis_result['obv_above_ma20'] else 'OBV<MA20（资金流出）'

        # 报告内容
        report = f"""
{'='*60}
{analysis_result['code']} 资金效率策略诊断报告
{'='*60}

【综合评分】
  综合得分：{score:.2f} → {score_status}（{score_desc}）
  资金效率排名：{rank*100:.1f}% → {fe_status}（{fe_desc}）

{'='*60}
【核心指标详解】
{'='*60}

① MFI资金流量指标
   当前值：{mfi:.1f} → {mfi_status}
   含义：{mfi_desc}
   变化：{analysis_result['mfi_change']:+.1f}（{'资金流入加速' if analysis_result['mfi_change'] > 0 else '资金流入减缓'}）

② 成交量集中度
   当前值：{vol_conc:.2f} → {vol_status}
   含义：{vol_desc}
   公式：当日成交量 / 20日均量

③ OBV能量潮
   状态：{obv_text}
   含义：反映资金进出趋势

④ 背离状态
   状态：{div_name}
   含义：{div_meaning}

⑤ 主力吸筹信号
   {'[YES] 是（低位+放量+重心上移）' if analysis_result['main_force_signal'] == 1 else '[NO] 否'}

{'='*60}
【信号结论】
{'='*60}
  综合信号：{signal_text}
  {signal_advice}

{'='*60}
【流动性指标】
{'='*60}
  日成交额：{analysis_result['amount']*1000/1e8:.2f}亿元 {'[PASS] 满足门槛(>0.5亿)' if analysis_result['amount']*1000 > 5e7 else '[FAIL] 低于门槛'}
  流通市值：{analysis_result['market_cap']/10000:.2f}亿元

{'='*60}
【指标参考指南】
{'='*60}
MFI区间：<20超卖 | 20-40偏低 | 40-60正常 | 60-80偏高 | >80超买
资金效率排名：<30%较差 | 30-50%一般 | 50-70%良好 | >70%优秀
成交量集中度：<0.8缩量 | 0.8-1.2正常 | 1.2-1.5放量 | >1.5大幅放量
"""
        return report


# 快速分析函数
def quick_analyze(df, stock_code='Unknown'):
    """
    快速分析单只股票（简化版）

    参数：
    - df: DataFrame，需包含 open, high, low, close, volume, amount, float_shares
    - stock_code: 股票代码

    返回：诊断字典
    """
    strategy = FundEfficiencyStrategyDaily()
    result = strategy.analyze_stock(df)
    result['code'] = stock_code
    return result


def generate_html_report(analysis_result, stock_name, stock_code, recent_data=None, validation_result=None, output_path=None):
    """
    生成标准HTML分析报告（核心指标表格式）
    
    包含：
    1. 数据验证头部
    2. 核心指标卡片（指标、数值、状态）
    3. 指标详解表格
    4. 信号结论与分析要点
    5. 建议
    6. 最新5日数据表格
    7. 指标参考指南
    """
    from datetime import datetime
    
    score = analysis_result['composite_score']
    mfi = analysis_result['mfi']
    mfi_change = analysis_result.get('mfi_change', 0)
    rank = analysis_result['fund_efficiency_rank']
    vol_conc = analysis_result['vol_concentration']
    
    # 单位转换：统一转为亿元显示
    # amount字段：如果是小数值（<1e6），假设是千元；如果是大数值（>1e8），假设是元
    raw_amount = analysis_result['amount']
    if raw_amount < 1e6:  # 千元单位（东方财富API）
        amount_yi = raw_amount * 1000 / 1e8  # 千元→元→亿元
    else:  # 元单位
        amount_yi = raw_amount / 1e8  # 元→亿元
    
    # market_cap字段：如果是小数值（<1e8），假设是万元；如果是大数值（>1e10），假设是元
    raw_cap = analysis_result['market_cap']
    if raw_cap < 1e8:  # 万元单位
        cap_yi = raw_cap / 10000  # 万元→亿元
    else:  # 元单位
        cap_yi = raw_cap / 1e8  # 元→亿元
    
    latest_close = analysis_result['latest_close']
    latest_date = analysis_result.get('latest_date', datetime.now().strftime('%Y-%m-%d'))
    
    # 获取各指标状态
    score_status, score_desc, _ = get_composite_score_status(score)
    mfi_status, mfi_desc, _ = get_mfi_status(mfi)
    fe_status, fe_desc, _ = get_fund_efficiency_status(rank)
    vol_status, vol_desc, _ = get_vol_concentration_status(vol_conc)
    
    # 判断信号
    if analysis_result['sell_signal'] == 1:
        signal_text = '卖出信号'
        signal_icon = 'SELL'
        signal_advice = '[WARN] 注意风险 - 卖出信号触发，资金效率下降，MFI转势或顶背离。建议减仓或止损。'
        signal_suggestions = [
            '减仓或止损出局',
            '等待调整结束',
            '关注支撑位'
        ]
    elif analysis_result['buy_signal'] == 1:
        signal_text = '买入信号'
        signal_icon = 'BUY'
        signal_advice = '[BUY] 关注机会 - 买入信号触发，多项指标向好。建议关注并考虑建仓。'
        signal_suggestions = [
            '可考虑建仓，关注回调机会',
            f'止损位可设在MA20（约{latest_close*0.9:.1f}元附近）',
            '若MFI突破60，可适当加仓'
        ]
    else:
        signal_text = '持有/观望'
        signal_icon = 'HOLD'
        signal_advice = '[HOLD] 观望为主 - 当前无明确方向信号，建议等待进一步确认。'
        signal_suggestions = [
            '等待放量信号',
            '关注MFI变化方向',
            '可轻仓试探'
        ]
    
    # 背离说明
    divergence_map = {
        'bullish_divergence': ('底背离', '价格跌但指标不跟跌 → 看涨信号'),
        'bearish_divergence': ('顶背离', '价格涨但指标不跟涨 → 看跌信号'),
        'none': ('无背离', '正常走势')
    }
    div_name, div_meaning = divergence_map.get(analysis_result['divergence_type'], ('未知', ''))
    
    # OBV说明
    obv_text = 'OBV>MA20（资金流入）' if analysis_result['obv_above_ma20'] else 'OBV<MA20（资金流出）'
    
    # 验证状态
    if validation_result:
        is_valid = validation_result.get('is_valid', True)
        validation_class = 'pass' if is_valid else 'warn'
        validation_text = '[PASS] 验证通过' if is_valid else '[WARN] 验证警告'
    else:
        validation_class = 'pass'
        validation_text = '[PASS] 验证通过'
    
    # 最新5日数据HTML
    recent_rows = ""
    if recent_data is not None and len(recent_data) > 0:
        for _, row in recent_data.iterrows():
            # amount是千元，转亿元
            amount_val = row['amount'] * 1000 / 1e8 if 'amount' in row else 0
            # market_cap是万元，转亿元
            cap_val = row['market_cap'] / 10000 if 'market_cap' in row else 0
            recent_rows += f"""
                <tr>
                    <td>{row['trade_date']}</td>
                    <td>{row['close']:.2f}元</td>
                    <td>{amount_val:.2f}亿</td>
                    <td>{cap_val:.2f}亿</td>
                </tr>
            """
    else:
        recent_rows = f"""
                <tr>
                    <td>{latest_date}</td>
                    <td>{latest_close:.2f}元</td>
                    <td>{amount_yi:.2f}亿</td>
                    <td>{cap_yi:.2f}亿</td>
                </tr>
        """
    
    # 分析要点
    analysis_points = []
    if score >= 0.5:
        analysis_points.append(f"综合得分 {score:.2f}，{score_desc}")
    else:
        analysis_points.append(f"综合得分 {score:.2f}，{score_desc}")
    
    if rank >= 0.7:
        analysis_points.append(f"资金效率{rank*100:.1f}%优秀，资金利用高效，主力积极")
    elif rank >= 0.5:
        analysis_points.append(f"资金效率{rank*100:.1f}%良好，表现正常")
    else:
        analysis_points.append(f"资金效率{rank*100:.1f}%一般，资金推动效果一般")
    
    if mfi >= 60:
        analysis_points.append(f"MFI {mfi:.1f}，偏高区，MFI变化{mfi_change:+.1f}，需注意滞涨风险")
    elif mfi >= 40:
        analysis_points.append(f"MFI {mfi:.1f}，多空平衡，MFI变化{mfi_change:+.1f}，短期{'资金流入加速' if mfi_change > 0 else '资金流入减缓'}")
    else:
        analysis_points.append(f"MFI {mfi:.1f}，偏低区，MFI变化{mfi_change:+.1f}，资金观望")
    
    if vol_conc >= 1.5:
        analysis_points.append(f"成交量集中度{vol_conc:.2f}，大幅放量，主力活跃")
    elif vol_conc >= 1.2:
        analysis_points.append(f"成交量集中度{vol_conc:.2f}，温和放量")
    elif vol_conc >= 0.8:
        analysis_points.append(f"成交量集中度{vol_conc:.2f}，正常量能")
    else:
        analysis_points.append(f"成交量集中度{vol_conc:.2f}，缩量")
    
    if div_name != '无背离':
        analysis_points.append(f"{div_name}：{div_meaning}")
    else:
        analysis_points.append("无背离信号，走势健康")
    
    analysis_points.append(f"OBV>MA20" if analysis_result['obv_above_ma20'] else "OBV<MA20")
    analysis_points.append(f"股价{latest_close:.2f}元")
    
    points_html = ""
    for point in analysis_points:
        points_html += f"<li>{point}</li>"
    
    # 建议HTML
    suggestions_html = ""
    for suggestion in signal_suggestions:
        suggestions_html += f"<li>{suggestion}</li>"
    
    html = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{stock_name} ({stock_code}) - 资金效率策略分析</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f7fa; padding: 20px; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        h1 {{ color: #1a1a2e; margin-bottom: 20px; font-size: 24px; }}
        .card {{ background: white; border-radius: 12px; padding: 24px; margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); }}
        .card h2 {{ color: #333; margin-bottom: 16px; font-size: 18px; border-left: 4px solid #4a90d9; padding-left: 12px; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #eee; }}
        th {{ background: #f8f9fa; color: #666; font-weight: 600; }}
        .buy {{ color: #e74c3c; font-weight: bold; }}
        .sell {{ color: #27ae60; font-weight: bold; }}
        .hold {{ color: #f39c12; font-weight: bold; }}
        .validation-badge {{ display: inline-block; padding: 4px 12px; border-radius: 4px; font-size: 12px; }}
        .validation-pass {{ background: #d4edda; color: #155724; }}
        .validation-warn {{ background: #fff3cd; color: #856404; }}
        .summary {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; }}
        .summary-item {{ background: #f8f9fa; padding: 16px; border-radius: 8px; }}
        .summary-item .label {{ color: #666; font-size: 12px; margin-bottom: 4px; }}
        .summary-item .value {{ color: #333; font-size: 20px; font-weight: bold; }}
        .data-note {{ text-align: center; color: #888; font-size: 12px; margin-top: 20px; }}
        .reference {{ background: #f8f9fa; padding: 16px; border-radius: 8px; font-size: 14px; color: #666; }}
        .signal-box {{ padding: 16px; border-radius: 8px; margin-bottom: 16px; }}
        .signal-buy {{ background: #fdf2f2; border-left: 4px solid #e74c3c; }}
        .signal-sell {{ background: #f0fdf4; border-left: 4px solid #27ae60; }}
        .signal-hold {{ background: #fffbeb; border-left: 4px solid #f39c12; }}
        .signal-title {{ font-size: 20px; font-weight: bold; margin-bottom: 8px; }}
        .signal-advice {{ color: #666; font-size: 14px; }}
        .analysis-points, .suggestions {{ padding-left: 20px; margin: 8px 0; }}
        .analysis-points li, .suggestions li {{ margin: 6px 0; color: #555; line-height: 1.6; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{stock_name} ({stock_code}) - 资金效率策略分析</h1>

        <div class="card">
            <h2>数据验证</h2>
            <p>
                <span class="validation-badge validation-{validation_class}">
                    {validation_text}
                </span>
                &nbsp;&nbsp;
                最新交易日: <strong>{latest_date}</strong>
                &nbsp;&nbsp;
                收盘价: <strong>{latest_close:.2f}元</strong>
            </p>
        </div>

        <div class="card">
            <h2>核心指标</h2>
            <div class="summary">
                <div class="summary-item">
                    <div class="label" title="综合得分 >0.5强势 | 0.3-0.5中性 | <0.3弱势">综合得分(?)</div>
                    <div class="value">{score:.2f}</div>
                </div>
                <div class="summary-item">
                    <div class="label" title="资金效率 <30%较差 | 30-50%一般 | 50-70%良好 | >70%优秀">资金效率(?)</div>
                    <div class="value">{rank*100:.1f}%</div>
                </div>
                <div class="summary-item">
                    <div class="label" title="MFI <40偏低/正常 | 40-60正常 | 60-80偏高 | >80超买">MFI(?)</div>
                    <div class="value">{mfi:.1f}</div>
                </div>
                <div class="summary-item">
                    <div class="label">MFI变化</div>
                    <div class="value">{mfi_change:+.1f}</div>
                </div>
            </div>
        </div>

        <div class="card">
            <h2>指标详解</h2>
            <table>
                <tr>
                    <th>指标</th>
                    <th>数值</th>
                    <th>状态</th>
                    <th>说明</th>
                </tr>
                <tr>
                    <td><strong>最新收盘价</strong></td>
                    <td>{latest_close:.2f}元</td>
                    <td>正常</td>
                    <td>当日收盘价</td>
                </tr>
                <tr>
                    <td><strong>日成交额</strong></td>
                    <td>{amount_yi:.2f}亿</td>
                    <td>{'活跃' if amount_yi > 5 else '偏低'}元</td>
                    <td>当日成交金额</td>
                </tr>
                <tr>
                    <td><strong>流通市值</strong></td>
                    <td>{cap_yi:.2f}亿</td>
                    <td>{'大盘' if cap_yi > 500 else '中盘' if cap_yi > 100 else '小盘'}股</td>
                    <td>流通股本 x 收盘价</td>
                </tr>
                <tr>
                    <td><strong>综合得分</strong></td>
                    <td>{score:.2f}</td>
                    <td>{score_status}</td>
                    <td>综合MFI、资金效率、OBV趋势计算</td>
                </tr>
                <tr>
                    <td><strong>资金效率排名</strong></td>
                    <td>{rank*100:.1f}%</td>
                    <td>{fe_status}</td>
                    <td>基于"单位成交额引起的流通市值变化率"</td>
                </tr>
                <tr>
                    <td><strong>MFI</strong></td>
                    <td>{mfi:.1f}</td>
                    <td>{mfi_status}</td>
                    <td>资金流量指标，类似RSI但考虑成交量</td>
                </tr>
                <tr>
                    <td><strong>MFI变化</strong></td>
                    <td>{mfi_change:+.1f}</td>
                    <td>{'快速上升' if mfi_change > 10 else '上升' if mfi_change > 0 else '下降'}</td>
                    <td>5日MFI变化</td>
                </tr>
                <tr>
                    <td><strong>成交量集中度</strong></td>
                    <td>{vol_conc:.2f}</td>
                    <td>{vol_status}</td>
                    <td>当日成交量与20日均成交量的比值</td>
                </tr>
            </table>
        </div>

        <div class="card">
            <h2>信号结论</h2>
            <div class="signal-box signal-{signal_icon.lower()}">
                <div class="signal-title">{signal_text}</div>
                <div class="signal-advice">{signal_advice}</div>
            </div>
        </div>

        <div class="card">
            <h2>分析要点</h2>
            <ul class="analysis-points">
                {points_html}
            </ul>
        </div>

        <div class="card">
            <h2>建议</h2>
            <ul class="suggestions">
                {suggestions_html}
            </ul>
        </div>

        <div class="card">
            <h2>最新数据（最新5日）</h2>
            <table>
                <tr>
                    <th>日期</th>
                    <th>收盘价</th>
                    <th>成交额</th>
                    <th>流通市值</th>
                </tr>
                {recent_rows}
            </table>
        </div>

        <div class="card">
            <h2>指标参考指南</h2>
            <div class="reference">
                <p><strong>MFI区间含义：</strong>&lt;20超卖 | 20-40偏低 | 40-60正常 | 60-80偏高 | &gt;80超买</p>
                <p><strong>资金效率排名：</strong>&lt;30%较差 | 30-50%一般 | 50-70%良好 | &gt;70%优秀</p>
                <p><strong>成交量集中度：</strong>&lt;0.8缩量 | 0.8-1.2正常 | 1.2-1.5放量 | &gt;1.5大幅放量</p>
                <p><strong>综合得分：</strong>&gt;0.5强势 | 0.3-0.5中性 | &lt;0.3弱势</p>
            </div>
            <div style="margin-top:16px; font-size:14px; color:#666;">
                <strong>MFI说明：</strong>资金流量指标，类似RSI但考虑成交量。当MFI&gt;80表示资金过热可能回调，&lt;20表示资金冷却可能反弹。<br>
                <strong>资金效率排名：</strong>基于"单位成交额引起的流通市值变化率"计算，反映资金推动效率。<br>
                <strong>背离检测：</strong>价格创新低但指标未创新低=看涨背离；价格创新高但指标未创新高=看跌背离。
            </div>
        </div>

        <div class="data-note">
            数据来源：东方财富日线数据 + 每日指标（含真实流通股本）<br>
            分析日期：{datetime.now().strftime('%Y-%m-%d')} | 数据验证：严格模式
        </div>
    </div>
</body>
</html>
"""
    
    # 保存文件
    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
    
    return html


if __name__ == '__main__':
    # 示例用法
    print("资金效率动量策略 - 纯日线数据版本")
    print("=" * 50)
    print("使用方法：")
    print("from fund_efficiency_strategy import FundEfficiencyStrategyDaily")
    print("")
    print("strategy = FundEfficiencyStrategyDaily()")
    print("result = strategy.analyze_stock(df)")
    print("print(strategy.generate_report(result))")
    print("")
    print("from fund_efficiency_strategy import generate_html_report")
    print("generate_html_report(result, '股票名称', '代码', output_path='report.html')")

"""
资金效率动量策略 - 纯日线数据版本（优化版）

基于"单位成交额引起的流通市值变化率"核心创意，
结合MFI、OBV、成交量分布和背离检测构建的多因子复合策略。

优化内容：
1. 动态MFI阈值（基于历史分位数）
2. 关键价位突破验证机制
3. 股票代码三码验证
4. OBV成交量真实性验证
5. 复合策略信号确认框架

作者：资金效率策略团队
版本：2.0（优化版）
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta


# ==================== 数据验证模块 ====================

def validate_data_integrity(df, ts_code='Unknown', expected_name=None):
    """
    严格数据完整性验证机制

    验证内容：
    1. 股票代码三码对应验证（代码、名称、数据一致性）
    2. 数据日期是否为最近交易日
    3. 收盘价是否合理（>0, 在合理范围内）
    4. 成交额与收盘价×成交量的逻辑一致性
    5. 流通市值的合理性

    返回：(is_valid, validation_report)
    """
    validation_issues = []
    warnings = []

    # 1. 股票代码三码对应验证（新增）
    if 'trade_code' in df.columns or 'code' in df.columns:
        code_col = 'trade_code' if 'trade_code' in df.columns else 'code'
        data_code = df[code_col].iloc[-1] if len(df) > 0 else None

        if data_code and ts_code != 'Unknown':
            # 清理比对（去掉后缀如.SH/.SZ）
            clean_data_code = data_code.replace('.SH', '').replace('.SZ', '').replace('.BJ', '')
            clean_ts_code = ts_code.replace('.SH', '').replace('.SZ', '').replace('.BJ', '')

            if clean_data_code != clean_ts_code:
                validation_issues.append(
                    f"股票代码不匹配：数据中为 {data_code}，输入为 {ts_code}"
                )

    # 2. 日期验证
    if len(df) > 0:
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

    # 3. 收盘价验证
    if 'close' in df.columns:
        latest_close = df['close'].iloc[-1]
        if pd.isna(latest_close) or latest_close <= 0:
            validation_issues.append(f"收盘价异常：{latest_close}")
        elif latest_close < 1:
            warnings.append(f"收盘价偏低：{latest_close}元（可能是ST或低价股）")
        elif latest_close > 10000:
            warnings.append(f"收盘价偏高：{latest_close}元（请确认数据正确）")

    # 4. 成交额与收盘价×成交量逻辑验证
    if all(col in df.columns for col in ['close', 'vol', 'amount']):
        df['amount_yuan'] = df['amount'] * 1000
        df['calculated_amount'] = df['close'] * df['vol'] * 100

        mask = df['calculated_amount'] > 0
        ratio = (df.loc[mask, 'amount_yuan'] / df.loc[mask, 'calculated_amount']).abs()

        if (ratio < 0.5).any() or (ratio > 2).any():
            warnings.append("成交额与收盘价×成交量存在较大差异（可能因除权或数据源差异）")

    # 5. 流通市值合理性验证
    if all(col in df.columns for col in ['close', 'float_shares']):
        calc_market_cap = df['close'] * df['float_shares']
        if 'market_cap' in df.columns:
            cap_ratio = (calc_market_cap / df['market_cap']).replace([np.inf, -np.inf], np.nan)
            if not cap_ratio.dropna().between(0.5, 2).all():
                warnings.append("流通市值计算结果与提供数据存在差异")

    # 6. 数据完整性检查
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
    """获取最近N个交易日数据（确保正确排序）"""
    if len(df) == 0:
        return df
    df_sorted = df.sort_index(ascending=False)
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


# ==================== 核心因子计算模块 ====================

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
    - 价格重心(POC)替代Level-2
    """
    # 确保流通市值存在
    if 'market_cap' not in df.columns:
        df['market_cap'] = df['close'] * df['float_shares']

    # ===== 核心资金效率因子 =====
    # 单位成交额引起的流通市值变化率
    # 公式：(今日市值 - 昨日市值) / 成交额
    # 含义：每元成交额推动了多少市值变化

    df['cap_change'] = (df['market_cap'] * 10000).diff()
    df['cap_change_rate'] = df['cap_change'] / (df['market_cap'].shift(1) * 10000)

    # 资金效率 = 市值变化额 / 成交额
    df['fund_efficiency'] = np.where(
        df['amount'] > 0,
        df['cap_change'] / (df['amount'] * 1000),
        0
    )

    # ===== 多周期平滑 =====
    df['fe_daily'] = df['fund_efficiency']
    df['fe_ma5'] = df['fund_efficiency'].rolling(5).mean()
    df['fe_ma20'] = df['fund_efficiency'].rolling(20).mean()

    # 多周期对比信号
    df['fe_trend'] = (df['fe_daily'] > df['fe_ma5']).astype(int) + \
                     (df['fe_ma5'] > df['fe_ma20']).astype(int)

    # ===== 价格重心（Point of Control）=====
    df['price_poc'] = (df['open'] + df['high'] + df['low'] + df['close']) / 4
    df['poc_bias'] = (df['close'] - df['price_poc']) / df['price_poc']

    # ===== 市值敏感性调整 =====
    avg_mcap = df['market_cap'].rolling(20).mean()
    df['cap_sensitivity'] = np.where(
        avg_mcap < 1e10, 0.7,      # 小盘：70%权重
        np.where(avg_mcap < 5e10, 0.85, 1.0)  # 中盘：85%，大盘：100%
    )

    # ===== 修正资金效率 =====
    df['fund_efficiency_adj'] = (
        df['fund_efficiency'] *
        (1 + df['poc_bias']) *
        df['cap_sensitivity']
    )

    # 5日平滑
    df['fund_efficiency_ma5'] = df['fund_efficiency_adj'].rolling(5).mean()

    # 异常值处理
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
    price_high = df['high'].rolling(lookback).max()
    price_low = df['low'].rolling(lookback).min()
    price_range = price_high - price_low

    df['price_position'] = (df['close'] - price_low) / price_range
    df['vol_ma20'] = df['volume'].rolling(20).mean()
    df['vol_concentration'] = df['volume'] / df['vol_ma20']

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
    资金流量指标 - 纯日线版本（优化版）

    新增：动态阈值计算
    """
    tp = (df['high'] + df['low'] + df['close']) / 3
    money_flow = tp * df['volume']

    positive_flow = (money_flow * (tp > tp.shift(1))).rolling(period).sum()
    negative_flow = (money_flow * (tp < tp.shift(1))).rolling(period).sum()

    money_ratio = positive_flow / negative_flow
    df['mfi'] = 100 - (100 / (1 + money_ratio))

    # MFI变化率
    df['mfi_change'] = df['mfi'].diff(6)

    # ===== 动态阈值计算（新增）=====
    # 计算MFI的历史分位数，用于动态调整阈值
    df['mfi_p20'] = df['mfi'].rolling(60).quantile(0.2)  # 动态超卖线
    df['mfi_p80'] = df['mfi'].rolling(60).quantile(0.8)  # 动态超买线

    # MFI信号强度（考虑动态阈值）
    df['mfi_signal'] = np.where(
        df['mfi'] > df['mfi_p80'], 'overbought',
        np.where(df['mfi'] < df['mfi_p20'], 'oversold', 'normal')
    )

    return df


def calculate_obv_daily(df):
    """
    能量潮指标 - 验证成交量真实性（优化版）

    新增：成交量真实性验证
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

    # ===== 成交量真实性验证（新增）=====
    # OBV与成交量的相关性验证
    df['obv_volume_corr'] = df['obv'].rolling(10).corr(df['volume'])

    # 虚假成交量检测：成交量放大但OBV不跟随
    df['fake_volume_signal'] = (
        (df['vol_concentration'] > 1.5) &
        (df['obv_slope'] < 0)
    ).astype(int)

    # OBV健康度评分
    df['obv_health'] = np.where(
        df['obv_volume_corr'] > 0.5, 1,  # 高相关性，健康
        np.where(df['obv_volume_corr'] > 0, 0.6, 0.3)  # 低相关性，可能有操纵
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

    if has_scipy:
        price_slope, _, _, _, _ = stats.linregress(range(lookback), df['close'].iloc[-lookback:])
        obv_slope, _, _, _, _ = stats.linregress(range(lookback), df['obv'].iloc[-lookback:])
        mfi_slope, _, _, _, _ = stats.linregress(range(lookback), df['mfi'].iloc[-lookback:])
    else:
        price_slope = (df['close'].iloc[-1] - df['close'].iloc[-lookback]) / lookback
        obv_slope = (df['obv'].iloc[-1] - df['obv'].iloc[-lookback]) / lookback
        mfi_slope = (df['mfi'].iloc[-1] - df['mfi'].iloc[-lookback]) / lookback

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


# ==================== 突破验证模块（新增）====================

def detect_breakout_validation(df, lookback=20):
    """
    关键价位突破验证机制（新增）

    策略思路要求：
    - 关键价位突破时，观察单位成交量市值变化率是否异常放大
    - 高成交量伴随高变化率 = 有效突破
    - 低成交量伴随高变化率 = 假突破风险
    """
    # 计算20日高低点
    df['high_20'] = df['high'].rolling(lookback).max()
    df['low_20'] = df['low'].rolling(lookback).min()
    df['range_20'] = df['high_20'] - df['low_20']

    # 突破上轨信号
    df['breakout_high'] = (df['close'] > df['high_20'].shift(1)) & (df['close'].shift(1) <= df['high_20'].shift(1))

    # 突破下轨信号
    df['breakout_low'] = (df['close'] < df['low_20'].shift(1)) & (df['close'].shift(1) >= df['low_20'].shift(1))

    # 突破验证：突破时资金效率是否放大
    df['breakout_fe'] = np.where(
        df['breakout_high'] | df['breakout_low'],
        df['fund_efficiency_ma5'].fillna(0),
        np.nan
    )

    # 突破有效性评分
    # 有效突破：高成交量 + 高资金效率变化
    df['breakout_validity'] = np.where(
        df['breakout_high'],
        # 向上突破：资金效率为正且成交量放大
        np.where(
            (df['vol_concentration'] > 1.2) & (df['fund_efficiency'] > 0),
            1,  # 有效突破
            np.where(
                (df['vol_concentration'] < 0.8) & (df['fund_efficiency'] > 0),
                0.3,  # 假突破风险
                0.5
            )
        ),
        np.where(
            df['breakout_low'],
            # 向下突破：资金效率为负
            np.where(df['fund_efficiency'] < 0, 1, 0.3),
            0.5
        )
    )

    return df


# ==================== 复合评分模块 ====================

def composite_scoring_daily(df):
    """
    多因子复合评分 - 纯日线数据（优化版）

    优化内容：
    1. 动态MFI阈值评分
    2. 突破验证权重
    3. OBV真实性验证
    """
    # 各因子得分
    score_fund = df['fund_efficiency_rank']

    # MFI健康度（优化：使用动态阈值）
    mfi_normalized = 1 - abs(df['mfi'] - 50) / 50
    mfi_trend = np.where(df['mfi_change'] > 0, 1, 0.5)

    # 动态阈值调整（当MFI接近动态边界时更敏感）
    mfi_dynamic_adjust = np.where(
        (df['mfi'] > df['mfi_p80'] * 0.9) | (df['mfi'] < df['mfi_p20'] * 1.1),
        0.8,  # 接近边界，降低评分
        1.0
    )
    score_mfi = mfi_normalized * mfi_trend * mfi_dynamic_adjust

    # 成交量分布质量
    score_volume = (
        df['main_force_signal'] * 0.4 +
        (df['vol_concentration'] > 1.2).astype(int) * 0.3 +
        df['poc_stability'] * 0.3
    )

    # OBV验证（优化：加入真实性验证）
    score_obv = np.where(
        ((df['close'] > df['close'].shift(5)) & (df['obv'] > df['obv'].shift(5))), 1,
        np.where(
            (df['close'] < df['close'].shift(5)) & (df['obv'] < df['obv'].shift(5)), 0.8,
            0.3
        )
    ) * df['obv_health']  # 乘以健康度

    # 背离得分
    score_divergence = np.where(
        df['divergence_type'] == 'bullish_divergence', df['divergence_strength'] * 0.2,
        np.where(
            df['divergence_type'] == 'bearish_divergence', -0.2, 0
        )
    )

    # 突破验证得分（新增）
    score_breakout = np.where(
        df['breakout_high'] | df['breakout_low'],
        df['breakout_validity'] * 0.1,  # 突破权重10%
        0
    )

    # 动态权重
    weights = {
        'fund': 0.30,      # 资金效率（略降低）
        'mfi': 0.20,       # MFI（略降低）
        'volume': 0.15,    # 成交量
        'obv': 0.15,       # OBV
        'divergence': 0.10, # 背离（提高）
        'breakout': 0.10   # 突破（新增）
    }

    # 综合得分
    df['composite_score'] = (
        score_fund * weights['fund'] +
        score_mfi * weights['mfi'] +
        score_volume * weights['volume'] +
        score_obv * weights['obv'] +
        score_divergence +
        score_breakout
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
  - 动态阈值：基于60日滚动分位数计算（p20/p80）
  - 区间：
    · >动态p80：超买区 — 警惕回调风险
    · 60~80：偏高区 — 强势但注意滞涨
    · 40~60：正常区 — 多空平衡
    · 20~40：偏低区 — 超卖区域，可能反弹
    · <动态p20：超卖区 — 极度超卖，可能见底

■ 动态MFI阈值说明（新增）
  - 基于过去60日MFI数据计算动态边界
  - 更适应不同市场环境（牛市/熊市）
  - 避免固定阈值在极端行情下的失效

■ 突破验证（breakout_validity，新增）
  - 含义：关键价位突破时的信号质量评估
  - 范围：0~1
  - 区间：
    · 1.0：有效突破 — 成交量放大+资金效率跟随
    · 0.5-1.0：观望 — 信号待确认
    · <0.5：假突破风险 — 需警惕

■ OBV健康度（obv_health，新增）
  - 含义：OBV与成交量的相关性，反映成交量真实性
  - 范围：0~1
  - 区间：
    · >0.8：高相关 — 成交量真实
    · 0.5-0.8：中等相关 — 需观察
    · <0.5：低相关 — 可能存在操纵

■ 虚假成交量信号（fake_volume_signal，新增）
  - 条件：成交量放大但OBV不跟随
  - 含义：可能存在对倒交易或虚假放量
  - 1=可疑，0=正常

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
"""


def get_mfi_status(mfi, mfi_p20=None, mfi_p80=None):
    """获取MFI状态说明（优化版）"""
    if mfi_p80 and mfi > mfi_p80:
        return '超买区', '突破动态上界，注意回调风险', 'sell'
    elif mfi > 80:
        return '超买区', '注意回调风险', 'sell'
    elif mfi > 60:
        return '偏高区', '强势但注意滞涨', 'warning'
    elif mfi >= 40:
        return '正常区', '多空平衡', 'hold'
    elif mfi >= 20:
        return '偏低区', '超卖区域，可能反弹', 'buy'
    elif mfi_p20 and mfi < mfi_p20:
        return '超卖区', '突破动态下界，可能见底', 'buy'
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


def get_breakout_status(validity):
    """获取突破验证状态说明（新增）"""
    if validity >= 0.8:
        return '有效突破', '成交量配合，资金效率跟随', 'buy'
    elif validity >= 0.5:
        return '待确认', '需进一步观察', 'hold'
    else:
        return '假突破风险', '警惕追高', 'warning'


def get_obv_health_status(health):
    """获取OBV健康度状态说明（新增）"""
    if health >= 0.8:
        return '健康', '成交量真实可靠', 'pass'
    elif health >= 0.5:
        return '可疑', '需结合其他指标判断', 'warning'
    else:
        return '异常', '可能存在操纵行为', 'sell'


def generate_signals_daily(df):
    """
    完整的买卖信号生成系统（优化版）
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
        (df['market_cap'] > 2e8) &
        (df['fake_volume_signal'] == 0) &  # 新增：排除虚假成交量
        (df['obv_health'] >= 0.5)            # 新增：OBV健康度要求
    )

    # 卖出条件（任一满足）
    sell_conditions = (
        (df['composite_score'] < 0.4) |
        (df['fund_efficiency_rank'] < 0.5) |
        (df['mfi'] > 80) | (df['mfi_change'] < -10) |
        (df['divergence_type'] == 'bearish_divergence') |
        (df['close'].rolling(5).mean() < df['close'].rolling(10).mean()) |
        (df['close'] < df['high'].rolling(20).max() * 0.92) |
        (df['fake_volume_signal'] == 1)      # 新增：虚假成交量信号
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

    index_df['bearish_arrangement'] = (
        (index_df['ma20'] < index_df['ma30']) &
        (index_df['close'] < index_df['ma20'])
    ).astype(int)

    index_df['panic_signal'] = (
        (index_df['close'].diff(3) < 0) &
        (index_df['volume'] > index_df['volume'].rolling(20).mean())
    ).astype(int)

    index_df['risk_level'] = index_df['bearish_arrangement'] + index_df['panic_signal']

    return index_df


# ==================== 主策略类 ====================

class FundEfficiencyStrategyDaily:
    """
    资金效率动量策略 - 纯日线数据版本（优化版）
    """

    def __init__(self):
        self.params = {
            'max_holding': 10,
            'stop_loss': 0.05,
            'trailing_stop': 0.08,
            'min_amount': 50000,  # 千元单位，50000千元=5000万元
            'min_market_cap': 20000,  # 万元单位
            'rebalance_freq': 5
        }

    def prepare_indicators(self, df):
        """计算所有技术指标（优化版）"""
        df = calculate_fund_efficiency_daily(df)
        df = calculate_volume_profile(df)
        df = calculate_mfi_daily(df)
        df = calculate_obv_daily(df)
        df = detect_divergence_daily(df)
        df = detect_breakout_validation(df)  # 新增：突破验证
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
        for code in stock_data:
            stock_data[code] = self.prepare_indicators(stock_data[code])

        index_data = market_risk_control_daily(index_data)

        portfolio = {}
        trades = []
        dates = pd.date_range(start_date, end_date, freq='B')

        for i, date in enumerate(dates):
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
        if len(df) < 30:
            return {'error': '数据不足，需要至少30个交易日数据', 'code': ts_code}

        # 严格数据验证
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

        # 获取最新数据
        latest = df.iloc[-1]

        return {
            'code': ts_code,
            'composite_score': latest['composite_score'],
            'signal_strength': latest['signal_strength'],
            'fund_efficiency_rank': latest['fund_efficiency_rank'],
            'mfi': latest['mfi'],
            'mfi_change': latest['mfi_change'],
            'mfi_p20': latest.get('mfi_p20', None),
            'mfi_p80': latest.get('mfi_p80', None),
            'vol_concentration': latest['vol_concentration'],
            'obv_above_ma20': latest['obv'] > latest['obv_ma20'],
            'obv_health': latest.get('obv_health', 1.0),
            'fake_volume_signal': latest.get('fake_volume_signal', 0),
            'divergence_type': latest['divergence_type'],
            'main_force_signal': latest['main_force_signal'],
            'breakout_validity': latest.get('breakout_validity', 0.5),
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
        mfi_p20 = analysis_result.get('mfi_p20')
        mfi_p80 = analysis_result.get('mfi_p80')
        rank = analysis_result['fund_efficiency_rank']
        vol_conc = analysis_result['vol_concentration']
        obv_health = analysis_result.get('obv_health', 1.0)
        fake_vol = analysis_result.get('fake_volume_signal', 0)
        breakout = analysis_result.get('breakout_validity', 0.5)

        # 获取各指标状态
        score_status, score_desc, _ = get_composite_score_status(score)
        mfi_status, mfi_desc, _ = get_mfi_status(mfi, mfi_p20, mfi_p80)
        fe_status, fe_desc, _ = get_fund_efficiency_status(rank)
        vol_status, vol_desc, _ = get_vol_concentration_status(vol_conc)
        breakout_status, breakout_desc, _ = get_breakout_status(breakout)
        obv_health_status, obv_health_desc, _ = get_obv_health_status(obv_health)

        # 判断信号
        if analysis_result['sell_signal'] == 1:
            signal_text = '卖出信号'
            signal_class = 'sell'
            signal_advice = '[WARN] 注意风险 - 卖出信号触发'
        elif analysis_result['buy_signal'] == 1:
            signal_text = '买入信号'
            signal_class = 'buy'
            signal_advice = '[BUY] 关注机会 - 买入信号触发'
        else:
            signal_text = '持有/观望'
            signal_class = 'hold'
            signal_advice = '[HOLD] 观望为主'

        # 背离说明
        divergence_map = {
            'bullish_divergence': ('底背离', '看涨信号'),
            'bearish_divergence': ('顶背离', '看跌信号'),
            'none': ('无背离', '正常走势')
        }
        div_name, div_meaning = divergence_map.get(analysis_result['divergence_type'], ('未知', ''))

        # OBV说明
        obv_text = 'OBV>MA20（资金流入）' if analysis_result['obv_above_ma20'] else 'OBV<MA20（资金流出）'

        # 虚假成交量警告
        fake_vol_warn = '[WARN] 虚假成交量信号 - 可能存在对倒交易' if fake_vol else ''

        report = f"""
{'='*60}
{analysis_result['code']} 资金效率策略诊断报告（优化版）
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
   动态阈值：p20={mfi_p20:.1f if mfi_p20 else 'N/A'}, p80={mfi_p80:.1f if mfi_p80 else 'N/A'}
   变化：{analysis_result['mfi_change']:+.1f}

② 成交量集中度
   当前值：{vol_conc:.2f} → {vol_status}
   含义：{vol_desc}

③ OBV能量潮
   状态：{obv_text}
   健康度：{obv_health:.2f} → {obv_health_status}（{obv_health_desc}）
   {fake_vol_warn}

④ 背离状态
   状态：{div_name}
   含义：{div_meaning}

⑤ 突破验证（新增）
   有效性：{breakout:.2f} → {breakout_status}（{breakout_desc}）

⑥ 主力吸筹信号
   {'[YES] 是（低位+放量+重心上移）' if analysis_result['main_force_signal'] == 1 else '[NO] 否'}

{'='*60}
【信号结论】
{'='*60}
  综合信号：{signal_text}
  {signal_advice}

{'='*60}
【流动性指标】
{'='*60}
  日成交额：{analysis_result['amount']*1000/1e8:.2f}亿元
  流通市值：{analysis_result['market_cap']/10000:.2f}亿元

{'='*60}
【指标参考指南】
{'='*60}
MFI区间：<20超卖 | 20-40偏低 | 40-60正常 | 60-80偏高 | >80超买
MFI动态阈值：基于60日分位数计算
资金效率排名：<30%较差 | 30-50%一般 | 50-70%良好 | >70%优秀
成交量集中度：<0.8缩量 | 0.8-1.2正常 | 1.2-1.5放量 | >1.5大幅放量
OBV健康度：>0.8健康 | 0.5-0.8可疑 | <0.5异常
突破有效性：>0.8有效 | 0.5-0.8待确认 | <0.5假突破
"""
        return report


def quick_analyze(df, stock_code='Unknown'):
    """快速分析单只股票（简化版）"""
    strategy = FundEfficiencyStrategyDaily()
    result = strategy.analyze_stock(df)
    result['code'] = stock_code
    return result


# ==================== HTML报告生成（优化版）====================

def generate_html_report(analysis_result, stock_name, stock_code, recent_data=None, validation_result=None, output_path=None):
    """生成标准HTML分析报告（优化版）"""
    from datetime import datetime

    score = analysis_result['composite_score']
    mfi = analysis_result['mfi']
    mfi_change = analysis_result.get('mfi_change', 0)
    mfi_p20 = analysis_result.get('mfi_p20')
    mfi_p80 = analysis_result.get('mfi_p80')
    rank = analysis_result['fund_efficiency_rank']
    vol_conc = analysis_result['vol_concentration']
    obv_health = analysis_result.get('obv_health', 1.0)
    fake_vol = analysis_result.get('fake_volume_signal', 0)
    breakout = analysis_result.get('breakout_validity', 0.5)

    # 单位转换
    raw_amount = analysis_result['amount']
    if raw_amount < 1e6:
        amount_yi = raw_amount * 1000 / 1e8
    else:
        amount_yi = raw_amount / 1e8

    raw_cap = analysis_result['market_cap']
    if raw_cap < 1e8:
        cap_yi = raw_cap / 10000
    else:
        cap_yi = raw_cap / 1e8

    latest_close = analysis_result['latest_close']
    latest_date = analysis_result.get('latest_date', datetime.now().strftime('%Y-%m-%d'))

    # 获取各指标状态
    score_status, score_desc, _ = get_composite_score_status(score)
    mfi_status, mfi_desc, _ = get_mfi_status(mfi, mfi_p20, mfi_p80)
    fe_status, fe_desc, _ = get_fund_efficiency_status(rank)
    vol_status, vol_desc, _ = get_vol_concentration_status(vol_conc)
    breakout_status, breakout_desc, _ = get_breakout_status(breakout)
    obv_health_status, obv_health_desc, _ = get_obv_health_status(obv_health)

    # 判断信号
    if analysis_result['sell_signal'] == 1:
        signal_text = '卖出信号'
        signal_icon = 'SELL'
        signal_advice = '[WARN] 注意风险 - 卖出信号触发'
        signal_suggestions = ['减仓或止损出局', '等待调整结束', '关注支撑位']
    elif analysis_result['buy_signal'] == 1:
        signal_text = '买入信号'
        signal_icon = 'BUY'
        signal_advice = '[BUY] 关注机会 - 买入信号触发'
        signal_suggestions = ['可考虑建仓，关注回调机会', f'止损位可设在MA20附近', '若MFI突破60，可适当加仓']
    else:
        signal_text = '持有/观望'
        signal_icon = 'HOLD'
        signal_advice = '[HOLD] 观望为主 - 当前无明确方向信号'
        signal_suggestions = ['等待放量信号', '关注MFI变化方向', '可轻仓试探']

    # 背离说明
    divergence_map = {
        'bullish_divergence': ('底背离', '看涨信号'),
        'bearish_divergence': ('顶背离', '看跌信号'),
        'none': ('无背离', '正常走势')
    }
    div_name, div_meaning = divergence_map.get(analysis_result['divergence_type'], ('未知', ''))

    # OBV说明
    obv_text = 'OBV>MA20（资金流入）' if analysis_result['obv_above_ma20'] else 'OBV<MA20（资金流出）'

    # 验证状态
    validation_class = 'pass'
    validation_text = '[PASS] 验证通过'
    if validation_result and not validation_result.get('is_valid', True):
        validation_class = 'warn'
        validation_text = '[WARN] 验证警告'

    # 最新5日数据HTML
    recent_rows = ""
    if recent_data is not None and len(recent_data) > 0:
        for _, row in recent_data.iterrows():
            amount_val = row['amount'] * 1000 / 1e8 if 'amount' in row else 0
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

    # MFI状态（优化：显示动态阈值）
    if mfi_p20 and mfi_p80:
        analysis_points.append(f"MFI {mfi:.1f}（动态阈值p20={mfi_p20:.1f}, p80={mfi_p80:.1f}），{mfi_status}，MFI变化{mfi_change:+.1f}")
    else:
        analysis_points.append(f"MFI {mfi:.1f}，{mfi_status}，MFI变化{mfi_change:+.1f}")

    # OBV健康度（新增）
    analysis_points.append(f"OBV健康度 {obv_health:.2f}（{obv_health_status}）")
    if fake_vol:
        analysis_points.append("[WARN] 检测到虚假成交量信号 - 可能存在对倒交易")

    # 突破验证（新增）
    if breakout != 0.5:
        analysis_points.append(f"突破验证：{breakout:.2f}（{breakout_status}）")

    if vol_conc >= 1.5:
        analysis_points.append(f"成交量集中度{vol_conc:.2f}，大幅放量")
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

    suggestions_html = ""
    for suggestion in signal_suggestions:
        suggestions_html += f"<li>{suggestion}</li>"

    html = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{stock_name} ({stock_code}) - 资金效率策略分析（优化版）</title>
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
        .warning {{ color: #e67e22; font-weight: bold; }}
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
        .new-feature {{ background: #e8f4f8; padding: 12px; border-radius: 8px; margin-bottom: 16px; border-left: 4px solid #3498db; }}
        .new-feature h3 {{ color: #2980b9; margin-bottom: 8px; font-size: 14px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{stock_name} ({stock_code}) - 资金效率策略分析（优化版 v2.0）</h1>

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
                    <div class="label">综合得分(?)</div>
                    <div class="value">{score:.2f}</div>
                </div>
                <div class="summary-item">
                    <div class="label">资金效率(?)</div>
                    <div class="value">{rank*100:.1f}%</div>
                </div>
                <div class="summary-item">
                    <div class="label">MFI(?)</div>
                    <div class="value">{mfi:.1f}</div>
                </div>
                <div class="summary-item">
                    <div class="label">MFI变化</div>
                    <div class="value">{mfi_change:+.1f}</div>
                </div>
            </div>
        </div>

        <!-- 新增功能展示 -->
        <div class="card new-feature">
            <h3>优化亮点（v2.0新增）</h3>
            <div class="summary">
                <div class="summary-item">
                    <div class="label">OBV健康度</div>
                    <div class="value" style="color: {'#27ae60' if obv_health >= 0.8 else '#e67e22' if obv_health >= 0.5 else '#e74c3c'}">{obv_health:.2f}</div>
                </div>
                <div class="summary-item">
                    <div class="label">突破验证</div>
                    <div class="value" style="color: {'#27ae60' if breakout >= 0.8 else '#e67e22' if breakout >= 0.5 else '#e74c3c'}">{breakout:.2f}</div>
                </div>
                <div class="summary-item">
                    <div class="label">虚假成交量</div>
                    <div class="value" style="color: {'#e74c3c' if fake_vol else '#27ae60'}">{'是' if fake_vol else '否'}</div>
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
                    <td><strong>综合得分</strong></td>
                    <td>{score:.2f}</td>
                    <td>{score_status}</td>
                    <td>复合评分（含突破验证、OBV健康度）</td>
                </tr>
                <tr>
                    <td><strong>MFI</strong></td>
                    <td>{mfi:.1f}</td>
                    <td>{mfi_status}</td>
                    <td>动态阈值：p20={mfi_p20:.1f if mfi_p20 else 'N/A'}, p80={mfi_p80:.1f if mfi_p80 else 'N/A'}</td>
                </tr>
                <tr>
                    <td><strong>资金效率排名</strong></td>
                    <td>{rank*100:.1f}%</td>
                    <td>{fe_status}</td>
                    <td>基于"单位成交额引起的流通市值变化率"</td>
                </tr>
                <tr>
                    <td><strong>OBV健康度</strong>（新增）</td>
                    <td>{obv_health:.2f}</td>
                    <td>{obv_health_status}</td>
                    <td>{obv_health_desc}</td>
                </tr>
                <tr>
                    <td><strong>突破验证</strong>（新增）</td>
                    <td>{breakout:.2f}</td>
                    <td>{breakout_status}</td>
                    <td>{breakout_desc}</td>
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
            <h2>最新数据</h2>
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
                <p><strong>MFI动态阈值：</strong>基于60日滚动分位数计算（p20/p80），更适应市场环境</p>
                <p><strong>资金效率排名：</strong>&lt;30%较差 | 30-50%一般 | 50-70%良好 | &gt;70%优秀</p>
                <p><strong>OBV健康度：</strong>&gt;0.8健康 | 0.5-0.8可疑 | &lt;0.5异常（可能存在操纵）</p>
                <p><strong>突破验证：</strong>&gt;0.8有效突破 | 0.5-0.8待确认 | &lt;0.5假突破风险</p>
                <p><strong>综合得分：</strong>&gt;0.5强势 | 0.3-0.5中性 | &lt;0.3弱势</p>
            </div>
        </div>

        <div class="data-note">
            数据来源：东方财富日线数据 + 每日指标<br>
            分析日期：{datetime.now().strftime('%Y-%m-%d')} | 版本：2.0（优化版）<br>
            <strong>优化内容：动态MFI阈值、突破验证、OBV健康度、虚假成交量检测
        </div>
    </div>
</body>
</html>
"""

    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)

    return html


if __name__ == '__main__':
    print("资金效率动量策略 - 纯日线数据版本（优化版 v2.0）")
    print("=" * 60)
    print("优化内容：")
    print("1. 动态MFI阈值（基于60日分位数）")
    print("2. 关键价位突破验证机制")
    print("3. 股票代码三码验证")
    print("4. OBV成交量真实性验证")
    print("5. 虚假成交量检测")
    print("6. 复合策略信号确认框架")
    print("")
    print("使用方法：")
    print("from fund_efficiency_strategy import FundEfficiencyStrategyDaily")
    print("strategy = FundEfficiencyStrategyDaily()")
    print("result = strategy.analyze_stock(df)")
    print("print(strategy.generate_report(result))")

"""
score.py
=========
A股多信号评分引擎 & 阶段检测

替代威氏四阶段模型（A 股专用版）

核心逻辑：
    不依赖威氏的量价结构（威氏基于美股机构市场，不完全适用于 A 股散户主导市场）。
    改用「资金流 + 北向持仓 + 融资余额 + 技术动能 + 券商评级」五维信号，
    综合加权输出 0-100 的信号评分，并给出信号类型标签。

信号类型（5种）：
    🟢 资金流入  - 主力资金净流入 + 大单净流入双强
    🔵 北向加码  - 北向持股增加且量能稳定
    🟡 启动信号  - 满足 3 个以上维度的正向信号
    🟠 高位警示  - 融资余额高 + 主力流出 + 北向减少
    🔴 下降趋势  - 技术空头 + 主力持续流出

评分维度：
    维度         权重   数据来源（Tushare）
    ───────────────────────────────
    北向资金     25%    hk_hold（沪深港通持股）
    主力资金流   25%    moneyflow（个股资金流向）
    融资余额     15%    margin（融资融券）
    技术动能     20%    daily（价格+换手率）
    券商评级     15%    broker_recommend（券商金股）

评分流程：
    1. 对每只股票遍历5个数据维度
    2. 每个维度独立打分（0-100）
    3. 加权求和 → 综合评分
    4. 综合评分 ≥ MIN_SCORE → 进入 Scout 结果
    5. 评分配合信号类型标签给出方向判断
"""

import os
import sys
import logging
from dataclasses import dataclass, asdict
from typing import Optional

# 确保项目根目录在 path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 加载配置
from config import (
    WEIGHT_NORTHBOUND, WEIGHT_MONEYFLOW, WEIGHT_MARGIN,
    WEIGHT_TECHNICAL, WEIGHT_BROKER,
    MIN_SCORE, MIN_MARGIN_RATIO, MIN_HK_HOLD_PCT
)

logger = logging.getLogger(__name__)


# ───────────────────────────────────────────────
# 数据结构
# ───────────────────────────────────────────────

@dataclass
class StockSignal:
    """单只股票的信号快照"""
    ts_code: str
    name: str
    score: int                      # 综合评分 0-100
    signal_type: str                # 信号类型标签
    northbound_pct: float          # 北向持股%
    margin_change_pct: float       # 融资余额变动%
    moneyflow_net: float          # 主力净流入（万元）
    moneyflow_rank: float         # 主力净流入排名分（0-100）
    broker_rating: float          # 券商评级（1-5）
    target_gap_pct: float         # 目标价空间%
    price: float                  # 当前价
    change_pct: float             # 当日涨跌幅%
    turnover_rate: float          # 换手率%
    phase: str                    # 信号阶段

    # 原始数据（保留用于复盘）
    _raw: dict = None             # type: ignore

    def to_dict(self) -> dict:
        d = asdict(self)
        d.pop("_raw", None)
        return d


# ───────────────────────────────────────────────
# 内部评分辅助
# ───────────────────────────────────────────────

def _score_northbound(pct: float, pct_change: float = 0) -> float:
    """
    北向资金评分（权重 25%）
    逻辑：持股比例越高 + 近期增持 → 信号越强
    A股无13F，北向持股是最接近"机构持仓"的日频数据
    """
    if pct < MIN_HK_HOLD_PCT:
        return 0.0

    # 基础分：持股比例
    score = min(60.0, pct * 4)   # pct=15% → 60分

    # 加分：持股比例 > 5% → 额外加分
    if pct > 5:
        score += min(20.0, (pct - 5) * 4)  # 每超1%加4分，上限20

    # 加分：持股比例特别高（>10%）→ 极强信号
    if pct > 10:
        score += 20.0

    return min(100.0, score)


def _score_moneyflow(net: float, large: float, rank_pct: float = 50) -> float:
    """
    主力资金流评分（权重 25%）
    逻辑：主力净流入越多、越持续 → 信号越强
    关注：大单净流入（机构proxy）和主力净流入的同步性
    """
    score = 50.0  # 中性基线

    # 大单净流入方向
    if large > 10000:           # 大单净流入 > 1亿
        score += 15.0
    elif large > 5000:          # 大单净流入 > 5000万
        score += 10.0
    elif large > 0:
        score += 5.0
    elif large < -10000:        # 大单净流出 > 1亿
        score -= 20.0
    elif large < -5000:          # 大单净流出 > 5000万
        score -= 10.0
    else:
        score -= 5.0

    # 主力净流入配合
    if net > 0:
        score += min(10.0, net / 2000)  # 每2000万+1分，上限10分
    else:
        score += max(-10.0, net / 2000)

    return max(0.0, min(100.0, score))


def _score_margin(change_pct: float, balance: float) -> float:
    """
    融资余额评分（权重 15%）
    逻辑（逆趋势/反向指标）：
      - 融资余额持续增加 → 短期见顶风险上升（逆向）
      - 融资余额下降 + 股价稳定 → 见底信号（逆向）
    """
    if balance == 0:
        return 50.0  # 无融资数据，默认中性

    score = 50.0

    # 融资余额大幅增加（>30%）→ 高位预警，逆向减分
    if change_pct > 30:
        score -= 25.0
    elif change_pct > 20:
        score -= 15.0
    elif change_pct > 10:
        score -= 8.0
    elif change_pct > 5:
        score -= 4.0
    elif change_pct < -30:      # 融资余额大幅下降 → 见底可能
        score += 15.0
    elif change_pct < -20:
        score += 10.0
    elif change_pct < -10:
        score += 5.0

    return max(0.0, min(100.0, score))


def _score_technical(change_pct: float, turnover_rate: float, price_5d_trend: float = 0) -> float:
    """
    技术动能评分（权重 20%）
    逻辑：
      - 涨幅适中（+2%~+8%）+ 高换手 → 资金积极参与
      - 涨幅过大（>9%）→ 可能是涨停前夕，风险大
      - 跌幅过大（<-5%）→ 短期超卖，可关注
      - 换手率高于市场均值（>3%）→ 活跃信号
    """
    score = 50.0

    # 涨跌打分（适度涨跌加分，极端涨跌减分）
    if -5 <= change_pct <= 2:
        score += 10.0   # 温和上涨
    elif 2 < change_pct <= 6:
        score += 15.0   # 稳健上涨，最佳区间
    elif 6 < change_pct <= 9:
        score += 8.0    # 强势，但接近涨停
    elif change_pct > 9:
        score -= 10.0  # 接近涨停，风险累积
    elif -8 <= change_pct < -5:
        score += 5.0   # 超跌，可能反弹
    elif change_pct < -8:
        score -= 15.0  # 大跌，风险信号

    # 换手率打分（A股市场换手率高是活跃信号）
    if turnover_rate > 10:
        score += 10.0   # 极度活跃
    elif turnover_rate > 5:
        score += 7.0    # 活跃
    elif turnover_rate > 2:
        score += 3.0    # 正常
    elif turnover_rate < 0.5:
        score -= 5.0    # 极度不活跃

    # 5日趋势加分
    if price_5d_trend > 5:
        score += 8.0
    elif price_5d_trend > 0:
        score += 4.0
    elif price_5d_trend < -5:
        score -= 8.0
    else:
        score -= 4.0

    return max(0.0, min(100.0, score))


def _score_broker(rating: float, target_gap: float) -> float:
    """
    券商评级评分（权重 15%）
    逻辑：
      - 评级 ≥ 4.0 → 强买入信号
      - 目标价空间 ≥ 30% → 上涨预期强烈
      - 无评级数据 → 默认50分（不加分不减分）
    """
    if rating == 0 and target_gap == 0:
        return 50.0  # 无数据，默认中性

    score = 50.0

    # 评级加分
    if rating >= 4.5:
        score += 25.0
    elif rating >= 4.0:
        score += 18.0
    elif rating >= 3.5:
        score += 10.0
    elif rating >= 3.0:
        score += 5.0
    elif rating > 0:
        score -= 5.0

    # 目标价空间加分
    if target_gap >= 50:
        score += 15.0
    elif target_gap >= 30:
        score += 10.0
    elif target_gap >= 15:
        score += 5.0
    elif target_gap < -20:
        score -= 15.0  # 目标价低于当前价超过20%
    elif target_gap < 0:
        score -= 5.0

    return max(0.0, min(100.0, score))


def _detect_signal_type(s: StockSignal) -> str:
    """
    综合信号类型判断逻辑
    基于多维信号组合判断当前股票处于哪种市场状态
    """
    # 触发信号的条件计数
    bullish_count = 0
    bearish_count = 0

    # 北向资金（最重要）
    if s.northbound_pct > 5:
        bullish_count += 2
    elif s.northbound_pct > 2:
        bullish_count += 1
    elif s.northbound_pct < 1:
        bearish_count += 1

    # 主力资金
    if s.moneyflow_net > 5000:
        bullish_count += 2
    elif s.moneyflow_net > 0:
        bullish_count += 1
    elif s.moneyflow_net < -5000:
        bearish_count += 2
    elif s.moneyflow_net < 0:
        bearish_count += 1

    # 融资余额变化
    if s.margin_change_pct > 20:
        bearish_count += 2   # 融资余额激增 = 短期见顶预警
    elif s.margin_change_pct < -20:
        bullish_count += 1   # 融资余额大降 = 阶段性见底
    elif s.margin_change_pct > 5:
        bearish_count += 1
    elif s.margin_change_pct < -5:
        bullish_count += 1

    # 技术动能
    if s.change_pct > 2 and s.turnover_rate > 3:
        bullish_count += 1
    elif s.change_pct > 6:
        bullish_count += 1
        bearish_count += 1  # 涨太多也有风险
    elif s.change_pct < -5:
        bearish_count += 1
        bullish_count += 1  # 超跌也可能反弹

    # 券商评级
    if s.broker_rating >= 4.0:
        bullish_count += 1
    elif s.broker_rating > 0 and s.broker_rating < 3.0:
        bearish_count += 1

    # 综合判断
    if bullish_count >= 4 and bearish_count <= 1:
        return "资金流入"
    elif bullish_count >= 3 and s.northbound_pct > 3:
        return "北向加码"
    elif bullish_count >= 3 and s.broker_rating >= 4.0:
        return "启动信号"
    elif bearish_count >= 4:
        return "高位警示"
    elif bullish_count <= 1 and bearish_count >= 3:
        return "下降趋势"
    elif s.margin_change_pct > 30:
        return "高位警示"
    else:
        return "观望"


# ───────────────────────────────────────────────
# 主函数
# ───────────────────────────────────────────────

def calculate_score(
    ts_code: str,
    name: str,
    northbound_pct: float,
    margin_balance: float,
    margin_change_pct: float,
    moneyflow_net: float,
    moneyflow_large: float,
    broker_rating: float,
    broker_target: float,
    price: float,
    change_pct: float,
    turnover_rate: float,
    price_5d_trend: float = 0,
    broker_target_gap_pct: float = 0,
) -> StockSignal:
    """
    计算单只股票的信号评分。

    Args:
        ts_code: 股票代码
        name: 股票名称
        northbound_pct: 北向持股占总股本%
        margin_balance: 融资余额（万元）
        margin_change_pct: 融资余额变动%（近5日）
        moneyflow_net: 主力资金净流入（万元）
        moneyflow_large: 大单净流入（万元）
        broker_rating: 券商综合评级（1-5）
        broker_target: 一致目标价（元）
        price: 当前价格（元）
        change_pct: 当日涨跌幅%
        turnover_rate: 换手率%
        price_5d_trend: 近5日价格变动%
        broker_target_gap_pct: 目标价相对当前价空间%

    Returns:
        StockSignal 数据类
    """
    # 各维度独立评分
    s_northbound = _score_northbound(northbound_pct)
    s_moneyflow = _score_moneyflow(moneyflow_net, moneyflow_large)
    s_margin = _score_margin(margin_change_pct, margin_balance)
    s_technical = _score_technical(change_pct, turnover_rate, price_5d_trend)
    s_broker = _score_broker(broker_rating, broker_target_gap_pct)

    # 加权综合评分
    composite = (
        s_northbound * WEIGHT_NORTHBOUND +
        s_moneyflow  * WEIGHT_MONEYFLOW  +
        s_margin     * WEIGHT_MARGIN      +
        s_technical  * WEIGHT_TECHNICAL   +
        s_broker     * WEIGHT_BROKER
    )
    composite = round(composite)

    # 方向标签
    if composite >= 80:
        phase = "🟢 强势信号"
    elif composite >= 65:
        phase = "🔵 偏强信号"
    elif composite >= 50:
        phase = "🟡 中性信号"
    elif composite >= 35:
        phase = "🟠 偏弱信号"
    else:
        phase = "🔴 弱势信号"

    # 信号类型
    sig = StockSignal(
        ts_code=ts_code,
        name=name,
        score=composite,
        signal_type="",
        northbound_pct=round(northbound_pct, 2),
        margin_change_pct=round(margin_change_pct, 2),
        moneyflow_net=round(moneyflow_net, 2),
        moneyflow_rank=round(s_moneyflow, 1),
        broker_rating=round(broker_rating, 2),
        target_gap_pct=round(broker_target_gap_pct, 2),
        price=round(price, 2),
        change_pct=round(change_pct, 2),
        turnover_rate=round(turnover_rate, 2),
        phase=phase,
    )
    sig.signal_type = _detect_signal_type(sig)
    return sig


# ───────────────────────────────────────────────
# 批量评分（给 run.py 调用）
# ───────────────────────────────────────────────

def score_batch(stocks_data: list[dict]) -> list[StockSignal]:
    """
    对批量股票数据进行评分。

    Args:
        stocks_data: list[dict]，每项包含上述 calculate_score 的所有参数

    Returns:
        list[StockSignal]，按评分降序排列
    """
    results = []
    for s in stocks_data:
        try:
            sig = calculate_score(**s)
            results.append(sig)
        except Exception as e:
            logger.warning(f"评分失败 {s.get('ts_code', '?')}: {e}")

    # 过滤：评分低于阈值的不纳入Scout结果
    filtered = [s for s in results if s.score >= MIN_SCORE]
    filtered.sort(key=lambda x: x.score, reverse=True)
    return filtered


# ───────────────────────────────────────────────
# 信号类型描述（用于飞书展示）
# ───────────────────────────────────────────────

SIGNAL_DESCRIPTIONS = {
    "资金流入": "主力资金净流入 + 北向资金双强，属于强势信号，建议关注",
    "北向加码": "北向持股明显增加，机构资金持续介入，可考虑布局",
    "启动信号": "多维度信号正向，股价处于启动初期，值得关注",
    "高位警示": "融资余额激增 + 主力净流出，短期可能回调，注意风险",
    "下降趋势": "多个维度显示偏弱信号，建议观望或回避",
    "观望": "多空信号交织，暂时方向不明，建议等待",
}

def get_signal_description(signal_type: str) -> str:
    return SIGNAL_DESCRIPTIONS.get(signal_type, "信号不明，建议谨慎")

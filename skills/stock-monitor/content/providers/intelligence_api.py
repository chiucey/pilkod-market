"""
providers/intelligence_api.py
===========================
标准数据接口 - Intelligence（情报数据）

此文件定义固定函数签名，所有 Provider 实现必须遵守。
接口永不改变，换数据源 = 改配置 + 加适配器文件。

Canonical Field Names（规范字段名）:
    ts_code        - 股票代码，如 '000001.SZ'
    name           - 股票名称
    northbound_pct - 北向持股占总股本%，来自沪深港通
    margin_balance  - 融资余额（万元）
    margin_change_pct - 融资余额变动%
    short_balance   - 融券余额（万元）
    moneyflow_net  - 主力资金净流入（万元）
    moneyflow_large - 大单净流入（万元）
    broker_rating   - 券商综合评级（1-5）
    broker_target   - 券商一致目标价（元）
    holder_buy_pct  - 股东增持占比（近30日）
    holder_trade_net - 股东增减持方向
    sector_momentum  - 板块动能得分（0-100）
    price           - 当前价格（元）
    change_pct      - 涨跌幅%（当日）
    turnover_rate   - 换手率%
    score           - 综合信号评分（0-100）
    signal_type     - 信号类型：启动期/上升期/派发期/下降期/资金流入/资金流出/观望
"""

from abc import ABC, abstractmethod
from typing import Literal


class IntelligenceProvider(ABC):
    """情报数据 Provider 接口（Decoupled Provider 模式）"""

    @abstractmethod
    def get_sector_stocks(
        self,
        sector: str = "科技",
        limit: int = 200,
    ) -> list[dict]:
        """
        获取指定行业的股票列表。

        Args:
            sector: 行业名称（如"科技"/"电子"/"计算机"）
            limit: 最大返回数量

        Returns:
            list[dict]: 股票列表，每项包含 ts_code, name, industry
        """

    @abstractmethod
    def get_northbound_hold(self, ts_code: str) -> dict:
        """
        获取北向资金（沪深港通）持股数据。

        Returns:
            dict: {
                'northbound_pct': float,   # 北向持股占总股本%
                'hold_date': str,           # 持股日期
                'close': float              # 当日收盘价
            }
        """

    @abstractmethod
    def get_moneyflow(self, ts_code: str, trade_date: str = None) -> dict:
        """
        获取个股资金流向数据（大单/主力/散户）。

        Args:
            ts_code: 股票代码
            trade_date: 交易日期 YYYYMMDD，默认取最新

        Returns:
            dict: {
                'moneyflow_net': float,    # 主力资金净流入（万元）
                'moneyflow_large': float,  # 大单净流入（万元）
                'moneyflow_medium': float,# 中单净流入（万元）
                'moneyflow_small': float,  # 小单净流入（万元）
                'change_pct': float        # 当日涨跌幅%
            }
        """

    @abstractmethod
    def get_margin(self, ts_code: str) -> dict:
        """
        获取融资融券数据。

        Returns:
            dict: {
                'margin_balance': float,      # 融资余额（万元）
                'margin_buy': float,           # 融资买入额（万元）
                'margin_repay': float,        # 融资偿还额（万元）
                'margin_change_pct': float,    # 融资余额变动%
                'short_balance': float,       # 融券余额（万元）
            }
        """

    @abstractmethod
    def get_holder_trade(self, ts_code: str, days: int = 30) -> dict:
        """
        获取股东增减持数据。

        Args:
            ts_code: 股票代码
            days: 统计天数

        Returns:
            dict: {
                'holder_trade_net': str,   # 'BUYING' / 'SELLING' / 'NEUTRAL'
                'holder_buy_pct': float,  # 增持股东占比%
                'holder_sell_pct': float,  # 减持股东占比%
                'holder_buy_vol': float,  # 增持数量（万股）
                'holder_sell_vol': float, # 减持数量（万股）
            }
        """

    @abstractmethod
    def get_broker_rating(self, ts_code: str) -> dict:
        """
        获取券商研报综合评级和目标价。

        Returns:
            dict: {
                'broker_rating': float,    # 综合评级（1-5）
                'broker_target': float,     # 一致目标价（元）
                'broker_count': int,       # 参与评级券商数
                'target_gap_pct': float,   # 目标价相对当前价空间%
            }
        """

    @abstractmethod
    def get_sector_momentum(self, ts_code: str) -> dict:
        """
        获取个股所在板块的资金动能。

        Returns:
            dict: {
                'sector_name': str,        # 板块名称
                'sector_momentum': float,   # 板块动能得分（0-100）
                'sector_change_pct': float, # 板块近5日涨跌幅%
            }
        """

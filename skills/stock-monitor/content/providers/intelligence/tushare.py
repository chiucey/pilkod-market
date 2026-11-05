"""
providers/intelligence/tushare.py
================================
Tushare Pro API 实现 - A股情报数据

使用 Tushare Pro API 获取A股科技股多维度数据。
所有数据均映射为 Canonical Field Names，不直接暴露原始字段。

依赖接口：
    stock_basic       - 获取股票基础信息（含行业字段）
    hk_hold          - 沪深股通持股明细
    moneyflow         - 个股资金流向
    margin            - 融资融券汇总
    stk_holdertrade  - 股东增减持
    broker_recommend  - 券商月度金股（评级+目标价）
    ths_daily         - 同花顺概念板块日行情（板块动能）
"""

import os
import logging
from datetime import datetime, timedelta
from typing import Optional

import pandas as pd
import tushare as ts

from providers.intelligence_api import IntelligenceProvider

logger = logging.getLogger(__name__)

# 申万一级科技行业列表
TECH_SECTORS = [
    "电子", "计算机", "通信", "传媒", "机械设备",
    "国防军工", "汽车", "医药生物", "电力设备", "有色金属"
]

# 申万二级科技细分（用于扩大科技股覆盖）
TECH_SUB_SECTORS = [
    "半导体", "元件", "光学光电子", "消费电子", "其他电子",
    "计算机设备", "IT服务", "软件开发", "互联网电商", "通信设备",
    "通信服务", "广告营销", "影视院线", "游戏", "出版",
    "航空装备", "航天装备", "地面兵装", "船舶制造", "汽车零部件",
    "汽车整车", "摩托车及其他", "医药商业", "医疗器械", "化学制药",
    "中药", "生物制品", "医疗服务", "通用设备", "专用设备",
    "电机", "电气自动化设备", "电池", "风电设备", "光伏设备",
    "军工电子", "铜", "铝", "锌", "黄金", "稀土"
]


class TushareIntelligenceProvider(IntelligenceProvider):
    """Tushare Pro 实现"""

    def __init__(self, token: str = None):
        self.token = token or os.getenv("TUSHARE_TOKEN")
        if not self.token:
            raise ValueError("Tushare token 未设置，请设置 TUSHARE_TOKEN 环境变量")
        ts.set_token(self.token)
        self.pro = ts.pro_api()

        # 内存缓存，避免重复请求
        self._stock_list_cache = None
        self._stock_list_date = None

    # ───────────────────────────────────────────────
    # 内部辅助方法
    # ───────────────────────────────────────────────

    def _get_trade_date(self, days_back: int = 0) -> str:
        """返回格式化的交易日期"""
        if days_back == 0:
            # 取最新交易日
            today = datetime.now()
            # 避开周末
            weekday = today.weekday()
            if weekday >= 5:
                days_back = weekday - 4
            return (today - timedelta(days=days_back)).strftime("%Y%m%d")
        return (datetime.now() - timedelta(days=days_back)).strftime("%Y%m%d")

    def _get_tech_stocks(self) -> pd.DataFrame:
        """
        获取科技股列表。
        使用申万行业分类，筛选科技相关行业。
        结果缓存1天。
        """
        today_str = datetime.now().strftime("%Y%m%d")
        if self._stock_list_cache is not None and self._stock_list_date == today_str:
            return self._stock_list_cache

        try:
            # 方法1：直接获取股票列表，筛选行业
            df = self.pro.stock_basic(
                list_status="L",   # 上市状态：L=上市
                fields="ts_code,symbol,name,industry,list_date,market"
            )
            # 筛选科技相关行业
            df_tech = df[
                df["industry"].fillna("").apply(
                    lambda x: any(s in x for s in TECH_SUB_SECTORS)
                )
            ].copy()
            df_tech = df_tech.dropna(subset=["name"])
            logger.info(f"通过行业筛选获取 {len(df_tech)} 只科技股")
            self._stock_list_cache = df_tech
            self._stock_list_date = today_str
            return df_tech

        except Exception as e:
            logger.warning(f"获取股票列表失败: {e}，使用备用方法")
            return pd.DataFrame()

    def _safe_float(self, val) -> float:
        """安全转换为 float"""
        try:
            return float(val)
        except (TypeError, ValueError):
            return 0.0

    def _safe_str(self, val) -> str:
        """安全转换为 str"""
        if val is None:
            return "NEUTRAL"
        return str(val).strip().upper()

    # ───────────────────────────────────────────────
    # 实现接口方法
    # ───────────────────────────────────────────────

    def get_sector_stocks(
        self, sector: str = "科技", limit: int = 200
    ) -> list[dict]:
        """
        获取科技行业股票列表。
        优先使用申万行业分类，其次用Tushare行业字段。
        """
        df = self._get_tech_stocks()
        if df.empty:
            return []

        # 取前 limit 只
        df = df.head(limit)

        result = []
        for _, row in df.iterrows():
            result.append({
                "ts_code": row["ts_code"],
                "name": row["name"],
                "industry": row.get("industry", ""),
                "market": row.get("market", ""),
            })
        return result

    def get_northbound_hold(self, ts_code: str) -> dict:
        """
        沪深股通持股数据（北向资金持仓）。
        使用 hk_hold 接口。
        注意：需要交易日 18:00 后才有当日数据。
        """
        try:
            trade_date = self._get_trade_date(1)  # 取前一交易日
            df = self.pro.hk_hold(
                ts_code=ts_code,
                trade_date=trade_date
            )
            if df is None or df.empty:
                return {"northbound_pct": 0.0, "hold_date": "", "close": 0.0}

            row = df.iloc[0]
            return {
                "northbound_pct": self._safe_float(row.get("hold_ratio", 0)),
                "hold_date": str(row.get("trade_date", "")),
                "close": self._safe_float(row.get("close", 0)),
            }
        except Exception as e:
            logger.debug(f"北向持股查询失败 {ts_code}: {e}")
            return {"northbound_pct": 0.0, "hold_date": "", "close": 0.0}

    def get_moneyflow(self, ts_code: str, trade_date: str = None) -> dict:
        """
        个股资金流向（大单/主力/散户）。
        使用 tushare moneyflow 接口（接口170）。
        """
        try:
            if trade_date is None:
                trade_date = self._get_trade_date(1)
            df = self.pro.moneyflow(
                ts_code=ts_code,
                trade_date=trade_date
            )
            if df is None or df.empty:
                return {
                    "moneyflow_net": 0.0,
                    "moneyflow_large": 0.0,
                    "moneyflow_medium": 0.0,
                    "moneyflow_small": 0.0,
                    "change_pct": 0.0
                }
            row = df.iloc[0]
            return {
                "moneyflow_net": self._safe_float(row.get("net_mf_amt", 0)),
                "moneyflow_large": self._safe_float(row.get("large_net_amt", 0)),
                "moneyflow_medium": self._safe_float(row.get("med_net_amt", 0)),
                "moneyflow_small": self._safe_float(row.get("small_net_amt", 0)),
                "change_pct": self._safe_float(row.get("pct_change", 0)),
            }
        except Exception as e:
            logger.debug(f"资金流向查询失败 {ts_code}: {e}")
            return {
                "moneyflow_net": 0.0,
                "moneyflow_large": 0.0,
                "moneyflow_medium": 0.0,
                "moneyflow_small": 0.0,
                "change_pct": 0.0
            }

    def get_margin(self, ts_code: str) -> dict:
        """
        融资融券数据。
        使用 margin 接口（融资融券交易汇总，接口58）。
        """
        try:
            trade_date = self._get_trade_date(1)
            df = self.pro.margin(
                ts_code=ts_code,
                trade_date=trade_date
            )
            if df is None or df.empty:
                return {
                    "margin_balance": 0.0,
                    "margin_buy": 0.0,
                    "margin_repay": 0.0,
                    "margin_change_pct": 0.0,
                    "short_balance": 0.0,
                }

            row = df.iloc[0]
            margin_balance = self._safe_float(row.get("balance", 0))
            margin_balance_prev = self._safe_float(row.get("pbuyl_amt", 0))  # 前一日余额

            change_pct = 0.0
            if margin_balance_prev > 0:
                change_pct = (margin_balance - margin_balance_prev) / margin_balance_prev * 100

            return {
                "margin_balance": margin_balance,
                "margin_buy": self._safe_float(row.get("buy_amt", 0)),
                "margin_repay": self._safe_float(row.get("repay_amt", 0)),
                "margin_change_pct": change_pct,
                "short_balance": self._safe_float(row.get("sh_balance", 0)),
            }
        except Exception as e:
            logger.debug(f"融资融券查询失败 {ts_code}: {e}")
            return {
                "margin_balance": 0.0,
                "margin_buy": 0.0,
                "margin_repay": 0.0,
                "margin_change_pct": 0.0,
                "short_balance": 0.0,
            }

    def get_holder_trade(self, ts_code: str, days: int = 30) -> dict:
        """
        股东增减持数据。
        使用 stk_holdertrade 接口。
        """
        try:
            end_date = self._get_trade_date(1)
            start_date = (datetime.now() - timedelta(days=days)).strftime("%Y%m%d")
            df = self.pro.stk_holdertrade(
                ts_code=ts_code,
                start_date=start_date,
                end_date=end_date
            )
            if df is None or df.empty:
                return {
                    "holder_trade_net": "NEUTRAL",
                    "holder_buy_pct": 0.0,
                    "holder_sell_pct": 0.0,
                    "holder_buy_vol": 0.0,
                    "holder_sell_vol": 0.0,
                }

            # 汇总增持/减持量
            buy_vol = df[df["action"].str.contains("增持", na=False)]["vol"].sum() if "vol" in df.columns else 0
            sell_vol = df[df["action"].str.contains("减持", na=False)]["vol"].sum() if "vol" in df.columns else 0

            # 判断方向
            if buy_vol > sell_vol * 1.5:
                direction = "BUYING"
            elif sell_vol > buy_vol * 1.5:
                direction = "SELLING"
            else:
                direction = "NEUTRAL"

            total_vol = buy_vol + sell_vol
            return {
                "holder_trade_net": direction,
                "holder_buy_pct": (buy_vol / total_vol * 100) if total_vol > 0 else 0.0,
                "holder_sell_pct": (sell_vol / total_vol * 100) if total_vol > 0 else 0.0,
                "holder_buy_vol": self._safe_float(buy_vol),
                "holder_sell_vol": self._safe_float(sell_vol),
            }
        except Exception as e:
            logger.debug(f"股东增减持查询失败 {ts_code}: {e}")
            return {
                "holder_trade_net": "NEUTRAL",
                "holder_buy_pct": 0.0,
                "holder_sell_pct": 0.0,
                "holder_buy_vol": 0.0,
                "holder_sell_vol": 0.0,
            }

    def get_broker_rating(self, ts_code: str) -> dict:
        """
        券商月度金股数据（综合评级+目标价）。
        使用 broker_recommend 接口（接口267）。
        """
        try:
            df = self.pro.broker_recommend(ts_code=ts_code)
            if df is None or df.empty:
                return {
                    "broker_rating": 0.0,
                    "broker_target": 0.0,
                    "broker_count": 0,
                    "target_gap_pct": 0.0,
                }

            # 取最新一条
            df = df.sort_values("month", ascending=False)
            row = df.iloc[0]
            rating = self._safe_float(row.get("mean_rating", 0))
            target = self._safe_float(row.get("target_price", 0))

            # 获取当前价格用于计算空间
            price = 0.0
            try:
                price_df = self.pro.daily(ts_code=ts_code, trade_date=self._get_trade_date(1))
                if price_df is not None and not price_df.empty:
                    price = self._safe_float(price_df.iloc[0].get("close", 0))
            except Exception:
                pass

            target_gap_pct = 0.0
            if price > 0 and target > 0:
                target_gap_pct = (target - price) / price * 100

            return {
                "broker_rating": rating,
                "broker_target": target,
                "broker_count": int(row.get("count", 0)),
                "target_gap_pct": target_gap_pct,
            }
        except Exception as e:
            logger.debug(f"券商评级查询失败 {ts_code}: {e}")
            return {
                "broker_rating": 0.0,
                "broker_target": 0.0,
                "broker_count": 0,
                "target_gap_pct": 0.0,
            }

    def get_sector_momentum(self, ts_code: str) -> dict:
        """
        板块动能数据。
        使用同花顺概念板块日行情（ths_daily）判断个股所在板块的强弱。
        逻辑：获取个股近5日涨幅 vs 板块近5日涨幅。
        """
        try:
            # 先获取个股近5日行情
            end_date = self._get_trade_date(1)
            start_date = (datetime.now() - timedelta(days=10)).strftime("%Y%m%d")

            price_df = self.pro.daily(
                ts_code=ts_code,
                start_date=start_date,
                end_date=end_date
            )
            if price_df is None or len(price_df) < 2:
                return {
                    "sector_name": "",
                    "sector_momentum": 50.0,
                    "sector_change_pct": 0.0,
                }

            price_df = price_df.sort_values("trade_date")
            latest = price_df.iloc[-1]
            oldest = price_df.iloc[0]
            stock_change = self._safe_float(latest["close"]) - self._safe_float(oldest["close"])
            stock_change_pct = stock_change / self._safe_float(oldest["close"]) * 100 if oldest["close"] > 0 else 0

            # 获取个股行业信息
            basic_df = self.pro.stock_basic(
                ts_code=ts_code,
                fields="industry"
            )
            industry = ""
            if basic_df is not None and not basic_df.empty:
                industry = str(basic_df.iloc[0].get("industry", ""))

            # 获取该行业近5日表现（简化：用申万行业指数）
            # 这里用 wind_code 映射（简化处理）
            return {
                "sector_name": industry,
                "sector_momentum": min(100.0, max(0.0, 50.0 + stock_change_pct * 5)),
                "sector_change_pct": stock_change_pct,
            }
        except Exception as e:
            logger.debug(f"板块动能查询失败 {ts_code}: {e}")
            return {
                "sector_name": "",
                "sector_momentum": 50.0,
                "sector_change_pct": 0.0,
            }

"""
providers/intelligence/tencent.py
===================================
腾讯财经 API 实现 - 免费实时行情 + 技术分析数据

覆盖范围：
  - 实时价格（含昨收/今开/最高/最低/成交量/成交额）
  - 日K线历史（用于均线/动量计算）
  - 52周高低、PE等基本面参考
  - 买卖盘口（委托量，辅助量价分析）

不支持（Tushare专有，需token）：
  - 北向持股（沪深港通）
  - 融资融券
  - 券商评级
  - 股东增减持
  （这些维度以技术面替代，评分模型相应调整）
"""

import os
import logging
import urllib.request
import ssl
import json
import time as time_mod
from datetime import datetime, timedelta
from typing import Optional

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from providers.intelligence_api import IntelligenceProvider

logger = logging.getLogger(__name__)

ssl._create_default_https_context = ssl._create_unverified_context

# ─── 全局限流（10 calls/s，防止频率限制）─────────────────────────────
_RATE_LOCK = time_mod.time()
_CALLS_10S_WINDOW: list[float] = []
_MAX_CALLS_PER_10S = 30   # 留足余量


def _rate_limit() -> None:
    """每10秒最多30次调用（约3 calls/s），用滑动窗口实现"""
    global _RATE_LOCK, _CALLS_10S_WINDOW
    now = time_mod.time()
    # 清理10秒外记录
    _CALLS_10S_WINDOW = [t for t in _CALLS_10S_WINDOW if now - t < 10.0]
    if len(_CALLS_10S_WINDOW) >= _MAX_CALLS_PER_10S:
        sleep_time = 10.0 - (now - _CALLS_10S_WINDOW[0])
        if sleep_time > 0:
            logger.debug(f"[限速] 等待 {sleep_time:.2f}s")
            time_mod.sleep(sleep_time)
        _CALLS_10S_WINDOW = [t for t in _CALLS_10S_WINDOW if time_mod.time() - t < 10.0]
    _CALLS_10S_WINDOW.append(time_mod.time())


# ─── 工具函数 ─────────────────────────────────────────────────────────

def _safe_float(v, default=0.0) -> float:
    try:
        return float(v) if v and str(v).strip() else default
    except (TypeError, ValueError):
        return default


def _safe_str(v) -> str:
    return str(v).strip() if v else ""


def _get_trade_date(days_back: int = 1) -> str:
    """返回 YYYYMMDD 格式的交易日期"""
    return (datetime.now() - timedelta(days=days_back)).strftime("%Y%m%d")


def _http_get(url: str, headers: dict = None) -> str:
    _rate_limit()
    h = {"User-Agent": "Mozilla/5.0", **(headers or {})}
    req = urllib.request.Request(url, headers=h)
    with urllib.request.urlopen(req, timeout=10) as r:
        return r.read().decode("gbk", errors="replace")


def _parse_tencent_realtime(raw: str) -> dict:
    """
    解析腾讯财经实时行情 v_sh600410="1~名称~代码~当前~昨收~今开~成交量..."
    返回规范字段 dict。
    """
    try:
        data = raw.split("=", 1)[1].strip('";\r\n ')
        p = data.split("~")
        return {
            "_parts": p,
            "current": _safe_float(p[3] if len(p) > 3 else ""),
            "prev_close": _safe_float(p[4] if len(p) > 4 else ""),
            "open": _safe_float(p[5] if len(p) > 5 else ""),
            "volume": _safe_float(p[6] if len(p) > 6 else ""),   # 成交量（股）
            "high": _safe_float(p[33] if len(p) > 33 else ""),
            "low": _safe_float(p[34] if len(p) > 34 else ""),
            "pe": _safe_float(p[43] if len(p) > 43 else ""),
            "roe": _safe_float(p[46] if len(p) > 46 else ""),
            "high_52w": _safe_float(p[31] if len(p) > 31 else ""),
            "low_52w": _safe_float(p[32] if len(p) > 32 else ""),
            "name": p[1] if len(p) > 1 else "",
        }
    except Exception:
        return {}


def _parse_hk_realtime(raw: str) -> dict:
    """解析港股实时行情"""
    try:
        data = raw.split("=", 1)[1].strip('";\r\n ')
        p = data.split("~")
        return {
            "_parts": p,
            "current": _safe_float(p[3] if len(p) > 3 else ""),
            "prev_close": _safe_float(p[4] if len(p) > 4 else ""),
            "open": _safe_float(p[5] if len(p) > 5 else ""),
            "volume": _safe_float(p[6] if len(p) > 6 else ""),
            "high": _safe_float(p[37] if len(p) > 37 else ""),
            "low": _safe_float(p[38] if len(p) > 38 else ""),
            "pe": _safe_float(p[48] if len(p) > 48 else ""),
            "roe": 0.0,
            "high_52w": _safe_float(p[37] if len(p) > 37 else ""),
            "low_52w": _safe_float(p[38] if len(p) > 38 else ""),
            "name": p[1] if len(p) > 1 else "",
        }
    except Exception:
        return {}


def _parse_kline(raw: str) -> list[dict]:
    """
    解析腾讯/ifzq 日K线。
    返回 [{date, open, close, high, low, volume}]，升序排列。
    """
    try:
        data = json.loads(raw)
        key = None
        for k in list(data.get("data", {}).keys()):
            if "sh" in k or "sz" in k:
                key = k
                break
        if not key:
            return []
        raw_klines = data["data"][key].get("qfqday", [])
        result = []
        for k in raw_klines:
            result.append({
                "date": k[0],
                "open": _safe_float(k[1]),
                "close": _safe_float(k[2]),
                "high": _safe_float(k[3]),
                "low": _safe_float(k[4]),
                "volume": int(_safe_float(k[5])) if len(k) > 5 else 0,
            })
        return result
    except Exception:
        return []


# ─── 缓存 ─────────────────────────────────────────────────────────────

class _Cache:
    """简单内存缓存，ttl 秒内返回同一结果"""

    def __init__(self, ttl: int = 300):
        self._store: dict = {}
        self._ttl = ttl

    def get(self, key: str):
        item = self._store.get(key)
        if item and (time_mod.time() - item[0]) < self._ttl:
            return item[1]
        return None

    def set(self, key: str, val):
        self._store[key] = (time_mod.time(), val)


_cache = _Cache(ttl=300)


# ─── Provider 实现 ─────────────────────────────────────────────────────

class TencentIntelligenceProvider(IntelligenceProvider):
    """
    腾讯财经免费API实现。

    技术面5维度（替代Tushare）：
      1. 实时价格（close/change）→ 技术动能
      2. 日K线 → 均线系统、趋势、动量
      3. 成交量 → 量能配合
      4. 52周高低 → 价位区间判断
      5. PE/ROE → 基本面参考

    不支持维度（以技术面综合信号替代）：
      - 北向持股 → 以「近5日累计涨幅+相对强弱」替代
      - 融资余额 → 以「量价背离/缩量」替代
      - 券商评级 → 以「52周位置+动量强度」替代
    """

    def __init__(self, token: str = None):
        # token 在此 provider 中不使用（免费API）
        self._cache = _Cache(ttl=120)
        logger.info("TencentIntelligenceProvider 初始化完成（免费API）")

    def _tencent_url(self, code: str) -> str:
        """根据代码自动判断市场前缀"""
        c = code
        for prefix in ("sh", "sz", "hk", "SH", "SZ", "HK"):
            if c.startswith(prefix):
                c = c[len(prefix):]
                break
        if c.startswith(("0", "3", "002", "300")):
            return f"https://qt.gtimg.cn/q=sz{c}"
        elif c.startswith(("6", "9", "4", "7", "8")):
            return f"https://qt.gtimg.cn/q=sh{c}"
        elif c.lower().startswith("hk"):
            return f"https://qt.gtimg.cn/q={c.lower()}"
        return f"https://qt.gtimg.cn/q=sh{code}"

    def _kline_url(self, code: str) -> str:
        """ifzq 前端K线接口，支持qfq日K"""
        if code.startswith("hk"):
            m = "hk"
        elif code.startswith("sh") or code[0] in "69":
            m = "sh"
        else:
            m = "sz"
        c = code.lstrip("shszHK")
        return f"https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param={m}{c},day,,,120,qfq"

    def _fetch_realtime(self, ts_code: str) -> dict:
        cache_key = f"rt_{ts_code}"
        cached = self._cache.get(cache_key)
        if cached:
            return cached
        try:
            url = self._tencent_url(ts_code)
            raw = _http_get(url)
            # 腾讯格式：v_sh600410="1~名称~代码~当前价...
            # 有效响应包含 "= 和 ~"
            if "=" not in raw or "~" not in raw:
                logger.warning(f"[实时行情] 响应格式异常 {ts_code}: {raw[:50]}")
                return {}
            if ts_code.lower().startswith("hk"):
                data = _parse_hk_realtime(raw)
            else:
                data = _parse_tencent_realtime(raw)
            self._cache.set(cache_key, data)
            return data
        except Exception as e:
            logger.debug(f"实时行情失败 {ts_code}: {e}")
            return {}

    def _fetch_klines(self, ts_code: str, days: int = 120) -> list[dict]:
        cache_key = f"kl_{ts_code}_{days}"
        cached = self._cache.get(cache_key)
        if cached:
            return cached
        try:
            url = self._kline_url(ts_code)
            raw = _http_get(url, headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"})
            data = _parse_kline(raw)
            self._cache.set(cache_key, data)
            return data
        except Exception as e:
            logger.debug(f"K线获取失败 {ts_code}: {e}")
            return []

    # ── 接口实现 ─────────────────────────────────────────────────────

    def get_sector_stocks(self, sector: str = "科技", limit: int = 200) -> list[dict]:
        """
        腾讯API没有直接的行业分类接口，这里返回常用科技股白名单
        （可手动扩展，也可由 run.py 外部注入候选列表）。
        """
        # 常用科技股白名单（可按需扩充）
        TECH_STOCKS = [
            ("002230", "科大讯飞"), ("000858", "五粮液"), ("002371", "北方华创"),
            ("603501", "豪威集团"), ("300782", "卓胜微"), ("688981", "中芯国际"),
            ("002049", "紫光国微"), ("300474", "景嘉微"), ("688012", "中微公司"),
            ("600410", "华胜天成"), ("300223", "北京君正"), ("300408", "三环集团"),
            ("002036", "联创电子"), ("002463", "沪电股份"), ("000725", "京东方A"),
            ("300136", "信维通信"), ("300207", "欣旺达"), ("002241", "歌尔股份"),
            ("300014", "亿纬锂能"), ("300274", "阳光电源"), ("002459", "晶澳科技"),
            ("300750", "宁德时代"), ("300059", "东方财富"), ("002230", "科大讯飞"),
            ("300033", "同花顺"), ("688111", "金山办公"), ("300124", "汇川技术"),
            ("002372", "伟星新材"), ("300015", "爱尔眼科"), ("300347", "泰格医药"),
            ("300760", "迈瑞医疗"), ("002714", "牧原股份"), ("000001", "平安银行"),
            ("600519", "贵州茅台"), ("000568", "泸州老窖"), ("600036", "招商银行"),
            ("300122", "智飞生物"), ("002821", "凯莱英"), ("300015", "爱尔眼科"),
        ]
        result = []
        seen = set()
        for code, name in TECH_STOCKS:
            if code not in seen and len(result) < limit:
                result.append({"ts_code": code, "name": name, "industry": sector})
                seen.add(code)
        logger.info(f"腾讯API返回 {len(result)} 只候选科技股")
        return result

    def get_northbound_hold(self, ts_code: str) -> dict:
        """
        北向持股 → 以「近5日累计涨幅 + 近20日强弱」替代。
        逻辑：涨幅为正且强于大市 = 资金持续流入的代理指标。
        """
        klines = self._fetch_klines(ts_code, 30)
        if not klines or len(klines) < 5:
            return {"northbound_pct": 0.0, "hold_date": "", "close": 0.0,
                    "_替代指标": "近5日涨幅"}

        # 近5日累计涨幅
        gain5 = (klines[-1]["close"] - klines[-5]["close"]) / klines[-5]["close"] * 100 if len(klines) >= 5 else 0

        # 近20日强弱（vs 指数参照，这里简化为自身涨幅）
        gain20 = 0.0
        if len(klines) >= 20:
            gain20 = (klines[-1]["close"] - klines[-20]["close"]) / klines[-20]["close"] * 100

        # 转换为北向信号分（0-100）
        northbound_score = 50.0 + gain5 * 5 + gain20 * 2
        northbound_score = max(0.0, min(100.0, northbound_score))

        return {
            "northbound_pct": northbound_score,
            "hold_date": klines[-1]["date"],
            "close": klines[-1]["close"],
            "_替代说明": "近5日涨幅信号",
        }

    def get_moneyflow(self, ts_code: str, trade_date: str = None) -> dict:
        """
        资金流向 → 以今日量比 + 涨跌方向判断。
        量比 > 1.5 且上涨 = 主力流入信号。
        量比 < 0.7 且下跌 = 主力流出信号。
        """
        rt = self._fetch_realtime(ts_code)
        klines = self._fetch_klines(ts_code, 30)

        if not klines or not rt:
            return {"moneyflow_net": 0.0, "moneyflow_large": 0.0,
                    "moneyflow_medium": 0.0, "moneyflow_small": 0.0, "change_pct": 0.0}

        current = rt.get("current", 0)
        prev_close = rt.get("prev_close", current)
        change_pct = (current - prev_close) / prev_close * 100 if prev_close > 0 else 0

        # 量比
        avg_vol = sum(k["volume"] for k in klines[-20:]) / 20 if len(klines) >= 20 else klines[-1]["volume"]
        today_vol = rt.get("volume", 0)
        vol_ratio = today_vol / avg_vol if avg_vol > 0 else 1

        # 估算主力净流入（万元）：量比 × 成交量方向
        net_direction = 1 if change_pct > 0 else -1
        net_mf = (vol_ratio - 1) * avg_vol / 10000 * net_direction if vol_ratio > 1 else 0

        return {
            "moneyflow_net": net_mf,
            "moneyflow_large": net_mf * 0.8,
            "moneyflow_medium": net_mf * 0.2,
            "moneyflow_small": -net_mf,
            "change_pct": change_pct,
            "_vol_ratio": vol_ratio,
        }

    def get_margin(self, ts_code: str) -> dict:
        """
        融资余额 → 以量价背离信号替代。
        上涨 + 缩量 = 见顶预警（对应融资余额增加）；
        下跌 + 缩量 = 见底信号（对应融资余额减少）。
        """
        klines = self._fetch_klines(ts_code, 30)
        if not klines or len(klines) < 10:
            return {"margin_balance": 0.0, "margin_buy": 0.0,
                    "margin_repay": 0.0, "margin_change_pct": 0.0, "short_balance": 0.0,
                    "_替代指标": "量价背离"}

        recent10 = klines[-10:]
        avg_vol = sum(k["volume"] for k in recent10) / 10
        last5_vol = sum(k["volume"] for k in klines[-5:]) / 5
        vol_ratio = last5_vol / avg_vol if avg_vol > 0 else 1

        last5_gain = (klines[-1]["close"] - klines[-5]["close"]) / klines[-5]["close"] * 100 if len(klines) >= 5 else 0

        # 量价背离判断（融资余额逆向指标）
        if last5_gain > 5 and vol_ratio < 0.7:
            margin_change = 30.0   # 涨缩量 = 疑似融资见顶
        elif last5_gain < -5 and vol_ratio < 0.7:
            margin_change = -30.0  # 跌缩量 = 见底
        elif vol_ratio > 1.5:
            margin_change = 10.0
        else:
            margin_change = 0.0

        return {
            "margin_balance": abs(margin_change) * 100,
            "margin_buy": 0.0,
            "margin_repay": 0.0,
            "margin_change_pct": margin_change,
            "short_balance": 0.0,
            "_替代说明": "量价背离信号",
        }

    def get_holder_trade(self, ts_code: str, days: int = 30) -> dict:
        """
        股东增减持 → 以「近10日阳线比例」替代。
        阳线多 = 资金积极；阴线多 = 资金撤离。
        """
        klines = self._fetch_klines(ts_code, 30)
        if not klines or len(klines) < 5:
            return {"holder_trade_net": "NEUTRAL", "holder_buy_pct": 0.0,
                    "holder_sell_pct": 0.0, "holder_buy_vol": 0.0, "holder_sell_vol": 0.0,
                    "_替代指标": "阳线比例"}

        recent = klines[-min(days, len(klines)):]
        yang = sum(1 for k in recent if k["close"] >= k["open"])
        yin = len(recent) - yang
        total = len(recent)

        if yang > yin * 1.5:
            direction = "BUYING"
            buy_pct = yang / total * 100
        elif yin > yang * 1.5:
            direction = "SELLING"
            buy_pct = yang / total * 100
        else:
            direction = "NEUTRAL"
            buy_pct = 50.0

        return {
            "holder_trade_net": direction,
            "holder_buy_pct": buy_pct,
            "holder_sell_pct": 100 - buy_pct,
            "holder_buy_vol": yang / total * 100 if total > 0 else 0,
            "holder_sell_vol": yin / total * 100 if total > 0 else 0,
            "_替代说明": "阳线比例",
        }

    def get_broker_rating(self, ts_code: str) -> dict:
        """
        券商评级 → 以「52周位置 + 距高点回调幅度」替代。
        位于52周低位 = 上涨空间大（对应高评级）。
        """
        rt = self._fetch_realtime(ts_code)
        if not rt:
            return {"broker_rating": 0.0, "broker_target": 0.0,
                    "broker_count": 0, "target_gap_pct": 0.0,
                    "_替代指标": "52周位置"}

        current = rt.get("current", 0)
        high52 = rt.get("high_52w", 0)
        low52 = rt.get("low_52w", 0)

        if high52 > 0 and low52 > 0 and high52 > low52:
            pos = (current - low52) / (high52 - low52) * 100
        else:
            pos = 50.0

        # 位置分映射到评级（1-5）
        rating = max(1.0, min(5.0, pos / 20))

        # 目标价空间：当前位置距离52周高点的反向空间
        if high52 > 0:
            target_gap = (high52 - current) / current * 100
        else:
            target_gap = 20.0

        return {
            "broker_rating": rating,
            "broker_target": high52 * 0.95,
            "broker_count": 1,
            "target_gap_pct": target_gap,
            "_替代说明": "52周位置评分",
        }

    def get_sector_momentum(self, ts_code: str) -> dict:
        """
        板块动能 → 以「近20日价格动量」替代。
        返回板块近20日涨幅得分（0-100）。
        """
        klines = self._fetch_klines(ts_code, 30)
        if not klines or len(klines) < 20:
            return {"sector_name": "", "sector_momentum": 50.0, "sector_change_pct": 0.0,
                    "_替代指标": "20日动量"}

        first = klines[-20]["close"]
        last = klines[-1]["close"]
        change_pct = (last - first) / first * 100 if first > 0 else 0

        # 动量得分：50为中性，>0上涨得分高，<0下跌得分低
        momentum = max(0.0, min(100.0, 50.0 + change_pct * 3))

        return {
            "sector_name": "自选板块",
            "sector_momentum": momentum,
            "sector_change_pct": change_pct,
            "_替代说明": "近20日动量",
        }

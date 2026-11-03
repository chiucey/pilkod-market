#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
行情数据获取模块 - 市场数据获取实现
使用新浪、腾讯财经API获取股票行情数据
支持模拟数据模式（当API不可用时）
"""

import json
import time
import re
import random
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple, Union
import urllib.request
import urllib.error
import ssl

# 忽略SSL证书验证
ssl._create_default_https_context = ssl._create_unverified_context

# ========== 股票名称映射 ==========
STOCK_NAMES = {
    # 上海主板 (600/601/603开头)
    "600519": "贵州茅台",
    "600036": "招商银行",
    "600276": "恒瑞医药",
    "600030": "中信证券",
    "600887": "伊利股份",
    "600009": "上海机场",
    "600028": "中国石化",
    "600031": "三一重工",
    "600050": "中国联通",
    "600016": "民生银行",
    "600000": "浦发银行",
    "600585": "海螺水泥",
    "601318": "中国平安",
    "601012": "隆基绿能",
    "601328": "交通银行",
    "601398": "工商银行",
    "601288": "农业银行",
    "601088": "中国神华",
    "601601": "中国太保",
    "601166": "兴业银行",
    "601668": "中国建筑",
    "601211": "国泰君安",
    "601688": "华泰证券",
    "600837": "海通证券",
    "603259": "药明康德",
    "603288": "海天味业",
    "603501": "韦尔股份",
    "603986": "兆易创新",
    "601899": "紫金矿业",
    "601888": "中国中免",
    "601012": "隆基绿能",
    "601857": "中国石油",
    "600690": "海尔智家",
    "600585": "海螺水泥",
    "600809": "山西汾酒",
    "600276": "恒瑞医药",
    "600426": "华鲁恒升",
    "601162": "天风证券",
    "600570": "恒生电子",
    "603160": "汇顶科技",
    "600745": "闻泰科技",
    "601658": "邮储银行",
    "601816": "京沪高铁",
    "600309": "万华化学",
    "600882": "宝隆矿业",
    # 深圳主板 (000开头)
    "000858": "五粮液",
    "000001": "平安银行",
    "000333": "美的集团",
    "002415": "海康威视",
    "000651": "格力电器",
    "000876": "新希望",
    "000568": "泸州老窖",
    "000100": "TCL科技",
    "000002": "万科A",
    "000063": "中兴通讯",
    "000725": "京东方A",
    "000338": "潍柴动力",
    "000661": "长春高新",
    "000596": "古井贡酒",
    "000895": "双汇发展",
    "000983": "山西焦煤",
    "000591": "太阳能",
    "000547": "航天发展",
    "000591": "太阳能",
    "000049": "德赛电池",
    "000538": "云南白药",
    "000423": "东阿阿胶",
    "000501": "鄂武商A",
    "000518": "四环生物",
    # 深圳创业板 (300开头)
    "300750": "宁德时代",
    "300015": "爱尔眼科",
    "300059": "东方财富",
    "300122": "智飞生物",
    "300142": "沃森生物",
    "300274": "阳光电源",
    "300450": "先导智能",
    "300498": "温氏股份",
    "300760": "迈瑞医疗",
    "300124": "汇川技术",
    "300347": "泰格医药",
    "300033": "同花顺",
    "300408": "三环集团",
    "300496": "中科创达",
    "300474": "景嘉微",
    "300014": "亿纬锂能",
    "300223": "鹏辉能源",
    "300124": "汇川技术",
    "300782": "卓胜微",
    "300661": "圣邦股份",
    "300751": "迈为股份",
    "300763": "锦浪科技",
    "300274": "阳光电源",
    # 科创板 (688开头)
    "688041": "海光信息",
    "688981": "中芯国际",
    "688599": "天合光能",
    "688012": "中微公司",
    "688126": "沪硅产业",
    "688111": "金山办公",
    "688008": "澜起科技",
    "688036": "传音控股",
    "688561": "奇安信",
    "688005": "容百科技",
    "688063": "派能科技",
    "688187": "时代电气",
    "688223": "晶科能源",
    "688256": "寒武纪",
    "688385": "复旦微电",
    "688050": "爱博医疗",
    "688185": "康希通信",
    "688123": "聚辰股份",
    "688521": "芯原股份",
    "688220": "翱捷科技"
}

# ========== 模拟数据生成器 ==========

def generate_mock_kline(symbol: str, days: int = 100, base_price: float = None) -> Dict:
    """生成模拟K线数据"""
    # 默认基准价格
    if base_price is None:
        price_ranges = {
            # 上海主板
            "600519": 1800, "600036": 35, "600276": 45, "600030": 20,
            "600887": 28, "600009": 55, "600028": 6, "600031": 15,
            "600050": 4, "600016": 4, "600000": 8, "600585": 30,
            "601318": 45, "601012": 25, "601328": 5, "601398": 5,
            "601288": 3, "601088": 35, "601601": 28, "601166": 17,
            "601668": 5, "601211": 15, "601688": 14, "600837": 9,
            "603259": 85, "603288": 65, "603501": 95, "603986": 120,
            "601899": 15, "601888": 70, "601857": 8, "600690": 22,
            "600809": 280, "600426": 35, "601162": 3, "600570": 45,
            "603160": 95, "600745": 55, "601658": 5, "601816": 5,
            "600309": 95, "600882": 15,
            # 深圳主板
            "000858": 150, "000001": 12, "000333": 60, "002415": 35,
            "000651": 38, "000876": 12, "000568": 180, "000100": 4,
            "000002": 8, "000063": 30, "000725": 4, "000338": 12,
            "000661": 160, "000596": 200, "000895": 25, "000983": 8,
            "000591": 8, "000547": 12, "000049": 45, "000538": 55,
            "000423": 40, "000501": 8, "000518": 4,
            # 创业板
            "300750": 180, "300015": 25, "300059": 18, "300122": 85,
            "300142": 35, "300274": 90, "300450": 35, "300498": 20,
            "300760": 280, "300124": 55, "300347": 90, "300033": 95,
            "300408": 30, "300496": 85, "300474": 55, "300014": 60,
            "300223": 25, "300782": 85, "300661": 120, "300751": 180,
            "300763": 85, "300274": 90,
            # 科创板
            "688041": 55, "688981": 45, "688599": 18, "688012": 120,
            "688126": 15, "688111": 280, "688008": 65, "688036": 80,
            "688561": 55, "688005": 35, "688063": 180, "688187": 55,
            "688223": 8, "688256": 150, "688385": 45, "688050": 180,
            "688185": 15, "688123": 55, "688521": 45, "688220": 35
        }
        base_price = price_ranges.get(symbol, 50)

    # 生成历史价格
    prices = []
    current_price = base_price

    for i in range(days):
        # 随机波动 ±3%
        change = random.uniform(-0.03, 0.03)
        # 加入小幅趋势
        trend = 0.0005 if i < days // 2 else -0.0003
        change += trend

        current_price = current_price * (1 + change)
        prices.append(round(current_price, 2))

    # 生成日期
    dates = []
    for i in range(days):
        date = datetime.now() - timedelta(days=days - i - 1)
        dates.append(date.strftime("%Y-%m-%d"))

    # 生成OHLCV
    kline = {
        "dates": dates,
        "open": [],
        "high": [],
        "low": [],
        "close": prices,
        "volume": [random.randint(500000, 2000000) for _ in range(days)],
        "turnover": []
    }

    for i, close in enumerate(prices):
        # 基于收盘价生成open/high/low
        spread = close * random.uniform(0.005, 0.015)
        open_price = close + random.uniform(-spread, spread)
        high = max(close, open_price) + close * random.uniform(0, 0.01)
        low = min(close, open_price) - close * random.uniform(0, 0.01)

        kline["open"].append(round(open_price, 2))
        kline["high"].append(round(high, 2))
        kline["low"].append(round(low, 2))
        kline["turnover"].append(round(close * kline["volume"][i] * random.uniform(10, 15), 2))

    return kline


def generate_mock_realtime(symbol: str) -> Dict:
    """生成模拟实时行情"""
    kline = generate_mock_kline(symbol, days=1)
    close = kline["close"][0]
    open_price = kline["open"][0]
    prev_close = close * random.uniform(0.97, 1.03)

    name = STOCK_NAMES.get(symbol, f"股票{symbol}")
    change = close - prev_close
    change_pct = change / prev_close * 100 if prev_close > 0 else 0

    return {
        "symbol": symbol,
        "name": name,
        "open": open_price,
        "prev_close": round(prev_close, 2),
        "close": close,
        "high": kline["high"][0],
        "low": kline["low"][0],
        "volume": kline["volume"][0],
        "turnover": kline["turnover"][0],
        "bid": round(close * 0.9999, 2),
        "ask": round(close * 1.0001, 2),
        "change": round(change, 2),
        "change_pct": round(change_pct, 2),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }


def generate_mock_valuation(symbol: str) -> Dict:
    """生成模拟估值数据"""
    valuations = {
        "600519": {"pe": 28.5, "pb": 5.2, "market_cap": 2200, "dividend": 2.3},
        "000858": {"pe": 22.0, "pb": 4.1, "market_cap": 580, "dividend": 3.1},
        "601318": {"pe": 9.5, "pb": 1.2, "market_cap": 850, "dividend": 4.5},
        "600036": {"pe": 8.5, "pb": 1.1, "market_cap": 920, "dividend": 5.2},
        "000001": {"pe": 7.2, "pb": 0.9, "market_cap": 230, "dividend": 4.8},
        "300750": {"pe": 35.0, "pb": 6.5, "market_cap": 850, "dividend": 0.8},
        "601012": {"pe": 15.0, "pb": 2.8, "market_cap": 1800, "dividend": 2.5},
        "002594": {"pe": 25.0, "pb": 4.5, "market_cap": 720, "dividend": 1.5},
        "600030": {"pe": 18.0, "pb": 1.5, "market_cap": 2800, "dividend": 2.0},
        "000333": {"pe": 12.0, "pb": 3.2, "market_cap": 3800, "dividend": 4.0}
    }

    val = valuations.get(symbol, {"pe": 15.0, "pb": 2.0, "market_cap": 500, "dividend": 2.5})

    return {
        "symbol": symbol,
        "name": STOCK_NAMES.get(symbol, f"股票{symbol}"),
        "price": 100,  # 会在外部覆盖
        "pe_ttm": val["pe"] * random.uniform(0.95, 1.05),
        "pe_lyr": val["pe"] * 0.95,
        "pb": val["pb"] * random.uniform(0.98, 1.02),
        "dividend_yield": val["dividend"],
        "market_cap": val["market_cap"],
        "float_market_cap": val["market_cap"] * 0.85,
        "total_shares": val["market_cap"] * 10,
        "float_shares": val["market_cap"] * 8.5
    }


class MarketDataFetcher:
    """行情数据获取器"""

    # 多组User-Agent随机轮换，防封禁
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    ]

    def __init__(self, use_cache: bool = True, cache_ttl: int = 300):
        self.use_cache = use_cache
        self.cache_ttl = cache_ttl
        self._cache: Dict[str, Tuple[float, any]] = {}

    def _get_headers(self) -> Dict[str, str]:
        """获取随机Headers"""
        return {
            'User-Agent': random.choice(self.USER_AGENTS),
            'Referer': 'https://finance.sina.com.cn',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive'
        }

    def _get_cache(self, key: str) -> Optional[any]:
        """获取缓存"""
        if not self.use_cache:
            return None
        if key in self._cache:
            timestamp, value = self._cache[key]
            if time.time() - timestamp < self.cache_ttl:
                return value
        return None

    def _set_cache(self, key: str, value: any):
        """设置缓存"""
        if self.use_cache:
            self._cache[key] = (time.time(), value)

    def _parse_tencent_quotes(self, response: str, symbols: List[str], cache_key: str) -> Dict:
        """解析腾讯财经实时行情数据"""
        result = {
            "code": 0,
            "message": "success",
            "data": {},
            "timestamp": datetime.now().isoformat(),
            "source": "Tencent Finance"
        }

        lines = response.strip().split('\n')
        for i, line in enumerate(lines):
            if '=' not in line or i >= len(symbols):
                continue

            # 腾讯格式: v_pvphq001_sh600519="..."
            try:
                data_str = line.split('="')[1].split('"')[0] if '="' in line else ""
                if not data_str:
                    continue

                fields = data_str.split('~')
                if len(fields) < 50:
                    continue

                symbol = symbols[i]
                result["data"][symbol] = {
                    "symbol": symbol,
                    "name": fields[1] if len(fields) > 1 else STOCK_NAMES.get(symbol, symbol),
                    "close": float(fields[3]) if fields[3] else 0,
                    "prev_close": float(fields[4]) if fields[4] else 0,
                    "open": float(fields[5]) if fields[5] else 0,
                    "volume": int(fields[6]) if fields[6] else 0,
                    "turnover": float(fields[7]) if fields[7] else 0,
                    "bid": float(fields[9]) if len(fields) > 9 and fields[9] else 0,
                    "ask": float(fields[19]) if len(fields) > 19 and fields[19] else 0,
                    "high": float(fields[33]) if len(fields) > 33 and fields[33] else 0,
                    "low": float(fields[34]) if len(fields) > 34 and fields[34] else 0,
                    "change": float(fields[31]) if len(fields) > 31 and fields[31] else 0,
                    "change_pct": float(fields[32]) if len(fields) > 32 and fields[32] else 0,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            except (ValueError, IndexError):
                continue

        self._set_cache(cache_key, result)
        return result

    def _fetch_eastmoney_kline(self, market: str, code: str, period_code: str, start_date: str, end_date: str, adjust: str) -> Optional[Dict]:
        """东方财富K线接口"""
        try:
            # 东方财富股票代码格式
            ef_market = "1" if market == "sh" else "0"
            secid = f"{ef_market}.{code}"
            url = f"https://push2his.eastmoney.com/api/qt/stock/kline/get?fields1=f1,f2,f3,f4,f5,f6&fields2=f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61&ut=7eea3edcaed734bea9cbfc24409ed989&klt=101&fqt={1 if adjust == 'qfq' else 0}&beg={start_date}&end={end_date}&smplmt={460}&lmt=1000000&secid={secid}"

            response = self._http_get(url)
            if not response:
                return None

            data = json.loads(response)
            klines = data.get('data', {}).get('klines', [])
            if not klines:
                return None

            result = {"dates": [], "open": [], "high": [], "low": [], "close": [], "volume": [], "turnover": []}
            for line in klines:
                fields = line.split(',')
                if len(fields) >= 6:
                    result["dates"].append(fields[0])
                    result["open"].append(float(fields[1]))
                    result["close"].append(float(fields[2]))
                    result["high"].append(float(fields[3]))
                    result["low"].append(float(fields[4]))
                    result["volume"].append(int(fields[5]))
                    result["turnover"].append(float(fields[6]) if len(fields) > 6 else 0)
            return result
        except Exception:
            return None

    def _fetch_netease_kline(self, market: str, code: str, start_date: str, end_date: str) -> Optional[Dict]:
        """163财经K线接口"""
        try:
            # 163财经股票代码格式
            nt_market = "0" if market == "sh" else "1"
            stock_code = f"{nt_market}{code}"
            url = f"http://quotes.money.163.com/service/chddata.html?code={stock_code}&start={start_date}&end={end_date}&fields=TCLOSE;HIGH;LOW;TOPEN;LCLOSE;CHG;PCHG;TURNOVER;VOTURNOVER;VATURNOVER"

            response = self._http_get(url)
            if not response:
                return None

            lines = response.strip().split('\n')
            if len(lines) < 2:
                return None

            result = {"dates": [], "open": [], "high": [], "low": [], "close": [], "volume": [], "turnover": []}
            for line in lines[1:]:  # 跳过表头
                fields = line.split(',')
                if len(fields) >= 10:
                    try:
                        result["dates"].append(fields[0])
                        result["close"].append(float(fields[3]) if fields[3] else 0)
                        result["open"].append(float(fields[6]) if fields[6] else 0)
                        result["high"].append(float(fields[4]) if fields[4] else 0)
                        result["low"].append(float(fields[5]) if fields[5] else 0)
                        result["volume"].append(int(float(fields[7])) if fields[7] else 0)
                        result["turnover"].append(float(fields[9]) if fields[9] else 0)
                    except (ValueError, IndexError):
                        continue
            return result if result["dates"] else None
        except Exception:
            return None

    def _http_get(self, url: str, timeout: int = 10, use_gbk: bool = False) -> Optional[str]:
        """HTTP GET请求，支持GBK编码自动转换"""
        try:
            headers = self._get_headers()
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=timeout) as response:
                raw_data = response.read()
                # 尝试GBK解码（新浪财经使用GBK编码）
                if use_gbk:
                    try:
                        return raw_data.decode('gbk')
                    except UnicodeDecodeError:
                        return raw_data.decode('utf-8', errors='replace')
                else:
                    try:
                        return raw_data.decode('utf-8')
                    except UnicodeDecodeError:
                        # UTF-8失败时自动尝试GBK
                        try:
                            return raw_data.decode('gbk')
                        except UnicodeDecodeError:
                            return raw_data.decode('utf-8', errors='replace')
        except Exception as e:
            print(f"请求失败: {url}, 错误: {e}")
            return None

    def _fetch_tencent_kline(self, market: str, code: str,
                              start_date: str, end_date: str,
                              period: str = "day",
                              count: int = 80,
                              adjust: str = "qfq") -> Optional[Dict]:
        """
        腾讯财经K线专用获取方法（已验证可用格式）

        Args:
            market: sh/sz（小写）
            code: 股票代码（不带前缀）
            start_date: YYYY-MM-DD 或 YYYYMMDD
            end_date: YYYY-MM-DD 或 YYYYMMDD
            period: day/week/month/1/5/15/30/60
            count: 数量（建议80-500）
            adjust: qfq/hfq/none

        Returns:
            {"dates":[], "open":[], "close":[], "high":[], "low":[], "volume":[]}
        """
        # 标准化日期格式
        def fmt_date(d):
            if not d: return ""
            d = str(d).replace("-", "")
            return f"{d[:4]}-{d[4:6]}-{d[6:8]}" if len(d) == 8 else d

        start_fmt = fmt_date(start_date)
        end_fmt   = fmt_date(end_date)

        # 确定 var 后缀和字段名
        if period == "day":
            var_part = "kline_dayqfq"
            field_key = "qfqday"
        elif period == "week":
            var_part = "kline_weekqfq"
            field_key = "qfqweek"
        elif period == "month":
            var_part = "kline_monthqfq"
            field_key = "qfqmonth"
        else:
            var_part = f"kline_{period}fq"
            field_key = f"qfq{period}"

        url = (f"https://web.ifzq.gtimg.cn/appstock/app/fqkline/get"
               f"?_var={var_part}&param={market}{code},{period},"
               f"{start_fmt},{end_fmt},{count},{adjust}")

        try:
            # 腾讯财经需要特定的Referer头
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Referer': 'https://finance.qq.com/'
            }
            req = urllib.request.Request(url, headers=headers)
            ctx = ssl._create_unverified_context()
            with urllib.request.urlopen(req, timeout=8, context=ctx) as resp:
                raw = resp.read().decode('utf-8')

            json_str = raw.split('=', 1)[1] if '=' in raw else raw
            d = json.loads(json_str)

            tencent_key = f"{market}{code}"
            qt = d.get('data', {}).get(tencent_key, {})
            klines = qt.get(field_key, [])

            if not klines or len(klines) < 2:
                return None

            result = {"dates": [], "open": [], "close": [],
                      "high": [], "low": [], "volume": [], "turnover": []}
            for item in klines:
                if len(item) >= 6:
                    result["dates"].append(str(item[0]))
                    result["open"].append(float(item[1]))
                    result["close"].append(float(item[2]))
                    result["high"].append(float(item[3]))
                    result["low"].append(float(item[4]))
                    vol = item[5]
                    # volume字段类型可能是 str / list / dict，做安全转换
# 安全转换volume字段（str/list/dict）
                    vol_val = item[5]
                    try:
                        if isinstance(vol_val, str):
                            vol_int = int(float(vol_val))
                            vol_int = int(float(vol_val[0]) if vol_val else 0)
                            vol_int = int(float(vol_val.get("vol", 0) or 0))
                        else:
                            vol_int = int(float(vol_val))
                    except (ValueError, TypeError):
                        vol_int = 0
                    result["data"]["volume"].append(vol_int)
                            result["volume"].append(int(float(vol.get('vol', vol.get('volume', 0)))))
                        else:
# 安全转换volume字段（str/list/dict）
                    vol_val = item[5]
                    try:
                        if isinstance(vol_val, str):
                            vol_int = int(float(vol_val))
                            vol_int = int(float(vol_val[0]) if vol_val else 0)
                            vol_int = int(float(vol_val.get("vol", 0) or 0))
                        else:
                            vol_int = int(float(vol_val))
                    except (ValueError, TypeError):
                        vol_int = 0
                    result["data"]["volume"].append(vol_int)
                    except (ValueError, TypeError):
                        result["volume"].append(0)
                    result["turnover"].append(float(item[6]) if len(item) > 6 else 0.0)
            return result
        except Exception as e:
            print(f"[腾讯K线] 获取失败 {market}{code}: {e}")
            return None

    def normalize_symbol(self, symbol: str, market: str = None) -> Tuple[str, str]:
        """标准化股票代码，返回 (市场代码, 完整代码)"""
        symbol = symbol.strip().upper()

        # 如果代码以6开头，则为上海
        if symbol.startswith('6') or symbol.startswith('5'):
            market = 'sh'
        # 如果代码以0、3开头，则为深圳
        elif symbol.startswith('0') or symbol.startswith('3'):
            market = 'sz'
        # 创业板以3开头
        elif symbol.startswith('300'):
            market = 'sz'
        # 科创板以688开头
        elif symbol.startswith('688'):
            market = 'sh'
        # 已经是完整代码
        elif symbol.startswith(('sh', 'sz', 'SH', 'SZ')):
            return symbol[:2].lower(), symbol[2:]

        if market is None:
            market = 'sz'  # 默认深圳

        return market, symbol

    def get_realtime_quotes(self, symbols: List[str]) -> Dict:
        """
        获取实时行情数据
        使用新浪财经实时行情接口

        Args:
            symbols: 股票代码列表，如 ["600519", "000858"]

        Returns:
            包含实时行情数据的字典
        """
        result = {
            "code": 0,
            "message": "success",
            "data": {},
            "timestamp": datetime.now().isoformat(),
            "source": "Sina Finance"
        }

        if not symbols:
            result["code"] = 1003
            result["message"] = "股票代码列表为空"
            return result

        # 构建新浪行情URL
        market_codes = []
        for symbol in symbols:
            market, code = self.normalize_symbol(symbol)
            market_codes.append(f"{market}{code}")

        url = f"https://hq.sinajs.cn/list={','.join(market_codes)}"

        # 检查缓存
        cache_key = f"realtime:{','.join(symbols)}"
        cached = self._get_cache(cache_key)
        if cached:
            return cached

        response = self._http_get(url)

        if not response:
            # 新浪API不可用，尝试腾讯财经备用
            print("[备用源] 新浪API失败，尝试腾讯财经...")
            tencent_url = f"https://qt.gtimg.cn/q={','.join(market_codes)}"
            response = self._http_get(tencent_url)
            if response and response.strip():
                result["source"] = "Tencent Finance"
                # 使用腾讯格式解析
                return self._parse_tencent_quotes(response, symbols, cache_key)
            else:
                # 腾讯也失败，使用模拟数据
                print("[模拟数据] API不可用，使用模拟数据")
                result["source"] = "Mock Data"
                for symbol in symbols:
                    result["data"][symbol] = generate_mock_realtime(symbol)
                self._set_cache(cache_key, result)
                return result

        # 解析数据
        lines = response.strip().split('\n')
        for i, line in enumerate(lines):
            if '=' not in line:
                continue
            if i >= len(symbols):
                break

            code_part = line.split('=')[0].split('_')[-1]
            data_str = line.split('="')[1].split('"')[0] if '="' in line else ""

            if not data_str:
                result["data"][symbols[i]] = {
                    "symbol": symbols[i],
                    "name": STOCK_NAMES.get(symbols[i], "未知"),
                    "error": "无数据"
                }
                continue

            fields = data_str.split(',')

            if len(fields) >= 32:
                result["data"][symbols[i]] = {
                    "symbol": symbols[i],
                    "name": fields[0],
                    "open": float(fields[1]) if fields[1] else 0,
                    "prev_close": float(fields[2]) if fields[2] else 0,
                    "close": float(fields[3]) if fields[3] else 0,
                    "high": float(fields[4]) if fields[4] else 0,
                    "low": float(fields[5]) if fields[5] else 0,
                    "volume": int(fields[8]) if fields[8] else 0,
                    "turnover": float(fields[9]) if fields[9] else 0,
                    "bid": float(fields[19]) if len(fields) > 19 and fields[19] else 0,
                    "ask": float(fields[21]) if len(fields) > 21 and fields[21] else 0,
                    "change": float(fields[3]) - float(fields[2]) if fields[3] and fields[2] else 0,
                    "change_pct": ((float(fields[3]) - float(fields[2])) / float(fields[2]) * 100) if fields[3] and fields[2] and float(fields[2]) > 0 else 0,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }

        self._set_cache(cache_key, result)
        return result

    def get_kline_data(self, symbol: str, period: str = "daily",
                       start_date: str = None, end_date: str = None,
                       adjust: str = "qfq") -> Dict:
        """
        获取K线数据
        使用腾讯财经K线接口

        Args:
            symbol: 股票代码，如 "600519"
            period: 周期类型，1min/5min/15min/30min/60min/daily/weekly/monthly
            start_date: 开始日期 YYYYMMDD
            end_date: 结束日期 YYYYMMDD
            adjust: 复权类型 qfq(前复权)/hfq(后复权)/none(不复权)

        Returns:
            包含K线数据的字典
        """
        result = {
            "code": 0,
            "message": "success",
            "data": {
                "symbol": symbol,
                "period": period,
                "dates": [],
                "open": [],
                "high": [],
                "low": [],
                "close": [],
                "volume": [],
                "turnover": []
            },
            "timestamp": datetime.now().isoformat(),
            "source": "Tencent Finance"
        }

        # 标准化股票代码
        market, code = self.normalize_symbol(symbol)
        secid = f"{market.upper()}{code}"

        # 周期映射：内部周期名 → 腾讯period值
        period_str_map = {
            "1min": "1", "5min": "5", "15min": "15",
            "30min": "30", "60min": "60",
            "daily": "day", "weekly": "week", "monthly": "month"
        }
        period_str = period_str_map.get(period, "day")

        # 日期处理
        if not end_date:
            end_date = datetime.now().strftime("%Y%m%d")
        if not start_date:
            start_date = (datetime.now() - timedelta(days=365)).strftime("%Y%m%d")

        # 检查缓存
        cache_key = f"kline:{symbol}:{period}:{start_date}:{end_date}"
        cached = self._get_cache(cache_key)
        if cached:
            return cached

        # 主要数据源：腾讯财经（已验证）
        kline_data = self._fetch_tencent_kline(
            market=market,
            code=code,
            start_date=start_date,
            end_date=end_date,
            period=period_str,
            count=80 if period == "daily" else 500,
            adjust="qfq" if adjust == "qfq" else "none"
        )

        if kline_data and kline_data.get("dates"):
            result["source"] = "Tencent Finance"
            result["data"] = kline_data
            result["data"]["count"] = len(kline_data["dates"])
            result["data"]["symbol"] = symbol
            result["data"]["period"] = period
            self._set_cache(cache_key, result)
            return result

        # 腾讯失败，尝试东方财富
        print("[备用源] 腾讯K线失败，尝试东方财富...")
        period_code = {"daily": "101", "weekly": "102", "monthly": "103"}.get(period, "101")
        ef_response = self._fetch_eastmoney_kline(market, code, period_code, start_date, end_date, adjust)
        if ef_response:
            result["source"] = "East Money"
            result["data"] = ef_response
            result["data"]["count"] = len(result["data"]["dates"])
            self._set_cache(cache_key, result)
            return result

        # 东方财富也失败，尝试163财经
        print("[备用源] 东方财富失败，尝试163财经...")
        netease_response = self._fetch_netease_kline(market, code, start_date, end_date)
        if netease_response:
            result["source"] = "163 Finance"
            result["data"] = netease_response
            result["data"]["count"] = len(result["data"]["dates"])
            self._set_cache(cache_key, result)
            return result

        # 所有API都失败，使用模拟数据
        print(f"[模拟数据] K线API不可用，为 {symbol} 生成模拟数据")
        result["source"] = "Mock Data"
        mock_data = generate_mock_kline(symbol, days=120)
        result["data"]["dates"] = mock_data["dates"]
        result["data"]["open"] = mock_data["open"]
        result["data"]["close"] = mock_data["close"]
        result["data"]["high"] = mock_data["high"]
        result["data"]["low"] = mock_data["low"]
        result["data"]["volume"] = mock_data["volume"]
        result["data"]["turnover"] = mock_data["turnover"]
        result["data"]["count"] = len(result["data"]["dates"])
        self._set_cache(cache_key, result)
        return result

        try:
            # 解析数据 (格式: kline_dayqfq={"code":0,"data":{"sh600519":{"qfqday":[[date,open,close,high,low,vol],...]}}})
            json_str = response.split('=', 1)[1] if '=' in response else response
            data = json.loads(json_str)

            # 腾讯K线的key格式: "sh600519"（小写市场前缀）
            tencent_key = f"{market}{code}"
            qt = data.get('data', {}).get(tencent_key, {})

            # 复权日K数据在 qfqday 字段（其他周期类似: qfqweek, qfqmonth）
            kline_field = f"qfq{period_str}" if period_str in ("day", "week", "month") else None
            if kline_field:
                klines = qt.get(kline_field, [])
            else:
                # 分钟K: 直接取 data 数组
                klines = qt.get('data', qt.get('qfq', []))

            if isinstance(klines, list):
                for item in klines:
                    if len(item) >= 6:
                        result["data"]["dates"].append(str(item[0]))
                        result["data"]["open"].append(float(item[1]))
                        result["data"]["close"].append(float(item[2]))
                        result["data"]["high"].append(float(item[3]))
                        result["data"]["low"].append(float(item[4]))
                        # 安全转换volume字段（可能为str/list/dict）
                    vol_val = item[5]
                    try:
                        if isinstance(vol_val, str):
                            vol_int = int(float(vol_val))
                            vol_int = int(float(vol_val[0]) if vol_val else 0)
                            vol_int = int(float(vol_val.get('vol', 0) or 0))
                        else:
                            vol_int = int(float(vol_val))
                    except (ValueError, TypeError):
                        vol_int = 0
                    result["data"]["volume"].append(vol_int)
                        result["data"]["turnover"].append(float(item[6]) if len(item) > 6 else 0.0)

            result["data"]["count"] = len(result["data"]["dates"])

        except Exception as e:
            # 解析失败，使用模拟数据
            print(f"[模拟数据] K线解析失败，为 {symbol} 使用模拟数据: {e}")
            result["source"] = "Mock Data"
            # 腾讯API不可用，尝试东方财富备用
            print(f"[备用源] 腾讯K线失败，尝试东方财富...")
            ef_response = self._fetch_eastmoney_kline(market, code, period_code, start_date, end_date, adjust)
            if ef_response:
                result["source"] = "East Money"
                result["data"] = ef_response
                result["data"]["count"] = len(result["data"]["dates"])
                self._set_cache(cache_key, result)
                return result

            # 东方财富也失败，尝试163财经
            print(f"[备用源] 东方财富失败，尝试163财经...")
            netease_response = self._fetch_netease_kline(market, code, start_date, end_date)
            if netease_response:
                result["source"] = "163 Finance"
                result["data"] = netease_response
                result["data"]["count"] = len(result["data"]["dates"])
                self._set_cache(cache_key, result)
                return result

            # 所有API都失败，使用模拟数据
            print(f"[模拟数据] K线API不可用，为 {symbol} 生成模拟数据")
            result["source"] = "Mock Data"
            mock_data = generate_mock_kline(symbol, days=120)
            result["data"]["dates"] = mock_data["dates"]
            result["data"]["open"] = mock_data["open"]
            result["data"]["close"] = mock_data["close"]
            result["data"]["high"] = mock_data["high"]
            result["data"]["low"] = mock_data["low"]
            result["data"]["volume"] = mock_data["volume"]
            result["data"]["turnover"] = mock_data["turnover"]
            result["data"]["count"] = len(result["data"]["dates"])
            self._set_cache(cache_key, result)
            return result

        try:
            # 解析数据 (格式: kline_dayqfq={"code":0,"data":{"sh600519":{"qfqday":[[date,open,close,high,low,vol],...]}}})
            json_str = response.split('=', 1)[1] if '=' in response else response
            data = json.loads(json_str)

            # 腾讯K线的key格式: "sh600519"（小写市场前缀）
            tencent_key = f"{market}{code}"
            qt = data.get('data', {}).get(tencent_key, {})

            # 复权日K数据在 qfqday 字段（其他周期类似: qfqweek, qfqmonth）
            kline_field = f"qfq{period_str}" if period_str in ("day", "week", "month") else None
            if kline_field:
                klines = qt.get(kline_field, [])
            else:
                # 分钟K: 直接取 data 数组
                klines = qt.get('data', qt.get('qfq', []))

            if isinstance(klines, list):
                for item in klines:
                    if len(item) >= 6:
                        result["data"]["dates"].append(str(item[0]))
                        result["data"]["open"].append(float(item[1]))
                        result["data"]["close"].append(float(item[2]))
                        result["data"]["high"].append(float(item[3]))
                        result["data"]["low"].append(float(item[4]))
                        # 安全转换volume字段（可能为str/list/dict）
                    vol_val = item[5]
                    try:
                        if isinstance(vol_val, str):
                            vol_int = int(float(vol_val))
                            vol_int = int(float(vol_val[0]) if vol_val else 0)
                            vol_int = int(float(vol_val.get('vol', 0) or 0))
                        else:
                            vol_int = int(float(vol_val))
                    except (ValueError, TypeError):
                        vol_int = 0
                    result["data"]["volume"].append(vol_int)
                        result["data"]["turnover"].append(float(item[6]) if len(item) > 6 else 0.0)

            result["data"]["count"] = len(result["data"]["dates"])

        except Exception as e:
            # 解析失败，使用模拟数据
            print(f"[模拟数据] K线解析失败，为 {symbol} 使用模拟数据: {e}")
            result["source"] = "Mock Data"
            mock_data = generate_mock_kline(symbol, days=120)
            result["data"]["dates"] = mock_data["dates"]
            result["data"]["open"] = mock_data["open"]
            result["data"]["close"] = mock_data["close"]
            result["data"]["high"] = mock_data["high"]
            result["data"]["low"] = mock_data["low"]
            result["data"]["volume"] = mock_data["volume"]
            result["data"]["turnover"] = mock_data["turnover"]
            result["data"]["count"] = len(result["data"]["dates"])

        self._set_cache(cache_key, result)
        return result

    def get_market_data(self, symbols: List[str], interval: str = "daily",
                        start_date: str = None, end_date: str = None,
                        adjust: str = "qfq") -> Dict:
        """
        获取股票行情数据 (K线)

        Args:
            symbols: 股票代码列表
            interval: 数据周期 1d/1w/1m
            start_date: 开始日期 YYYY-MM-DD
            end_date: 结束日期 YYYY-MM-DD
            adjust: 复权类型

        Returns:
            包含K线数据的字典
        """
        result = {
            "code": 0,
            "message": "success",
            "data": {},
            "timestamp": datetime.now().isoformat()
        }

        # 转换日期格式
        start = start_date.replace('-', '') if start_date else None
        end = end_date.replace('-', '') if end_date else None

        # 周期映射
        period_map = {
            "1m": "1min",
            "5m": "5min",
            "15m": "15min",
            "30m": "30min",
            "60m": "60min",
            "1h": "60min",
            "1d": "daily",
            "1w": "weekly",
            "1mo": "monthly"
        }

        period = period_map.get(interval, "daily")

        for symbol in symbols:
            data = self.get_kline_data(symbol, period, start, end, adjust)
            if data["code"] == 0:
                result["data"][symbol] = data["data"]
            else:
                result["data"][symbol] = {"error": data["message"]}

        return result


class FundamentalsFetcher:
    """基本面数据获取器"""

    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0'
    ]

    def _get_headers(self) -> Dict[str, str]:
        return {
            'User-Agent': random.choice(self.USER_AGENTS),
            'Referer': 'https://finance.eastmoney.com'
        }

    def _http_get(self, url: str, timeout: int = 15) -> Optional[str]:
        """HTTP GET请求，支持GBK编码自动转换"""
        try:
            headers = self._get_headers()
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=timeout) as response:
                raw_data = response.read()
                try:
                    return raw_data.decode('utf-8')
                except UnicodeDecodeError:
                    try:
                        return raw_data.decode('gbk')
                    except UnicodeDecodeError:
                        return raw_data.decode('utf-8', errors='replace')
        except Exception as e:
            print(f"请求失败: {url}, 错误: {e}")
            return None

    def get_financial_summary(self, symbol: str) -> Dict:
        """
        获取股票财务摘要数据
        使用新浪财经财务接口

        Args:
            symbol: 股票代码，如 "600519"

        Returns:
            包含财务摘要的字典
        """
        result = {
            "code": 0,
            "message": "success",
            "data": {
                "symbol": symbol,
                "valuation": {},
                "financial": {}
            },
            "timestamp": datetime.now().isoformat()
        }

        # 标准化代码
        if symbol.startswith('6'):
            market = 'sh'
        else:
            market = 'sz'

        # 获取财务数据
        url = f"https://money.finance.sina.com.cn/corp/go.php/vFD_FinanceSummary/stockid/{symbol}.phtml"

        # 获取估值数据
        val_url = f"https://hq.sinajs.cn/list={market}{symbol}"

        response = self._http_get(val_url)

        if response:
            try:
                # 解析实时数据中的估值信息
                line = response.strip()
                if '="' in line:
                    data_str = line.split('="')[1].split('"')[0]
                    fields = data_str.split(',')

                    if len(fields) >= 35:
                        price = float(fields[3]) if fields[3] else 0

                        result["data"]["valuation"] = {
                            "name": fields[0],
                            "price": price,
                            "change": float(fields[3]) - float(fields[2]) if fields[3] and fields[2] else 0,
                            "change_pct": ((float(fields[3]) - float(fields[2])) / float(fields[2]) * 100) if fields[3] and fields[2] and float(fields[2]) > 0 else 0,
                            "open": float(fields[1]) if fields[1] else 0,
                            "prev_close": float(fields[2]) if fields[2] else 0,
                            "high": float(fields[4]) if fields[4] else 0,
                            "low": float(fields[5]) if fields[5] else 0,
                            "volume": int(fields[8]) if fields[8] else 0,
                            "market_cap": float(fields[9]) if fields[9] else 0,  # 市值
                            "pe_ttm": float(fields[39]) if len(fields) > 39 and fields[39] else None,  # 市盈率TTM
                            "pb": float(fields[46]) if len(fields) > 46 and fields[46] else None,  # 市净率
                        }
            except Exception as e:
                result["message"] = f"数据解析部分失败: {str(e)}"

        # 获取基本面财务数据
        fund_url = f"https://stock.finance.sina.com.cn/stock/go.php/vFinanceAnalyze/kind/mainIndex/index.phtml?symbol={market.upper()}{symbol}"

        fund_response = self._http_get(fund_url)

        if fund_response:
            result["data"]["financial"]["raw_data"] = "需要进一步解析HTML"

        return result

    def get_valuation_metrics(self, symbol: str) -> Dict:
        """
        获取估值指标

        Args:
            symbol: 股票代码

        Returns:
            包含估值指标的字典
        """
        result = {
            "code": 0,
            "message": "success",
            "data": {},
            "timestamp": datetime.now().isoformat()
        }

        # 标准化代码
        if symbol.startswith('6'):
            market = 'sh'
        else:
            market = 'sz'

        url = f"https://hq.sinajs.cn/list={market}{symbol}"
        response = self._http_get(url)

        if not response:
            # API不可用，使用模拟数据
            print(f"[模拟数据] 估值API不可用，为 {symbol} 使用模拟数据")
            result["data"] = generate_mock_valuation(symbol)
            return result

        try:
            line = response.strip()
            if '="' in line:
                data_str = line.split('="')[1].split('"')[0]
                fields = data_str.split(',')

                if len(fields) >= 46:
                    price = float(fields[3]) if fields[3] else 0
                    prev_close = float(fields[2]) if fields[2] else 0

                    result["data"] = {
                        "symbol": symbol,
                        "name": fields[0],
                        "price": price,
                        "pe_ttm": float(fields[39]) if len(fields) > 39 and fields[39] and fields[39] != '-' else None,
                        "pe_lyr": float(fields[40]) if len(fields) > 40 and fields[40] and fields[40] != '-' else None,
                        "pb": float(fields[46]) if len(fields) > 46 and fields[46] and fields[46] != '-' else None,
                        "dividend_yield": float(fields[47]) if len(fields) > 47 and fields[47] and fields[47] != '-' else None,
                        "market_cap": float(fields[44]) / 100000000 if len(fields) > 44 and fields[44] else None,  # 亿
                        "float_market_cap": float(fields[45]) / 100000000 if len(fields) > 45 and fields[45] else None,  # 亿
                        "total_shares": float(fields[43]) / 100000000 if len(fields) > 43 and fields[43] else None,  # 亿股
                        "float_shares": float(fields[42]) / 100000000 if len(fields) > 42 and fields[42] else None,  # 亿股
                    }
        except Exception as e:
            # 解析失败，使用模拟数据
            print(f"[模拟数据] 估值解析失败，为 {symbol} 使用模拟数据")
            result["data"] = generate_mock_valuation(symbol)

        return result


# ========== 对外API函数 ==========

def get_realtime_quotes(symbols: List[str]) -> Dict:
    """
    获取实时行情数据

    Args:
        symbols: 股票代码列表，如 ["600519", "000858"]

    Returns:
        实时行情数据字典
    """
    fetcher = MarketDataFetcher()
    return fetcher.get_realtime_quotes(symbols)


def get_market_data(symbols: List[str], interval: str = "daily",
                    start_date: str = None, end_date: str = None,
                    adjust: str = "qfq") -> Dict:
    """
    获取K线行情数据

    Args:
        symbols: 股票代码列表
        interval: 数据周期 1d/1w/1m
        start_date: 开始日期 YYYY-MM-DD
        end_date: 结束日期 YYYY-MM-DD
        adjust: 复权类型 qfq/hfq/none

    Returns:
        K线数据字典
    """
    fetcher = MarketDataFetcher()
    return fetcher.get_market_data(symbols, interval, start_date, end_date, adjust)


def get_kline_data(symbol: str, period: str = "daily",
                   start_date: str = None, end_date: str = None,
                   adjust: str = "qfq") -> Dict:
    """
    获取单只股票K线数据

    Args:
        symbol: 股票代码
        period: 周期 daily/weekly/monthly/1min/5min/15min/30min/60min
        start_date: 开始日期 YYYYMMDD
        end_date: 结束日期 YYYYMMDD
        adjust: 复权类型

    Returns:
        K线数据字典
    """
    fetcher = MarketDataFetcher()
    return fetcher.get_kline_data(symbol, period, start_date, end_date, adjust)


def get_fundamentals(symbol: str) -> Dict:
    """
    获取基本面数据

    Args:
        symbol: 股票代码

    Returns:
        基本面数据字典
    """
    fetcher = FundamentalsFetcher()
    return fetcher.get_financial_summary(symbol)


def get_valuation(symbol: str) -> Dict:
    """
    获取估值指标

    Args:
        symbol: 股票代码

    Returns:
        估值指标字典
    """
    fetcher = FundamentalsFetcher()
    return fetcher.get_valuation_metrics(symbol)


# ========== CLI测试 ==========

if __name__ == "__main__":
    print("=" * 60)
    print("行情数据获取模块 - 测试")
    print("=" * 60)

    # 测试1: 实时行情
    print("\n【测试1】获取实时行情")
    test_symbols = ["600519", "000858", "601318"]
    result = get_realtime_quotes(test_symbols)
    print(f"状态码: {result['code']}")
    print(f"消息: {result['message']}")
    for symbol, data in result['data'].items():
        print(f"\n{symbol} ({data.get('name', 'N/A')}):")
        print(f"  当前价: {data.get('price', 'N/A')}")
        print(f"  涨跌幅: {data.get('change_pct', 'N/A')}%")
        print(f"  换手率: {data.get('turnover', 'N/A')}")
        print(f"  市盈率TTM: {data.get('pe_ttm', 'N/A')}")

    # 测试2: K线数据
    print("\n" + "=" * 60)
    print("\n【测试2】获取K线数据 (日线)")
    result = get_kline_data("600519", period="daily", adjust="qfq")
    print(f"状态码: {result['code']}")
    print(f"股票: {result['data'].get('symbol', 'N/A')}")
    print(f"数据条数: {result['data'].get('count', 0)}")
    if result['data'].get('dates'):
        print(f"最新日期: {result['data']['dates'][-1]}")
        print(f"最新收盘: {result['data']['close'][-1]}")

    # 测试3: 估值指标
    print("\n" + "=" * 60)
    print("\n【测试3】获取估值指标")
    result = get_valuation("600519")
    print(f"状态码: {result['code']}")
    print(f"数据: {json.dumps(result['data'], ensure_ascii=False, indent=2)}")

    print("\n" + "=" * 60)
    print("测试完成!")
    print("=" * 60)
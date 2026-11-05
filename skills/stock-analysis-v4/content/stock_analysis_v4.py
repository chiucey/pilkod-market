#!/usr/bin/env python3
"""
股票深度分析 SKILL v4.0.5 - 完整4层架构版
数据优先级：腾讯API > 网页搜索 > MCP工具 > 本地缓存

【核心原则】
1. 腾讯API返回数据无误时以最新时效性为准
2. 历史区间抓取仅在提示词出现时执行
3. 新闻默认搜索近一月范围
4. 新闻分类：行业新闻 + 国际新闻
"""

import json
import re
import os
import sqlite3
import urllib.request
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional


# ============================================================================
# 第一层：腾讯财经API - 绝对优先数据源
# ============================================================================

class TencentFinanceAPI:
    """腾讯财经API - 第一优先级数据源"""

    BASE_URL = "https://qt.gtimg.cn/q="
    HIST_URL = "https://web.ifzq.gtimg.cn/appstock/app/fqkline/get"

    def __init__(self):
        self.cache = StockCacheDB()

    def _convert_symbol(self, symbol: str) -> str:
        """转换股票代码为腾讯格式"""
        symbol = symbol.strip().upper()
        if symbol.startswith(('SZ', 'SH', 'BJ')):
            return symbol.lower()
        if symbol.startswith('6'):
            return f'sh{symbol}'
        elif symbol.startswith(('0', '3')):
            return f'sz{symbol}'
        elif symbol.startswith(('4', '8')):
            return f'bj{symbol}'
        return f'sz{symbol}'

    def get_realtime_quote(self, symbols: List[str]) -> Dict[str, Any]:
        """获取实时行情（腾讯API - 最新时效）"""
        try:
            qt_symbols = ','.join([self._convert_symbol(s) for s in symbols])
            url = f"{self.BASE_URL}{qt_symbols}"

            req = urllib.request.Request(url)
            req.add_header('User-Agent', 'Mozilla/5.0')
            req.add_header('Referer', 'https://gu.qq.com/')

            with urllib.request.urlopen(req, timeout=10) as response:
                text = response.read().decode('gbk')

            result = {}
            for line in text.strip().split('\n'):
                if '=' not in line:
                    continue
                match = re.search(r'v_(\w+)=["\'](.+?)["\'];?\s*$', line)
                if match:
                    qt_code = match.group(1)
                    fields = match.group(2).split('~')
                    if len(fields) >= 68:
                        data = self._parse_fields(fields)
                        result[qt_code] = data
                        self.cache.update_realtime(qt_code, data)

            if result:
                return {
                    "status": "success",
                    "source": "Tencent_API",
                    "data": result,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "freshness": "realtime"
                }
            return {"status": "error", "source": "Tencent_API", "message": "无数据"}
        except Exception as e:
            return {"status": "error", "source": "Tencent_API", "message": str(e)}

    def _parse_fields(self, fields: List[str]) -> Dict:
        """解析腾讯财经实时行情字段"""
        return {
            "name": fields[1] if len(fields) > 1 else "",
            "code": fields[2] if len(fields) > 2 else "",
            "current_price": float(fields[3]) if fields[3] else 0,
            "yesterday_close": float(fields[4]) if len(fields) > 4 and fields[4] else 0,
            "today_open": float(fields[5]) if len(fields) > 5 and fields[5] else 0,
            "volume": int(fields[37]) if len(fields) > 37 and fields[37] else 0,
            "change_amount": float(fields[31]) if len(fields) > 31 and fields[31] else 0,
            "change_percent": float(fields[32]) if len(fields) > 32 and fields[32] else 0,
            "high_52w": float(fields[67]) if len(fields) > 67 and fields[67] else 0,
            "low_52w": float(fields[68]) if len(fields) > 68 and fields[68] else 0,
            "turnover_rate": float(fields[38]) if len(fields) > 38 and fields[38] else 0,
            "pe": float(fields[39]) if len(fields) > 39 and fields[39] else 0,
            "pb": float(fields[46]) if len(fields) > 46 and fields[46] else 0,
            "market_cap": float(fields[45]) if len(fields) > 45 and fields[45] else 0,
            "float_market_cap": float(fields[44]) if len(fields) > 44 and fields[44] else 0,
        }

    def get_historical_kline(self, symbol: str, days: int = 750) -> Dict[str, Any]:
        """
        获取历史K线
        【注意】此为历史数据模块，仅在用户明确要求历史分析时调用
        """
        try:
            qt_symbol = self._convert_symbol(symbol)
            url = f"{self.HIST_URL}?_var=kline_dayhfq&param={qt_symbol},day,,,{days},qfq"

            req = urllib.request.Request(url)
            req.add_header('User-Agent', 'Mozilla/5.0')
            req.add_header('Referer', 'https://gu.qq.com/')

            with urllib.request.urlopen(req, timeout=15) as response:
                text = response.read().decode('gbk')

            json_match = re.search(r'=\s*(\{.+\})\s*;?\s*$', text, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group(1))
                qt_data = data.get('data', {})
                day_data = qt_data.get('day', [])

                klines = []
                for item in day_data:
                    if len(item) >= 5:
                        klines.append({
                            "date": item[0],
                            "open": float(item[1]) if item[1] else 0,
                            "close": float(item[2]) if item[2] else 0,
                            "high": float(item[3]) if item[3] else 0,
                            "low": float(item[4]) if item[4] else 0,
                            "volume": int(float(item[5])) if len(item) > 5 and item[5] else 0
                        })

                self.cache.update_kline(qt_symbol, klines)
                return {
                    "status": "success",
                    "source": "Tencent_API",
                    "symbol": qt_symbol,
                    "data": klines,
                    "data_type": "historical",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            return {"status": "error", "source": "Tencent_API", "message": "K线解析失败"}
        except Exception as e:
            return {"status": "error", "source": "Tencent_API", "message": str(e)}


# ============================================================================
# 第二层：网页搜索 - 时效性优先
# ============================================================================

class WebSearchProvider:
    """
    网页搜索 - 第二优先级数据源
    【核心原则】
    1. 默认搜索近一月新闻
    2. 分类：行业新闻 + 国际新闻
    3. 确保时效性为最新
    """

    def __init__(self):
        self.freshness_days = 30  # 默认近一月

    def get_search_keywords(self, symbol: str, data_type: str = "news",
                           include_international: bool = True) -> Dict[str, Any]:
        """
        返回搜索关键词（带时效性）

        Args:
            symbol: 股票代码
            data_type: news | financial | announcement | industry | international
            include_international: 是否包含国际新闻
        """
        now = datetime.now()

        # 时效性标签
        time_tag = f"site:finance.{'sina|163|ifeng' if data_type == 'news' else 'eastmoney'} {now.strftime('%Y-%m')}"

        keywords_map = {
            "news": {
                "industry": [
                    f"{symbol} 最新消息 {now.strftime('%Y年%m月')}",
                    f"{symbol} 今日行情",
                    f"{symbol} 近期动态",
                    f"{symbol} 公司公告"
                ],
                "international": [
                    f"{symbol} international news",
                    f"{symbol} global market",
                    f"global aluminum price {symbol}"
                ] if include_international else []
            },
            "financial": {
                "industry": [
                    f"{symbol} 2025年年报",
                    f"{symbol} 最新财务数据 {now.strftime('%Y年')}",
                    f"{symbol} 业绩预告"
                ],
                "international": [
                    f"{symbol} financial report analysis",
                    f"{symbol} quarterly earnings"
                ] if include_international else []
            },
            "announcement": {
                "industry": [
                    f"{symbol} 公告",
                    f"{symbol} 重大事项",
                    f"{symbol} 临时公告"
                ],
                "international": []
            },
            "industry": {
                "industry": [
                    f"铝行业 最新动态",
                    f"电解铝 市场行情",
                    f"有色金属 行业新闻"
                ],
                "international": [
                    f"aluminum industry global outlook",
                    f"LME aluminum price trend",
                    f"global aluminum market analysis"
                ] if include_international else []
            },
            "international": {
                "industry": [],
                "international": [
                    f"美联储 利率决策",
                    f"全球宏观经济",
                    f"国际大宗商品"
                ]
            }
        }

        data = keywords_map.get(data_type, keywords_map["news"])

        return {
            "status": "search_required",
            "source": "Web_Search",
            "data_type": data_type,
            "freshness": {
                "default_range": f"近{self.freshness_days}天",
                "timestamp": now.strftime("%Y-%m-%d %H:%M:%S")
            },
            "news_categories": {
                "industry_news": data["industry"],
                "international_news": data["international"]
            },
            "search_keywords": data["industry"] + data["international"],
            "suggestion": f"请使用batch_web_search工具搜索，优先获取最近{self.freshness_days}天内的新闻"
        }

    def format_news_query(self, symbol: str, category: str = "all",
                         days: int = 30) -> Dict[str, Any]:
        """
        格式化新闻查询

        Args:
            symbol: 股票代码
            category: all | industry | international
            days: 新闻时间范围（默认30天）
        """
        now = datetime.now()
        start_date = (now - timedelta(days=days)).strftime("%Y-%m-%d")

        queries = {
            "all": [
                {"keyword": f"{symbol} 最新", "time_range": f"{start_date}|{now.strftime('%Y-%m-%d')}"},
                {"keyword": f"{symbol} industry news", "time_range": "1m"}
            ],
            "industry": [
                {"keyword": f"{symbol} 行业动态", "time_range": f"{start_date}|{now.strftime('%Y-%m-%d')}"},
                {"keyword": f"铝行业 新闻", "time_range": "1m"}
            ],
            "international": [
                {"keyword": f"{symbol} international", "time_range": "1m"},
                {"keyword": "aluminum market global", "time_range": "1m"}
            ]
        }

        return {
            "status": "query_ready",
            "source": "Web_Search",
            "category": category,
            "time_range": f"{start_date} to {now.strftime('%Y-%m-%d')}",
            "queries": queries.get(category, queries["all"])
        }


# ============================================================================
# 第三层：MCP工具 - 补充数据源
# ============================================================================

class MCPToolsAdapter:
    """MCP工具 - 第三优先级数据源"""

    def __init__(self, mcp_tools: Dict = None):
        self.mcp_tools = mcp_tools or {}

    def _convert_symbol(self, symbol: str) -> str:
        """转换股票代码"""
        symbol = symbol.strip().upper()
        if symbol.startswith('6'):
            return f'{symbol}.SS'
        elif symbol.startswith(('0', '3')):
            return f'{symbol}.SZ'
        elif symbol.startswith(('4', '8')):
            return f'{symbol}.BJ'
        return symbol

    def get_financial_data(self, symbol: str) -> Dict[str, Any]:
        """获取财务数据"""
        if 'stocks_financial_data' in self.mcp_tools:
            try:
                result = self.mcp_tools['stocks_financial_data']({
                    "queries": [{"symbol": self._convert_symbol(symbol)}]
                })
                if result and result.get('data'):
                    return {
                        "status": "success",
                        "source": "MCP_API",
                        "data": result['data'],
                        "note": "作为补充数据源"
                    }
            except:
                pass
        return {"status": "fallback", "source": "MCP", "message": "MCP财务数据不可用"}

    def get_news(self, symbol: str, count: int = 10) -> Dict[str, Any]:
        """获取新闻"""
        if 'stocks_news' in self.mcp_tools:
            try:
                result = self.mcp_tools['stocks_news']({
                    "queries": [{"symbol": self._convert_symbol(symbol), "snippet_count": count}]
                })
                if result and result.get('data'):
                    return {
                        "status": "success",
                        "source": "MCP_API",
                        "data": result['data']
                    }
            except:
                pass
        return {"status": "fallback", "source": "MCP", "message": "MCP新闻数据不可用"}

    def get_stock_info(self, symbol: str) -> Dict[str, Any]:
        """获取股票信息"""
        if 'stocks_info' in self.mcp_tools:
            try:
                result = self.mcp_tools['stocks_info']({
                    "queries": [{"symbol": self._convert_symbol(symbol)}]
                })
                if result and result.get('data'):
                    return {
                        "status": "success",
                        "source": "MCP_API",
                        "data": result['data']
                    }
            except:
                pass
        return {"status": "fallback", "source": "MCP", "message": "MCP股票信息不可用"}


# ============================================================================
# 第四层：本地缓存 - 备用数据源
# ============================================================================

class StockCacheDB:
    """本地缓存数据库 - 第四优先级备用数据源"""

    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = os.path.join(os.path.dirname(__file__), "stock_cache.db")
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS realtime_cache (
                symbol TEXT PRIMARY KEY,
                name TEXT,
                current_price REAL,
                change_percent REAL,
                change_amount REAL,
                volume INTEGER,
                turnover_rate REAL,
                pe REAL,
                pb REAL,
                market_cap REAL,
                float_market_cap REAL,
                high_52w REAL,
                low_52w REAL,
                yesterday_close REAL,
                today_open REAL,
                update_time TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS kline_cache (
                symbol TEXT,
                date TEXT,
                open REAL,
                close REAL,
                high REAL,
                low REAL,
                volume INTEGER,
                PRIMARY KEY (symbol, date)
            )
        """)

        conn.commit()
        conn.close()

    def update_realtime(self, symbol: str, data: Dict):
        """更新实时行情缓存"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO realtime_cache
            (symbol, name, current_price, change_percent, change_amount,
             volume, turnover_rate, pe, pb, market_cap, float_market_cap,
             high_52w, low_52w, yesterday_close, today_open, update_time)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            symbol, data.get('name'), data.get('current_price'),
            data.get('change_percent'), data.get('change_amount'),
            data.get('volume'), data.get('turnover_rate'),
            data.get('pe'), data.get('pb'),
            data.get('market_cap'), data.get('float_market_cap'),
            data.get('high_52w'), data.get('low_52w'),
            data.get('yesterday_close'), data.get('today_open'),
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))
        conn.commit()
        conn.close()

    def get_realtime(self, symbol: str) -> Optional[Dict]:
        """获取实时行情缓存"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM realtime_cache WHERE symbol = ?", (symbol,))
        row = cursor.fetchone()
        conn.close()

        if row:
            return {
                "symbol": row[0], "name": row[1], "current_price": row[2],
                "change_percent": row[3], "change_amount": row[4],
                "volume": row[5], "turnover_rate": row[6],
                "pe": row[7], "pb": row[8],
                "market_cap": row[9], "float_market_cap": row[10],
                "high_52w": row[11], "low_52w": row[12],
                "yesterday_close": row[13], "today_open": row[14],
                "update_time": row[15],
                "source": "Local_Cache",
                "freshness": "historical"
            }
        return None

    def update_kline(self, symbol: str, klines: List[Dict]):
        """更新K线缓存"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        for k in klines:
            cursor.execute("""
                INSERT OR REPLACE INTO kline_cache
                (symbol, date, open, close, high, low, volume)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (symbol, k.get('date'), k.get('open'), k.get('close'),
                  k.get('high'), k.get('low'), k.get('volume')))
        conn.commit()
        conn.close()

    def get_kline(self, symbol: str, days: int = 750) -> List[Dict]:
        """获取K线缓存"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT date, open, close, high, low, volume
            FROM kline_cache
            WHERE symbol = ?
            ORDER BY date DESC
            LIMIT ?
        """, (symbol, days))
        rows = cursor.fetchall()
        conn.close()

        return [
            {"date": r[0], "open": r[1], "close": r[2],
             "high": r[3], "low": r[4], "volume": r[5]}
            for r in reversed(rows)
        ]


# ============================================================================
# 数据获取策略引擎
# ============================================================================

class StockDataEngine:
    """
    股票数据获取引擎 - 4层架构

    【核心原则】
    1. 腾讯API返回数据无误时以最新时效性为准
    2. 历史区间抓取仅在用户明确要求时执行
    3. 新闻默认搜索近一月范围
    """

    def __init__(self, mcp_tools: Dict = None):
        self.tencent_api = TencentFinanceAPI()
        self.web_search = WebSearchProvider()
        self.mcp_adapter = MCPToolsAdapter(mcp_tools)
        self.mcp_tools = mcp_tools
        self.cache = self.tencent_api.cache

    def get_realtime_quote(self, symbols: List[str]) -> Dict[str, Any]:
        """
        获取实时行情
        【第一优先】腾讯API → 【第四优先】本地缓存
        """
        # 第一优先：腾讯财经API
        result = self.tencent_api.get_realtime_quote(symbols)
        if result.get('status') == 'success':
            return result

        # 第四优先：本地缓存
        cached_data = {}
        for symbol in symbols:
            qt_symbol = self.tencent_api._convert_symbol(symbol)
            cached = self.cache.get_realtime(qt_symbol)
            if cached:
                cached_data[qt_symbol] = cached

        if cached_data:
            return {
                "status": "cache_fallback",
                "source": "Local_Cache",
                "data": cached_data,
                "warning": "数据来自缓存，可能非最新"
            }

        return {
            "status": "search_required",
            "source": "Web_Search",
            "symbols": symbols
        }

    def get_historical_kline(self, symbol: str, days: int = 750,
                            explicit_request: bool = False) -> Dict[str, Any]:
        """
        获取K线数据
        【注意】仅在用户明确要求历史分析时调用

        Args:
            symbol: 股票代码
            days: 历史天数
            explicit_request: 是否为明确的历史分析请求
        """
        if not explicit_request:
            return {
                "status": "skipped",
                "source": "None",
                "message": "历史K线数据仅在用户明确要求时获取"
            }

        # 腾讯API
        result = self.tencent_api.get_historical_kline(symbol, days)
        if result.get('status') == 'success':
            return result

        # 本地缓存
        cached = self.cache.get_kline(symbol, days)
        if cached:
            return {
                "status": "cache_fallback",
                "source": "Local_Cache",
                "symbol": symbol,
                "data": cached
            }

        return {"status": "search_required", "source": "Web_Search"}

    def get_news(self, symbol: str, count: int = 10,
                 include_international: bool = True) -> Dict[str, Any]:
        """
        获取新闻（带分类和时效性）

        【第二优先】网页搜索 → 【第三优先】MCP工具
        新闻分类：行业新闻 + 国际新闻
        默认时间范围：近30天
        """
        # 第一优先：网页搜索（带时效性）
        web_result = self.web_search.get_search_keywords(
            symbol, "news", include_international
        )

        # 第二优先：MCP工具
        mcp_result = self.mcp_adapter.get_news(symbol, count)
        if mcp_result.get('status') == 'success':
            return {
                "status": "success",
                "source": "MCP_API",
                "data": mcp_result.get('data'),
                "news_categories": web_result.get("news_categories"),
                "time_range": f"近30天"
            }

        return web_result

    def get_financial_data(self, symbol: str) -> Dict[str, Any]:
        """获取财务数据"""
        # 第一优先：网页搜索
        web_result = self.web_search.get_search_keywords(symbol, "financial")

        # 第二优先：MCP工具
        mcp_result = self.mcp_adapter.get_financial_data(symbol)
        if mcp_result.get('status') == 'success':
            return mcp_result

        return web_result


# ============================================================================
# 主分析函数
# ============================================================================

def analyze_stock(stock_code: str, mcp_tools: Dict = None,
                  explicit_historical: bool = False) -> Dict[str, Any]:
    """
    股票深度分析 - 主入口

    Args:
        stock_code: 股票代码
        mcp_tools: MCP工具字典
        explicit_historical: 是否明确请求历史K线分析
    """
    engine = StockDataEngine(mcp_tools)

    # 实时数据（第一优先：腾讯API）
    realtime = engine.get_realtime_quote([stock_code])

    # 历史数据（仅在明确要求时获取）
    kline = engine.get_historical_kline(stock_code, explicit_request=explicit_historical)

    # 新闻数据（第二优先：网页搜索，含分类）
    news = engine.get_news(stock_code, include_international=True)

    # 财务数据（网页搜索 + MCP）
    financial = engine.get_financial_data(stock_code)

    return {
        "_meta": {
            "stock_code": stock_code,
            "version": "4.0.5",
            "data_priority": {
                "1st": "Tencent_API (实时行情)",
                "2nd": "Web_Search (新闻/公告)",
                "3rd": "MCP_API (财务补充)",
                "4th": "Local_Cache (备用)"
            },
            "news_categories": ["行业新闻", "国际新闻"],
            "news_time_range": "近30天",
            "analysis_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        },
        "realtime_data": realtime,
        "historical_data": kline,
        "news_data": news,
        "financial_data": financial
    }


def analyze_stocks(stock_codes: List[str], mcp_tools: Dict = None) -> Dict[str, Any]:
    """多股票对比分析 - 主入口"""
    engine = StockDataEngine(mcp_tools)

    symbols = [s.strip().upper() for s in stock_codes]
    quote_result = engine.get_realtime_quote(symbols)

    kline_results = {}
    for code in stock_codes:
        kline_results[code] = engine.get_historical_kline(code, explicit_request=False)

    comparison = _generate_comparison(quote_result.get('data', {}))

    return {
        "_meta": {
            "version": "4.0.5",
            "stock_count": len(stock_codes),
            "data_priority": "Tencent_API > Web_Search > MCP_API > Local_Cache",
            "analysis_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        },
        "stocks": stock_codes,
        "realtime_data": quote_result,
        "historical_data": kline_results,
        "comparison": comparison
    }


def _generate_comparison(quotes: Dict) -> Dict[str, Any]:
    """生成对比数据"""
    sorted_by_change = sorted(quotes.items(), key=lambda x: x[1].get('change_percent', 0), reverse=True)

    return {
        "change_ranking": [
            {"code": qt_code, "name": data.get('name', ''), "price": data.get('current_price', 0),
             "change_percent": data.get('change_percent', 0)}
            for qt_code, data in sorted_by_change
        ],
        "summary": f"今日涨幅最大: {sorted_by_change[0][1].get('name', '')} {sorted_by_change[0][1].get('change_percent', 0):+.2f}%"
        if sorted_by_change else ""
    }


def format_report(result: Dict[str, Any]) -> str:
    """格式化分析报告"""
    output = []
    output.append("=" * 60)
    output.append("📊 股票深度分析报告 v4.0.5")
    output.append("=" * 60)

    meta = result.get('_meta', {})
    output.append(f"\n⏰ 分析时间: {meta.get('analysis_time', 'N/A')}")
    output.append(f"📌 数据优先级: {meta.get('data_priority', {}).get('1st', 'N/A')}")
    output.append(f"📰 新闻范围: {meta.get('news_time_range', '近30天')}")

    # 实时数据
    realtime = result.get('realtime_data', {})
    if realtime.get('data'):
        source = realtime.get('source', 'unknown')
        freshness = realtime.get('freshness', 'unknown')
        output.append(f"\n📊 实时数据 ({source}) - {freshness}:")
        for qt_code, data in realtime.get('data', {}).items():
            change = data.get('change_percent', 0)
            icon = "🔴" if change > 0 else ("🟢" if change < 0 else "⚪")
            output.append(f"\n{icon} {data.get('name', qt_code)} ({data.get('code', qt_code)})")
            output.append(f"   💰 当前价格: {data.get('current_price', 0)} 元")
            output.append(f"   📊 涨跌幅: {data.get('change_percent', 0):+.2f}%")
            output.append(f"   📈 52周最高: {data.get('high_52w', 0)} | 📉 52周最低: {data.get('low_52w', 0)}")
            output.append(f"   🔄 换手率: {data.get('turnover_rate', 0)}%")
            output.append(f"   💵 市盈率: {data.get('pe', 0)} | 市净率: {data.get('pb', 0)}")
            output.append(f"   🏦 总市值: {data.get('market_cap', 0):.2f}亿 | 流通: {data.get('float_market_cap', 0):.2f}亿")

    # 新闻数据
    news = result.get('news_data', {})
    if news.get('status') == 'success':
        output.append(f"\n📰 新闻数据 ({news.get('source', 'unknown')}):")
        output.append(f"   分类: {meta.get('news_categories', [])}")
    elif news.get('search_keywords'):
        output.append(f"\n📰 新闻搜索提示:")
        output.append(f"   请搜索以下关键词获取最新新闻:")
        for kw in news.get('search_keywords', [])[:3]:
            output.append(f"   - {kw}")

    output.append("\n" + "=" * 60)
    output.append("⚠️  本报告仅供参考，不构成投资建议")
    output.append("=" * 60)

    return "\n".join(output)


def format_multi_report(result: Dict[str, Any]) -> str:
    """格式化多股票对比报告"""
    output = []
    output.append("=" * 60)
    output.append("📊 多股票对比分析报告 v4.0.5")
    output.append("=" * 60)

    meta = result.get('_meta', {})
    output.append(f"\n⏰ 分析时间: {meta.get('analysis_time', 'N/A')}")
    output.append(f"📈 股票数量: {meta.get('stock_count', 0)}")

    realtime = result.get('realtime_data', {})
    if realtime.get('data'):
        output.append(f"\n📊 实时数据 ({realtime.get('source', 'unknown')}):")
        for qt_code, data in realtime.get('data', {}).items():
            change = data.get('change_percent', 0)
            icon = "🔴" if change > 0 else ("🟢" if change < 0 else "⚪")
            output.append(f"\n{icon} {data.get('name', qt_code)} ({data.get('code', qt_code)})")
            output.append(f"   💰 价格: {data.get('current_price', 0)} 元 | 涨跌: {change:+.2f}%")
            output.append(f"   🏦 市值: {data.get('market_cap', 0):.2f}亿 | 52周: {data.get('low_52w', 0):.2f}~{data.get('high_52w', 0):.2f}")

    comparison = result.get('comparison', {})
    if comparison.get('change_ranking'):
        output.append("\n📈 涨跌幅排名:")
        for i, item in enumerate(comparison['change_ranking'], 1):
            medal = ["🥇", "🥈", "🥉"][i-1] if i <= 3 else f" {i}."
            output.append(f"   {medal} {item['name']}: {item['change_percent']:+.2f}%")

    output.append("\n" + "=" * 60)
    output.append("⚠️  本报告仅供参考，不构成投资建议")
    output.append("=" * 60)

    return "\n".join(output)


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("用法: python stock_analysis_v4.py <股票代码1> [股票代码2] ...")
        sys.exit(1)

    codes = sys.argv[1:]

    if len(codes) == 1:
        result = analyze_stock(codes[0])
        print(format_report(result))
    else:
        result = analyze_stocks(codes)
        print(format_multi_report(result))

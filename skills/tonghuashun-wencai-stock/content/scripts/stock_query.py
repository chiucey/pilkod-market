#!/usr/bin/env python3
"""
同花顺+新浪财经数据查询脚本
数据源：
  1. 新浪财经实时行情（hq.sinajs.cn）— 免费无限
  2. 新浪涨幅榜（vip.stock.finance.sina.com.cn）— 免费无限，实时
  3. 东方财富板块（push2.eastmoney.com）— 免费无限
"""

import urllib.request
import urllib.parse
import json
import re
import sys
from datetime import datetime
from typing import Optional, List, Dict, Any


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://finance.sina.com.cn",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "zh-CN,zh;q=0.9",
}


# ════════════════════════════════════════════════════════
#  新浪涨幅榜（全市场A股，按涨幅排序）
# ════════════════════════════════════════════════════════
def _sina_req(url: str) -> str:
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=12) as resp:
        return resp.read().decode("utf-8", errors="replace")


def get_limit_stocks() -> tuple:
    """
    从新浪涨幅榜获取全市场涨停/跌停股
    返回 (up_list, down_list)
    """
    all_stocks = {}  # symbol -> dict（自动去重）
    for page in range(1, 10):
        url = (
            f"https://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/"
            f"Market_Center.getHQNodeData?num=80&sort=changepercent&asc=0"
            f"&node=hs_a&symbol=&_s_r_a=page&p={page}"
        )
        try:
            raw = _sina_req(url)
            items = json.loads(raw)
            if not items:
                break
            for it in items:
                sym = it.get("symbol", "")
                if not sym or sym in all_stocks:
                    continue
                try:
                    pct = float(it.get("changepercent") or 0)
                except Exception:
                    pct = 0
                try:
                    price = float(it.get("trade") or 0)
                except Exception:
                    price = 0
                try:
                    amount = float(it.get("amount") or 0)
                except Exception:
                    amount = 0
                all_stocks[sym] = {
                    "name":  it.get("name", ""),
                    "code":  sym,
                    "price": price,
                    "pct":   pct,
                    "amount": amount,
                }
        except Exception:
            break

    up, down = [], []
    for s in all_stocks.values():
        if s["pct"] >= 9.90:
            up.append(s)
        elif s["pct"] <= -9.90:
            down.append(s)
    return up, down


# ════════════════════════════════════════════════════════
#  实时行情（单只或批量，新浪 hq.sinajs.cn）
# ════════════════════════════════════════════════════════
def get_realtime_quote(codes: List[str]) -> List[Dict]:
    """
    获取单只或多只股票实时行情
    codes 格式: ['sh600036', 'sz300001', 'sh688628']
    """
    if not codes:
        return []
    sym = ",".join(codes)
    url = f"https://hq.sinajs.cn/list={sym}"
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://finance.sina.com.cn",
    })
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            content = resp.read().decode("gbk", errors="replace")
    except Exception as e:
        return [{"error": str(e)}]

    results = []
    for line in content.strip().split("\n"):
        m = re.match(r'var hq_str_(\w+)="([^"]*)"', line)
        if not m:
            continue
        code = m.group(1)
        fields = m.group(2).split(",")
        # 字段：name,open,close,current,high,low,vol,amount,...
        if len(fields) < 10:
            fields += [""] * (10 - len(fields))
        try:
            current = float(fields[3]) if fields[3] else 0
            close   = float(fields[2]) if fields[2] else 0
            chg_pct = ((current - close) / close * 100) if close else 0
        except Exception:
            chg_pct = 0
        results.append({
            "code":     code,
            "name":     fields[0],
            "price":    fields[3],    # 当前价
            "open":     fields[1],    # 今日开盘
            "close":    fields[2],    # 昨收
            "high":     fields[4],    # 最高
            "low":      fields[5],    # 最低
            "vol":      fields[8],    # 成交量(手)
            "amount":   fields[9],    # 成交额(元)
            "chgpct":   round(chg_pct, 2),
        })
    return results


# ════════════════════════════════════════════════════════
#  申万行业涨跌（东方财富 push2.eastmoney.com）
#  节点说明: 1.2.3.4=上证A股/深圳A股/沪B股/深B股
#  行业分类：按证监会分类 node=90
# ════════════════════════════════════════════════════════
EM_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Referer": "https://www.eastmoney.com",
}


def get_sector_top_em(num: int = 10) -> List[Dict]:
    """
    东方财富行业涨幅榜（证监会行业分类）
    返回涨幅前N行业
    """
    url = (
        "https://push2.eastmoney.com/api/qt/clist/get"
        "?cb=jQuery&fid=f3&po=1&pz=50&pn=1&np=1"
        "&fltt=2&invt=2&fid=f3&fs=m:90+t:2"
        "&fields=f12,f14,f3,f4,f8"
    )
    req = urllib.request.Request(url, headers=EM_HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
    except Exception as e:
        return [{"error": f"eastmoney blocked: {e}"}]

    # 提取JSON（jQuery包裹）
    m = re.search(r'jQuery\((.*)\)', raw, re.DOTALL)
    if not m:
        return [{"error": "parse failed", "raw": raw[:100]}]
    try:
        obj = json.loads(m.group(1))
        diff = obj.get("data", {}).get("diff", [])
    except Exception:
        return [{"error": "json parse failed"}]

    results = []
    for it in diff:
        try:
            pct = float(it.get("f3", 0))  # f3=涨跌幅
        except Exception:
            pct = 0
        results.append({
            "code":  it.get("f12", ""),
            "name":  it.get("f14", ""),
            "pct":   pct,
        })
    results.sort(key=lambda x: x["pct"], reverse=True)
    return results[:num]


# ════════════════════════════════════════════════════════
#  大资金活跃股（成交额/市值比排序）
# ════════════════════════════════════════════════════════
def get_top_stocks_by_ratio(num: int = 30) -> List[Dict]:
    """
    从新浪获取成交活跃股，按 (成交额/市值) 比率排序
    市值字段 mktcap 单位=万元，amount 单位=元
    ratio = amount / (mktcap*10000) = 换手倍数（资金/市值占比）
    """
    all_stocks = {}
    for page in range(1, 10):
        url = (
            f"https://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/"
            f"Market_Center.getHQNodeData?num=80&sort=amount&asc=0"
            f"&node=hs_a&symbol=&_s_r_a=page&p={page}"
        )
        try:
            raw = _sina_req(url)
            items = json.loads(raw)
            if not items:
                break
            for it in items:
                sym = it.get("symbol", "")
                if not sym or sym in all_stocks:
                    continue
                try:
                    amt    = float(it.get("amount") or 0)
                    mktcap = float(it.get("mktcap") or 0)
                    if mktcap <= 0:
                        continue
                    ratio = amt / (mktcap * 10000)
                except Exception:
                    ratio = 0
                try:
                    pct = float(it.get("changepercent") or 0)
                except Exception:
                    pct = 0
                all_stocks[sym] = {
                    "name":   it.get("name", ""),
                    "code":   sym,
                    "price":  float(it.get("trade") or 0),
                    "pct":    pct,
                    "amount": amt,
                    "ratio":  ratio,
                }
        except Exception:
            break

    items = sorted(all_stocks.values(), key=lambda x: x["ratio"], reverse=True)
    return items[:num]


# ════════════════════════════════════════════════════════
#  涨停股/跌停股/主力资金（统一接口，调用上方函数）
# ════════════════════════════════════════════════════════
def get_limit_up() -> List[Dict]:
    up, _ = get_limit_stocks()
    return up

def get_limit_down() -> List[Dict]:
    _, down = get_limit_stocks()
    return down

def get_main_flow(topn: int = 10) -> List[Dict]:
    """
    获取成交额/市值比TOP股（资金活跃度指标）
    """
    return get_top_stocks_by_ratio(num=topn)


# ════════════════════════════════════════════════════════
#  工具方法
# ════════════════════════════════════════════════════════
def fmt_amount(yuan: float) -> str:
    try:
        v = float(yuan)
        if abs(v) >= 1e8: return f"{v/1e8:.2f}亿"
        if abs(v) >= 1e4: return f"{v/1e4:.0f}万"
        return f"{v:.0f}元"
    except Exception:
        return str(yuan)


def to_json(data, indent: int = 2) -> str:
    return json.dumps(data, ensure_ascii=False, indent=indent)


# ════════════════════════════════════════════════════════
#  兼容旧接口（THSWenCaiQuerier 类）
# ════════════════════════════════════════════════════════
class THSWenCaiQuerier:
    """兼容旧调用方式"""

    def __init__(self):
        self.headers = HEADERS

    def _get(self, url: str, params: Optional[Dict] = None) -> str:
        if params:
            url += "?" + urllib.parse.urlencode(params)
        req = urllib.request.Request(url, headers=self.headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.read().decode("utf-8", errors="replace")

    def query_wencai(self, query: str, count: int = 20) -> List[Dict]:
        """通用搜索（走新浪涨幅榜，适合查涨停、跌停等）"""
        q = query.strip()
        if "涨停" in q:
            return [{"股票代码": s["code"], "股票名称": s["name"],
                     "现价": s["price"], "涨跌幅": f"{s['pct']:.2f}%",
                     "成交额": fmt_amount(s["amount"])}
                    for s in get_limit_up()]
        if "跌停" in q:
            return [{"股票代码": s["code"], "股票名称": s["name"],
                     "现价": s["price"], "涨跌幅": f"{s['pct']:.2f}%",
                     "成交额": fmt_amount(s["amount"])}
                    for s in get_limit_down()]
        if "主力" in q or "资金" in q:
            return [{"股票代码": s["code"], "股票名称": s["name"],
                     "现价": s["price"], "涨跌幅": f"{s['pct']:.2f}%",
                     "成交额": fmt_amount(s["amount"]),
                     "资金市值比": f"{s['ratio']*100:.2f}%"}
                    for s in get_main_flow(topn=count)]
        # 默认走涨幅榜
        return get_limit_up()

    def get_realtime_quote(self, codes: List[str]) -> List[Dict]:
        return get_realtime_quote(codes)

    def get_limit_up(self) -> List[Dict]:
        return get_limit_up()

    def get_limit_down(self) -> List[Dict]:
        return get_limit_down()

    def get_main_flow(self, topn: int = 10) -> List[Dict]:
        return get_main_flow(topn=topn)

    def to_json(self, data, indent: int = 2) -> str:
        return json.dumps(data, ensure_ascii=False, indent=indent)


# ════════════════════════════════════════════════════════
#  主入口
# ════════════════════════════════════════════════════════
def main():
    querier = THSWenCaiQuerier()
    if len(sys.argv) < 2:
        print("用法: python3 stock_query.py <查询内容>")
        print("  涨停 / 跌停 / 主力净流入前10 / <股票代码>")
        result = querier.get_limit_up()
    else:
        query = " ".join(sys.argv[1:])
        print(f"查询: {query}")
        result = querier.query_wencai(query)
    print(querier.to_json(result))


if __name__ == "__main__":
    main()

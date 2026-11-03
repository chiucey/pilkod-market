"""
stock_pool.py
=============
全市场股票池获取 - 东方财富行业分类
数据源：东方财富行业板块数据
覆盖：证监会行业分类 → 申万行业分类 → 概念板块
"""
import urllib.request
import ssl
import json
import time
import sys
import os

ssl._create_default_https_context = ssl._create_unverified_context

# ─── 限速：1 calls/s ──────────────────────────────────────────────────
_last_call = 0.0

def rate_limit(min_interval=1.0):
    global _last_call
    elapsed = time.time() - _last_call
    if elapsed < min_interval:
        time.sleep(min_interval - elapsed)
    _last_call = time.time()


def get_tencent_board_stocks(board_code: str) -> list[dict]:
    """
    获取腾讯财经板块成分股
    board_code: 腾讯板块代码，如 "bz0900"（科技类）"sh001004"（全部A股）
    """
    rate_limit(1.0)
    url = f"https://proxy.finance.qq.com/ifzqgtimg/appstock/app/newfqkline/get?param={board_code},day,,,20,qfq&_var=fd_d"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as r:
            raw = r.read().decode("utf-8", errors="replace")
        if "var fd_d=" in raw:
            raw = raw.split("var fd_d=", 1)[1]
        data = json.loads(raw.strip().rstrip(";"))
        return data
    except Exception:
        return []


def get_eastmoney_sector_stocks(sector_id: str) -> list[str]:
    """
    获取东方财富行业板块成分股
    sector_id: 东方财富行业ID
    """
    rate_limit(0.8)
    url = (
        f"https://push2.eastmoney.com/api/qt/clist/get"
        f"?cb=jQuery&pn=1&pz=5000&po=1&np=1"
        f"&ut=b2884a393a59ad64002292a3e90d46a7"
        f"&fltt=2&invt=2"
        f"&fid=f3"
        f"&fs=m:90+t:{sector_id}"
        f"&fields=f12,f14"
    )
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0",
            "Referer": "https://quote.eastmoney.com/"
        })
        with urllib.request.urlopen(req, timeout=15) as r:
            raw = r.read().decode("utf-8", errors="replace")
        # JSONP: jQuery({...})
        m = raw.strip()
        if m.startswith("jQuery"):
            m = m[m.index("(") + 1:m.rindex(")")]
        data = json.loads(m)
        stocks = []
        for item in data.get("data", {}).get("diff", []):
            stocks.append({"code": str(item.get("f12", "")), "name": item.get("f14", "")})
        return stocks
    except Exception as e:
        print(f"  ⚠️ eastmoney sector {sector_id} failed: {e}")
        return []


def get_all_a_stocks() -> list[dict]:
    """
    获取全部A股（沪市+深市+北交所）
    """
    rate_limit(0.5)
    stocks = []
    markets = [
        ("sh", "m:1+t:2,m:1+t:23"),   # 沪市主板
        ("sh", "m:1+t:9"),              # 沪市科创板
        ("sz", "m:0+t:80,m:0+t:81"),   # 深市主板
        ("sz", "m:0+t:6"),              # 深市中小板
        ("sz", "m:0+t:80,m:0+t:90"),   # 创业板
        ("bj", "m:0+t:81"),             # 北交所
    ]
    for mkt, fs in markets:
        url = (
            f"https://push2.eastmoney.com/api/qt/clist/get"
            f"?pn=1&pz=5000&po=1&np=1"
            f"&fltt=2&invt=2"
            f"&fid=f3"
            f"&fs={fs}"
            f"&fields=f12,f14"
        )
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": "Mozilla/5.0",
                "Referer": "https://www.eastmoney.com/"
            })
            with urllib.request.urlopen(req, timeout=15) as r:
                raw = r.read().decode("utf-8", errors="replace")
            data = json.loads(raw)
            for item in data.get("data", {}).get("diff", []):
                code = str(item.get("f12", ""))
                name = item.get("f14", "")
                if code:
                    prefix = {"sh": "6", "sz": "0", "bj": "8"}.get(mkt, "")
                    stocks.append({
                        "code": f"{prefix}{code}",
                        "name": name,
                        "market": mkt
                    })
        except Exception as e:
            print(f"  ⚠️ eastmoney market {mkt} failed: {e}")

    print(f"  获取到 {len(stocks)} 只A股")
    return stocks


def get_tech_stocks_by_sw() -> list[dict]:
    """
    按申万行业分类获取科技股
    申万一级科技行业：
    电子、计算机、通信、传媒、机械设备(部分)、国防军工(部分)、汽车(部分)、
    医药生物(部分)、电力设备(部分)、有色金属(部分)
    """
    # 东方财富 申万行业指数 板块ID
    SW_INDUSTRIES = {
        # 申万一级行业
        "电子": "2.26",    # SW电子
        "计算机": "2.27",  # SW计算机
        "通信": "2.37",    # SW通信
        "传媒": "2.39",    # SW传媒
        "机械设备": "2.14", # SW机械设备（含部分科技）
        "国防军工": "2.36", # SW国防军工
        "汽车": "2.25",    # SW汽车
        "医药生物": "2.28", # SW医药生物
        "电力设备": "2.15", # SW电力设备
        "有色金属": "2.24", # SW有色金属
        # 申万二级（核心科技）
        "半导体": "2.46",   # SW半导体
        "元件": "2.47",     # SW元件
        "光学光电子": "2.49", # SW光学光电子
        "消费电子": "2.50",  # SW消费电子
        "计算机设备": "2.52", # SW计算机设备
        "软件开发": "2.53",  # SW软件开发
        "IT服务": "2.54",   # SW IT服务
        "通信设备": "2.57", # SW通信设备
        "通用设备": "2.60", # SW通用设备
        "专用设备": "2.61", # SW专用设备
        "电池": "2.64",     # SW电池
        "风电设备": "2.65", # SW风电设备
        "光伏设备": "2.66", # SW光伏设备
        "军工电子": "2.100",# SW军工电子
        "铜": "2.73",       # SW铜
        "铝": "2.74",       # SW铝
        "锌": "2.75",       # SW锌
        "黄金": "2.76",     # SW黄金
        "稀土": "2.79",     # SW稀土
    }

    all_tech = {}
    print("正在从东方财富获取申万行业分类数据...")

    for industry, sw_id in SW_INDUSTRIES.items():
        print(f"  → {industry}({sw_id})...", end=" ", flush=True)
        # 东方财富行业分类接口
        url = (
            f"https://push2.eastmoney.com/api/qt/clist/get"
            f"?pn=1&pz=5000&po=1&np=1"
            f"&fltt=2&invt=2"
            f"&fid=f3"
            f"&fs=b:{sw_id}+f:!50"   # b:=按行业筛选, !50=排除退市
            f"&fields=f12,f14,f100"
        )
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": "Mozilla/5.0",
                "Referer": "https://quote.eastmoney.com/"
            })
            with urllib.request.urlopen(req, timeout=15) as r:
                raw = r.read().decode("utf-8", errors="replace")
            data = json.loads(raw)
            items = data.get("data", {}).get("diff", []) or []
            count = 0
            for item in items:
                code = str(item.get("f12", ""))
                name = item.get("f14", "")
                if code and len(code) >= 6:
                    key = code
                    if key not in all_tech:
                        all_tech[key] = {
                            "code": code,
                            "name": name,
                            "industry": industry,
                        }
                        count += 1
            print(f"获取{count}只（累计{len(all_tech)}只）")
        except Exception as e:
            print(f"失败: {e}")

    result = list(all_tech.values())
    print(f"\n✅ 申万行业筛选完成：共 {len(result)} 只科技股")
    return result


def save_pool(stocks: list[dict], path: str = "data/stock_pool.json"):
    """保存股票池到文件"""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(stocks, f, ensure_ascii=False, indent=2)
    print(f"✅ 股票池已保存: {path} ({len(stocks)} 只)")


def load_pool(path: str = "data/stock_pool.json") -> list[dict]:
    """从文件加载股票池"""
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        return json.load(f)


if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

    print("=" * 60)
    print("获取A股全市场股票池")
    print("=" * 60)

    # 方法1：按申万行业筛选科技股（推荐）
    tech_stocks = get_tech_stocks_by_sw()
    save_pool(tech_stocks)

    # 也可获取全A股（作为参考）
    print("\n获取全A股（作为参考）...")
    all_stocks = get_all_a_stocks()
    print(f"全A数量: {len(all_stocks)} 只")

    print("\n行业分布：")
    from collections import Counter
    c = Counter(s.get("industry", "未知") for s in tech_stocks)
    for industry, count in c.most_common():
        print(f"  {industry}: {count}只")

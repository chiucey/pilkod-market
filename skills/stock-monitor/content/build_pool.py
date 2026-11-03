#!/usr/bin/env python3
"""
build_pool.py  - 东方财富全市场行业分类版
=============================================
直接从东方财富获取全量A股列表（含证监会行业字段），
按科技关键词过滤，构建完整的科技股候选池。

数据源：东方财富 全市场股票列表
行业字段：f100（证监会二级行业分类）
"""
import urllib.request
import ssl
import json
import time
import os

ssl._create_default_https_context = ssl._create_unverified_context

_last = 0.0

def wait(min_gap=0.6):
    global _last
    elapsed = time.time() - _last
    if elapsed < min_gap:
        time.sleep(min_gap - elapsed)
    _last = time.time()


def fetch_page(page: int, page_size: int = 500) -> tuple[list, int]:
    """
    获取单页股票列表
    fs=m:0+t:6 (创业板) + m:1+t:2,m:1+t:23 (沪市) + m:0+t:80,m:0+t:81 (深市) + m:0+t:81 (北交所)
    f:!50 = 排除退市
    """
    wait(0.5)
    url = (
        f"https://push2.eastmoney.com/api/qt/clist/get"
        f"?pn={page}&pz={page_size}&po=1&np=1"
        f"&fltt=2&invt=2&fid=f3"
        f"&fs=m:0+t:6,m:1+t:2,m:1+t:23,m:0+t:80,m:0+t:81,m:0+t:81"
        f"&fields=f12,f14,f100"   # f100 = 证监会二级行业
    )
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://quote.eastmoney.com/"
    })
    with urllib.request.urlopen(req, timeout=20) as r:
        raw = r.read().decode("utf-8", errors="replace")
    data = json.loads(raw)
    total = data.get("data", {}).get("total", 0)
    items = data.get("data", {}).get("diff", []) or []
    return items, total


# ─── 科技行业关键词（证监会行业分类匹配）───────────────────────────────
TECH_KEYWORDS = [
    # 一级：电子/计算机/通信
    "电子", "计算机", "通信设备", "通信服务", "软件", "互联网",
    # 二级：半导体/元件/光电子
    "半导体", "元件", "光学光电子", "消费电子", "其他电子",
    "计算机设备", "IT服务", "软件开发", "互联网服务", "互联网和相关服务",
    # 军工/高端制造
    "航空", "航天", "船舶", "兵器", "国防", "军工",
    "铁路", "航空装备", "航天装备", "地面兵装", "船舶制造",
    # 新能源/电力设备
    "电池", "光伏", "风电", "核电", "水电", "电力", "电气", "电网",
    "输变电", "配电", "储能", "充电桩", "电机", "电气自动化",
    # 有色/新材料
    "铜", "铝", "锌", "铅", "锡", "黄金", "白银", "稀土", "钴", "锂",
    "钨", "锗", "有色金属", "稀土",
    # 汽车/智能驾驶
    "汽车", "新能源汽车", "电车", "汽车零部件", "汽车服务",
    "摩托车", "自行车", "无人驾驶", "智能汽车",
    # 医药（部分）
    "医疗器械", "生物药品", "化学药品", "中药", "原料药", "兽药",
    "医药", "医疗", "健康",
    # 机械设备/自动化
    "机械", "设备", "自动化", "机器人", "数控", "传感器", "仪表",
    "专用设备", "通用设备", "金属制品", "轨道交通",
    # 环保/节能
    "环保", "节能", "污染", "废物", "水务", "燃气",
    # 化工（科技化工）
    "化工", "新材料", "碳纤维", "石墨", "膜材料",
]


def is_tech_industry(industry: str) -> bool:
    if not industry:
        return False
    for kw in TECH_KEYWORDS:
        if kw in industry:
            return True
    return False


def normalize_code(code: str) -> str:
    """东方财富6位代码标准化"""
    code = code.strip()
    if not code:
        return ""
    if code.startswith(("6", "9")):
        return f"sh{code}"
    elif code.startswith(("0", "3", "1")):
        return f"sz{code}"
    elif code.startswith("8"):
        return f"bj{code}"
    return f"sz{code}"


def main():
    print("=" * 60)
    print("Stock Pool Builder - 东方财富全市场版")
    print("=" * 60)

    all_stocks = {}
    page = 1
    page_size = 500
    total = None

    while True:
        print(f"\n获取第 {page} 页 (每页{page_size}只)...", end=" ", flush=True)
        try:
            items, total = fetch_page(page, page_size)
        except Exception as e:
            print(f"失败: {e}")
            break

        if not items:
            print("无数据，停止")
            break

        page_stocks = 0
        page_tech = 0
        for item in items:
            code = str(item.get("f12", ""))
            name = str(item.get("f14", "")).strip()
            industry = str(item.get("f100", "")).strip()

            if not code or len(code) < 6:
                continue

            # 判断是否科技股
            is_tech = is_tech_industry(industry)

            # 判断交易所前缀
            if code.startswith(("6", "9")):
                prefix = "sh"
            elif code.startswith(("0", "3", "1")):
                prefix = "sz"
            elif code.startswith("8"):
                prefix = "bj"
            else:
                prefix = "sz"

            stock = {
                "code": code,
                "name": name,
                "industry": industry,
                "market": prefix,
                "ts_code": prefix + code,
                "is_tech": is_tech,
            }

            if code not in all_stocks:
                all_stocks[code] = stock
                page_stocks += 1
                if is_tech:
                    page_tech += 1

        print(f"本页新增 {page_stocks} 只（科技 {page_tech} 只），累计 {len(all_stocks)} 只" +
              (f"，科技股 {sum(1 for s in all_stocks.values() if s.get('is_tech'))} 只" if total else ""))

        # 判断是否到最后一页
        if total and page * page_size >= total:
            break
        page += 1

        # 安全保护
        if page > 20:
            print("达到最大页数，停止")
            break

    # 提取科技股
    tech_stocks = [s for s in all_stocks.values() if s.get("is_tech")]
    print(f"\n" + "=" * 60)
    print(f"✅ 抓取完成！")
    print(f"   全A股票: {len(all_stocks)} 只")
    print(f"   科技股:   {len(tech_stocks)} 只")
    print("=" * 60)

    # ── 添加升爷持仓（确保覆盖）─────────────────────────────────────
    portfolio = [
        ("510500","中证500ETF","sh",""),("588080","科创50ETF","sh",""),
        ("600410","华胜天成","sh","计算机"),("600497","驰宏锌锗","sh","有色金属"),
        ("601618","中国中冶","sh","土木工程"),("601788","光大证券","sh","资本市场"),
        ("603501","豪威集团","sh","计算机"),("000538","云南白药","sz","医药生物"),
        ("002230","科大讯飞","sz","软件"),("002950","奥美医疗","sz","医药生物"),
        ("300172","中电环保","sz","环保"),("09988","阿里巴巴","hk",""),
        ("02015","理想汽车","hk",""),
    ]
    added = 0
    for code, name, mkt, industry in portfolio:
        key = code.lstrip("0123456789") or code
        if key not in all_stocks:
            all_stocks[key] = {"code": code, "name": name, "industry": industry,
                                "market": mkt, "ts_code": f"{mkt}{code}", "is_tech": True}
            added += 1
    print(f"   + 升爷持仓 {added} 只（不在列表中的）")

    # ── 统计 ──────────────────────────────────────────────────────
    tech_only = [s for s in all_stocks.values() if s.get("is_tech")]
    print(f"\n科技股行业分布（TOP15）：")
    from collections import Counter
    ind_cnt = Counter(s.get("industry", "未知") for s in tech_only)
    for industry, cnt in ind_cnt.most_common(15):
        print(f"  {industry}: {cnt}只")

    # ── 保存两份 ──────────────────────────────────────────────────
    out_dir = "/workspace/stock-scout/data"
    os.makedirs(out_dir, exist_ok=True)

    # 完整股票池
    full_path = f"{out_dir}/stock_pool_full.json"
    with open(full_path, "w", encoding="utf-8") as f:
        json.dump(list(all_stocks.values()), f, ensure_ascii=False, indent=2)

    # 科技股池（推荐）
    tech_path = f"{out_dir}/stock_pool.json"
    with open(tech_path, "w", encoding="utf-8") as f:
        json.dump(tech_only, f, ensure_ascii=False, indent=2)

    print(f"\n📁 保存完成:")
    print(f"   完整股票池: {full_path} ({len(all_stocks)}只)")
    print(f"   科技股池:   {tech_path} ({len(tech_only)}只)")

    return tech_only


if __name__ == "__main__":
    main()

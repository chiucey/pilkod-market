#!/usr/bin/env python3
"""
FIN Data - 金融市场数据查询（免API Key版）
主要用新浪实时接口 + AKShare 宏观数据
"""

import sys, re, ssl, urllib.request, json
from datetime import datetime

# ── 新浪实时行情（快） ──────────────────────────────────
HEADERS = {"User-Agent": "Mozilla/5.0", "Referer": "https://finance.sina.com.cn"}

NAME2CODE = {
    "璞泰来": "sh603659", "宁德时代": "sz300750", "比亚迪": "sz002594",
    "贵州茅台": "sh600519", "中国平安": "sh601318", "招商银行": "sh600036",
    "工商银行": "sh601398", "建设银行": "sh601939", "中国银行": "sh601988",
    "农业银行": "sh601288", "中际旭创": "sz300308", "阳光电源": "sz300274",
    "腾讯控股": "hk00700", "阿里巴巴": "hk09988", "美团": "hk03690",
}

def resolve(txt: str) -> str:
    for name, code in NAME2CODE.items():
        if name in txt: return code
    m = re.search(r'\b(\d{6})\b', txt)
    if m:
        c = m.group(1)
        if c.startswith(("00","30")): return f"sz{c}"
        if c.startswith(("60","68")): return f"sh{c}"
        return f"sh{c}"
    return ""


def sina_quote(codes: list) -> list:
    """新浪批量行情"""
    if not codes: return []
    ctx = ssl.create_default_context()
    ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
    url = f"https://hq.sinajs.cn/list={','.join(codes)}"
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=8, context=ctx) as r:
            raw = r.read().decode("gbk", errors="replace")
    except Exception as e:
        return []
    results = []
    for line in raw.strip().split("\n"):
        m = re.search(r'hq_str_(\w+)="(.+?)"', line)
        if not m: continue
        f = m.group(2).split(",")
        if len(f) < 10: continue
        try:
            cur = float(f[3]); cl = float(f[2])
            pct = (cur-cl)/cl*100 if cl else 0
            vol = float(f[6]); amt = float(f[8])
        except: continue
        is_hk = m.group(1).startswith("hk")
        results.append({
            "代码": m.group(1), "名称": f[0],
            "最新价": f"{cur:.3f}", "昨收": f[2], "今开": f[1],
            "最高": f[4], "最低": f[5],
            "涨跌幅": f"{'+'if pct>=0 else''}{pct:.2f}%",
            "涨跌额": f"{'+'if cur-cl>=0 else''}{cur-cl:.3f}",
            "成交量": f"{vol/1e4:.1f}万股",
            "成交额": f"{amt/1e8:.2f}亿" if amt>=1e8 else f"{amt/1e4:.0f}万",
            "时间": f[30] if len(f)>30 else "-",
            "市场": "港股" if is_hk else "A股",
        })
    return results


# ── AKShare 宏观数据（可用） ─────────────────────────────

def akshare_cpi():
    import akshare as ak
    try:
        df = ak.macro_china_cpi_yearly()
        return {"status": "success", "data": df.tail(12).to_dict("records")}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def akshare_pmi():
    import akshare as ak
    try:
        df = ak.macro_china_pmi_yearly()
        return {"status": "success", "data": df.tail(12).to_dict("records")}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def akshare_hsgt():
    """北向/外资资金"""
    import akshare as ak
    try:
        df = ak.stock_hsgt_fund_flow_summary_em()
        return {"status": "success", "data": df.to_dict("records")}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def akshare_lhb():
    """龙虎榜"""
    import akshare as ak
    try:
        df = ak.stock_hsgt_stock_statistics_em()
        cols = [c for c in df.columns if any(x in c for x in ["代码","名称","收盘","涨跌幅","净买","上榜原因"])]
        sub = df[[c for c in cols if c in df.columns]].head(20)
        return {"status": "success", "data": sub.to_dict("records")}
    except Exception as e:
        return {"status": "error", "message": str(e)}


# ── 格式化输出 ──────────────────────────────────────────

def fmt_quote(rows: list) -> str:
    if not rows: return "❌ 获取行情失败"
    lines = ["📊 A股/港股实时行情\n"]
    for r in rows:
        pct_str = r["涨跌幅"]
        try:
            pct_f = float(pct_str.rstrip("%"))
            arrow = "🟢" if pct_f >= 0 else "🔴"
        except: arrow = "⚪"
        lines.append(f"{arrow} {r['名称']}（{r['市场']}）")
        lines.append(f"   最新价: {r['最新价']} 元  涨跌: {pct_str}  ({r['涨跌额']})")
        lines.append(f"   今开: {r['今开']}  最高: {r['最高']}  最低: {r['最低']}")
        lines.append(f"   成交额: {r['成交额']}  时间: {r['时间']}")
        lines.append("")
    return "\n".join(lines)

def fmt_table(data: list, title: str) -> str:
    if not data: return f"📭 {title}: 暂无数据"
    keys = list(data[0].keys())
    lines = [title, "="*40]
    for r in data[:15]:
        row_str = " | ".join(f"{k}:{r.get(k,'-')}" for k in keys if r.get(k) is not None)
        lines.append(f"  {row_str}")
    return "\n".join(lines)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python fin_data.py <查询内容>")
        sys.exit(1)

    query = " ".join(sys.argv[1:])
    print(f"\n🔍 金融市场查询: {query}\n")

    if any(kw in query for kw in ["cpi","通胀","物价"]):
        res = akshare_cpi()
        print(fmt_table(res.get("data",[]), "📈 CPI 同比数据（近12个月）"))

    elif any(kw in query for kw in ["pmi"]):
        res = akshare_pmi()
        print(fmt_table(res.get("data",[]), "📊 PMI 数据"))

    elif any(kw in query for kw in ["北向","北上","外资","陆股通","港股通"]):
        res = akshare_hsgt()
        if res["status"] == "error":
            print(f"❌ {res['message']}")
        else:
            print(fmt_table(res.get("data",[]), "💰 北向资金流"))

    elif any(kw in query for kw in ["龙虎榜","游资"]):
        res = akshare_lhb()
        if res["status"] == "error":
            print(f"❌ {res['message']}")
        else:
            print(fmt_table(res.get("data",[]), "🏆 龙虎榜 TOP20"))

    else:
        # 股票行情（新浪）
        parts = re.findall(r'[\w\u4e00-\u9fff]+', query)
        codes = [resolve(w) for w in parts]
        codes = [c for c in codes if c and codes.count(c) == 1]
        if not codes:
            print("未识别股票名称或代码")
        else:
            rows = sina_quote(codes)
            print(fmt_quote(rows))

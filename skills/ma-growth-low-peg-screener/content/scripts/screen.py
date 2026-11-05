#!/usr/bin/env python3
"""多周期均线渐进收敛 + 高成长低估值选股器"""
import json, urllib.request, time, statistics, zipfile, os, io
from datetime import datetime, timedelta

# ========== 配置 ==========
TOKEN_FILE = "/root/.openclaw/skills/tushare-data/token.env"
OUTPUT_DIR = "/workspace"
TODAY = datetime.today().strftime("%Y%m%d")

MAX_MARKET_CAP = 200
MIN_REV_GROWTH = 20
MIN_PROFIT_GROWTH = 20
MAX_PEG = 1.0
MIN_DAILY_TURNOVER = 5000
MIN_LISTED_DAYS = 365
MAX_MA_SPREAD = 2.0
CONVERGENCE_WINDOW = 5

# ========== Tushare ==========
def load_token():
    with open(TOKEN_FILE) as f:
        for line in f:
            t = line.strip()
            if t and "=" in t:
                k, v = t.split("=", 1)
                if k.strip() == "TUSHARE_TOKEN":
                    return v.strip()
    return ""

def call_api(api_name, params, fields=""):
    token = load_token()
    body = json.dumps({"api_name": api_name, "token": token, "params": params, "fields": fields}).encode()
    req = urllib.request.Request("http://api.tushare.pro", data=body,
        headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read())
            if result and result.get("code") == 0:
                return result
            # API报错但有data字段
            if result and result.get("data") is not None:
                return result
            return None
    except Exception:
        return None

# ========== 获取股票列表 ==========
def get_all_stocks():
    sh = call_api("hs_const", {"hs_type": "SH"}, "ts_code")
    sz = call_api("hs_const", {"hs_type": "SZ"}, "ts_code")
    sh_data = sh.get("data") if sh else None
    sz_data = sz.get("data") if sz else None
    sh_items = (sh_data.get("items") or []) if sh_data else []
    sz_items = (sz_data.get("items") or []) if sz_data else []
    return [r[0] for r in sh_items] + [r[0] for r in sz_items]

# ========== 日线数据 ==========
def get_daily_data(ts_code, start_date, end_date):
    res = call_api("daily", {"ts_code": ts_code, "start_date": start_date, "end_date": end_date})
    if not res:
        return None
    data = res.get("data", {})
    if not data:
        return None
    fields = data.get("fields", [])
    items = data.get("items", [])
    if not fields or not items:
        return None
    try:
        close_idx = fields.index("close")
        trade_date_idx = fields.index("trade_date")
        vol_idx = fields.index("vol") if "vol" in fields else None
        items_sorted = sorted(items, key=lambda x: str(x[trade_date_idx]))
        result = []
        for item in items_sorted:
            result.append({
                "date": str(item[trade_date_idx]),
                "close": float(item[close_idx]),
                "vol": float(item[vol_idx]) if vol_idx is not None else 0.0
            })
        return result
    except Exception:
        return None

# ========== 均线收敛检测 ==========
def calc_ma_convergence(daily_data):
    if not daily_data or len(daily_data) < 70:
        return None
    closes = [d["close"] for d in daily_data]
    vols = [d["vol"] for d in daily_data]
    latest_close = closes[-1]
    if latest_close <= 0:
        return None

    def ma(n):
        if len(closes) < n:
            return None
        return sum(closes[-n:]) / n

    ma5 = ma(5); ma10 = ma(10); ma20 = ma(20); ma30 = ma(30); ma60 = ma(60)
    if None in [ma5, ma10, ma20, ma30, ma60]:
        return None

    mas = [ma5, ma10, ma20, ma30, ma60]
    spreads = [abs(m - ma60) / latest_close * 100 for m in mas]
    max_spread = max(spreads)
    cv_now = statistics.stdev(mas) / latest_close * 100

    # MA粘合过滤
    if max_spread > MAX_MA_SPREAD:
        return None

    # 渐进收敛
    daily_ranges = []
    for i in range(-6, -1):
        idx = i
        if abs(idx) <= len(closes):
            start_i = max(0, i - 4)
            seg = closes[start_i:i+1] if i >= 0 else closes[:i+1]
            if seg:
                rng = (max(seg) - min(seg)) / closes[i] * 100
                daily_ranges.append(rng)

    if len(daily_ranges) < 3:
        return None

    narrowing_days = sum(1 for i in range(1, len(daily_ranges)) if daily_ranges[i] < daily_ranges[i-1])
    if narrowing_days < 3:
        return None

    # 均线包裹
    if not (min(mas) <= latest_close <= max(mas) * 1.01):
        return None

    # 趋势保护
    if len(closes) >= 80:
        ma60_now = ma60
        ma60_old = sum(closes[-(60+20):-20]) / 60
        if ma60_now < ma60_old * 0.98:
            return None

    # 流动性
    avg_vol = sum(vols[-30:]) / min(30, len(vols)) if len(vols) >= 5 else 0
    if avg_vol < MIN_DAILY_TURNOVER * 10000 / latest_close:
        return None

    # 收敛评分
    conv_score = 0.0
    for offset in [5, 10, 20]:
        if len(closes) >= offset + 30:
            hc = closes[:-offset]
            def hm(n, h):
                return sum(h[-n:]) / n if len(h) >= n else None
            h5 = hm(5, hc); h10 = hm(10, hc); h20 = hm(20, hc)
            h30 = hm(30, hc); h60 = hm(60, hc)
            if None not in [h5, h10, h20, h30, h60]:
                hcv = statistics.stdev([h5,h10,h20,h30,h60]) / hc[-1] * 100
                conv_score += (hcv - cv_now)

    return {
        "passing": True,
        "cv_now": round(cv_now, 4),
        "max_spread": round(max_spread, 4),
        "conv_score": round(conv_score, 4),
        "narrowing_days": narrowing_days,
        "latest_close": round(latest_close, 2),
    }

# ========== 基本面 ==========
def get_financial_data(ts_code):
    try:
        fin = call_api("fina_indicator", {
            "ts_code": ts_code,
            "start_date": datetime.today().replace(month=1, day=1).strftime("%Y%m%d")
        }, "")
        if not fin:
            return None
        fdata = fin.get("data")
        if not fdata:
            return None
        fitems = fdata.get("items") or []
        if not fitems:
            return None
        ffields = fdata.get("fields", [])
        ann_idx = ffields.index("ann_date") if "ann_date" in ffields else 0
        latest = sorted(fitems, key=lambda x: str(x[ann_idx]), reverse=True)[0]
        def f(name):
            if name not in ffields: return None
            v = latest[ffields.index(name)]
            return float(v) if v not in [None, ""] else None

        rev_growth = f("revenue_yoy")
        profit_growth = f("profit_yoy")
        roe = f("roe")
        gross_margin = f("gross_margin")

        basic = call_api("daily_basic", {
            "ts_code": ts_code,
            "trade_date": datetime.today().strftime("%Y%m%d")
        }, "")
        market_cap = pe = None
        if basic:
            bdata = basic.get("data")
            if bdata:
                bitems = bdata.get("items") or []
                bfields = bdata.get("fields") or []
            if bitems and bfields:
                bi = bitems[0]
                mc_i = bfields.index("total_market_cap") if "total_market_cap" in bfields else -1
                pe_i = bfields.index("pe") if "pe" in bfields else -1
                if mc_i >= 0 and bi[mc_i]: market_cap = float(bi[mc_i]) / 10000
                if pe_i >= 0 and bi[pe_i]: pe = float(bi[pe_i])

        peg = None
        if pe and profit_growth and profit_growth > 0:
            peg = round(pe / profit_growth, 2)

        return {
            "rev_growth": round(rev_growth, 2) if rev_growth else None,
            "profit_growth": round(profit_growth, 2) if profit_growth else None,
            "market_cap": round(market_cap, 2) if market_cap else None,
            "pe": round(pe, 2) if pe else None,
            "peg": peg,
            "roe": round(roe, 2) if roe else None,
            "gross_margin": round(gross_margin, 2) if gross_margin else None,
        }
    except Exception:
        return None

def is_clean_stock(ts_code):
    try:
        res = call_api("name_change", {"ts_code": ts_code}, "")
        if not res:
            return True
        rdata = res.get("data") if res else None; items = (rdata.get("items") or []) if rdata else []
        for item in items:
            name = "".join(str(x) for x in item if x)
            if any(k in name for k in ["ST", "*ST", "退"]):
                return False
        return True
    except Exception:
        return True

# ========== 主筛选 ==========
def screen():
    trade_cal = call_api("trade_cal", {"exchange": "SSE", "start_date": "20260401", "end_date": "20260416"})
    tc_data = trade_cal.get("data") if trade_cal else None
    cal_items_all = (tc_data.get("items") or []) if tc_data else []
    cal_items = [r for r in cal_items_all if len(r) > 3 and r[3] == 1]
    last_date = cal_items[-1][1] if cal_items else "20260416"
    start_date = (datetime.strptime(last_date, "%Y%m%d") - timedelta(days=100)).strftime("%Y%m%d")
    print(f"最后交易日: {last_date}，数据起始: {start_date}")

    codes = get_all_stocks()
    print(f"全市场股票数量: {len(codes)}")

    tech_candidates = []
    print("\n第一阶段：均线收敛筛选...")
    for i, code in enumerate(codes):
        daily = get_daily_data(code, start_date, last_date)
        if daily:
            conv = calc_ma_convergence(daily)
            if conv and conv["passing"] and is_clean_stock(code):
                tech_candidates.append({"code": code, "conv": conv})
        if (i+1) % 100 == 0:
            print(f"  进度 {i+1}/{len(codes)}，技术面候选: {len(tech_candidates)}")
        time.sleep(0.04)

    print(f"技术面收敛候选: {len(tech_candidates)} 只")

    print("\n第二阶段：基本面筛选...")
    final_results = []
    for i, cand in enumerate(tech_candidates):
        code = cand["code"]
        fin = get_financial_data(code)
        if not fin:
            continue
        mg = fin["market_cap"]
        rg = fin["rev_growth"]
        pg_fin = fin["profit_growth"]
        peg = fin["peg"]
        if mg is not None and mg > MAX_MARKET_CAP: continue
        if rg is not None and rg < MIN_REV_GROWTH: continue
        if pg_fin is not None and pg_fin < MIN_PROFIT_GROWTH: continue
        if peg is not None and peg >= MAX_PEG: continue
        final_results.append({**cand["conv"], **fin, "code": code, "trade_date": last_date})
        if (i+1) % 20 == 0:
            print(f"  进度 {i+1}/{len(tech_candidates)}，通过: {len(final_results)}")
        time.sleep(0.05)

    print(f"\n最终通过: {len(final_results)} 只")
    return final_results, last_date

# ========== Excel 输出 ==========
def build_xlsx(results, trade_date):
    headers = ["代码","收盘价(元)","MA离散系数(%)","最大MA偏离(%)","收敛评分",
               "5日收敛天数","总市值(亿)","PE(倍)","PEG","营收增速(%)",
               "利润增速(%)","ROE(%)","毛利率(%)","筛选日期"]

    def esc(s):
        if s is None: return ""
        return str(s).replace("&","&amp;").replace("<","&lt;").replace(">","&gt;").replace('"',"&quot;")

    rows_xml = ""
    for i, r in enumerate(results):
        vals = [r.get("code",""), r.get("latest_close"), r.get("cv_now"),
                r.get("max_spread"), r.get("conv_score"), r.get("narrowing_days"),
                r.get("market_cap"), r.get("pe"), r.get("peg"),
                r.get("rev_growth"), r.get("profit_growth"), r.get("roe"),
                r.get("gross_margin"), r.get("trade_date","")]
        row = f'<row r="{i+2}">'
        for j, v in enumerate(vals):
            col = chr(65+j)
            if isinstance(v, float): row += f'<c r="{col}{i+2}"><v>{v}</v></c>'
            elif isinstance(v, int): row += f'<c r="{col}{i+2}"><v>{v}</v></c>'
            else: row += f'<c r="{col}{i+2}" t="inlineStr"><is><t>{esc(v)}</t></is></c>'
        row += "</row>"
        rows_xml += row

    col_widths = [12,12,14,14,12,12,12,10,10,12,12,10,12,12]
    cols_xml = "".join(f'<col min="{j+1}" max="{j+1}" width="{w}" customWidth="1"/>' for j,w in enumerate(col_widths))

    hdr_row = "".join(f'<c r="{chr(65+j)}1" t="inlineStr"><is><t>{esc(h)}</t></is></c>' for j,h in enumerate(headers))

    sheet = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
  <sheetViews><sheetView workbookViewId="0" showGridLines="1"/></sheetViews>
  <sheetFormatPr defaultRowHeight="15"/>
  <cols>{cols_xml}</cols>
  <sheetData><row r="1">{hdr_row}</row>{rows_xml}</sheetData>
</worksheet>"""

    ct = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>
  <Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>
  <Override PartName="/xl/sharedStrings.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sharedStrings+xml"/>
</Types>"""

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", ct)
        zf.writestr("_rels/.rels", """<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>""")
        zf.writestr("xl/workbook.xml", """<?xml version="1.0" encoding="UTF-8"?><workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets><sheet name="均线收敛成长股" sheetId="1" r:id="rId1" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"/></sheets></workbook>""")
        zf.writestr("xl/_rels/workbook.xml.rels", """<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/></Relationships>""")
        zf.writestr("xl/worksheets/sheet1.xml", sheet)
        zf.writestr("xl/sharedStrings.xml", """<?xml version='1.0' encoding='UTF-8'?><sst xmlns='http://schemas.openxmlformats.org/spreadsheetml/2006/main' count='0' uniqueCount='0'/>""")

    filename = f"ma_growth_peg_{trade_date}.xlsx"
    out = os.path.join(OUTPUT_DIR, filename)
    with open(out, "wb") as f:
        f.write(buf.getvalue())
    return out, len(results)

if __name__ == "__main__":
    print("="*60)
    print("多周期均线渐进收敛 + 高成长低估值选股器")
    print(f"运行时间: {datetime.today().strftime('%Y-%m-%d %H:%M')}")
    print(f"MA最大偏离: ≤{MAX_MA_SPREAD}% | 连续收敛天数: ≥3天/5天")
    print(f"总市值: ≤{MAX_MARKET_CAP}亿 | 营收增速: ≥{MIN_REV_GROWTH}%")
    print(f"利润增速: ≥{MIN_PROFIT_GROWTH}% | PEG: <{MAX_PEG}")
    print(f"最低日均成交: {MIN_DAILY_TURNOVER}万元")
    print("="*60)
    results, trade_date = screen()
    if results:
        results.sort(key=lambda x: -x.get("conv_score", 0))
        path, n = build_xlsx(results, trade_date)
        print(f"\n✅ 完成！{n} 只股票通过筛选")
        print(f"📄 结果已保存: {path}")
    else:
        print("\n⚠️ 无股票符合全部条件（可适当放宽条件重试）")

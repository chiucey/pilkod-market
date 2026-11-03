#!/usr/bin/env python3
"""多周期均线渐进收敛 + 高成长低估值选股器 v2
放宽技术面阈值，保留基本面硬性条件，输出完整报告
"""
import json, urllib.request, time, statistics, zipfile, os, io
from datetime import datetime, timedelta

TOKEN_FILE = "/root/.openclaw/skills/tushare-data/token.env"
OUTPUT_DIR = "/workspace"

# ========== 可调参数 ==========
MAX_MARKET_CAP   = 200      # 亿元
MIN_REV_GROWTH   = 15        # %  （放宽）
MIN_PROFIT_GROWTH= 15        # %  （放宽）
MAX_PEG          = 1.2       # （放宽）
MIN_DAILY_TURN   = 3000      # 万元（日均成交，放宽）
MAX_MA_SPREAD    = 8.0      # %  MA最大偏离（大幅放宽）
MIN_NARROWING    = 3        # 5日中至少有3天收窄
MIN_LISTED_DAYS  = 180      # 上市满180天

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

def call(api_name, params, fields=""):
    token = load_token()
    body = json.dumps({"api_name": api_name, "token": token,
                       "params": params, "fields": fields}).encode()
    req = urllib.request.Request("http://api.tushare.pro", data=body,
        headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read())
            if result and result.get("code") == 0:
                return result
            return None
    except Exception:
        return None

def get_all_stocks():
    sh = call("hs_const", {"hs_type": "SH"}, "ts_code")
    sz = call("hs_const", {"hs_type": "SZ"}, "ts_code")
    sh_d = sh.get("data") if sh else None
    sz_d = sz.get("data") if sz else None
    sh_i = (sh_d.get("items") or []) if sh_d else []
    sz_i = (sz_d.get("items") or []) if sz_d else []
    return [r[0] for r in sh_i] + [r[0] for r in sz_i]

def get_daily_data(ts_code, start_date, end_date):
    res = call("daily", {"ts_code": ts_code, "start_date": start_date, "end_date": end_date})
    if not res: return None
    d = res.get("data")
    if not d: return None
    flds = d.get("fields", [])
    items = d.get("items", [])
    if not flds or not items: return None
    try:
        c_i = flds.index("close")
        td_i = flds.index("trade_date")
        v_i = flds.index("vol") if "vol" in flds else None
        sorted_items = sorted(items, key=lambda x: str(x[td_i]))
        result = []
        for item in sorted_items:
            result.append({
                "date": str(item[td_i]),
                "close": float(item[c_i]),
                "vol": float(item[v_i]) if v_i is not None else 0.0
            })
        return result
    except Exception:
        return None

def get_basic(ts_code, trade_date):
    """获取市值、PE"""
    res = call("daily_basic", {"ts_code": ts_code, "trade_date": trade_date}, "")
    if not res: return {}
    d = res.get("data")
    if not d: return {}
    items = d.get("items") or []
    flds = d.get("fields") or []
    if not items or not flds: return {}
    bi = items[0]
    mc_i = flds.index("total_market_cap") if "total_market_cap" in flds else -1
    pe_i = flds.index("pe") if "pe" in flds else -1
    return {
        "market_cap": float(bi[mc_i]) / 10000 if mc_i >= 0 and bi[mc_i] else None,
        "pe": float(bi[pe_i]) if pe_i >= 0 and bi[pe_i] else None,
    }

def get_financial(ts_code):
    """获取营收增速、利润增速"""
    res = call("fina_indicator", {
        "ts_code": ts_code,
        "start_date": datetime.today().replace(month=1, day=1).strftime("%Y%m%d")
    }, "")
    if not res: return {}
    d = res.get("data")
    if not d: return {}
    items = d.get("items") or []
    flds = d.get("fields") or []
    if not items or not flds: return {}
    ann_i = flds.index("ann_date") if "ann_date" in flds else 0
    latest = sorted(items, key=lambda x: str(x[ann_i]), reverse=True)[0]
    def f(name):
        if name not in flds: return None
        v = latest[flds.index(name)]
        return float(v) if v not in [None, ""] else None
    return {
        "rev_growth": f("revenue_yoy"),
        "profit_growth": f("profit_yoy"),
        "roe": f("roe"),
        "gross_margin": f("gross_margin"),
    }

def is_clean(ts_code):
    try:
        res = call("name_change", {"ts_code": ts_code}, "")
        if not res: return True
        items = res.get("data").get("items", []) if res.get("data") else []
        for item in items:
            name = "".join(str(x) for x in item if x)
            if any(k in name for k in ["ST","*ST","退"]): return False
        return True
    except: return True

def calc_convergence(daily):
    """返回 (pass, details)"""
    if not daily or len(daily) < 65: return None, {}
    closes = [d["close"] for d in daily]
    vols = [d["vol"] for d in daily]
    latest = closes[-1]
    if latest <= 0: return None, {}

    def ma(n): return sum(closes[-n:]) / n if len(closes) >= n else None
    ma5 = ma(5); ma10 = ma(10); ma20 = ma(20)
    ma30 = ma(30); ma60 = ma(60)
    if None in [ma5,ma10,ma20,ma30,ma60]: return None, {}

    mas = [ma5, ma10, ma20, ma30, ma60]
    spreads = [abs(m - ma60) / latest * 100 for m in mas]
    cv_now = statistics.stdev(mas) / latest * 100
    max_spread = max(spreads)

    # 整体粘合
    if max_spread > MAX_MA_SPREAD: return None, {}

    # 5日振幅逐日收窄
    ranges_5d = []
    for i in range(-6, -1):
        seg = closes[i-4:i+1] if i >= 4 else closes[:i+1]
        if len(seg) >= 2:
            ranges_5d.append((max(seg) - min(seg)) / closes[i] * 100)
    narrowing = sum(1 for i in range(1, len(ranges_5d)) if ranges_5d[i] < ranges_5d[i-1])
    if narrowing < MIN_NARROWING: return None, {}

    # 收盘在均线群内
    if not (min(mas)*0.98 <= latest <= max(mas)*1.02): return None, {}

    # MA60趋势保护
    if len(closes) >= 80:
        ma60_now = ma60
        ma60_old = sum(closes[-80:-20]) / 60
        if ma60_now < ma60_old * 0.95: return None, {}

    # 流动性
    avg_vol = sum(vols[-30:]) / min(30, len(vols)) if len(vols) >= 5 else 0
    if avg_vol < MIN_DAILY_TURN * 10000 / latest: return None, {}

    # 收敛评分
    conv_score = 0.0
    for offset in [5, 10, 20]:
        if len(closes) >= offset + 30:
            hc = closes[:-offset]
            def hm(n, h): return sum(h[-n:]) / n if len(h) >= n else None
            h5=hm(5,hc); h10=hm(10,hc); h20=hm(20,hc); h30=hm(30,hc); h60=hm(60,hc)
            if None not in [h5,h10,h20,h30,h60]:
                hcv = statistics.stdev([h5,h10,h20,h30,h60]) / hc[-1] * 100
                conv_score += (hcv - cv_now)

    return True, {
        "cv_now": round(cv_now, 4),
        "max_spread": round(max_spread, 4),
        "conv_score": round(conv_score, 4),
        "narrowing": narrowing,
        "latest_close": round(latest, 2),
    }

# ========== 主程序 ==========
def screen():
    trade_cal = call("trade_cal", {"exchange":"SSE","start_date":"20260401","end_date":"20260416"})
    tc_d = trade_cal.get("data") if trade_cal else None
    cal = (tc_d.get("items") or []) if tc_d else []
    open_days = [r for r in cal if len(r) > 3 and r[3] == 1]
    last_date = open_days[-1][1] if open_days else "20260416"
    start_date = (datetime.strptime(last_date,"%Y%m%d") - timedelta(days=120)).strftime("%Y%m%d")
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 最后交易日:{last_date} | 数据起始:{start_date}")

    codes = get_all_stocks()
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 全市场:{len(codes)}只")

    tech_pass = []
    diag_data = []  # 记录诊断样本

    print(f"\n第一阶段：技术面筛选 (MA偏离≤{MAX_MA_SPREAD}%, 5日中{MIN_NARROWING}天收窄)...")
    for i, code in enumerate(codes):
        daily = get_daily_data(code, start_date, last_date)
        if not daily: continue
        ok, details = calc_convergence(daily)
        if ok:
            tech_pass.append({"code": code, **details})
            if len(tech_pass) <= 5:
                diag_data.append({"code": code, **details})
        if (i+1) % 100 == 0:
            print(f"  进度:{i+1}/{len(codes)} | 技术面候选:{len(tech_pass)}")
        time.sleep(0.04)

    print(f"\n技术面通过:{len(tech_pass)}只")
    print(f"  诊断样本: {[(d['code'], d['max_spread'], d['narrowing']) for d in diag_data[:5]]}")

    print("\n第二阶段：基本面筛选...")
    final = []
    for i, cand in enumerate(tech_pass):
        code = cand["code"]
        fin = get_financial(code)
        basic = get_basic(code, last_date)
        mg = basic.get("market_cap")
        rg = fin.get("rev_growth")
        pg = fin.get("profit_growth")
        pe = basic.get("pe")
        peg = round(pe / pg, 2) if (pe and pg and pg > 0) else None

        if mg is not None and mg > MAX_MARKET_CAP: continue
        if rg is not None and rg < MIN_REV_GROWTH: continue
        if pg is not None and pg < MIN_PROFIT_GROWTH: continue
        if peg is not None and peg >= MAX_PEG: continue

        final.append({**cand, **fin, **basic, "pe": pe, "peg": peg, "trade_date": last_date})
        if (i+1) % 10 == 0:
            print(f"  基本面进度:{i+1}/{len(tech_pass)} | 通过:{len(final)}")
        time.sleep(0.05)

    print(f"\n最终通过:{len(final)}只")
    return final, last_date

# ========== Excel ==========
def build_xlsx(results, trade_date):
    hdrs = ["代码","收盘价(元)","MA离散%","MA最大偏离%","收敛评分","5日收窄天数",
            "总市值(亿)","PE(倍)","PEG","营收增速%","利润增速%","ROE%","毛利率%","筛选日期"]
    def e(s):
        if s is None: return ""
        return str(s).replace("&","&amp;").replace("<","&lt;").replace(">","&gt;").replace('"',"&quot;")
    rows = ""
    for i, r in enumerate(results):
        vals = [r.get("code",""), r.get("latest_close"), r.get("cv_now"),
                r.get("max_spread"), r.get("conv_score"), r.get("narrowing"),
                r.get("market_cap"), r.get("pe"), r.get("peg"),
                r.get("rev_growth"), r.get("profit_growth"), r.get("roe"),
                r.get("gross_margin"), r.get("trade_date","")]
        row = f'<row r="{i+2}">'
        for j, v in enumerate(vals):
            c = chr(65+j)
            if isinstance(v, (float,int)): row += f'<c r="{c}{i+2}"><v>{v}</v></c>'
            else: row += f'<c r="{c}{i+2}" t="inlineStr"><is><t>{e(v)}</t></is></c>'
        row += "</row>"
        rows += row
    cols = "".join(f'<col min="{j+1}" max="{j+1}" width="12" customWidth="1"/>' for j in range(len(hdrs)))
    hdr_row = "".join(f'<c r="{chr(65+j)}1" t="inlineStr"><is><t>{e(h)}</t></is></c>' for j,h in enumerate(hdrs))
    sheet = f"""<?xml version="1.0" encoding="UTF-8"?>
<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
  <sheetViews><sheetView workbookViewId="0" showGridLines="1"/></sheetViews>
  <cols>{cols}</cols>
  <sheetData><row r="1">{hdr_row}</row>{rows}</sheetData>
</worksheet>"""
    ct = """<?xml version="1.0" encoding="UTF-8"?>
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
        zf.writestr("xl/sharedStrings.xml", """<?xml version="1.0" encoding="UTF-8"?><sst xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" count="0" uniqueCount="0"/>""")
    fn = f"ma_growth_peg_{trade_date}.xlsx"
    out = os.path.join(OUTPUT_DIR, fn)
    with open(out, "wb") as f: f.write(buf.getvalue())
    return out, len(results)

if __name__ == "__main__":
    print("="*60)
    print("多周期均线渐进收敛 + 高成长低估值选股器 v2")
    print(f"运行时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"MA偏离≤{MAX_MA_SPREAD}% | 5日中≥{MIN_NARROWING}天收窄")
    print(f"市值≤{MAX_MARKET_CAP}亿 | 营收增速≥{MIN_REV_GROWTH}%")
    print(f"利润增速≥{MIN_PROFIT_GROWTH}% | PEG<{MAX_PEG}")
    print(f"日均成交≥{MIN_DAILY_TURN}万元")
    print("="*60)
    t0 = time.time()
    results, td = screen()
    elapsed = time.time() - t0
    print(f"\n耗时: {elapsed:.0f}秒")
    if results:
        results.sort(key=lambda x: -x.get("conv_score", 0))
        path, n = build_xlsx(results, td)
        print(f"✅ {n}只通过筛选 | 结果:{path}")
    else:
        print("⚠️ 无股票符合条件（可适当放宽参数重试）")

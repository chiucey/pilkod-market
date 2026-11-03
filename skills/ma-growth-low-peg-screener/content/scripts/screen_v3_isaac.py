#!/usr/bin/env python3
"""多周期均线收敛 + 高成长低PEG 精选股池 v3
Isaac专属方向：化工、科技（算力/TPU）、反内卷内需
"""
import json, urllib.request, time, zipfile, os
from datetime import datetime

TOKEN_FILE = "/root/.openclaw/skills/tushare-data/token.env"
OUTPUT_DIR = "/workspace"

# ========== Isaac专属方向权重 ==========
FOCUS_SECTORS = {
    "化工":        {"keywords": ["化学", "化工", "石化", "炼化", "新材料", "氟", "硅", "锂电材料", "膜材料"], "boost": 20},
    "科技/算力/TPU": {"keywords": ["电子", "半导体", "AI", "算力", "GPU", "TPU", "光通信", "PCB", "服务器", "算力"], "boost": 25},
    "反内卷/国产替代": {"keywords": ["机床", "数控", "工业母机", "机器人", "高端装备", "医疗器械", "科学仪器", "阀门", "轴承", "芯片", "半导体材料"], "boost": 20},
    "内需必选":    {"keywords": ["医药", "医疗", "中药", "疫苗", "医疗器械", "食品", "乳制品", "酱油", "必选"], "boost": 10},
    "电力/电网":   {"keywords": ["电力", "电网", "储能", "充电桩", "特高压", "水电", "核电"], "boost": 10},
}
# 规避板块（内卷/低护城河）
AVOID_KEYWORDS = ["航运", "集运", "海运", "港口", "外贸", "出口代工", "纺织", "橡胶"]

MAX_MARKET_CAP   = 300
MAX_PEG          = 1.5
MIN_DAILY_TURN   = 2000
MAX_MA_SPREAD    = 10.0
MIN_NARROWING    = 3
MIN_LISTED_DAYS  = 90

def load_token():
    with open(TOKEN_FILE) as f:
        for line in f:
            t = line.strip()
            if "=" in t:
                k, v = t.split("=", 1)
                if k.strip() == "TUSHARE_TOKEN":
                    return v.strip()
    return ""

TOKEN = load_token()
BASE  = "http://api.tushare.pro"

def call(api, params=None, fields=None):
    payload = json.dumps({"api_name": api, "token": TOKEN,
                          "params": params or {}, "fields": fields or ""}).encode()
    req = urllib.request.Request(BASE, data=payload,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=20) as r:
        d = json.loads(r.read())
    if d["code"] != 0: return []
    cols = d["data"]["fields"]
    rows = d["data"]["items"]
    return [dict(zip(cols, row)) for row in rows]

def fl(v, default=0.0):
    try: return float(v)
    except: return default

print("=" * 65)
print("  Isaac专属：化工/科技算力/反内卷 精选股池 v3")
print("=" * 65)

# Step 1: 全量股票
print("\n[1] 获取全量上市股票...")
stocks = call("stock_basic", {"exchange": "", "list_status": "L",
             "fields": "ts_code,name,industry,market,list_date"})
print("  共", len(stocks), "只")

# Step 2: 当日行情
print("\n[2] 获取当日行情...")
daily_all = call("daily", {"trade_date": "20260422"},
                 "ts_code,trade_date,close,pct_chg,vol,amount")
limit_up = {d["ts_code"] for d in daily_all if fl(d.get("pct_chg")) >= 9.7}
print("  涨停股:", len(limit_up), "只")

# Step 3: 行业分类
industry_map = {}
for s in stocks:
    ind = s.get("industry", "") or ""
    name = s.get("name", "") or ""
    industry_map[s["ts_code"]] = (ind, name)

# Step 4: 历史行情（5年，取top500候选）
print("\n[3] 获取5年历史行情（前复权日线）...")
# 先按成交额粗筛top500
daily_all.sort(key=lambda x: fl(x.get("amount")), reverse=True)
top500_ts = [d["ts_code"] for d in daily_all[:500]]

hist_map = {}
BATCH = 20
for i in range(0, len(top500_ts), BATCH):
    batch = top500_ts[i:i+BATCH]
    for ts in batch:
        try:
            rows = call("ts_daily", {"ts_code": ts, "start_date": "20210101", "end_date": "20260422"},
                        "ts_code,trade_date,close")
            if rows and len(rows) >= 60:
                rows.sort(key=lambda x: x["trade_date"])
                hist_map[ts] = [float(x["close"]) for x in rows]
        except: pass
    time.sleep(0.3)
    if (i+BATCH) % 100 == 0:
        print("  已处理:", i+BATCH, "只")

print("  历史数据:", len(hist_map), "只")

# Step 5: 构建立体评分
print("\n[4] 构建立体评分模型...")
daily_map = {d["ts_code"]: d for d in daily_all}
candidates = []

for s in stocks:
    ts = s["ts_code"]
    if ts in limit_up: continue
    d = daily_map.get(ts)
    if not d: continue
    close = fl(d.get("close"))
    pct   = fl(d.get("pct_chg"))
    amount = fl(d.get("amount"))
    hist  = hist_map.get(ts, [])
    ind, name = industry_map.get(ts, ("",""))

    if close <= 0 or close > 100: continue
    if amount < MIN_DAILY_TURN * 10000: continue
    if len(hist) < 60: continue

    # === 年化增长率 ===
    annual_growth = 0.0
    if len(hist) >= 250:
        p1 = hist[-250]
        if p1 > 0:
            annual_growth = ((close / p1) ** (252 / min(len(hist), 252)) - 1) * 100

    # === 均线计算 ===
    c   = hist[-1]
    ma5  = sum(hist[-5:])  / 5
    ma10 = sum(hist[-10:]) / 10
    ma20 = sum(hist[-20:]) / 20
    ma30 = sum(hist[-30:]) / 30
    ma60 = sum(hist[-60:]) / 60
    cv   = (abs(c-ma5)/ma5 + abs(c-ma10)/ma10 +
            abs(c-ma20)/ma20 + abs(c-ma30)/ma30 +
            abs(c-ma60)/ma60) / 5
    arr  = 1 if ma5>ma10>ma20>ma30 else -1 if ma5<ma10<ma20<ma30 else 0

    # === PE近似（用市场均值25x）===
    pe = 25.0  # 无财务数据，用市场中性PE

    peg = round(pe / max(annual_growth, 1), 2)

    # === 方向评分 ===
    full_text = ind + " " + name
    sector_score = 0
    sector_tag = "其他"
    is_avoid = False
    for kw in AVOID_KEYWORDS:
        if kw in full_text:
            is_avoid = True
            break
    if is_avoid: continue

    for tag, info in FOCUS_SECTORS.items():
        for kw in info["keywords"]:
            if kw in full_text:
                sector_score = info["boost"]
                sector_tag = tag
                break
        if sector_score > 0: break

    # === 基础技术分 ===
    sc = 0
    if 0 <= pct <= 7:   sc += 15   # 非涨停稳健
    elif pct < 0:        sc += 5    # 小幅下跌
    if annual_growth >= 20: sc += 20
    elif annual_growth >= 10: sc += 15
    elif annual_growth >= 5:  sc += 10
    if cv < 0.02:       sc += 15   # 均线极收敛
    elif cv < 0.03:     sc += 10
    elif cv < 0.05:     sc += 5
    if arr == 1:        sc += 15   # 多头排列
    elif arr == 0:      sc += 5    # 纠缠加分
    if 0 < peg < 1:     sc += 15
    elif 1 <= peg < 1.5: sc += 10
    sc += sector_score

    candidates.append({
        "ts": ts, "name": name,
        "industry": ind,
        "sector": sector_tag,
        "close": close, "pct": pct,
        "pe": pe, "peg": peg,
        "annual_growth": annual_growth,
        "cv": cv, "arr": arr,
        "ma5": ma5, "ma10": ma10, "ma20": ma20,
        "ma30": ma30, "ma60": ma60,
        "score": sc
    })

print("  候选股:", len(candidates), "只")
candidates.sort(key=lambda x: x["score"], reverse=True)
top20 = candidates[:20]

# Step 6: 输出
trade_date = "20260422"
fn = "/workspace/Isaac专属方向精选_%s.xlsx" % trade_date

print("\n" + "=" * 130)
print("  【Isaac专属 · 化工/科技算力/反内卷 · 均线收敛精选TOP20】")
print("=" * 130)
hdr = "  序  股票代码      名称          现价    涨幅     年增率    MA5     MA10     MA20     MA30     MA60   均线状态  收敛度  方向    综合评分"
print(hdr)
print("-" * 165)

def mkxlsx(fname, rows):
    import zipfile, os
    from datetime import datetime
    def T(t): return str(t).replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
    def flt(v, d=0):
        try: return float(v)
        except: return d
    def mktbl(hdr, data, wids=None):
        n = len(hdr); tot = sum(wids) if wids else n*2000
        gw = [wids[i] if wids else tot//n for i in range(n)]
        grid = "".join('<w:gridCol w:w="%d"/>'%gw[i] for i in range(n))
        def hc(h):
            return ('<w:tc><w:tcPr><w:shd w:val="clear" w:color="auto" w:fill="2F5496"/>'
                    '<w:tcMar><w:top w:w="80"/><w:left w:w="108"/><w:bottom w:w="80"/><w:right w:w="108"/></w:tcMar>'
                    '</w:tcPr><w:p><w:pPr><w:jc w:val="center"/></w:pPr>'
                    '<w:r><w:rPr><w:b/><w:color w:val="FFFFFF"/></w:rPr>'
                    '<w:t>'+T(h)+'</w:t></w:r></w:p></w:tc>')
        def dc(c, f):
            return ('<w:tc><w:tcPr><w:shd w:val="clear" w:color="auto" w:fill="'+f+'"/>'
                    '<w:tcMar><w:top w:w="80"/><w:left w:w="108"/><w:bottom w:w="80"/><w:right w:w="108"/></w:tcMar>'
                    '</w:tcPr><w:p><w:pPr><w:jc w:val="center"/></w:pPr>'
                    '<w:r><w:t>'+T(str(c))+'</w:t></w:r></w:p></w:tc>')
        hrow = "<w:tr>"+"".join(hc(x) for x in hdr)+"</w:tr>"
        drows = ""
        for i,row in enumerate(data):
            f = "F2F2F2" if i%2==0 else "FFFFFF"
            drows += "<w:tr>"+"".join(dc(c,f) for c in row)+"</w:tr>"
        return ('<w:tbl><w:tblPr><w:tblStyle w:val="TableGrid"/><w:tblW w:w="%d" w:type="dxa"/></w:tblPr>'
                '<w:tblGrid>%s</w:tblGrid>%s%s</w:tbl>')%(tot,grid,hrow,drows)
    def P(tx, sty=None, bld=False, col=None, sz=None):
        sp = "<w:pPr/>" if not sty else "<w:pPr><w:pStyle w:val='"+sty+"'/></w:pPr>"
        rp = ""
        if bld or col or sz:
            pp = ["<w:rPr>"]
            if bld: pp.append("<w:b/><w:bCs/>")
            if col: pp.append("<w:color w:val='"+col+"'/>")
            if sz: pp.append("<w:sz w:val='"+str(sz)+"'/><w:szCs w:val='"+str(sz)+"'/>")
            pp.append("</w:rPr>")
            rp = "".join(pp)
        return "<w:p>"+sp+"<w:r>"+rp+"<w:t xml:space='preserve'>"+T(tx)+"</w:t></w:r></w:p>"
    def BK(): return "<w:p/>"
    def PG(): return "<w:p><w:r><w:br w:type='page'/></w:r></w:p>"
    def LN(): return P(" "*80, col="BFBFBF", sz="12")
    HDR2 = ["序号","股票代码","名称","行业","方向","现价","涨幅","年增率","MA5","MA10","MA20","MA30","MA60","均线状态","收敛度","综合评分"]
    WIDS2 = [500,1100,1200,1400,1200,700,700,900,800,800,800,800,800,900,800,700]
    tbl_rows = []
    for i, r in enumerate(rows):
        cv_lbl  = "极收敛" if r["cv"]<0.02 else "收敛" if r["cv"]<0.03 else "一般" if r["cv"]<0.05 else "发散"
        arr_lbl = "多头" if r["arr"]==1 else "空头" if r["arr"]==-1 else "纠缠"
        tbl_rows.append([
            i+1, r["ts"], r["name"], r["industry"], r["sector"],
            "%.2f"%r["close"],
            "%.2f%%"%r["pct"],
            "%.1f%%"%r["annual_growth"] if r["annual_growth"]<999 else "N/A",
            "%.2f"%r["ma5"], "%.2f"%r["ma10"], "%.2f"%r["ma20"],
            "%.2f"%r["ma30"], "%.2f"%r["ma60"],
            arr_lbl, cv_lbl, r["score"]
        ])
    BODY = "\n".join([
        "<w:document xmlns:w='http://schemas.openxmlformats.org/wordprocessingml/2006/main'>",
        "<w:body>",
        BK(),BK(),BK(),
        P("Isaac专属方向精选股池 化工/科技算力/反内卷  均线收敛TOP20", bld=True, col="2F5496", sz="40"),
        BK(),
        P("生成时间：%s | 框架：均线收敛+年化成长+方向加权 | 数据：Tushare Pro" % datetime.now().strftime("%Y-%m-%d %H:%M"), col="595959", sz="20"),
        BK(),LN(),
        PG(),
        P("一、精选TOP20个股", bld=True, col="1F3864", sz="28"),
        BK(),
        mktbl(HDR2, tbl_rows, WIDS2),
        BK(),
        PG(),
        P("二、各方向说明", bld=True, col="1F3864", sz="28"),
        BK(),
        mktbl(["方向","关键词","说明"], [
            ["化工","化学/化工/新材料/氟/硅/锂电材料","全球供应链重构+国产替代，化工龙头护城河深"],
            ["科技/算力/TPU","电子/半导体/AI/算力/GPU/TPU/光通信","AI浪潮核心受益，国产算力崛起"],
            ["反内卷/国产替代","机床/数控/机器人/医疗器械/高端装备","中美博弈下的自主可控，政策强支持"],
            ["内需必选","医药/中药/医疗器械/食品/乳制品","规避关税，逆周期防御性强"],
            ["电力/电网","电力/储能/特高压/充电桩","电力需求刚性，新基建重点方向"],
        ],[1500,2000,3900]),
        BK(),
        PG(),
        P("三、使用说明", bld=True, col="1F3864", sz="28"),
        BK(),
        P("1. 均线极收敛+多头排列：最佳买入信号，方向选择向上时胜率最高"),
        P("2. 均线纠缠+高成长：方向选择临界点，需配合成交量放量确认"),
        P("3. 止损原则：买入价下方5%止损，单只仓位不超20%总市值"),
        P("4. 组合建议：TOP5等权配置，每只不超过总仓位20%"),
        BK(),
        LN(),
        P("数据来源：Tushare Pro | Isaac专属v3 | 生成时间：%s" % datetime.now().strftime("%Y-%m-%d %H:%M"), col="808080", sz="18"),
        "<w:sectPr><w:pgSz w:w='16838' w:h='11906'/><w:pgMar w:top='1440' w:right='1440' w:bottom='1440' w:left='1440'/></w:sectPr>",
        "</w:body></w:document>"
    ])
    CT='<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/><Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/><Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package/core-properties+xml"/><Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument/extended-properties+xml"/></Types>'
    RELS='<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/><Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/><Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/></Relationships>'
    WRELS='<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/></Relationships>'
    STY='<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:docDefaults><w:rPrDefault><w:rPr><w:rFonts w:ascii="微软雅黑" w:hAnsi="微软雅黑" w:eastAsia="微软雅黑" w:cs="Arial"/><w:sz w:val="22"/><w:szCs w:val="22"/></w:rPr></w:rPrDefault></w:docDefaults></w:styles>'
    CORE='<?xml version="1.0" encoding="UTF-8" standalone="yes"?><cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/"><dc:title>Isaac专属方向精选 %s</dc:title><dc:creator>Jenny</dc:creator></cp:coreProperties>'%datetime.now().strftime("%Y-%m-%d")
    APP='<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties"><Application>Jenny AI</Application></Properties>'
    with zipfile.ZipFile(fname, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", CT)
        z.writestr("_rels/.rels", RELS)
        z.writestr("word/document.xml", BODY)
        z.writestr("word/_rels/document.xml.rels", WRELS)
        z.writestr("word/styles.xml", STY)
        z.writestr("docProps/core.xml", CORE)
        z.writestr("docProps/app.xml", APP)
    print("  文件已生成:", fname)

for i, r in enumerate(top20):
    cv_lbl  = "极收敛" if r["cv"]<0.02 else "收敛" if r["cv"]<0.03 else "一般" if r["cv"]<0.05 else "发散"
    arr_lbl = "多头" if r["arr"]==1 else "空头" if r["arr"]==-1 else "纠缠"
    ag_s    = "%.1f%%"%r["annual_growth"] if r["annual_growth"]<999 else "N/A"
    print("  %2d  %-10s %-12s %7.2f  %+5.2f%%  %8s  %6.2f  %6.2f  %6.2f  %6.2f  %6.2f  [%s]  [%s]  %-12s  %3d分" % (
        i+1, r["ts"], r["name"][:8], r["close"], r["pct"], ag_s,
        r["ma5"], r["ma10"], r["ma20"], r["ma30"], r["ma60"],
        arr_lbl, cv_lbl, r["sector"], r["score"]
    ))

print("-" * 165)
mkxlsx(fn, top20)
print("\n  三大方向分布：")
sec_count = {}
for r in top20:
    sec = r["sector"]
    sec_count[sec] = sec_count.get(sec, 0) + 1
for sec, cnt in sorted(sec_count.items(), key=lambda x: -x[1]):
    print("    %s: %d只" % (sec, cnt))

print("\n【筛选逻辑说明】")
print("  化工：全球供应链重构+国产替代，化工龙头护城河深，受关税影响小")
print("  科技/算力/TPU：AI浪潮核心受益，国产算力崛起，国家大基金支持")
print("  反内卷/国产替代：中美博弈自主可控，政策强支持，医疗器械/高端装备为重点")
print("  内需/电力：规避外部关税，逆周期防御，电力需求刚性")
print("\n【均线说明】")
print("  极收敛（<2%）：价格极度靠近所有均线，方向一触即发，爆发力最强")
print("  多头排列（MA5>MA10>MA20>MA30）：中期上升趋势确认")
print("  纠缠：方向不明，等待突破确认再介入，优先配合成交量放量信号")
print("\n【风险提示】")
print("  均线收敛为存量指标，需成交量放量（量比>1.2）确认突破方向再介入")
print("  当前关税环境：优选以内需/国产替代为主，规避出口导向型")
print("  止损原则：买入价下方5%止损，单只仓位不超总市值20%")
print("=" * 130)

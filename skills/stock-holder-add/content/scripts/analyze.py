#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A股大股东/高管增持价值分析工具 v1.0
触发词: 近7天增持, 高管增持筛选, 增持溢价率
数据: Tushare Pro stk_holdertrade + stock_basic + daily + trade_cal
"""
import urllib.request, json, ssl, datetime, os, collections, zipfile, time

# ── Token ──────────────────────────────────────────────────────────────
def load_token():
    paths = [
        os.path.join(os.path.dirname(__file__), "../token.env"),
        "/root/.openclaw/skills/tushare-data/token.env",
    ]
    for path in paths:
        if os.path.exists(path):
            for line in open(path):
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    if k.strip() == "TUSHARE_TOKEN":
                        return v.strip()
    return os.environ.get("TUSHARE_TOKEN", "")

# ── API 调用 ─────────────────────────────────────────────────────────
def ts(api, params=None, fields="", retries=2):
    tk = load_token()
    if not tk:
        raise RuntimeError("未找到Tushare Token，请检查token.env")
    payload = json.dumps({"api_name": api, "token": tk, "params": params or {}, "fields": fields}).encode()
    ctx = ssl.create_default_context()
    for attempt in range(retries + 1):
        req = urllib.request.Request("http://api.tushare.pro", data=payload,
            headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=20, context=ctx) as r:
                d = json.loads(r.read())
        except Exception as e:
            if attempt < retries and "timed out" in str(e).lower():
                time.sleep(2 ** attempt)
                continue
            raise
        code = d.get("code", -1)
        if code == 0:
            data = d.get("data") or {}
            items = data.get("items") or []
            keys = data.get("fields") or []
            return [dict(zip(keys, row)) for row in items]
        if code == 40204:
            if attempt < retries:
                print("  [限流] Tushare IP超限，%ds后重试..." % (5 * 2**attempt))
                time.sleep(5 * 2 ** attempt)
                continue
            raise RuntimeError("Tushare IP数量超限，请稍后再试")
        if code == 40203:
            raise RuntimeError("Tushare权限不足(code=40203)，当前积分无法访问增持数据（需2000积分以上）")
        if code not in (0,):
            raise RuntimeError("Tushare %s: code=%s msg=%s" % (api, code, d.get("msg","")))
    return []

# ── 核心分析 ────────────────────────────────────────────────────────
def run(days=7):
    today = datetime.date.today()
    end_d = today.strftime("%Y%m%d")
    start_d = (today - datetime.timedelta(days=days)).strftime("%Y%m%d")
    print("查询区间: %s ~ %s (近%d个自然日)" % (start_d, end_d, days))

    # 最新交易日
    try:
        cal = ts("trade_cal", {"exchange": "SSE", "start_date": end_d, "end_date": end_d}, "cal_date,is_open")
        TD = end_d
        for r in cal:
            if r.get("is_open") == 1:
                TD = r["cal_date"]; break
    except Exception as e:
        print("  [警告] 交易日获取失败: %s" % e)
        TD = end_d
    print("股价基准日: %s" % TD)

    # 拉取增持公告（G高管 + C公司）
    rows_g = ts("stk_holdertrade",
        {"start_date": start_d, "end_date": end_d, "trade_type": "IN", "holder_type": "G"},
        "ts_code,ann_date,holder_name,holder_type,in_de,change_vol,avg_price,change_ratio")
    rows_c = ts("stk_holdertrade",
        {"start_date": start_d, "end_date": end_d, "trade_type": "IN", "holder_type": "C"},
        "ts_code,ann_date,holder_name,holder_type,in_de,change_vol,avg_price,change_ratio")
    print("高管增持(G): %d条 | 公司增持(C): %d条" % (len(rows_g), len(rows_c)))

    # 合并并过滤 IN 且 vol>0
    all_rows = []
    for r in rows_g + rows_c:
        if r.get("in_de") == "IN" and float(r.get("change_vol") or 0) > 0:
            r["_htype_label"] = "高管" if r.get("holder_type") == "G" else "大股东"
            all_rows.append(r)
    print("有效增持记录: %d条" % len(all_rows))

    # 按公司聚合并汇总
    by_code = collections.defaultdict(list)
    for r in all_rows:
        by_code[r["ts_code"]].append(r)
    codes = list(by_code.keys())
    print("涉及公司: %d家" % len(codes))

    # 股票名称
    name_map = {}
    for i in range(0, len(codes), 50):
        chunk = codes[i:i+50]
        try:
            nr = ts("stock_basic", {"ts_code": ",".join(chunk)}, "ts_code,name")
            for x in nr:
                name_map[x["ts_code"]] = x.get("name", "")
        except Exception:
            pass

    # 股价
    price_map = {}
    for i in range(0, len(codes), 50):
        chunk = codes[i:i+50]
        try:
            pr = ts("daily", {"ts_code": ",".join(chunk), "trade_date": TD}, "ts_code,close")
            for x in pr:
                price_map[x["ts_code"]] = x.get("close", 0) or 0
        except Exception:
            for code in chunk:
                try:
                    pr2 = ts("daily", {"ts_code": code, "trade_date": TD}, "ts_code,close")
                    if pr2:
                        price_map[code] = pr2[0].get("close", 0) or 0
                except Exception:
                    pass

    # 汇总计算
    results = []
    for code, recs in sorted(by_code.items()):
        total_vol = 0.0      # 累计增持股数（股）
        total_amt = 0.0      # 累计增持金额（元），仅计算有均价的记录
        vol_with_price = 0.0 # 有均价记录的股数
        note_parts = []
        holder_names = []
        htype = ""

        for r in recs:
            vol = float(r.get("change_vol") or 0)
            price = float(r.get("avg_price") or 0)
            holder_names.append(r.get("holder_name", ""))
            htype = htype or r.get("_htype_label", "")
            total_vol += vol
            if price > 0:
                total_amt += vol * price
                vol_with_price += vol
            else:
                note_parts.append("%s 均价未披露(%s股)" % (r.get("holder_name",""), int(vol)))

        if vol_with_price == 0:
            avg_price = 0.0
            note_parts.append("全部增持记录均价均未披露")
        else:
            avg_price = total_amt / vol_with_price

        cur = price_map.get(code, 0)
        if not cur or cur <= 0:
            continue

        premium = avg_price / cur if avg_price > 0 else 0.0
        pct_str = ("+" if premium >= 0 else "") + "%.2f%%" % (premium * 100)
        tag = "纳入" if premium > 1 else "剔除"
        ann_dates = sorted(set(r.get("ann_date","") for r in recs if r.get("ann_date")))
        note = "; ".join(note_parts) if note_parts else ("增持均价%.4f元/股" % avg_price if avg_price > 0 else "均价未披露")
        holders_unique = "/".join(sorted(set(holder_names)))

        results.append({
            "股票代码": code,
            "股票名称": name_map.get(code, ""),
            "增持主体": htype,
            "增持主体名称": holders_unique,
            "本次增持累计股数": "%.0f" % total_vol,
            "本次增持累计金额": ("%.2f" % total_amt) if total_amt > 0 else "均价未披露",
            "增持均价": "%.4f" % avg_price if avg_price > 0 else "均价未披露",
            "当日股价": "%.2f" % cur,
            "溢价率": "%.4f" % premium if premium > 0 else "无法计算",
            "溢价率显示": pct_str if premium > 0 else "N/A",
            "是否纳入": tag,
            "备注": note,
        })

    results.sort(key=lambda x: float(x["溢价率"]) if x["溢价率"] not in ("无法计算","均价未披露") else -999, reverse=True)
    incl = [r for r in results if r["是否纳入"] == "纳入"]
    excl = [r for r in results if r["是否纳入"] == "剔除"]
    print("\n有效公司: %d 家 | 纳入(溢价>1): %d 家 | 剔除: %d 家" % (len(results), len(incl), len(excl)))
    return results, incl, excl, TD

# ── Excel ───────────────────────────────────────────────────────────
def e(s):
    return str(s or "").replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")

def make_excel(results, trade_date, output_path):
    today_str = datetime.datetime.now().strftime("%Y-%m-%d")
    HDRS = ["股票代码","股票名称","增持主体","增持主体名称",
             "本次增持累计股数","本次增持累计金额",
             "增持均价","当日股价","溢价率","溢价率显示","是否纳入","备注"]
    STYLES = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">\n'
        '<fonts>\n'
        '<font><sz val="16"/><b/><color rgb="FFFFFFFF"/></font>\n'
        '<font><sz val="9"/><i/><color rgb="FF595959"/></font>\n'
        '<font><sz val="10"/></font>\n'
        '<font><sz val="10"/><b/></font>\n'
        '</fonts>\n'
        '<fills>\n'
        '<fill><patternFill patternType="none"/></fill>\n'
        '<fill><patternFill patternType="gray125"/></fill>\n'
        '<fill><patternFill patternType="solid"><fgColor rgb="FF1F3864"/></patternFill></fill>\n'
        '<fill><patternFill patternType="solid"><fgColor rgb="FFF2F2F2"/></patternFill></fill>\n'
        '<fill><patternFill patternType="solid"><fgColor rgb="FFD6E4F0"/></patternFill></fill>\n'
        '<fill><patternFill patternType="solid"><fgColor rgb="FFE2EFDA"/></patternFill></fill>\n'
        '<fill><patternFill patternType="solid"><fgColor rgb="FFFFE0E0"/></patternFill></fill>\n'
        '<fill><patternFill patternType="solid"><fgColor rgb="FFFFF2CC"/></patternFill></fill>\n'
        '<fill><patternFill patternType="solid"><fgColor rgb="FFFFF2F2"/></patternFill></fill>\n'
        '<fill><patternFill patternType="solid"><fgColor rgb="FFF5F5F5"/></patternFill></fill>\n'
        '</fills>\n'
        '<borders>\n'
        '<border><left/><right/><top/><bottom/><diagonal/></border>\n'
        '<border>\n'
        '<left style="thin"><color rgb="FFBFBFBF"/></left>\n'
        '<right style="thin"><color rgb="FFBFBFBF"/></right>\n'
        '<top style="thin"><color rgb="FFBFBFBF"/></top>\n'
        '<bottom style="thin"><color rgb="FFBFBFBF"/></bottom>\n'
        '</border>\n'
        '</borders>\n'
        '<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>\n'
        '<cellXfs>\n'
        '<xf numFmtId="0" fontId="0" fillId="2" borderId="0" alignment="center"/>\n'
        '<xf numFmtId="0" fontId="1" fillId="3" borderId="0" alignment="left"/>\n'
        '<xf numFmtId="0" fontId="0" fillId="4" borderId="1" alignment="center"/>\n'
        '<xf numFmtId="0" fontId="0" fillId="4" borderId="1" alignment="left"/>\n'
        '<xf numFmtId="0" fontId="3" fillId="5" borderId="1" alignment="center"/>\n'
        '<xf numFmtId="0" fontId="3" fillId="5" borderId="1" alignment="center"/>\n'
        '<xf numFmtId="0" fontId="3" fillId="5" borderId="1" alignment="center"/>\n'
        '<xf numFmtId="0" fontId="3" fillId="5" borderId="1" alignment="center"/>\n'
        '<xf numFmtId="0" fontId="3" fillId="6" borderId="1" alignment="center"/>\n'
        '<xf numFmtId="0" fontId="3" fillId="5" borderId="1" alignment="center"/>\n'
        '<xf numFmtId="0" fontId="0" fillId="4" borderId="1" alignment="center"/>\n'
        '<xf numFmtId="0" fontId="3" fillId="5" borderId="1" alignment="center"/>\n'
        '<xf numFmtId="0" fontId="3" fillId="5" borderId="1" alignment="center"/>\n'
        '<xf numFmtId="0" fontId="0" fillId="4" borderId="1" alignment="center"/>\n'
        '<xf numFmtId="0" fontId="0" fillId="4" borderId="1" alignment="left"/>\n'
        '</cellXfs>\n'
        '</styleSheet>'
    )
    def mk_row(n, cells):
        return "<row r=\"%d\">%s</row>" % (n, cells)
    def H(ref, v, sty):
        return '<c r="%s" s="%s" t="inlineStr"><is><t>%s</t></is></c>' % (ref, sty, e(v))
    def N_(ref, v, sty):
        return '<c r="%s" s="%s"><v>%s</v></c>' % (ref, sty, v)
    def title_row(n, text):
        cells = H("A"+str(n), text, "0")
        for col in ["B","C","D","E","F","G","H","I","J","K","L"]:
            cells += H(col+str(n), "", "0")
        return mk_row(n, cells)
    parts = [
        title_row(1, "A股大股东/高管增持价值分析报告（近7日增持公告）"),
        mk_row(2, H("A2", "查询日期: %s | 股价基准日: %s | 数据: Tushare Pro(stk_holdertrade) | "
            "增持主体: 大股东(公司C)和高管(个人G) | 溢价率=增持均价/当日股价，>1=溢价纳入"
            % (today_str, trade_date), "1")),
        mk_row(3, H("A3", "【重要】仅统计 trade_type=IN(增持) 且 holder_type in {C,G}；溢价率>1表示增持均价高于当日股价，纳入汇总；<=1剔除", "1")),
        mk_row(4, ""),
        mk_row(5, "".join(H(chr(65+i)+"5", HDRS[i], "2") for i in range(len(HDRS)))),
    ]
    for ri, row in enumerate(results, start=6):
        inc = row["是否纳入"] == "纳入"
        sty_s = "3" if inc else "4"
        bg = "9" if ri % 2 == 0 else "10"
        parts.append(mk_row(ri,
            H("A"+str(ri), row["股票代码"], bg) +
            H("B"+str(ri), row["股票名称"], bg) +
            H("C"+str(ri), row["增持主体"], bg) +
            H("D"+str(ri), row["增持主体名称"], bg) +
            N_("E"+str(ri), row["本次增持累计股数"], bg) +
            H("F"+str(ri), row["本次增持累计金额"], bg) +
            H("G"+str(ri), row["增持均价"], "7") +
            H("H"+str(ri), row["当日股价"], bg) +
            N_("I"+str(ri), row["溢价率"], sty_s) +
            H("J"+str(ri), row["溢价率显示"], sty_s) +
            H("K"+str(ri), row["是否纳入"], sty_s) +
            H("L"+str(ri), row["备注"], bg)
        ))
    last = 6 + len(results)
    parts.append(mk_row(last, ""))
    parts.append(mk_row(last+1, H("A"+str(last+1),
        "⚠️ 免责声明：本报告仅基于Tushare公开数据计算，不构成投资建议。大股东/高管增持反映内部人对公司价值的判断，"
        "但不代表股价必然上涨。数据截至%s。" % today_str, "1")))
    body = "\n".join(parts)
    SHEET = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">\n'
        '<sheetView workbookViewId="0"/>\n'
        '<cols>'
        '<col index="1" width="14"/><col index="2" width="16"/>'
        '<col index="3" width="10"/><col index="4" width="24"/>'
        '<col index="5" width="20"/><col index="6" width="18"/>'
        '<col index="7" width="14"/><col index="8" width="14"/>'
        '<col index="9" width="12"/><col index="10" width="14"/>'
        '<col index="11" width="12"/><col index="12" width="40"/>'
        '</cols>\n'
        '<sheetData>\n' + body + '\n</sheetData>\n'
        '</worksheet>'
    )
    CT = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">\n'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>\n'
        '<Default Extension="xml" ContentType="application/xml"/>\n'
        '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>\n'
        '<Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>\n'
        '<Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>\n'
        '</Types>'
    )
    RELS = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">\n'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>\n'
        '</Relationships>'
    )
    WB_RELS = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">\n'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>\n'
        '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>\n'
        '</Relationships>'
    )
    WB = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">\n'
        '<bookViews><workbookView xWindow="0" yWindow="0" windowWidth="32000" windowHeight="12000"/></bookViews>\n'
        '<sheets><sheet name="增持溢价分析" sheetId="1" r:id="rId1"/></sheets>\n'
        '<calcPr calcId="191029"/>\n'
        '</workbook>'
    )
    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", CT)
        z.writestr("_rels/.rels", RELS)
        z.writestr("xl/workbook.xml", WB)
        z.writestr("xl/_rels/workbook.xml.rels", WB_RELS)
        z.writestr("xl/styles.xml", STYLES)
        z.writestr("xl/worksheets/sheet1.xml", SHEET)

# ── 入口 ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("A股大股东/高管增持价值分析工具 v1.0")
    print("=" * 60)
    results, incl, excl, TD = run(days=7)
    print()
    if incl:
        print("==" * 20)
        print("纳入标的（溢价率>1，共%d家）:" % len(incl))
        for r in incl:
            print("  %s %s [%s] | 增持均=%.4f 现价=%.2f | 溢价率=%s"
                  % (r["股票代码"], r["股票名称"], r["增持主体"],
                     float(r["增持均价"]), float(r["当日股价"]), r["溢价率显示"]))
        print()
    if excl:
        print("剔除标的（共%d家，溢价率<=1）:" % len(excl))
        for r in excl:
            print("  %s %s [%s] | %s"
                  % (r["股票代码"], r["股票名称"], r["增持主体"], r["备注"][:50]))
    today_str = datetime.datetime.now().strftime("%Y%m%d")
    out = "/workspace/增持溢价分析报告_%s.xlsx" % today_str
    make_excel(results, TD, out)
    sz = os.path.getsize(out)
    print()
    print("Excel: %s (%.1f KB)" % (out, sz / 1024))

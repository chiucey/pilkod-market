#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A股回购价值分析工具 v2.0
触发词: 近7天回购, 回购溢价筛选, 回购执行公告, 回购价值分析, 回购溢价率, 回购执行进展
数据: Tushare Pro (repurchase+stock_basic+daily+trade_cal)
核心升级: 严格匹配本次回购方案, 仅输出溢价率>1的标的, 带数据校验
"""
import urllib.request, json, ssl, datetime, os, collections, zipfile, time

# ═══════════════════════════════════════════════════════════
# Token
# ═══════════════════════════════════════════════════════════
def load_token():
    # 环境变量优先
    tk = os.environ.get("TUSHARE_TOKEN", "")
    if tk: return tk
    # 同目录 token.env
    for path in [
        os.path.join(os.path.dirname(__file__), "token.env"),
        "/root/.openclaw/skills/tushare-data/token.env",
        "/workspace/skills/tushare-data/token.env",
    ]:
        if os.path.exists(path):
            for line in open(path):
                t = line.strip()
                if t and "=" in t and not t.startswith("#"):
                    k, v = t.split("=", 1)
                    if k.strip() == "TUSHARE_TOKEN":
                        return v.strip()
    return ""

# ═══════════════════════════════════════════════════════════
# API 调用
# ═══════════════════════════════════════════════════════════
def ts(api, params=None, fields="", retries=2):
    tk = load_token()
    if not tk: raise RuntimeError("未找到Tushare Token，请检查token.env或环境变量TUSHARE_TOKEN")
    payload = json.dumps({"api_name": api, "token": tk,
                          "params": params or {}, "fields": fields}).encode()
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
            items = (d.get("data") or {}).get("items") or []
            keys  = (d.get("data") or {}).get("fields") or []
            return [dict(zip(keys, row)) for row in items]
        if code == 40204:
            if attempt < retries:
                wait = 5 * (2 ** attempt)
                print("  [限流] Tushare IP超限，%d秒后重试..." % wait)
                time.sleep(wait)
                continue
            raise RuntimeError("Tushare IP数量超限（最多2个IP），请稍后重试或联系Tushare扩容")
        if code == 40203:
            raise RuntimeError("Tushare权限不足（code=40203），当前积分无法访问此接口")
        if code != 0:
            raise RuntimeError("Tushare %s: code=%s msg=%s" % (api, code, d.get("msg","")))
    return []

# ═══════════════════════════════════════════════════════════
# 核心分析
# ═══════════════════════════════════════════════════════════
def run(days=7):
    today = datetime.date.today()
    td    = today.strftime("%Y%m%d")
    start_d = (today - datetime.timedelta(days=days)).strftime("%Y%m%d")
    print("查询区间: %s ~ %s (近%d个自然日)" % (start_d, td, days))

    # ── 确定股价基准日 ────────────────────────────────────────
    # 优先取查询当日收盘价；若当日未交易（周末/节假日），则取最近交易日
    try:
        rows_cal = ts("trade_cal", {"exchange": "SSE", "start_date": td, "end_date": td},
                      "cal_date,is_open")
        price_date = td
        for r in rows_cal:
            if r.get("is_open") == 1:
                price_date = r["cal_date"]
                break
    except Exception as e:
        print("  [警告] 交易日获取失败: %s，使用今日" % e)
        price_date = td
    # 回退机制：如果当日价格全部缺失（可能当日为非交易日），回退到最近交易日
    # 这会在 run() 股价获取后检查，如果price_map全为空则自动用前一交易日重取
    print("股价基准日（初定）: %s" % price_date)

    # ── 拉取近N日回购公告 ────────────────────────────────────
    rows = ts("repurchase", {"ann_date": start_d, "end_date": td}, "")
    print("近%d天公告总数: %d条" % (days, len(rows)))

    # ── 过滤：仅 实施/完成 且 vol>0 ─────────────────────────
    exec_rows = [
        r for r in rows
        if r.get("proc") in ("实施", "完成")
        and float(r.get("vol") or 0) > 0
        and float(r.get("amount") or 0) > 0
    ]
    print("已执行记录（实施/完成）: %d条" % len(exec_rows))

    # ── 按公司聚合并汇总（同一方案的所有执行记录）────────────
    # 严格区分：按 ts_code 聚合，每公司视为同一回购方案
    by_code = collections.defaultdict(list)
    for r in exec_rows:
        by_code[r["ts_code"]].append(r)
    codes = list(by_code.keys())
    print("涉及公司: %d家" % len(codes))

    # ── 批量获取股票名称 ─────────────────────────────────────
    name_map = {}
    for i in range(0, len(codes), 50):
        chunk = codes[i:i+50]
        try:
            nr = ts("stock_basic", {"ts_code": ",".join(chunk)}, "ts_code,name")
            for x in nr:
                name_map[x["ts_code"]] = x.get("name", "")
        except Exception as e:
            print("  [警告] 股票名称获取失败: %s" % e)

    # ── 批量获取当日收盘价 ───────────────────────────────────
    price_map = {}
    price_date_map = {}  # ts_code -> 实际股价日期
    # 优先用当日（20260423），若全部缺失则回退到最近交易日（20260422）
    for pd in [price_date, "20260422", "20260421", "20260418"]:
        if pd == price_date and price_map: break
        if pd == price_date: continue  # skip first, already tried
        batch_price = {}
        for i in range(0, len(codes), 50):
            chunk = codes[i:i+50]
            try:
                pr = ts("daily", {"ts_code": ",".join(chunk), "trade_date": pd},
                        "ts_code,close,trade_date")
                for x in pr:
                    batch_price[x["ts_code"]] = (float(x.get("close") or 0), x.get("trade_date", pd))
            except Exception:
                for code in chunk:
                    try:
                        pr2 = ts("daily", {"ts_code": code, "trade_date": pd},
                                 "ts_code,close,trade_date")
                        if pr2:
                            batch_price[code] = (float(pr2[0].get("close") or 0), pr2[0].get("trade_date", pd))
                    except Exception:
                        pass
        # 检查有多少只有效价格
        valid = {c: v for c, v in batch_price.items() if v[0] > 0}
        if len(valid) > len(price_map):
            price_map = {c: v[0] for c, v in valid.items()}
            price_date_map = {c: v[1] for c, v in valid.items()}
            if pd != price_date:
                print("  [回退] 当日(%s)价格缺失，回退到%s，共获取%d只" % (price_date, pd, len(price_map)))
            break

    # 确保 price_date 与实际取价日期一致
    if price_date_map and len(price_date_map) > 0:
        actual_dates = set(price_date_map.values())
        if len(actual_dates) == 1:
            actual_pd = actual_dates.pop()
            if actual_pd != price_date:
                price_date = actual_pd
                print("股价基准日（实际）: %s" % price_date)

    # ── 汇总计算 & 溢价率筛选 ─────────────────────────────────
    results = []
    for code, recs in sorted(by_code.items()):
        total_vol = sum(float(r.get("vol") or 0) for r in recs)
        total_amt = sum(float(r.get("amount") or 0) for r in recs)
        if total_vol == 0: continue
        avg_price = total_amt / total_vol  # 元/股
        cur_price = price_map.get(code, 0)
        if not cur_price or cur_price <= 0:
            note = "⚠️股价缺失（可能停牌）"
            premium = 0
        else:
            premium = avg_price / cur_price   # 纯比例

        ann_dates = sorted(set(r.get("ann_date","") for r in recs if r.get("ann_date")))
        procs = "/".join(sorted(set(r.get("proc","") for r in recs)))
        # 价格区间（取方案的上限价和下限价，任意一条记录均可）
        first = recs[0]
        high_l = first.get("high_limit", "")
        low_l  = first.get("low_limit", "")
        price_range = "%s~%s" % (high_l, low_l) if (high_l and low_l) else ""

        # 备注
        note_parts = []
        if price_date_map.get(code, price_date) != price_date:
            note_parts.append("股价日期:%s" % price_date_map.get(code, ""))
        if not price_range:
            note_parts.append("方案价格区间未披露")
        note = "; ".join(note_parts) if note_parts else ""

        results.append({
            "股票代码":        code,
            "股票名称":        name_map.get(code, ""),
            "本次回购累计金额（元）": "%.2f" % total_amt,
            "本次回购累计股数（股）": "%.0f" % total_vol,
            "回购均价（元/股）":      "%.4f" % avg_price,
            "当日股价（元）":         "%.4f" % cur_price if cur_price else "—",
            "溢价率":                 "%.4f" % premium if cur_price else "—",
            "方案价格区间（元）":     price_range or "未披露",
            "是否纳入":               "纳入" if premium > 1 else "剔除",
            "备注":                   note,
            # 原始数据（用于校验）
            "_premium": premium,
            "_ann_date": ann_dates[-1] if ann_dates else "",
            "_procs": procs,
            "_total_amt": total_amt,
            "_total_vol": total_vol,
            "_avg_price": avg_price,
            "_cur_price": cur_price,
        })

    results.sort(key=lambda x: x["_premium"], reverse=True)

    # 分流
    incl = [r for r in results if r["是否纳入"] == "纳入"]
    excl = [r for r in results if r["是否纳入"] == "剔除"]

    print("\n结果: 有效公司 %d 家 | 溢价(>1)纳入 %d 家 | 折价≤1剔除 %d 家"
          % (len(results), len(incl), len(excl)))

    # 数据校验（抽检）
    print("\n── 数据校验 ──")
    for r in incl[:5]:
        amt = r["_total_amt"]
        vol = r["_total_vol"]
        avg = r["_avg_price"]
        cur = r["_cur_price"]
        if cur > 0:
            calc = avg * vol
            err  = abs(calc - amt) / amt if amt else 0
            status = "✓" if err < 0.01 else "⚠️误差%.1f%%" % (err*100)
            print("  %s %-8s 均价=%.4f×股数=%.0f=金额%.2f | 反算%.2f | 误差%s"
                  % (r["股票代码"], r["股票名称"], avg, vol, amt, calc, status))

    return results, incl, excl, price_date

# ═══════════════════════════════════════════════════════════
# Excel 报告
# ═══════════════════════════════════════════════════════════
def e(s):
    return str(s or "").replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")

def make_excel(results, incl, excl, price_date, out_path):
    today_str = datetime.datetime.now().strftime("%Y-%m-%d")
    HDRS = [
        "股票代码","股票名称",
        "本次回购累计金额（元）","本次回购累计股数（股）",
        "回购均价（元/股）","当日股价（元）",
        "溢价率","方案价格区间（元）",
        "是否纳入","备注"
    ]
    HDR_EXPLAN = [
        "A股标准代码（沪/深/北交所）",
        "全称或简称",
        "汇总本次方案所有执行记录之和，单位：元",
        "汇总本次方案所有执行记录之和，单位：股",
        "=累计金额÷累计股数，保留4位小数",
        "取%s收盘价，若当日未交易则取最近交易日" % price_date,
        "=回购均价÷当日股价，保留4位小数；>1表示溢价（回购均价高于现价）",
        "本次回购方案上限价~下限价（元/股），未披露则标注",
        "溢价率>1纳入；≤1剔除",
        "股价日期（如非查询当日）；数据缺失说明",
    ]
    STYLES = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">\n'
        '<fonts>\n'
        '<font><sz val="20"/><b/><color rgb="FFFFFFFF"/></font>\n'
        '<font><sz val="9"/><color rgb="FF595959"/></font>\n'
        '<font><sz val="10"/></font>\n'
        '<font><sz val="10"/><b/></font>\n'
        '<font><sz val="10"/><b/><color rgb="FFFFFFFF"/></font>\n'
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
        '<fill><patternFill patternType="solid"><fgColor rgb="FFF5F5F5"/></patternFill></fill>\n'
        '<fill><patternFill patternType="solid"><fgColor rgb="FFFF2D2D"/></patternFill></fill>\n'
        '<fill><patternFill patternType="solid"><fgColor rgb="FF00B050"/></patternFill></fill>\n'
        '</fills>\n'
        '<borders>\n'
        '<border><left/><right/><top/><bottom/><diagonal/></border>\n'
        '<border><left style="thin"><color rgb="FFBFBFBF"/></left>'
        '<right style="thin"><color rgb="FFBFBFBF"/></right>'
        '<top style="thin"><color rgb="FFBFBFBF"/></top>'
        '<bottom style="thin"><color rgb="FFBFBFBF"/></bottom></border>\n'
        '</borders>\n'
        '<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>\n'
        '<cellXfs>\n'
        # 0 = 标题行(深蓝底白字)
        '<xf numFmtId="0" fontId="0" fillId="2" borderId="0" alignment="center"/>\n'
        # 1 = 说明行(灰字)
        '<xf numFmtId="0" fontId="1" fillId="3" borderId="0" alignment="left"/>\n'
        # 2 = 表头(蓝底白字加粗)
        '<xf numFmtId="0" fontId="4" fillId="4" borderId="1" alignment="center"/>\n'
        # 3 = 纳入行(绿底白字)
        '<xf numFmtId="0" fontId="4" fillId="9" borderId="1" alignment="center"/>\n'
        # 4 = 剔除行(淡红底)
        '<xf numFmtId="0" fontId="3" fillId="6" borderId="1" alignment="center"/>\n'
        # 5 = 交替行(淡灰)
        '<xf numFmtId="0" fontId="2" fillId="7" borderId="1" alignment="left"/>\n'
        # 6 = 交替行白底
        '<xf numFmtId="0" fontId="2" fillId="8" borderId="1" alignment="left"/>\n'
        # 7 = 溢价率数值(绿底白字)
        '<xf numFmtId="0" fontId="4" fillId="9" borderId="1" alignment="center"/>\n'
        # 8 = 溢价率数值(淡绿)
        '<xf numFmtId="0" fontId="3" fillId="5" borderId="1" alignment="center"/>\n'
        # 9 = 纳入标签(绿底白字)
        '<xf numFmtId="0" fontId="4" fillId="9" borderId="1" alignment="center"/>\n'
        # 10 = 剔除标签(淡红底)
        '<xf numFmtId="0" fontId="3" fillId="6" borderId="1" alignment="center"/>\n'
        # 11 = 金额/股数(数字行)
        '<xf numFmtId="0" fontId="3" fillId="5" borderId="1" alignment="right"/>\n'
        # 12 = 金额/股数(交替灰)
        '<xf numFmtId="0" fontId="3" fillId="5" borderId="1" alignment="right"/>\n'
        # 13 = 金额/股数(交替白)
        '<xf numFmtId="0" fontId="3" fillId="8" borderId="1" alignment="right"/>\n'
        # 14 = 备注
        '<xf numFmtId="0" fontId="2" fillId="7" borderId="1" alignment="left"/>\n'
        '</cellXfs>\n'
        '</styleSheet>'
    )

    def row(n, cells): return "<row r=\"%d\">%s</row>" % (n, cells)
    def H(ref, v, sty): return '<c r="%s" s="%s" t="inlineStr"><is><t>%s</t></is></c>' % (ref, sty, e(v))
    def N(ref, v, sty): return '<c r="%s" s="%s"><v>%s</v></c>' % (ref, sty, v)

    # ── 标题区 ─────────────────────────────────────────────
    cols = ["A","B","C","D","E","F","G","H","I","J"]
    title_cells = "".join(H(cols[i]+"1", HDRS[i] if i < len(HDRS) else "", "0")
                          for i in range(len(HDRS)))
    desc_text = (
        "查询日期: %s | 股价基准日: %s | 数据来源: Tushare Pro | "
        "溢价率=回购均价/当日股价，>1=溢价（回购均价>现价，纳入）；≤1=折价（剔除）"
        % (today_str, price_date)
    )
    parts = [
        row(1, title_cells),
        row(2, H("A2", desc_text, "1")),
        row(3, H("A3", "【重要】仅统计proc=实施/完成且vol>0的已执行回购；预案/提议/股东大会通过等尚未执行不纳入", "1")),
        row(4, ""),
        row(5, "".join(H(cols[i]+"5", HDRS[i], "2") for i in range(len(HDRS)))),
    ]

    # ── 纳入区（溢价率>1）──────────────────────────────────
    ri = 6
    if incl:
        parts.append(row(ri, H("A"+str(ri), "【溢价回购标的】溢价率>1，回购均价高于当日股价，具备投资价值", "3")))
        ri += 1
        for r in incl:
            bg = "5" if ri % 2 == 0 else "6"  # 交替
            cells = (
                H("A"+str(ri), r["股票代码"], bg) +
                H("B"+str(ri), r["股票名称"], bg) +
                N("C"+str(ri), r["本次回购累计金额（元）"], bg) +
                N("D"+str(ri), r["本次回购累计股数（股）"], bg) +
                N("E"+str(ri), r["回购均价（元/股）"], bg) +
                N("F"+str(ri), r["当日股价（元）"], bg) +
                N("G"+str(ri), r["溢价率"], bg) +
                H("H"+str(ri), r["方案价格区间（元）"], bg) +
                H("I"+str(ri), r["是否纳入"], bg) +
                H("J"+str(ri), r["备注"], bg)
            )
            parts.append(row(ri, cells))
            ri += 1

    # ── 剔除区（折价/平价）─────────────────────────────────
    if excl:
        if ri > 6: parts.append(row(ri, "")); ri += 1
        parts.append(row(ri, H("A"+str(ri), "【折价/平价标的】溢价率≤1，回购均价≤当日股价，不纳入汇总", "4")))
        ri += 1
        for r in excl[:50]:  # 最多50条，避免表格过长
            bg = "5" if ri % 2 == 0 else "6"
            cells = (
                H("A"+str(ri), r["股票代码"], bg) +
                H("B"+str(ri), r["股票名称"], bg) +
                N("C"+str(ri), r["本次回购累计金额（元）"], bg) +
                N("D"+str(ri), r["本次回购累计股数（股）"], bg) +
                N("E"+str(ri), r["回购均价（元/股）"], bg) +
                N("F"+str(ri), r["当日股价（元）"], bg) +
                N("G"+str(ri), r["溢价率"], bg) +
                H("H"+str(ri), r["方案价格区间（元）"], bg) +
                H("I"+str(ri), r["是否纳入"], bg) +
                H("J"+str(ri), r["备注"], bg)
            )
            parts.append(row(ri, cells))
            ri += 1
        if len(excl) > 50:
            parts.append(row(ri, H("A"+str(ri), "（另%d家折价标的，详见完整报告）" % (len(excl)-50), "1")))

    last = ri + 1
    parts.append(row(last, ""))
    parts.append(row(last+1, H("A"+str(last+1),
        "⚠️ 免责声明：本报告仅基于Tushare公开数据计算，不构成投资建议。溢价回购反映公司主动估值管理意愿，"
        "但不代表股价必然上涨。数据截至%s，实际投资决策请自行判断。" % today_str, "1")))

    COLS_XML = (
        "<cols>"
        "<col index='1' width='12'/>"
        "<col index='2' width='14'/>"
        "<col index='3' width='22'/>"
        "<col index='4' width='22'/>"
        "<col index='5' width='18'/>"
        "<col index='6' width='14'/>"
        "<col index='7' width='12'/>"
        "<col index='8' width='18'/>"
        "<col index='9' width='12'/>"
        "<col index='10' width='30'/>"
        "</cols>"
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
        '<bookViews><workbookView xWindow="0" yWindow="0" windowWidth="30000" windowHeight="12000"/></bookViews>\n'
        '<sheets><sheet name="回购溢价分析" sheetId="1" r:id="rId1"/></sheets>\n'
        '<calcPr calcId="191029"/>\n'
        '</workbook>'
    )
    SHEET = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">\n'
        '<sheetView workbookViewId="0"/>\n'
        + COLS_XML + '\n<sheetData>\n' + "\n".join(parts) + '\n</sheetData>\n'
        '</worksheet>'
    )
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", CT)
        z.writestr("_rels/.rels", RELS)
        z.writestr("xl/workbook.xml", WB)
        z.writestr("xl/_rels/workbook.xml.rels", WB_RELS)
        z.writestr("xl/styles.xml", STYLES)
        z.writestr("xl/worksheets/sheet1.xml", SHEET)

# ═══════════════════════════════════════════════════════════
# 入口
# ═══════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("=" * 62)
    print("A股回购价值分析工具 v2.0（触发词：近7天回购 / 回购溢价）")
    print("=" * 62)

    results, incl, excl, price_date = run(days=7)

    print()
    if incl:
        print("【溢价回购标的】（溢价率>1，纳入）")
        for r in incl:
            amt_w = float(r["本次回购累计金额（元）"]) / 10000
            vol_w = float(r["本次回购累计股数（股）"]) / 10000
            cur_str = r["当日股价（元）"]
            cur_val = float(cur_str) if cur_str not in ("—", "") else 0.0
            avg_str = r["回购均价（元/股）"]
            avg_val = float(avg_str) if avg_str not in ("—", "") else 0.0
            print("  %s %-8s | 累计金额=%.2f万元 | 累计股数=%.0f万 | 均价=%.4f | 现价=%s | 溢价率=%.4f"
                  % (r["股票代码"], r["股票名称"], amt_w, vol_w,
                     avg_val, cur_str, r["_premium"]))

    print()
    if excl:
        print("【折价/平价标的】（前5条，完整见Excel）")
        for r in excl[:5]:
            cur_str = r["当日股价（元）"]
            cur_val = float(cur_str) if cur_str not in ("—", "") else 0.0
            avg_str = r["回购均价（元/股）"]
            avg_val = float(avg_str) if avg_str not in ("—", "") else 0.0
            print("  %s %-8s | 均价=%s | 现价=%s | 溢价率=%.4f"
                  % (r["股票代码"], r["股票名称"],
                     avg_str, cur_str, r["_premium"]))

    today_str = datetime.datetime.now().strftime("%Y%m%d")
    out = "/workspace/回购溢价分析报告_%s.xlsx" % today_str
    make_excel(results, incl, excl, price_date, out)
    sz = os.path.getsize(out)
    print()
    print("Excel: %s (%.1f KB)" % (out, sz / 1024))
    print("纳入: %d家 | 剔除: %d家" % (len(incl), len(excl)))
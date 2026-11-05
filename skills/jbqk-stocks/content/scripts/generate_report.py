#!/usr/bin/env python3
"""
基本情况选股报告生成器
用法：
  python3 generate_report.py --test
  python3 generate_report.py --type fundamental --date 20260427 \
      --stocks "朗姿股份,和而泰" --codes "002612,002402"
"""
import zipfile, os, sys, getopt

N = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"

# ---- XML building helpers ----
def cell_xml(tx, bg="FFFFFF", bd=False, fg=None, ct=True):
    jc = "center" if ct else "left"
    b = "<w:b/>" if bd else ""
    c = f'<w:color w:val="{fg}"/>' if fg else ""
    rpr = f"<w:rPr>{b}<w:sz w:val='36'/>{c}</w:rPr>"
    r = f"<w:r {rpr}><w:t xml:space='preserve'>{tx}</w:t></w:r>"
    p = f"<w:p><w:pPr><w:jc w:val='{jc}'/></w:pPr>{r}</w:p>"
    shd = f'<w:shd w:val="clear" w:color="auto" w:fill="{bg}"/>'
    tcpr = f"<w:tcPr>{shd}</w:tcPr>"
    return f"<w:tc>{tcpr}{p}</w:tc>"

def hc(tx, bg="1F497D"): return cell_xml(tx, bg, True, "FFFFFF")
def cr(tx, bg="FFFFFF", fg=None): return cell_xml(tx, bg, False, fg)

def build_tbl(hdrs, rows, hbc="1F497D"):
    n = len(hdrs)
    g = "".join(f'<w:gridCol xmlns:w="{N}"/>' for _ in range(n))
    tr = f"<w:tr>{''.join(hc(h, hbc) for h in hdrs)}</w:tr>"
    for rd in rows:
        tr += "".join(cr(str(v)) for v in rd)
    bdr = (f'<w:tblBorders>'
           f'<w:top w:val="single" w:sz="8" w:space="0" w:color="{hbc}"/>'
           f'<w:left w:val="single" w:sz="8" w:space="0" w:color="{hbc}"/>'
           f'<w:bottom w:val="single" w:sz="8" w:space="0" w:color="{hbc}"/>'
           f'<w:right w:val="single" w:sz="8" w:space="0" w:color="{hbc}"/>'
           f'<w:insideH w:val="single" w:sz="4" w:space="0" w:color="AAAAAA"/>'
           f'<w:insideV w:val="single" w:sz="4" w:space="0" w:color="AAAAAA"/>'
           f'</w:tblBorders>')
    tpr = f"<w:tblPr><w:tblW w:type='pct' w:w='5000'/>{bdr}</w:tblPr>"
    return f'<w:tbl xmlns:w="{N}">{tpr}<w:tblGrid/>{g}{tr}</w:tbl>'

def P(tx, bd=False, fg=None, sz=21, ct=False):
    b = "<w:b/>" if bd else ""
    c = f'<w:color w:val="{fg}"/>' if fg else ""
    rpr = f"<w:rPr>{b}<w:sz w:val='{sz*2}'/>{c}</w:rPr>"
    r = f"<w:r {rpr}><w:t xml:space='preserve'>{tx}</w:t></w:r>"
    jc = "<w:jc w:val='center'/>" if ct else ""
    ppr = f"<w:pPr>{jc}</w:pPr>" if ct else "<w:pPr/>"
    return f"<w:p xmlns:w='{N}'>{ppr}{r}</w:p>"

def SP(): return f"<w:p xmlns:w='{N}'><w:pPr><w:spacing w:before='200' w:after='200'/></w:pPr></w:p>"

def H(tx, fg="1F497D", sz=28):
    rpr = f"<w:rPr><w:b/><w:sz w:val='{sz*2}'/><w:color w:val='{fg}'/></w:rPr>"
    r = f"<w:r {rpr}><w:t xml:space='preserve'>{tx}</w:t></w:r>"
    return f"<w:p xmlns:w='{N}'>{r}</w:p>"

def rank_list(items, key, reverse=True):
    """排序后返回 {name: rank}"""
    def val(x):
        v = x.get(key, 0)
        return v if isinstance(v, (int, float)) and v is not None else -9999
    sorted_items = sorted(items, key=val, reverse=reverse)
    return {item["name"]: i+1 for i, item in enumerate(sorted_items)}

def to_score(rank, n):
    return max(1, n - rank + 1)

def bg_score(total):
    if total >= 4.0: return "C6EFCE"
    if total >= 3.0: return "FFEB9C"
    if total >= 2.0: return "FFF2CC"
    return "FFC7CE"

def gen_fundamental_report(date_str, stocks):
    B = []
    n = len(stocks)

    # ---- 封面 ----
    B.append(P("基本面选股分析报告", True, "1F497D", 32, True))
    B.append(P(f"报告日期：{date_str}  |  基本情况选股系统", False, "666666", 12, True))
    B.append(P("评级维度：盈利能力25% | 成长性25% | 估值20% | ROE10% | 毛利率10% | 股息率10%", False, "888888", 9, True))
    B.append(SP())

    # ---- 第1步：原始数据 ----
    B.append(H("一、原始基本面数据一览"))
    B.append(SP())
    hdrs1 = ["股票","代码","股价","PE","PB","营收增速","净利润增速","毛利率","ROE","股息率"]
    rows1 = []
    for s in stocks:
        rows1.append([
            s.get("name","?"), s.get("code","?"), s.get("price","——"),
            s.get("pe","——"), s.get("pb","——"),
            s.get("revenue_yoy","——"), s.get("profit_yoy","——"),
            s.get("gross_margin","——"), s.get("roe","——"),
            s.get("dividend_yield","——"),
        ])
    B.append(build_tbl(hdrs1, rows1, "2B579A"))
    B.append(SP())

    # ---- 第2步：六维度评分 ----
    B.append(H("二、六维度基本面评分（5分制，5=最优）"))
    B.append(SP())
    B.append(P("5分=最优（该维度第1名），1分=最差（该维度末名）。空值/负值自动最低分。", False, "888888", 9))
    B.append(SP())

    profit_ranks = rank_list(stocks, "profit_yoy", reverse=True)
    revenue_ranks = rank_list(stocks, "revenue_yoy", reverse=True)
    pe_ranks = rank_list(stocks, "pe", reverse=False)  # 低PE优
    roe_ranks = rank_list(stocks, "roe", reverse=True)
    gm_ranks = rank_list(stocks, "gross_margin", reverse=True)
    dy_ranks = rank_list(stocks, "dividend_yield", reverse=True)

    hdrs2 = ["股票","盈利\n(净利润增速)","成长\n(营收增速)","估值\n(低PE优)","ROE","毛利率","股息率","综合"]
    total_rows = []
    for s in stocks:
        nm = s["name"]
        ps = to_score(profit_ranks.get(nm, n), n)
        rs = to_score(revenue_ranks.get(nm, n), n)
        es = to_score(pe_ranks.get(nm, n), n)
        os_ = to_score(roe_ranks.get(nm, n), n)
        gs = to_score(gm_ranks.get(nm, n), n)
        ds = to_score(dy_ranks.get(nm, n), n)
        total = ps*0.25 + rs*0.25 + es*0.20 + os_*0.10 + gs*0.10 + ds*0.10
        total_rows.append((nm, total, ps, rs, es, os_, gs, ds))

    total_rows.sort(key=lambda x: x[1], reverse=True)
    for rank, (nm, total, ps, rs, es, os_, gs, ds) in enumerate(total_rows, 1):
        medal = "🥇" if rank==1 else "🥈" if rank==2 else "🥉" if rank==3 else f" {rank} "
        bg = bg_score(total)
        B.append(build_tbl(hdrs2, [[f"{medal}{nm}", f"{ps}分", f"{rs}分", f"{es}分", f"{os_}分", f"{gs}分", f"{ds}分",
                                    {"v": f"{total:.2f}分", "bg": bg}]], "375623"))
    B.append(SP())

    # ---- 第3步：综合排名 ----
    B.append(H("三、综合排名结论"))
    B.append(SP())
    for rank, (nm, total, *_) in enumerate(total_rows, 1):
        tag = "强烈推荐" if rank==1 else "值得关注" if rank==2 else "谨慎关注" if rank==3 else "一般"
        color = "375623" if rank==1 else "2B579A" if rank==2 else "855700" if rank==3 else "666666"
        medal = "🥇" if rank==1 else "🥈" if rank==2 else "🥉" if rank==3 else f"  {rank}"
        B.append(P(f"{medal} 第{rank}名：{nm}（综合{total:.2f}分）— {tag}", True, color, 12, True))
    B.append(SP())

    # ---- 第4步：各维度冠军 ----
    try:
        bp = max(stocks, key=lambda x: x.get("profit_yoy", -9999) if isinstance(x.get("profit_yoy"),(int,float)) else -9999)
        br = max(stocks, key=lambda x: x.get("revenue_yoy", -9999) if isinstance(x.get("revenue_yoy"),(int,float)) else -9999)
        bpe = min(stocks, key=lambda x: x.get("pe", 99999) if isinstance(x.get("pe"),(int,float)) else 99999)
        broe = max(stocks, key=lambda x: x.get("roe", -9999) if isinstance(x.get("roe"),(int,float)) else -9999)
        bgm = max(stocks, key=lambda x: x.get("gross_margin", -9999) if isinstance(x.get("gross_margin"),(int,float)) else -9999)
        bdy = max(stocks, key=lambda x: x.get("dividend_yield", -9999) if isinstance(x.get("dividend_yield"),(int,float)) else -9999)
    except:
        bp = br = bpe = broe = bgm = bdy = stocks[0] if stocks else {}

    dim_data = [
        ["净利润增速王", f"{bp['name']}（净利润{bp.get('profit_yoy','?')}）"],
        ["营收增速王", f"{br['name']}（营收增速{br.get('revenue_yoy','?')}）"],
        ["低估值王", f"{bpe['name']}（PE={bpe.get('pe','?')}倍）"],
        ["ROE王", f"{broe['name']}（ROE={broe.get('roe','?')}）"],
        ["毛利率王", f"{bgm['name']}（{bgm.get('gross_margin','?')}）"],
        ["股息率王", f"{bdy['name']}（{bdy.get('dividend_yield','?')}）"],
    ]
    B.append(build_tbl(["维度","最优股票（数据）"], dim_data, "2B579A"))
    B.append(SP())

    # ---- 第5步：风险提示 ----
    B.append(H("四、风险提示", "C00000", 14))
    for r in [
        "本报告仅供研究参考，不构成投资建议。",
        "基本面评分基于历史财务数据，不代表未来表现。",
        "市场有风险，投资需谨慎，请以实盘为准。",
    ]:
        B.append(P("⚠ "+r, False, "C00000", 9))
    B.append(SP())
    B.append(P(f"报告生成：{date_str}  |  基本情况选股系统  |  仅供研究参考", False, "888888", 8, True))

    return "\n".join(B)


def save_doc(body, out_path):
    sect = f'<w:sectPr xmlns:w="{N}"><w:pgSz w:w="16838" w:h="11906"/><w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440"/></w:sectPr>'
    doc = f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:document xmlns:w="{N}"><w:body>{body}{sect}</w:body></w:document>'
    styles = f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:styles xmlns:w="{N}"><w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/><w:rPr><w:rFonts w:ascii="宋体" w:hAnsi="宋体"/><w:sz w:val="21"/></w:rPr></w:style></w:styles>'
    rels = f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/></Relationships>'
    ct = f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/><Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/></Types>'
    root = f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>'
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", ct)
        z.writestr("_rels/.rels", root)
        z.writestr("word/document.xml", doc)
        z.writestr("word/styles.xml", styles)
        z.writestr("word/_rels/document.xml.rels", rels)
    print(f"Saved: {out_path}, Size: {os.path.getsize(out_path):,} bytes")


if __name__ == "__main__":
    opts = dict(getopt.getopt(sys.argv[1:], "", ["type=","date=","stocks=","codes=","test"])[0])
    date_str = opts.get("--date", "20260427")
    out_dir = "/workspace/股票分析"

    if "--test" in opts:
        stocks = [
            {"name":"朗姿股份","code":"002612","price":"约17元","pe":7.5,"pb":2.3,"revenue_yoy":"+2.85%","profit_yoy":"+283.41%","gross_margin":"59.65%","roe":"29.38%","dividend_yield":"约7%"},
            {"name":"和而泰","code":"002402","price":"约31.5元","pe":47,"pb":5.1,"revenue_yoy":"+17.47%","profit_yoy":"+75%","gross_margin":"约25%","roe":"12.14%","dividend_yield":"约0.3%"},
            {"name":"兴齐眼药","code":"300573","price":"约68元","pe":65,"pb":8.2,"revenue_yoy":"+15%","profit_yoy":"+45%","gross_margin":"约72%","roe":"18%","dividend_yield":"约0.5%"},
            {"name":"宝光股份","code":"600379","price":"约12元","pe":35,"pb":2.8,"revenue_yoy":"+5%","profit_yoy":"+8%","gross_margin":"约28%","roe":"6%","dividend_yield":"约2%"},
            {"name":"凯大催化","code":"920974","price":"约7.6元","pe":22,"pb":1.9,"revenue_yoy":"+3%","profit_yoy":"-5%","gross_margin":"约18%","roe":"4%","dividend_yield":"约1%"},
        ]
        body = gen_fundamental_report(date_str, stocks)
        save_doc(body, f"{out_dir}/基本情况选股报告_测试_{date_str}.docx")
        print("Test done.")
    else:
        stocks_raw = opts.get("--stocks", "")
        codes_raw = opts.get("--codes", "")
        names = [s.strip() for s in stocks_raw.split(",") if s.strip()]
        codes = [c.strip() for c in codes_raw.split(",") if c.strip()] if codes_raw else ["--"]*len(names)
        stocks = [{"name": n, "code": c} for n, c in zip(names, codes)]
        body = gen_fundamental_report(date_str, stocks)
        save_doc(body, f"{out_dir}/基本情况选股分析报告_{date_str}.docx")
        print("Done.")
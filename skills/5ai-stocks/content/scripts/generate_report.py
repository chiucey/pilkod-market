#!/usr/bin/env python3
"""
股票分析报告生成器
支持两类报告：
  1. 5AI选股分析报告（5只股票横向对比，综合排名）
  2. 个股深度分析报告（单只股票全面分析，含投资建议）
用法：
  python3 generate_report.py --type 5ai      --date 20260427 --stocks "朗姿股份,和而泰,..."
  python3 generate_report.py --type single  --date 20260427 --stock "朗姿股份" --code "002612"
  python3 generate_report.py --test
"""
import zipfile, os, sys, getopt, re

N = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"

def Tbl(hdrs, rows, hbc="1F497D"):
    def cell(tx, bg="FFFFFF", bd=False, fg=None):
        b = "<w:b/>" if bd else ""
        c = f'<w:color w:val="{fg}"/>' if fg else ""
        rpr = f"<w:rPr>{b}<w:sz w:val='36'/>{c}</w:rPr>"
        r = f"<w:r {rpr}><w:t xml:space='preserve'>{tx}</w:t></w:r>"
        p = f"<w:p><w:pPr><w:jc w:val='center'/></w:pPr>{r}</w:p>"
        shd = f'<w:shd w:val="clear" w:color="auto" w:fill="{bg}"/>'
        tcpr = f"<w:tcPr>{shd}</w:tcPr>"
        return f"<w:tc>{tcpr}{p}</w:tc>"
    def hc(tx, bg=hbc): return cell(tx, bg, True, "FFFFFF")
    def cr(tx, bg="FFFFFF", fg=None): return cell(tx, bg, False, fg)
    n = len(hdrs)
    g = "".join(f'<w:gridCol xmlns:w="{N}"/>' for _ in range(n))
    tr = f"<w:tr>{''.join(hc(h) for h in hdrs)}</w:tr>"
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


# ============================================================
# 报告类型一：5AI选股分析报告（多股横向对比）
# ============================================================
def gen_5ai_report(date_str, stocks_data):
    """生成5AI选股分析报告
    stocks_data: list of dicts [{name, code, price, chg, vol, amount, highlight}, ...]
    """
    B = []
    B.append(P(f"5AI超短线选股分析报告", True, "1F497D", 32, True))
    B.append(P(f"报告日期：{date_str}  |  5AI联合分析系统", False, "666666", 12, True))
    B.append(SP())
    B.append(Tbl(["股票简称","代码","最新价","涨跌幅","成交量","成交额","基本面要点"],
        [[s["name"], s["code"], s["price"], s["chg"], s["vol"], s["amount"], s["highlight"]]
         for s in stocks_data],
        "2B579A"))
    B.append(SP())
    B.append(H("一、五路AI独立评分"))
    B.append(SP())
    B.append(P("5个AI（DeepSeek/Kimi/豆包AI/千问/MiniMax）对每只股票6个维度独立评分（1-10分）：", False, "444444", 10))
    B.append(P("维度权重：基本面10% | 趋势强度20% | 资金动能20% | 交易情绪30% | 技术指标10% | 风险10%", False, "375623", 10))
    B.append(SP())
    B.append(H("二、三种方法综合排名"))
    B.append(SP())
    B.append(P("方法一（平均分法）：5AI加权得分均值，高分优先", False, "444444", 10))
    B.append(P("方法二（积分法）：每AI对5股排名，第1名=1分，汇总后总分最低最优", False, "444444", 10))
    B.append(P("方法三（投票法）：每AI前2名各1票，票数高优先", False, "444444", 10))
    B.append(SP())
    B.append(H("三、综合排名结果"))
    B.append(SP())
    B.append(P("【此处由调用脚本填充AI评分结果】", False, "888888", 10))
    B.append(SP())
    B.append(H("四、风险提示", "C00000", 14))
    for r in [
        "本报告仅供研究参考，不构成投资建议。",
        "超短线持仓1-3天，最大止损4%，最大止盈7%。",
        "市场有风险，投资需谨慎。",
    ]:
        B.append(P("⚠ "+r, False, "C00000", 9))
    B.append(P(f"报告生成：{date_str}  |  5AI联合分析系统  |  仅供研究参考", False, "888888", 8, True))
    return "\n".join(B)


# ============================================================
# 报告类型二：个股深度分析报告
# ============================================================
def gen_single_report(date_str, stock_name, code, price_data, fin_data,
                     biz_data, cap_data, risk_data, view_data, rec_data):
    """生成个股深度分析报告
    各参数均为 dict，格式如下：
      price_data: {price, chg, market_cap, pe, pb, dividend, business, industry}
      fin_data:   {revenue, revenue_yoy, profit, profit_yoy, gp, net_margin, roe, eps, cash_flow}
      biz_data:   list of [板块, 数据, 说明]
      cap_data:   list of [指标, 数据, 说明]
      risk_data:  list of [风险类型, 描述, 等级]
      view_data:  list of [机构, 评级, 观点]
      rec_data:   {short, short_plan, mid, mid_plan, long, long_plan, hold}
    """
    B = []

    # 封面
    B.append(P(f"{stock_name}（{code}）投资价值深度分析报告", True, "1F497D", 28, True))
    B.append(P(f"报告日期：{date_str}  |  数据来源：东方财富/公司公告（最新）", False, "888888", 10, True))
    B.append(SP())

    # 概要卡片
    rows = [
        ["股票简称", stock_name],
        ["股票代码", code],
        ["最新股价", price_data.get("price","——")],
        ["总市值", price_data.get("market_cap","——")],
        ["市盈率 PE", price_data.get("pe","——")],
        ["市净率 PB", price_data.get("pb","——")],
        ["股息率", price_data.get("dividend","——")],
        ["业务定位", price_data.get("business","——")],
        ["行业地位", price_data.get("industry","——")],
    ]
    B.append(Tbl(["项目","内容"], rows, "2B579A"))
    B.append(SP())

    # 一、基本面概览
    B.append(H("一、基本面综合评估一览表"))
    B.append(SP())
    rows = [[k]+list(v) for k,v in fin_data.items()]
    if rows:
        max_cols = max(len(r) for r in rows)
        hdrs = ["指标"] + ["数值"]*(max_cols-1)
        B.append(Tbl(hdrs, rows, "375623"))
    B.append(SP())

    # 二、业务亮点
    if biz_data:
        B.append(H("二、业务亮点及行业地位"))
        B.append(SP())
        B.append(Tbl(["业务/亮点","核心数据","说明"], biz_data, "2B579A"))
        B.append(SP())

    # 三、资金面
    if cap_data:
        B.append(H("三、资金面及交易情绪"))
        B.append(SP())
        B.append(Tbl(["日期/指标","价格/数据","说明"], cap_data, "375623"))
        B.append(SP())

    # 四、核心风险
    if risk_data:
        B.append(H("四、核心风险点", "C00000", 24))
        B.append(SP())
        B.append(Tbl(["风险类型","风险描述","等级"], risk_data, "C00000"))
        B.append(SP())

    # 五、机构观点
    if view_data:
        B.append(H("五、机构观点汇总"))
        B.append(SP())
        B.append(Tbl(["机构","评级/观点","核心逻辑"], view_data, "375623"))
        B.append(SP())

    # 六、投资建议
    B.append(H("六、综合投资建议", "1F497D", 28))
    B.append(SP())

    if rec_data.get("short"):
        B.append(P("【超短线/短期操作】（1天-3个月）", True, "375623", 13))
        B.append(P(rec_data["short"], True, "375623", 11))
        for line in rec_data.get("short_plan", []):
            B.append(P(line, False, "444444", 10))
        B.append(SP())

    if rec_data.get("mid"):
        B.append(P("【中期操作建议】（3-12个月）", True, "2B579A", 13))
        B.append(P(rec_data["mid"], True, "2B579A", 11))
        for line in rec_data.get("mid_plan", []):
            B.append(P(line, False, "444444", 10))
        B.append(SP())

    if rec_data.get("long"):
        B.append(P("【长期投资建议】（1年以上）", True, "888888", 13))
        B.append(P(rec_data["long"], True, "888888", 11))
        for line in rec_data.get("long_plan", []):
            B.append(P(line, False, "444444", 10))
        B.append(SP())

    if rec_data.get("hold"):
        B.append(P("【已持有者操作建议】", True, "375623", 13))
        B.append(P(rec_data["hold"], False, "444444", 10))
        B.append(SP())

    # 七、风险提示
    B.append(H("七、风险提示", "C00000", 14))
    for r in [
        "本报告仅供研究参考，不构成投资建议，投资者据此操作风险自担。",
        "市场有风险，投资需谨慎，股价波动受多重因素影响。",
        f"本报告数据截至{date_str}，请以实盘为准。",
    ]:
        B.append(P("⚠ "+r, False, "C00000", 9))
    B.append(SP())
    B.append(P(f"报告生成：{date_str}  |  5AI联合分析系统  |  仅供研究参考", False, "888888", 8, True))

    return "\n".join(B)


def build_doc(body):
    sect = f'<w:sectPr xmlns:w="{N}"><w:pgSz w:w="16838" w:h="11906"/><w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440"/></w:sectPr>'
    doc = f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:document xmlns:w="{N}"><w:body>{body}{sect}</w:body></w:document>'
    styles = f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:styles xmlns:w="{N}"><w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/><w:rPr><w:rFonts w:ascii="宋体" w:hAnsi="宋体"/><w:sz w:val="21"/></w:rPr></w:style></w:styles>'
    rels = f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/></Relationships>'
    ct = f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/><Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/></Types>'
    root = f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>'
    return {"[Content_Types].xml": ct, "_rels/.rels": root,
            "word/document.xml": doc, "word/styles.xml": styles,
            "word/_rels/document.xml.rels": rels}

def save_doc(body, out_path):
    files = build_doc(body)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as z:
        for k, v in files.items():
            z.writestr(k, v)
    print(f"Saved: {out_path}, Size: {os.path.getsize(out_path):,} bytes")


if __name__ == "__main__":
    opts, args = getopt.getopt(sys.argv[1:], "", ["type=", "date=", "stock=", "code=", "stocks=", "test"])
    opts = dict(opts)

    stype = opts.get("--type", "5ai")
    date_str = opts.get("--date", "20260427")
    out_dir = "/workspace/股票分析"

    if "--test" in opts or stype == "test":
        # 测试模式：生成朗姿股份示例报告
        fin_data = {
            "营业收入": ["60.03亿元", "58.37亿元", "+2.85%", "稳健"],
            "归母净利润": ["9.99亿元", "2.61亿元", "+283.41%", "爆发"],
            "扣非净利润": ["2.69亿元", "2.17亿元", "+23.77%", "主业稳定"],
            "毛利率": ["59.65%", "58.30%", "+1.35pct", "高水平"],
            "净利率": ["17.44%", "4.47%", "+12.97pct", "大幅提升"],
            "EPS": ["2.26元", "0.59元", "+283%", "业绩爆发"],
            "ROE": ["29.38%", "7.71%", "+21.67pct", "显著"],
        }
        biz_data = [
            ["时尚女装", "19.99亿（33.3%）", "+3.85%，毛利率64.63%"],
            ["医疗美容", "30.26亿（50.4%）", "首次超越女装，医美龙头"],
            ["绿色婴童", "——", "稳健补充业务线"],
            ["线上渠道", "占女装48.58%", "抖音/天猫/京东行业前列"],
        ]
        cap_data = [
            ["4月22日", "约17.40-17.56元", "+0.52%，向上突破"],
            ["4月24日", "16.93元", "-0.35%，小幅调整"],
            ["近期支撑", "约16元", "200日均线附近"],
            ["近期压力", "约17.50-18元", "前期高点"],
        ]
        risk_data = [
            ["投资收益波动", "9.99亿净利含7.3亿投资收益，扣非仅2.69亿", "高"],
            ["增速放缓", "总营收仅+2.85%，医美扩张待观察", "中"],
            ["医美监管", "行业政策趋严，合规成本上升", "中"],
            ["历史减持", "实控人曾有减持记录（2021年）", "中"],
        ]
        view_data = [
            ["申万宏源", "看好", "化妆品医美龙头，受益消费复苏"],
            ["东方财富研究", "买入/增持", "高分红提升配置价值"],
            ["公司管理层", "积极", "1+N医美连锁战略推进"],
        ]
        rec_data = {
            "short": "★★★★☆ 推荐关注",
            "short_plan": ["16.0-16.5元建仓，目标18-19元，止损15.0元"],
            "mid": "★★★★☆ 值得关注",
            "mid_plan": ["除权后15-16元建仓，目标20-22元，止损14元"],
            "long": "★★★★★ 强烈推荐",
            "long_plan": ["高股息+医美龙头，长线持有3年预期50%+"],
            "hold": "继续持有，享受10派12元分红，止损15元",
        }
        body = gen_single_report(
            date_str, "朗姿股份", "002612.SZ",
            {"price": "约16.80-17.56元（4月22-24日）", "pe": "约7-8倍", "dividend": "10派12元（股息率7%+）",
             "business": "时尚女装+医美+婴童", "industry": "A股医美机构龙头之一"},
            fin_data, biz_data, cap_data, risk_data, view_data, rec_data
        )
        out = f"{out_dir}/测试报告_示例_{date_str}.docx"
        save_doc(body, out)
        print("Test report generated.")

    if stype == "single":
        stock = opts.get("--stock", "未知股票")
        code = opts.get("--code", "——")
        body = gen_single_report(date_str, stock, code,
            {"price": "——", "business": "——", "industry": "——"},
            {}, [], [], [], [], {})
        fname = f"{stock}{code}_投资价值分析报告_{date_str}.docx"
        out = f"{out_dir}/{fname}"
        save_doc(body, out)
        print(f"Single report: {out}")

    elif stype == "5ai":
        stocks_str = opts.get("--stocks", "")
        stocks = [s.strip() for s in stocks_str.split(",") if s.strip()]
        data = [{"name": s, "code": "——", "price": "——", "chg": "——",
                 "vol": "——", "amount": "——", "highlight": "——"} for s in stocks]
        body = gen_5ai_report(date_str, data)
        out = f"{out_dir}/5AI超短线选股分析报告_{date_str}.docx"
        save_doc(body, out)
        print(f"5AI report: {out}")
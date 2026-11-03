#!/usr/bin/env python3
"""
⚖️ 法律文书起草助手 · Legal Brief Drafter
根据案件素材自动生成结构化法律文书

支持：答辩状 / 代理词 / 上诉状 / 反驳意见书 / 质证意见 / 法律意见书
"""

import sys
import json
import re
from datetime import date

# ─────────────────────────────────────────────
#  工具函数
# ─────────────────────────────────────────────

def print_header():
    header = f"""
╔══════════════════════════════════════════════════════╗
║   ⚖️  法律文书起草助手  Legal Brief Drafter        ║
║   适用场景：民事 · 行政 · 消费者 · 合同纠纷           ║
╚══════════════════════════════════════════════════════╝
    """
    print(header)

def confidence_badge(level: str) -> str:
    badges = {
        "high":   "🟢 高置信度",
        "medium": "🟡 中置信度",
        "low":    "🔴 低置信度",
    }
    return badges.get(level, level)

def today() -> str:
    return date.today().strftime("%Y年%m月%d日")

def wrap_text(text: str, width: int = 80) -> str:
    """简单文字自动换行"""
    lines = []
    for para in text.split("\n"):
        if not para.strip():
            lines.append("")
            continue
        words = para.split()
        cur = ""
        for w in words:
            if len(cur) + len(w) + 1 <= width:
                cur = (cur + " " + w).strip()
            else:
                if cur:
                    lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)
    return "\n".join(lines)

# ─────────────────────────────────────────────
#  核心生成函数
# ─────────────────────────────────────────────

def extract_facts(evidence: str) -> dict:
    """解析证据材料"""
    result = {"support": [], "attack": [], "neutral": []}
    if not evidence:
        return result
    lines = [l.strip() for l in evidence.split("\n") if l.strip()]
    for line in lines:
        if re.search(r"(转账|付款|签字|盖章|原件|真实)", line):
            result["support"].append(line)
        elif re.search(r"(自制|无签字|无日期|复印件|无法核实)", line):
            result["attack"].append(line)
        else:
            result["neutral"].append(line)
    return result


def generate_objection(doc_type: str, user_input: dict) -> str:
    """生成答辩状"""
    name = user_input.get("答辩人", "答辩人（姓名）")
    pname = user_input.get("原告", "原告")
    court = user_input.get("法院", "XXXX人民法院")
    case_no = user_input.get("案号", "（XXXX）X字第XXX号")
    claims = user_input.get("对方诉求", "无")
    defense = user_input.get("答辩立场", "无")
    facts = user_input.get("事实依据", "")
    law = user_input.get("适用法条", "")
    auth_facts = extract_facts(facts)

    obj = f"""
民事答辩状

{court}
{case_no}

答辩人：{name}
委托代理人：XXXX 律师（联系方式）

答辩人因与{pname}（案号：{case_no}）一案，现提出答辩如下：

一、关于对方诉讼请求的答辩

对方诉称：{claims}

答辩人认为：{defense}

二、关于事实依据的答辩

经答辩人核实本案相关证据材料，事实情况如下：

"""

    if auth_facts["support"]:
        obj += "（一）有利于答辩人的证据：\n"
        for i, ev in enumerate(auth_facts["support"], 1):
            obj += f"  {i}. {ev}\n"
        obj += "\n"

    if auth_facts["attack"]:
        obj += "（二）对对方证据的质疑：\n"
        for i, ev in enumerate(auth_facts["attack"], 1):
            obj += f"  {i}. {ev}　→ 证据三性存疑，不应被采信\n"
        obj += "\n"

    if law:
        obj += f"""三、关于法律适用的答辩

本案应适用的法律条文如下：

{law}

综上所述，答辩人认为对方诉讼请求缺乏事实和法律依据，恳请贵院依法驳回其全部诉讼请求。

此致

{court}

答辩人（签名）：__________
{today()}
"""
    return obj


def generate_agent_opinion(doc_type: str, user_input: dict) -> str:
    """生成代理词"""
    role = user_input.get("代理人身份", "代理人")
    court = user_input.get("法院", "XXXX人民法院")
    case_no = user_input.get("案号", "（XXXX）X字第XXX号")
    case_summary = user_input.get("案件事实", "")
    legal_arg = user_input.get("法律论证", "")
    auth_facts = user_input.get("证据材料", "")
    evidence = extract_facts(auth_facts)

    opinion = f"""
{case_no}
{court}

代　理　词

{role}针对本案争议焦点，发表如下代理意见：

一、案件基本事实

{case_summary}

二、本案核心争议焦点分析

{legal_arg}

三、关于证据的认定意见

"""
    if evidence["support"]:
        opinion += "  原告提交的证据中，以下证据真实、合法、与本案关联，应予采信：\n"
        for ev in evidence["support"]:
            opinion += f"  ✅ {ev}\n"

    if evidence["attack"]:
        opinion += "\n  对方提交的证据存在重大瑕疵，不能成立：\n"
        for ev in evidence["attack"]:
            opinion += f"  ❌ {ev}\n"

    opinion += f"""
四、结论意见

基于上述事实与法律分析，{role}恳请贵院：
  1. 支持我方主要诉讼请求；
  2. 驳回对方缺乏事实依据的诉讼主张。

此致
{court}

{role}（签名）：__________
代理律师（签名）：__________
{today()}
"""
    return opinion


def generate_appeal(doc_type: str, user_input: dict) -> str:
    """生成上诉状"""
    appellant = user_input.get("上诉人", "上诉人")
    appellee = user_input.get("被上诉人", "被上诉人")
    court = user_input.get("原审法院", "XXXX人民法院")
    orig_case = user_input.get("原审案号", "（XXXX）X字第XXX号")
    judgment = user_input.get("原审判决内容", "")
    appeal_reason = user_input.get("上诉理由", "")
    new_facts = user_input.get("新事实证据", "")
    new_law = user_input.get("新法律依据", "")

    appeal = f"""
民事上诉状

上诉人：{appellant}
被上诉人：{appellee}
原审法院：{court}
原审案号：{orig_case}

上诉人因不服{court}{orig_case}号民事判决，现依法提出上诉。

一、上诉请求

1. 撤销{court}{orig_case}号判决第X项；
2. 依法改判支持上诉人的全部诉讼请求（或：发回重审）。

二、原审判决认定的事实

原审认定：{judgment}

三、上诉理由

{appeal_reason}

四、新提交的证据与事实

{new_facts}

五、适用的新法律依据

{new_law}

综上所述，原审判决认定事实不清、适用法律错误，上诉人恳请二审法院依法支持上诉请求。

此致
XXXX中级人民法院

上诉人（签名）：__________
{today()}
"""
    return appeal


def generate_rebuttal(doc_type: str, user_input: dict) -> str:
    """生成反驳意见书"""
    target = user_input.get("被反驳方", "对方")
    court = user_input.get("法院", "XXXX人民法院")
    case_no = user_input.get("案号", "（XXXX）X字第XXX号")
    their_point = user_input.get("对方论点", "")
    rebuttal = user_input.get("反驳论点", "")
    rebuttal_law = user_input.get("反驳法律依据", "")

    text = f"""
反驳意见书

{court}　{case_no}

针对{target}在本案中提出的以下论点，答辩人提出正式反驳：

───────────────────────────────────
对方主张：{their_point}
───────────────────────────────────

对此，答辩人逐一反驳如下：

{rebuttal}

法律依据：{rebuttal_law}

综上，对方的上述论点不能成立，恳请合议庭在事实认定和法律适用时不予采纳。

答辩人（签名）：__________
{today()}
"""
    return text


def generate_evidence_opinion(doc_type: str, user_input: dict) -> str:
    """生成质证意见"""
    court = user_input.get("法院", "XXXX人民法院")
    case_no = user_input.get("案号", "（XXXX）X字第XXX号")
    evidence_list = user_input.get("证据清单", "")

    lines = [l.strip() for l in evidence_list.split("\n") if l.strip()]

    result = f"""
质证意见书

{court}　{case_no}

就对方提交的证据，答辩人发表如下质证意见：

"""
    for i, line in enumerate(lines, 1):
        ev_desc = line
        # 判断证据类型
        if re.search(r"(转账记录|银行流水|回单)", ev_desc):
            verdict = "认可真实性、合法性、关联性"
            badge = "🟢"
        elif re.search(r"(合同|协议|原件)", ev_desc):
            verdict = "认可真实性；对合法性、证明目的保留意见"
            badge = "🟡"
        elif re.search(r"(证人|证言)", ev_desc):
            verdict = "真实性无法确认；证人有利害关系，证明力弱"
            badge = "🔴"
        elif re.search(r"(复印件|照片|截图)", ev_desc):
            verdict = "真实性不认可，无法与原件核实"
            badge = "🔴"
        elif re.search(r"(自制|手写|无签字)", ev_desc):
            verdict = "真实性存疑；无第三方印证"
            badge = "🔴"
        else:
            verdict = "视具体内容判断"
            badge = "🟡"

        result += f"{i}. {ev_desc}\n   质证意见：{badge} {verdict}\n\n"

    result += f"""
以上质证意见，恳请合议庭在事实认定时予以充分考虑。

质证人（签名）：__________
{today()}
"""
    return result


def generate_legal_opinion(doc_type: str, user_input: dict) -> str:
    """生成法律意见书"""
    client = user_input.get("委托人", "委托人")
    case = user_input.get("案件概要", "")
    issues = user_input.get("法律问题", "")
    analysis = user_input.get("法律分析", "")
    conclusion = user_input.get("结论建议", "")
    law_basis = user_input.get("法律依据", "")

    text = f"""
法律意见书

致：{client}

一、委托事项

{case}

二、涉及的法律问题

{issues}

三、法律分析与论证

{analysis}

四、法律依据

{law_basis}

五、结论与建议

{conclusion}

附注：本意见书仅供委托人参考，不构成正式法律服务。

经办律师（签名）：__________
{today()}
"""
    return text


# ─────────────────────────────────────────────
#  主控逻辑
# ─────────────────────────────────────────────

DOC_GENERATORS = {
    "答辩状":          generate_objection,
    "代理词":          generate_agent_opinion,
    "上诉状":          generate_appeal,
    "反驳意见书":      generate_rebuttal,
    "质证意见":        generate_evidence_opinion,
    "法律意见书":      generate_legal_opinion,
}

DOC_DESCRIPTIONS = {
    "答辩状":    "被告针对原告起诉状的正式书面回应",
    "代理词":    "诉讼代理人在庭审中代表当事人发表的综合法律意见",
    "上诉状":    "当事人不服一审判决，向二审法院提出的正式上诉文件",
    "反驳意见书":"针对对方单个或多个论点的逐一书面反驳",
    "质证意见":  "针对证据真实性、合法性、关联性的逐条审查意见",
    "法律意见书":"综合法律问题分析报告（含结论与建议）",
}

SAMPLE_CASES = {
    "民事合同纠纷": {
        "文书类型": "答辩状",
        "答辩人": "XXX（公司/个人）",
        "原告": "XXX",
        "法院": "XX市XX区人民法院",
        "案号": "（2026）X民初XXXX号",
        "对方诉求": "要求支付货款人民币XX万元及利息",
        "答辩立场": "已全额付款，有银行转账记录为证",
        "事实依据": "转账记录（2026年X月X日）\n合同原件（双方签字盖章）\n对方出具的收据",
        "适用法条": "《民法典》第565条（合同解除）\n《民法典》第566条（解除后果）\n《民事诉讼法》第67条（举证责任）",
    },
    "行政诉讼": {
        "文书类型": "答辩状",
        "答辩人": "XXX（行政机关）",
        "原告": "XXX（行政相对人）",
        "法院": "XX市XX区人民法院",
        "案号": "（2026）X行初XXXX号",
        "对方诉求": "撤销我单位作出的XX号行政处罚决定",
        "答辩立场": "行政处罚决定事实清楚、程序合法、适用法律正确",
        "事实依据": "行政处罚决定书（原件）\n调查笔录\n相关法规依据",
        "适用法条": "《行政处罚法》第54条\n《行政诉讼法》第69条（驳回诉讼请求）",
    },
    "消费者维权": {
        "文书类型": "质证意见",
        "法院": "XX市XX区人民法院",
        "案号": "（2026）X民初XXXX号",
        "证据清单": "购物发票（真实）\n产品实物照片（真实、合法）\n厂家出具的检测报告（自制，真实性存疑）\n录音资料（未经对方同意，合法性存疑）",
    },
}


def show_help():
    print("""
⚖️ 法律文书起草助手 — 使用说明

【文书类型】

  答辩状     被告对原告起诉的正式书面回应
  代理词     诉讼代理人庭审综合法律意见
  上诉状     不服一审判决的正式上诉文件
  反驳意见书  针对对方论点的逐条反驳
  质证意见   证据三性逐条审查意见
  法律意见书 综合法律问题分析报告

【输入格式示例】

  文书类型：答辩状
  法院：XX市XX区人民法院
  案号：（2026）X民初1234号
  答辩人：张三
  原告：李四
  对方诉求：要求支付货款20万元及利息
  答辩立场：已全额付款，有银行转账记录为证
  事实依据：银行转账记录（2026-01-15）
           合同原件（双方签字盖章）
  适用法条：民法典第565、566条

【使用方式】

  python3 legal_brief.py                # 交互模式（引导输入）
  python3 legal_brief.py --case 民事合同纠纷  # 使用示例案件快速生成
  python3 legal_brief.py --sample 答辩状   # 查看答辩状填写说明
  python3 legal_brief.py --types        # 显示支持的文书类型

【直接传入参数】

  python3 legal_brief.py \
    --type 答辩状 \
    --input '{"答辩人":"张三","法院":"北京海淀区法院","对方诉求":"支付货款"}'
""")

def show_types():
    print("\n支持的文书类型：\n")
    for k, v in DOC_DESCRIPTIONS.items():
        print(f"  📄 {k}：{v}")
    print()

def show_sample(case_type: str):
    if case_type in SAMPLE_CASES:
        print(f"\n📋 示例案件 [{case_type}]：\n")
        for k, v in SAMPLE_CASES[case_type].items():
            print(f"  {k}：{v}")
        print()
    else:
        print(f"未知案件类型，可选：{', '.join(SAMPLE_CASES.keys())}")


def main():
    args = sys.argv[1:]

    if "--help" in args or "-h" in args:
        show_help()
        return

    if "--types" in args:
        show_types()
        return

    if "--case" in args:
        idx = args.index("--case")
        case_key = args[idx + 1] if idx + 1 < len(args) else ""
        show_sample(case_key)
        return

    if "--sample" in args:
        idx = args.index("--sample")
        stype = args[idx + 1] if idx + 1 < len(args) else ""
        if stype in DOC_GENERATORS:
            print(f"\n📄 {stype} 填写说明：\n")
            print(f"  {DOC_DESCRIPTIONS.get(stype, '')}\n")
        else:
            print("可选文书类型：", "、".join(DOC_GENERATORS.keys()))
        return

    # 交互式引导
    print_header()
    print("请告诉我您需要起草什么类型的法律文书。\n")
    print("支持的类型：", "、".join(DOC_GENERATORS.keys()))
    print("\n也可以直接粘贴以下格式的内容：\n")
    print("  文书类型：答辩状")
    print("  法院：XX市XX区人民法院")
    print("  案号：（2026）X民初1234号")
    print("  对方诉求：...")
    print("  答辩立场：...（或对应内容）\n")

    doc_type = input("请输入文书类型（如：答辩状）：").strip()
    if not doc_type:
        print("未输入文书类型，退出。")
        return

    if doc_type not in DOC_GENERATORS:
        print(f"不支持的类型。可用：{', '.join(DOC_GENERATORS.keys())}")
        return

    print(f"\n请提供案件信息（直接粘贴内容，回车后按 Ctrl+D 结束）：\n")
    print("格式示例：")
    print("  法院：XX市XX区人民法院")
    print("  对方诉求：...")
    print("  答辩立场：...（或对应内容）\n")

    lines = []
    try:
        while True:
            line = input()
            lines.append(line)
    except EOFError:
        pass

    user_text = "\n".join(lines)

    # 简单键值提取
    user_dict = {}
    for line in lines:
        if ":" in line:
            idx = line.index(":")
            k = line[:idx].strip()
            v = line[idx+1:].strip()
            if k and v:
                user_dict[k] = v

    # 生成文书
    gen = DOC_GENERATORS[doc_type]
    result = gen(doc_type, user_dict)

    # 输出
    print("\n" + "="*60)
    print(f"📄 生成完毕：《{doc_type}》")
    print("="*60)
    print(wrap_text(result))
    print()
    print("⚠️  注意：本文件为参考文本，引用的法条请以现行有效版本为准。")
    print("⚠️  重要案件请咨询执业律师。")

if __name__ == "__main__":
    main()

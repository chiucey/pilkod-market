#!/usr/bin/env python3
"""
⚖️ 九章 · 标准法律文书模板库
Standard Legal Document Templates for Chinese Courts

覆盖：民事起诉状 / 答辩状 / 上诉状 / 反诉状 / 申请书 / 律师函 / 法律意见书
"""

import sys
from datetime import date

TODAY = date.today().strftime("%Y年%m月%d日")

# ─────────────────────────────────────────────
# 工具函数
# ─────────────────────────────────────────────

def hr(char="─", length=60):
    return char * length

def section(title):
    return f"\n{hr()}【{title}】{hr()}\n"

# ─────────────────────────────────────────────
# 民事起诉状
# ─────────────────────────────────────────────

def civil_complaint(data: dict) -> str:
    court = data.get("法院", "XXXX人民法院")
    case_no = data.get("案号提示", "（XXXX）X民初XXXX号")
    p = data.get("原告", "原告（姓名/名称）")
    p_id = data.get("原告身份证/统一社会信用代码", "XXXXXXXX")
    p_addr = data.get("原告地址", "XXXX")
    p_tel = data.get("原告电话", "XXXXXXXX")
    d = data.get("被告", "被告（姓名/名称）")
    d_id = data.get("被告身份证/统一社会信用代码", "XXXXXXXX")
    d_addr = data.get("被告地址", "XXXX")
    d_tel = data.get("被告电话", "XXXXXXXX")
    claim_amount = data.get("诉讼请求金额", "XX万元")
    claim_items = data.get("诉讼请求明细", "1. 判令被告支付……")
    facts = data.get("事实与理由", "……")
    evidence = data.get("证据清单", "1. 证据一……")
    law_basis = data.get("法律依据", "《中华人民共和国民法典》第XXX条")

    return f"""民事起诉状

{court}：
{case_no}

原告：{p}
住所地（户籍地）：{p_addr}
联系方式：{p_tel}
法定代表人/负责人：__________　　职务：__________

被告：{d}
住所地（户籍地）：{d_addr}
联系方式：{d_tel}
法定代表人/负责人：__________　　职务：__________

诉讼请求

一、判令被告向原告支付【{claim_amount}】，其中包括：
　　{claim_items}

二、本案诉讼费用由被告承担。

事实与理由

{facts}

证据清单

{evidence}

法律依据

{law_basis}

综上所述，被告的行为严重侵害了原告的合法权益，原告为维护自身合法权益，依据《中华人民共和国民事诉讼法》第122条之规定，特向贵院提起诉讼，请依法支持原告的诉讼请求。

此致

{court}

起诉人（原告）（签名或盖章）：__________
{today()}
附件：{evidence.split(chr(10))[0] if evidence else '证据材料若干'}　共___份
"""

# ─────────────────────────────────────────────
# 民事答辩状
# ─────────────────────────────────────────────

def civil_answer(data: dict) -> str:
    court = data.get("法院", "XXXX人民法院")
    case_no = data.get("案号", "（XXXX）X民初XXXX号")
    d = data.get("答辩人（被告）", "被告（姓名/名称）")
    d_addr = data.get("被告地址", "XXXX")
    p = data.get("原告", "原告（姓名/名称）")
    defense_req = data.get("答辩请求", "请求驳回原告的全部诉讼请求")
    defense_reasons = data.get("答辩理由", "……")
    facts = data.get("事实依据", "……")
    evidence = data.get("证据清单", "1. ……")
    law_basis = data.get("法律依据", "《民法典》第XXX条")

    return f"""民事答辩状

{court}：
{case_no}

答辩人（被告）：{d}
住所地：{d_addr}
联系方式：__________

委托代理人：__________（律师/公民）　电话：__________

原告（被答辩）：{p}

答辩请求

{ defense_req }

答辩理由

{ defense_reasons }

事实与证据

{ facts }

证据清单

{ evidence }

法律依据

{ law_basis }

综上所述，原告的诉讼请求缺乏事实和法律依据，恳请贵院依法驳回原告的全部诉讼请求。

此致

{court}

答辩人（被告）（签名或盖章）：__________
{today()}
"""

# ─────────────────────────────────────────────
# 民事上诉状
# ─────────────────────────────────────────────

def civil_appeal(data: dict) -> str:
    court = data.get("上诉法院", "XXXX中级人民法院")
    orig_court = data.get("原审法院", "XXXX人民法院")
    orig_case = data.get("原审案号", "（XXXX）X民初XXXX号")
    appellant = data.get("上诉人", "上诉人（姓名/名称）")
    appellant_addr = data.get("上诉人地址", "XXXX")
    appellee = data.get("被上诉人", "被上诉人（姓名/名称）")
    orig_judgment = data.get("原审判决内容", "……")
    appeal_req = data.get("上诉请求", "1. 撤销XXXX判决第X项……")
    appeal_reasons = data.get("上诉理由", "……")
    new_facts = data.get("新事实证据", "……")
    law_basis = data.get("法律依据", "《民事诉讼法》第XXX条")

    return f"""民事上诉状

{court}：
案号：（XXXX）X民终XXXX号

上诉人：{appellant}
住所地：{appellant_addr}
联系方式：__________
委托代理人：__________　电话：__________

被上诉人：{ appellee}
住所地：__________

上诉人因与被上诉人{orig_court}{orig_case}一案，不服该院年月日作出的民事判决，现依法提出上诉。

上诉请求

{ appeal_req }

一、原审判决认定的内容

原审认定：{ orig_judgment }

二、上诉理由

{ appeal_reasons }

三、新提交的证据

{ new_facts }

四、法律依据

{ law_basis }

综上所述，原审判决存在认定事实不清、适用法律错误的情形，恳请二审法院依法支持上诉请求。

此致

{court}

上诉人（签名或盖章）：__________
{today()}
"""

# ─────────────────────────────────────────────
# 反诉状
# ─────────────────────────────────────────────

def counter_claim(data: dict) -> str:
    court = data.get("法院", "XXXX人民法院")
    case_no = data.get("案号", "（XXXX）X民初XXXX号")
    counter_p = data.get("反诉人（被告）", "反诉人（姓名/名称）")
    orig_p = data.get("原诉原告", "原诉原告")
    claim_req = data.get("反诉请求", "1. 判令反诉被告……")
    facts = data.get("事实与理由", "……")
    evidence = data.get("证据清单", "1. ……")
    law_basis = data.get("法律依据", "《民法典》第XXX条")

    return f"""反诉状

{court}：
{case_no}

反诉人（本案被告）：{counter_p}
住所地：__________
委托代理人：__________　电话：__________

被反诉人（原诉原告）：{orig_p}

反诉请求

{ claim_req }

事实与理由

{ facts }

证据清单

{ evidence }

法律依据

{ law_basis }

综上所述，反诉人特向贵院提起反诉，请依法受理并支持反诉请求。

此致

{court}

反诉人（签名或盖章）：__________
{today()}
"""

# ─────────────────────────────────────────────
# 行政起诉状
# ─────────────────────────────────────────────

def admin_complaint(data: dict) -> str:
    court = data.get("法院", "XXXX人民法院")
    plaintiff = data.get("原告（行政相对人）", "原告（姓名/名称）")
    plaintiff_addr = data.get("原告地址", "XXXX")
    defendant = data.get("被告（行政机关）", "被告（机关名称）")
    defendant_addr = data.get("被告地址", "XXXX")
    admin_act = data.get("行政行为", "XXXX号《XXXX决定书》")
    act_date = data.get("行政行为日期", "XXXX年XX月XX日")
    claim_req = data.get("诉讼请求", "1. 撤销……")
    facts = data.get("事实与理由", "……")
    evidence = data.get("证据清单", "1. ……")
    law_basis = data.get("法律依据", "《行政诉讼法》第XX条")

    return f"""行政起诉状

{court}：

原告：{plaintiff}
住所地：{plaintiff_addr}
联系方式：__________

被告：{defendant}
住所地：{defendant_addr}
法定代表人：__________　职务：__________

诉讼请求

{ claim_req }

事实与理由

一、原告主体资格

原告系行政行为的相对人，与被诉行政行为有利害关系。

二、案件事实

{ facts }

三、被诉行政行为违法性分析

被诉行政行为：{admin_act}（落款日期：{act_date}）

该行政行为存在以下违法之处：
　1. 程序违法：……
　2. 事实认定错误：……
　3. 适用法律错误：……

证据清单

{ evidence }

法律依据

{ law_basis }

综上所述，原告为维护自身合法权益，依据《中华人民共和国行政诉讼法》第49条之规定，特向贵院提起诉讼，请依法支持原告的诉讼请求。

此致

{court}

起诉人（原告）（签名或盖章）：__________
{today()}
"""

# ─────────────────────────────────────────────
# 劳动仲裁申请书
# ─────────────────────────────────────────────

def labor_application(data: dict) -> str:
    arbitration_comm = data.get("仲裁委员会", "XX市XX区劳动人事争议仲裁委员会")
    applicant = data.get("申请人", "申请人（劳动者）")
    applicant_addr = data.get("申请人地址", "XXXX")
    applicant_tel = data.get("申请人电话", "XXXXXXXX")
    respondent = data.get("被申请人", "被申请人（单位）")
    respondent_addr = data.get("被申请人地址", "XXXX")
    claim_req = data.get("仲裁请求", "1. 支付违法解除劳动合同赔偿金XX元……")
    facts = data.get("事实与理由", "……")
    evidence = data.get("证据清单", "1. 劳动合同……")
    law_basis = data.get("法律依据", "《劳动争议调解仲裁法》第XX条")

    return f"""劳动争议仲裁申请书

{arbitration_comm}：

申请人：{applicant}
住所（通讯地址）：{applicant_addr}
联系电话：{applicant_tel}

被申请人：{respondent}
住所（通讯地址）：{respondent_addr}
法定代表人：__________　职务：__________

仲裁请求

{ claim_req }

事实与理由

{ facts }

证据清单

{ evidence }

法律依据

{ law_basis }

综上所述，申请人依据相关法律规定，特向贵委提出仲裁申请，请依法支持申请人的仲裁请求。

此致

{arbitration_comm}

申请人（签名）：__________
{today()}
"""

# ─────────────────────────────────────────────
# 申请书类（通用）
# ─────────────────────────────────────────────

def application_letter(data: dict) -> str:
    court = data.get("法院", "XXXX人民法院")
    case_no = data.get("案号", "（XXXX）X民初XXXX号")
    app_type = data.get("申请事项", "证据保全")
    applicant = data.get("申请人", "申请人（姓名/名称）")
    facts = data.get("事实与理由", "……")
    evidence = data.get("证据清单", "1. ……")
    law_basis = data.get("法律依据", "《民事诉讼法》第XX条")

    return f"""申请书

{case_no}

{ court }：

申请人：{applicant}

申请事项

{ app_type }

事实与理由

{ facts }

证据清单

{ evidence }

法律依据

{ law_basis }

综上所述，申请人恳请贵院依法审查并支持申请人的申请。

此致

{ court }

申请人（签名或盖章）：__________
{today()}
"""

# ─────────────────────────────────────────────
# 律师函（催告函）
# ─────────────────────────────────────────────

def lawyer_letter(data: dict) -> str:
    letter_type = data.get("函件类型", "催告函")
    sender_lawfirm = data.get("发出律所", "XXXX律师事务所")
    recipient = data.get("收函方", "XXXX公司/先生/女士")
    recipient_addr = data.get("收函方地址", "XXXX")
    ref_matter = data.get("涉及事项", "……")
    letter_content = data.get("函件内容", "……")
    deadline = data.get("期限要求", "收函之日起XX日内")
    lawfirm = data.get("律所名称", "XXXX律师事务所")
    lawyer = data.get("承办律师", "XXXX")
    lawyer_tel = data.get("律师电话", "XXXXXXXX")

    content_lines = letter_content.strip().split("\n")
    content_block = "\n".join(f"　{line}" for line in content_lines if line.strip())

    return f"""{sender_lawfirm}
电话：{lawyer_tel}

{'='*55}
　律师函
{'='*55}

编号：（XXXX）XX函字第XXX号
发函日期：{TODAY}

收函方：{recipient}
通讯地址：{recipient_addr}

关于：{ref_matter}

{recipient}：

本所接受【委托人（姓名/名称）】的委托，指派{lawyer}律师就上述事项向贵方正式函告如下：

{content_block}

请贵方于 {deadline} 前就上述事项作出正式书面回应。

如贵方未能按期回应或妥善处理，本所将依委托人之申请，依法采取诉讼等一切必要法律措施，由此产生的一切法律后果均由贵方承担。

特此函告。

{lawfirm}
承办律师：{lawyer}
联系电话：{lawyer_tel}
联系地址：__________
{today()}

附：本函一式两份，本所留存一份，收函方一份。

---
本律师函不构成正式法律意见，仅为法律事务沟通函件。
"""

# ─────────────────────────────────────────────
# 法律意见书
# ─────────────────────────────────────────────

def legal_opinion(data: dict) -> str:
    client = data.get("委托人", "委托人（姓名/名称）")
    matter = data.get("法律事项", "……")
    questions = data.get("法律问题", "1. ……")
    analysis = data.get("法律分析", "……")
    conclusion = data.get("结论建议", "……")
    law_basis = data.get("法律依据", "《……法》第XX条")
    lawfirm = data.get("出具律所", "XXXX律师事务所")
    lawyer = data.get("承办律师", "XXXX")
    lawyer_tel = data.get("律师电话", "XXXXXXXX")

    return f"""法律意见书

编号：（XXXX）XX意见字第XXX号
出具日期：{TODAY()}

委托人：{client}
法律事项：{matter}

一、涉及的法律问题

{ questions }

二、法律分析与论证

{ analysis }

三、法律依据

{ law_basis }

四、结论与建议

{ conclusion }

附注

1. 本意见书仅依据委托人提供的材料出具，材料真实性由委托人负责。
2. 本意见书仅供委托人参考，不构成正式法律服务承诺。
3. 重要法律事务请咨询承办律师。

{ lawfirm }
承办律师（签名）：__________
联系方式：{ lawyer_tel }
{today()}
"""

# ─────────────────────────────────────────────
# 主控逻辑
# ─────────────────────────────────────────────

TEMPLATES = {
    "民事起诉状":     {"fn": civil_complaint,     "desc": "原告向法院提起民事诉讼"},
    "答辩状":         {"fn": civil_answer,        "desc": "被告针对起诉状的正式书面回应"},
    "上诉状":         {"fn": civil_appeal,        "desc": "当事人不服一审判决上诉至二审"},
    "反诉状":         {"fn": counter_claim,       "desc": "被告在本诉中提出独立反诉请求"},
    "行政起诉状":     {"fn": admin_complaint,      "desc": "公民/法人针对行政行为提起诉讼"},
    "劳动仲裁申请书": {"fn": labor_application,    "desc": "劳动者向仲裁委申请劳动仲裁"},
    "申请书":         {"fn": application_letter,   "desc": "通用申请书（证据保全/财产保全/鉴定等）"},
    "律师函":         {"fn": lawyer_letter,        "desc": "律师名义发出的催告函/律师函"},
    "法律意见书":     {"fn": legal_opinion,        "desc": "综合法律问题分析报告"},
}

def show_list():
    print("\n" + "="*55)
    print("⚖️  九章 · 标准法律文书模板库")
    print("="*55)
    print(f"\n支持的文书类型（共 {len(TEMPLATES)} 种）：\n")
    for i, (name, info) in enumerate(TEMPLATES.items(), 1):
        print(f"  {i:2d}. {name:<12s}  {info['desc']}")
    print()

def show_usage():
    print("""
用法：

  python3 zhang_legal.py                          # 交互模式
  python3 zhang_legal.py --list                  # 查看所有模板
  python3 zhang_legal.py --show <文书名称>        # 查看某类文书说明
  python3 zhang_legal.py --sample <文书名称>      # 查看填写示例

在 OpenClaw 中：直接描述案件，我自动调用对应模板生成文书。
""")

if __name__ == "__main__":
    args = sys.argv[1:]
    if "--list" in args:
        show_list()
    elif "--help" in args or "-h" in args:
        show_usage()
    elif "--show" in args:
        idx = args.index("--show")
        name = args[idx+1] if idx+1 < len(args) else ""
        if name in TEMPLATES:
            print(f"\n📄 {name}：{TEMPLATES[name]['desc']}\n")
        else:
            print("未知文书类型")
    else:
        show_list()
        show_usage()

"""
市场监督管理投诉举报案件处理核心脚本
基于《市场监督管理投诉举报处理办法》（总局令第121号，2026年4月15日施行）
"""

from typing import Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum


class CaseType(Enum):
    COMPLAINT = "complaint"
    REPORT = "report"


class CaseStatus(Enum):
    DRAFT = "draft"
    PENDING_REVIEW = "pending"
    ACCEPTED = "accepted"
    NOT_ACCEPTED = "not_accepted"
    MEDIATION = "mediation"
    MEDIATION_ENDED = "ended"
    INVESTIGATION = "investigation"
    TRANSFERRED = "transferred"


@dataclass
class ReviewResult:
    is_acceptable: bool
    not_acceptance_reasons: list = field(default_factory=list)
    missing_materials: list = field(default_factory=list)
    risk_warnings: list = field(default_factory=list)
    suggestions: list = field(default_factory=list)


@dataclass
class JurisdictionResult:
    has_jurisdiction: bool
    primary_authority: str = ""
    alternative_authorities: list = field(default_factory=list)
    legal_basis: list = field(default_factory=list)
    notes: str = ""


@dataclass
class DeadlineResult:
    acceptance_deadline: str = ""
    mediation_deadline: str = ""
    investigation_deadline: str = ""
    termination_notice_deadline: str = ""


@dataclass
class ComplianceResult:
    is_compliant: bool
    issues: list = field(default_factory=list)
    overall_assessment: str = ""


@dataclass
class ViolationAnalysis:
    violation_type: str
    suspected_articles: list = field(default_factory=list)
    evidence_sufficiency: str = "partial"
    report_suggestion: str = ""
    additional_clues: list = field(default_factory=list)


# ── 工作日计算 ──
def _add_workdays(dt: datetime, days: int) -> datetime:
    current = dt
    added = 0
    while added < days:
        current += timedelta(days=1)
        if current.weekday() < 5:
            added += 1
    return current


# ── 投诉材料审查 ──
def review_complaint(materials: dict) -> ReviewResult:
    result = ReviewResult(is_acceptable=True)
    complainant = materials.get("complainant_info", {})
    respondent = materials.get("respondent_info", {})

    # 身份信息
    for f in ["name", "phone", "address"]:
        if not complainant.get(f):
            result.missing_materials.append(f"投诉人{f}未提供（第10条第1项）")
    if not respondent.get("name"):
        result.missing_materials.append("被投诉人名称/姓名未提供（第10条第2项）")
    if not respondent.get("address"):
        result.missing_materials.append("被投诉人地址未提供（第10条第2项）")
    if not materials.get("claim"):
        result.missing_materials.append("投诉请求为空（第10条第3项）")
    if not materials.get("facts"):
        result.missing_materials.append("事实依据为空（第10条第3项）")

    # 委托代理
    if materials.get("entrustment"):
        e = materials["entrustment"]
        if not e.get("authorization_letter"):
            result.missing_materials.append("未提供授权委托书原件（第11条）")
        if not e.get("agent_id"):
            result.missing_materials.append("未提供受托人身份证明（第11条）")

    # 证据风险
    if not materials.get("evidence"):
        result.risk_warnings.append("未提供任何证据材料，可能影响受理和调解效果")

    # 消费目的
    if not materials.get("consumer_purpose", True):
        result.is_acceptable = False
        result.not_acceptance_reasons.append("【第16条第3项】不是为生活消费需要购买、使用商品或接受服务")

    # 时效
    dispute_date = materials.get("dispute_date")
    if dispute_date:
        try:
            d = datetime.strptime(dispute_date, "%Y-%m-%d")
            if (datetime.now() - d).days > 365 * 3:
                result.is_acceptable = False
                result.not_acceptance_reasons.append("【第16条第4项】知道或应当知道权益受损之日起已超过三年")
        except Exception:
            pass

    # 材料虚假/冒名
    if materials.get("fake_materials"):
        result.is_acceptable = False
        result.not_acceptance_reasons.append("【第16条第5项】提供虚假材料")
    if materials.get("impersonation"):
        result.is_acceptable = False
        result.not_acceptance_reasons.append("【第16条第6项】冒用他人名义")

    # 一事不再理
    if materials.get("already_processed"):
        result.is_acceptable = False
        result.not_acceptance_reasons.append("【第16条第2项】已由法院/仲裁/市场监管部门/消协受理或处理")

    # 建议
    if result.is_acceptable and not result.missing_materials:
        result.suggestions.append("材料齐备，可提交投诉")
        result.suggestions.append("建议通过全国12315平台或邮寄方式提交，保留提交凭证")
    elif result.is_acceptable:
        result.suggestions.append("材料基本齐备但有缺失项，建议补充完整后再提交")
    else:
        result.suggestions.append("存在不予受理情形，建议核实后重新准备材料或通过民事诉讼等途径维权")

    return result


# ── 投诉书生成 ──
def generate_complaint_letter(complainant: dict, respondent: dict, claim: str,
                             facts: str, evidence: list = None,
                             entrustment: dict = None) -> str:
    evidence = evidence or []
    now = datetime.now().strftime("%Y年%m月%d日")
    lines = ["【投诉书】", "", "一、投诉人基本信息",
             f"  姓名：{complainant.get('name','________')}",
             f"  联系电话：{complainant.get('phone','________')}",
             f"  通讯地址：{complainant.get('address','________')}"]
    if entrustment:
        lines += ["", "二、委托代理人",
                  f"  姓名：{entrustment.get('name','________')}",
                  "  授权委托书：已提供原件", "  代理人身份证：已提供"]
    lines += ["", "二、被投诉人基本信息",
              f"  名称（姓名）：{respondent.get('name','________')}",
              f"  统一社会信用代码/身份证号：{respondent.get('credit_code','________')}",
              f"  注册地址/住所地：{respondent.get('address','________')}",
              "", "三、具体的投诉请求", f"  {claim}", "",
              "四、消费者权益争议事实依据", f"  {facts}"]
    if evidence:
        lines += ["", "五、证据材料清单"]
        for i, e in enumerate(evidence, 1):
            lines.append(f"  {i}. {e}")
    lines += ["", "六、消费目的声明",
              "  本次购买商品/接受服务属于为生活消费需要购买、使用商品（或接受服务），",
              "  不是出于生产经营、投资等目的。",
              "  本人声明上述信息真实无误，如有虚假愿意承担相应法律责任。", "",
              f"  投诉人签名：{complainant.get('name','________')}",
              f"  日期：{now}"]
    return "\n".join(lines)


# ── 举报书生成 ──
def generate_report_letter(reporter: dict, respondent: dict, violation_type: str,
                           clues: list, evidence: list = None,
                           legal_basis: list = None, additional_notes: str = "") -> str:
    evidence = evidence or []
    legal_basis = legal_basis or []
    now = datetime.now().strftime("%Y年%m月%d日")
    lines = ["【举报书】", "", "一、举报人基本信息",
             f"  姓名/名称：{reporter.get('name','________')}",
             f"  联系电话：{reporter.get('phone','________')}",
             f"  通讯地址：{reporter.get('address','________')}", "",
             "二、被举报人基本信息",
             f"  名称（姓名）：{respondent.get('name','________')}",
             f"  统一社会信用代码/身份证号：{respondent.get('credit_code','________')}",
             f"  注册地址/住所地：{respondent.get('address','________')}", "",
             "三、涉嫌违法行为类型", f"  {violation_type}", "",
             "四、具体线索描述"]
    for i, c in enumerate(clues, 1):
        lines.append(f"  {i}. {c}")
    if legal_basis:
        lines += ["", "五、涉嫌违反的法律条款"]
        for lb in legal_basis:
            lines.append(f"  · {lb}")
    if evidence:
        lines += ["", "六、事实依据（证据材料）"]
        for i, e in enumerate(evidence, 1):
            lines.append(f"  {i}. {e}")
    if additional_notes:
        lines += ["", "七、其他补充说明", f"  {additional_notes}"]
    lines += ["", "八、举报请求",
              "  请求市场监督管理部门依法对被举报人的上述违法行为进行调查处理。", "",
              "九、承诺声明",
              "  本举报人声明，上述举报内容真实可靠，对举报内容的真实性负责。",
              "  如有虚假，愿承担相应法律责任。", "",
              f"  举报人签名：{reporter.get('name','________')}",
              f"  日期：{now}"]
    return "\n".join(lines)


# ── 管辖判断 ──
def determine_jurisdiction(case_type: str, respondent_type: str = "general",
                           platform_info: dict = None,
                           respondent_address: dict = None) -> JurisdictionResult:
    platform_info = platform_info or {}
    respondent_address = respondent_address or {}
    result = JurisdictionResult(has_jurisdiction=True)

    if case_type == "complaint":
        if respondent_type == "general":
            result.primary_authority = "被投诉人实际经营地或住所地县级市场监管部门"
            result.legal_basis = ["第13条第1款"]
        elif respondent_type == "platform":
            result.primary_authority = f"平台经营者住所地县级市场监管部门"
            result.legal_basis = ["第13条第2款"]
            result.notes = f"平台：{platform_info.get('name','名称')}，住所地：{platform_info.get('registered_address','以ICP备案为准')}"
        elif respondent_type == "platform_seller":
            displayed = respondent_address.get("displayed", "")
            contactable = respondent_address.get("actual_contactable", True)
            if displayed and contactable:
                result.primary_authority = "平台公示地址所在地县级市场监管部门"
                result.alternative_authorities = ["平台经营者住所地县级市场监管部门"]
                result.legal_basis = ["第13条第3款"]
                result.notes = "两部门均有管辖权，举报人可自主选择"
            else:
                result.primary_authority = "平台经营者住所地县级市场监管部门"
                result.legal_basis = ["第13条第3款但书"]
                result.notes = "平台内经营者未依法公示地址或公示地址无法联系，由平台经营者住所地县级市场监管部门处理"

    elif case_type == "report":
        if respondent_type == "general":
            result.primary_authority = "被举报行为发生地县级以上市场监管部门"
            result.legal_basis = ["第29条"]
        elif respondent_type == "platform":
            result.primary_authority = "平台经营者住所地县级以上市场监管部门"
            result.alternative_authorities = ["平台内经营者实际经营地县级以上市场监管部门"]
            result.legal_basis = ["第31条"]
        elif respondent_type == "platform_seller":
            result.primary_authority = "平台内经营者实际经营地县级以上市场监管部门"
            result.alternative_authorities = ["平台经营者住所地县级以上市场监管部门（先收到者处理）"]
            result.legal_basis = ["第31条第2款"]
        elif respondent_type == "advertiser":
            result.primary_authority = "广告发布者所在地市场监管部门"
            result.alternative_authorities = ["广告主所在地（互联网广告主自行发布时）", "广告经营者所在地（先收到者处理）"]
            result.legal_basis = ["第32条"]

    return result


# ── 时限计算 ──
def calculate_deadlines(case_type: str = "complaint",
                         acceptance_date: str = None,
                         clue_found_date: str = None) -> DeadlineResult:
    today = datetime.now()
    acc_dt = datetime.strptime(acceptance_date, "%Y-%m-%d") if acceptance_date else today
    result = DeadlineResult()
    result.acceptance_deadline = _add_workdays(acc_dt, 7).strftime("%Y-%m-%d")
    if case_type == "complaint":
        result.mediation_deadline = (acc_dt + timedelta(days=60)).strftime("%Y-%m-%d")
        result.termination_notice_deadline = _add_workdays(today, 7).strftime("%Y-%m-%d")
    if clue_found_date:
        clue_dt = datetime.strptime(clue_found_date, "%Y-%m-%d")
        result.investigation_deadline = _add_workdays(clue_dt, 15).strftime("%Y-%m-%d")
    return result


# ── 合规检查 ──
def check_procedure_compliance(case_type: str, timeline: dict,
                                procedures_followed: list = None) -> ComplianceResult:
    procedures_followed = procedures_followed or []
    result = ComplianceResult(is_compliant=True)
    received = timeline.get("received")
    acceptance = timeline.get("acceptance_decision")

    if received and acceptance:
        rec_dt = datetime.strptime(received, "%Y-%m-%d")
        acc_dt = datetime.strptime(acceptance, "%Y-%m-%d")
        workdays = sum(1 for i in range((acc_dt - rec_dt).days + 1)
                       if (rec_dt + timedelta(days=i)).weekday() < 5)
        if workdays > 7:
            result.is_compliant = False
            result.issues.append({
                "step": "受理决定", "requirement": "7个工作日内",
                "actual": f"{workdays}个工作日", "severity": "高",
                "suggestion": "超期受理决定可能导致程序违法，应立即补正手续"
            })
        else:
            result.issues.append({
                "step": "受理决定", "status": "合规",
                "detail": f"受理决定在收到后{workdays}个工作日内作出"
            })

    if timeline.get("suspected_crime_found"):
        result.issues.append({
            "step": "涉嫌犯罪移送",
            "status": "待移送",
            "detail": "发现涉嫌夹带、掉包、造假、敲诈勒索等行为，应依第42条移送公安机关"
        })

    result.overall_assessment = ("程序合规" if result.is_compliant
                                  else f"存在{sum(1 for i in result.issues if i.get('severity')=='高')}处高风险问题")
    return result


# ── 违法线索分析 ──
COMMON_VIOLATIONS = {
    "过期食品": {
        "articles": ["《食品安全法》第34条", "《食品安全法》第124条"],
        "evidence": ["购物小票/发票", "实物照片（显示生产日期/保质期）", "购物过程录像"]
    },
    "缺斤短两": {
        "articles": ["《计量法》第27条", "《侵害消费者权益行为处罚办法》第5条"],
        "evidence": ["购物凭证", "复秤照片/视频", "计量器具检定证书"]
    },
    "价格欺诈": {
        "articles": ["《价格法》第14条", "《禁止价格欺诈行为的规定》"],
        "evidence": ["标价照片/录像", "促销宣传截图", "实际结算小票"]
    },
    "虚假宣传": {
        "articles": ["《广告法》第28条", "《反不正当竞争法》第8条"],
        "evidence": ["宣传页面截图/录像", "产品实物照片"]
    },
    "拒绝开具发票": {
        "articles": ["《消费者权益保护法》第22条", "《发票管理办法》第20条"],
        "evidence": ["购物凭证", "要求开发票的聊天记录/电话录音", "已付款证明"]
    },
    "产品质量问题": {
        "articles": ["《产品质量法》第32条", "《消费者权益保护法》第23条"],
        "evidence": ["购物凭证", "产品实物及照片", "检测报告（如有）"]
    },
}


def analyze_violation(facts: list = None, case_context: str = "") -> ViolationAnalysis:
    facts = facts or []
    text = " ".join(facts) + " " + case_context

    for vtype, info in COMMON_VIOLATIONS.items():
        if vtype in text:
            return ViolationAnalysis(
                violation_type=vtype,
                suspected_articles=info["articles"],
                evidence_sufficiency="partial",
                report_suggestion=(
                    f"涉嫌{vtype}行为。\n证据要求：" +
                    "、".join(info["evidence"]) +
                    f"\n管辖部门：违法行为发生地县级市场监管部门"
                ),
                additional_clues=info["evidence"]
            )

    return ViolationAnalysis(
        violation_type="待定（需进一步分析）",
        suspected_articles=[],
        evidence_sufficiency="partial",
        report_suggestion="现有事实不足以确定违法类型，建议补充具体细节并收集购物凭证、发票等基础证据。",
        additional_clues=["补充具体时间、地点、经过", "收集购物凭证和发票", "明确经营者名称"]
    )

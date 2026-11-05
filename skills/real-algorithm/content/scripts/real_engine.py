"""
REAL 算法完整工作流 v2.0
观点-事实分离与可信度评估引擎（整合优化版）
适用场景：金融分析、研报解读、新闻验证、投资建议分析
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Any
from enum import Enum
import re
from datetime import datetime
import json
import uuid


# ==================== 枚举定义（统一规范） ====================

class InfoType(str, Enum):
    """信息分类"""
    FACT = "fact"           # 事实
    OPINION = "opinion"     # 观点
    UNKNOWN = "unknown"     # 待分类


class EvidenceType(str, Enum):
    """事实证据类型"""
    HUMAN_TESTIMONY = "human"      # 人证（陈述/证言）
    PHYSICAL_EVIDENCE = "physical" # 物证（客观记录/数据）
    UNKNOWN = "unknown"


class CredibilityLevel(str, Enum):
    """可信度等级（五级制）"""
    VERY_HIGH = "very_high"  # ≥0.85
    HIGH = "high"            # 0.70-0.85
    MEDIUM = "medium"        # 0.55-0.70
    LOW = "low"              # 0.35-0.55
    VERY_LOW = "very_low"    # <0.35

    @classmethod
    def from_score(cls, score: float) -> "CredibilityLevel":
        if score >= 0.85: return cls.VERY_HIGH
        if score >= 0.70: return cls.HIGH
        if score >= 0.55: return cls.MEDIUM
        if score >= 0.35: return cls.LOW
        return cls.VERY_LOW


class LogicQuality(str, Enum):
    """逻辑质量评估"""
    STRONG = "strong"          # 逻辑严密
    ACCEPTABLE = "acceptable"  # 逻辑可接受
    WEAK = "weak"              # 逻辑薄弱
    INVALID = "invalid"        # 逻辑谬误


class OpinionType(str, Enum):
    """观点类型"""
    PREDICTION = "prediction"      # 预测
    RECOMMENDATION = "recommendation"  # 投资建议
    JUDGMENT = "judgment"          # 市场判断
    INTERPRETATION = "interpretation" # 解读分析
    GENERAL = "general"            # 一般观点


# ==================== 数据模型 ====================

@dataclass
class Source:
    """信息来源"""
    name: str
    source_type: str
    url: Optional[str] = None
    publish_time: Optional[datetime] = None
    author: Optional[str] = None
    author_title: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "type": self.source_type,
            "author": self.author,
            "author_title": self.author_title,
            "url": self.url,
            "publish_time": self.publish_time.isoformat() if self.publish_time else None,
            "metadata": self.metadata
        }


@dataclass
class Fact:
    """事实节点"""
    fact_id: str
    content: str
    source: Source
    evidence_type: EvidenceType
    evidence_subtype: Optional[str] = None
    credibility_score: float = 0.0
    credibility_level: CredibilityLevel = CredibilityLevel.VERY_LOW
    verification_notes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            "fact_id": self.fact_id,
            "content": self.content,
            "source": self.source.to_dict(),
            "evidence_type": self.evidence_type.value,
            "evidence_subtype": self.evidence_subtype,
            "credibility": {
                "level": self.credibility_level.value,
                "score": round(self.credibility_score, 4)
            },
            "verification_notes": self.verification_notes
        }


@dataclass
class Opinion:
    """观点节点"""
    opinion_id: str
    content: str
    source: Source
    opinion_type: OpinionType = OpinionType.GENERAL
    has_factual_support: bool = False
    supporting_facts: List[Fact] = field(default_factory=list)
    supporting_fact_ids: List[str] = field(default_factory=list)
    logic_quality: LogicQuality = LogicQuality.INVALID
    logic_score: float = 0.0
    logic_analysis: str = ""
    credibility_score: float = 0.0
    credibility_level: CredibilityLevel = CredibilityLevel.VERY_LOW

    def to_dict(self) -> Dict:
        return {
            "opinion_id": self.opinion_id,
            "content": self.content,
            "source": self.source.to_dict(),
            "opinion_type": self.opinion_type.value,
            "has_factual_support": self.has_factual_support,
            "supporting_fact_ids": self.supporting_fact_ids,
            "logic_quality": {
                "level": self.logic_quality.value,
                "score": round(self.logic_score, 4),
                "analysis": self.logic_analysis
            },
            "credibility": {
                "level": self.credibility_level.value,
                "score": round(self.credibility_score, 4)
            }
        }


@dataclass
class SupportLink:
    """观点-事实支撑关系"""
    fact_id: str
    opinion_id: str
    support_score: float
    relation: str = "supports"


@dataclass
class AnalysisResult:
    """单条信息分析结果"""
    item_id: str
    original_text: str
    info_type: InfoType
    fact: Optional[Fact] = None
    opinion: Optional[Opinion] = None
    analysis_time: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict:
        result = {
            "item_id": self.item_id,
            "original_text": self.original_text,
            "type": self.info_type.value,
            "analysis_time": self.analysis_time.isoformat()
        }
        if self.fact:
            result["fact"] = self.fact.to_dict()
        if self.opinion:
            result["opinion"] = self.opinion.to_dict()
        return result


@dataclass
class BatchAnalysisReport:
    """批量分析报告"""
    facts: List[Fact] = field(default_factory=list)
    opinions: List[Opinion] = field(default_factory=list)
    links: List[SupportLink] = field(default_factory=list)
    summary: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return {
            "summary": self.summary,
            "facts": [f.to_dict() for f in self.facts],
            "opinions": [o.to_dict() for o in self.opinions],
            "links": [
                {"fact_id": l.fact_id, "opinion_id": l.opinion_id, "support_score": round(l.support_score, 4)}
                for l in self.links
            ]
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)


# ==================== 核心配置（可调参数） ====================

# 观点指示词（主观表达）
OPINION_INDICATORS = [
    "认为", "预计", "预测", "看好", "看空", "推荐", "建议",
    "判断", "评估", "觉得", "相信", "怀疑", "担心", "乐观",
    "悲观", "积极", "消极", "高估", "低估", "有潜力",
    "将", "可能", "或许", "大概", "应该", "值得", "具有",
    "标志", "意味着", "显示", "反映", "表明", "暗示"
]

# 事实指示词（客观陈述）
FACT_INDICATORS = [
    "营收", "利润", "净利润", "同比增长", "同比下降", "环比",
    "毛利率", "净利率", "ROE", "资产负债率", "现金流",
    "宣布", "发布", "披露", "报告显示", "数据显示", "公告",
    "签署", "收购", "合并", "投资", "融资", "分红", "减持",
    "获批", "通过", "完成", "达成", "实现"
]

# 事实数据模式
FACT_PATTERNS = [
    r'\d{4}年', r'\d+\.?\d*%', r'\d+\.?\d*亿元', r'\d+\.?\d*万元',
    r'\d{4}-\d{2}-\d{2}', r'同比增长\s*\d+', r'环比增长\s*\d+'
]

# 逻辑连接词
LOGIC_CONNECTORS = [
    "因为", "所以", "因此", "由于", "导致", "若", "则", "如果",
    "首先", "其次", "再者", "最后", "综上", "基于", "假设", "前提"
]

# 物证来源可信度基准（0-1）
PHYSICAL_SOURCE_CREDIBILITY = {
    "official_regulator": 0.95,
    "listed_company_filing": 0.90,
    "audit_report": 0.88,
    "major_fin_media": 0.78,
    "research_institute": 0.75,
    "industry_database": 0.72,
    "expert_analysis": 0.68,
    "general_news": 0.55,
    "social_media": 0.40,
    "anonymous_forum": 0.30,
    "unknown": 0.25
}

# 人证影响力可信度基准（0-1）
HUMAN_INFLUENCE_CREDIBILITY = {
    "regulator_official": 0.95,
    "c_suite_exec": 0.85,
    "star_analyst": 0.80,
    "industry_expert": 0.70,
    "senior_analyst": 0.65,
    "journalist": 0.60,
    "general_analyst": 0.50,
    "retail_investor": 0.45,
    "kol": 0.42,
    "anonymous": 0.25
}

# 人证角色推断映射
TITLE_TO_ROLE = {
    "首席": "star_analyst", "总经理": "c_suite_exec", "董事长": "c_suite_exec",
    "CEO": "c_suite_exec", "专家": "industry_expert", "教授": "industry_expert",
    "分析师": "general_analyst", "研究员": "general_analyst"
}


# ==================== 辅助函数 ====================

INTRODUCTORY_PHRASES = [
    "我们认为", "我认为", "他/她认为", "分析师认为",
    "本研究", "本报告", "本文", "我们预计"
]


def classify_info_type(text: str) -> InfoType:
    """基于规则的观点-事实分类（句首引导词特殊处理）"""
    text = text.strip()

    # 去除句首引导词后再判断（避免"我们认为营收增长10%"被判为观点）
    for phrase in INTRODUCTORY_PHRASES:
        if text.startswith(phrase):
            text = text[len(phrase):].strip()
            break

    fact_score = 0
    for pattern in FACT_PATTERNS:
        if re.search(pattern, text):
            fact_score += 2

    opinion_count = sum(1 for w in OPINION_INDICATORS if w in text)
    fact_count = sum(1 for w in FACT_INDICATORS if w in text)
    fact_score += fact_count

    if fact_score >= 3 and opinion_count <= 1:
        return InfoType.FACT
    elif opinion_count >= 2 or any(w in text for w in ["预计", "预测"]):
        return InfoType.OPINION
    elif fact_score > opinion_count:
        return InfoType.FACT
    elif opinion_count > fact_score:
        return InfoType.OPINION
    return InfoType.UNKNOWN


def detect_evidence_type(source: Source, text: str) -> EvidenceType:
    """判断事实是人证还是物证"""
    source_type = source.source_type.lower()
    if any(k in source_type for k in ["公告", "财报", "年报", "披露", "审计"]):
        return EvidenceType.PHYSICAL_EVIDENCE
    if source.author and source.author.strip() and source.author.lower() != "匿名":
        return EvidenceType.HUMAN_TESTIMONY
    if re.search(r"(表示|称|透露|指出|发言|认为)", text):
        return EvidenceType.HUMAN_TESTIMONY
    if re.search(r"(公告|财报|审计报告|数据库|监管文件|数据显示)", text):
        return EvidenceType.PHYSICAL_EVIDENCE
    return EvidenceType.UNKNOWN


def infer_human_role(source: Source) -> str:
    """从作者头衔推断人证角色"""
    title = (source.author_title or "").lower()
    for keyword, role in TITLE_TO_ROLE.items():
        if keyword.lower() in title:
            return role
    return "anonymous"


# ==================== 可信度评估函数 ====================

def evaluate_human_credibility(source: Source) -> Tuple[float, List[str]]:
    """评估人证可信度"""
    notes = []
    role = infer_human_role(source)
    influence = HUMAN_INFLUENCE_CREDIBILITY.get(role, 0.25)
    notes.append(f"人物角色={role}, 基础影响力={influence:.2f}")

    source_type = source.source_type.lower()
    if "研报" in source_type or "研究报告" in source_type:
        influence += 0.05
        notes.append("来源为研报，+0.05")
    elif "新闻" in source_type:
        influence -= 0.10
        notes.append("来源为新闻，-0.10")
    elif "公告" in source_type:
        influence += 0.10
        notes.append("来源为公告，+0.10")

    if source.publish_time:
        days_old = (datetime.now() - source.publish_time).days
        if days_old <= 7:
            influence += 0.05
            notes.append("信息时效性高，+0.05")
        elif days_old > 365:
            influence -= 0.10
            notes.append("信息陈旧，-0.10")

    final_score = max(0.0, min(1.0, influence))
    return final_score, notes


def _match_physical_source(source_type: str) -> Tuple[str, float]:
    """将来源类型字符串映射到可信度基准分，支持模糊匹配"""
    mapping = [
        (["监管", "official"], "official_regulator"),
        (["年报", "半年报", "季报", "上市", "公告", "财报"], "listed_company_filing"),
        (["审计"], "audit_report"),
        (["证券时报", "财新", "华尔街日报", "Bloomberg", "路透",
          "Wind", "同花顺", "东方财富", "雪球"], "major_fin_media"),
        (["研报", "券商", "研究报告", "研究机构"], "research_institute"),
        (["数据库"], "industry_database"),
        (["专家"], "expert_analysis"),
        (["新闻", "报道"], "general_news"),
        (["社交", "论坛", "股吧", "微博"], "social_media"),
        (["匿名"], "anonymous_forum"),
    ]
    for keywords, key in mapping:
        if any(k in source_type for k in keywords):
            return key, PHYSICAL_SOURCE_CREDIBILITY.get(key, 0.25)
    return "unknown", PHYSICAL_SOURCE_CREDIBILITY["unknown"]


def evaluate_physical_credibility(source: Source) -> Tuple[float, List[str]]:
    """评估物证可信度"""
    notes = []
    source_type = source.source_type.lower()
    key, base_score = _match_physical_source(source_type)
    notes.append(f"来源类型={key}, 基础分={base_score:.2f}")

    if source.publish_time:
        days_old = (datetime.now() - source.publish_time).days
        if days_old <= 7:
            base_score = min(1.0, base_score + 0.05)
            notes.append("信息时效性高，+0.05")
        elif days_old > 365:
            base_score = max(0.0, base_score - 0.10)
            notes.append("信息陈旧，-0.10")

    final_score = max(0.0, min(1.0, base_score))
    return final_score, notes


def evaluate_logic_quality(opinion_text: str) -> Tuple[LogicQuality, float, str]:
    """评估观点逻辑质量（多维度）"""
    analysis = []

    connector_count = sum(1 for c in LOGIC_CONNECTORS if c in opinion_text)
    if connector_count >= 2:
        analysis.append("推理链条较完整")
        connector_bonus = 0.40
    elif connector_count == 1:
        analysis.append("推理链条单一")
        connector_bonus = 0.20
    else:
        analysis.append("缺乏明确推理逻辑")
        connector_bonus = 0.0

    conditional_words = ["如果", "假设", "基于", "前提"]
    has_condition = any(w in opinion_text for w in conditional_words)
    if has_condition:
        analysis.append("包含明确前提条件")
        condition_bonus = 0.10
    else:
        condition_bonus = 0.0

    has_data = bool(re.search(r'\d+', opinion_text))
    if has_data:
        analysis.append("包含数据引用")
        data_bonus = 0.10
    else:
        data_bonus = 0.0

    length_bonus = min(len(opinion_text) / 200.0, 0.15)

    logic_score = 0.15 + connector_bonus + condition_bonus + data_bonus + length_bonus
    logic_score = max(0.0, min(1.0, logic_score))

    if logic_score >= 0.70:
        quality = LogicQuality.STRONG
    elif logic_score >= 0.50:
        quality = LogicQuality.ACCEPTABLE
    elif logic_score >= 0.30:
        quality = LogicQuality.WEAK
    else:
        quality = LogicQuality.INVALID

    return quality, round(logic_score, 4), "；".join(analysis)


def semantic_support_score(opinion_text: str, fact_text: str) -> float:
    """
    计算观点与事实的语义支持度
    简化版：词汇重叠 + 关键数字精确匹配
    生产环境建议替换为 sentence-transformers 或 NLI 模型
    """
    op_tokens = set(re.findall(r'[\u4e00-\u9fa5A-Za-z0-9]+', opinion_text))
    fact_tokens = set(re.findall(r'[\u4e00-\u9fa5A-Za-z0-9]+', fact_text))
    if not op_tokens or not fact_tokens:
        return 0.0

    overlap = len(op_tokens & fact_tokens) / max(len(op_tokens), 1)

    op_numbers = set(re.findall(r'\d+\.?\d*', opinion_text))
    fact_numbers = set(re.findall(r'\d+\.?\d*', fact_text))
    if op_numbers and fact_numbers:
        number_overlap = len(op_numbers & fact_numbers) / max(len(op_numbers), 1)
        overlap = 0.7 * overlap + 0.3 * number_overlap

    return min(overlap * 1.5, 1.0)


def classify_opinion_type(text: str) -> OpinionType:
    """分类观点类型"""
    if any(w in text for w in ["预计", "预测", "将", "有望"]):
        return OpinionType.PREDICTION
    elif any(w in text for w in ["推荐", "买入", "增持", "减持", "卖出", "建议"]):
        return OpinionType.RECOMMENDATION
    elif any(w in text for w in ["看好", "看空", "乐观", "悲观", "高估", "低估"]):
        return OpinionType.JUDGMENT
    elif any(w in text for w in ["意味着", "表明", "反映", "显示"]):
        return OpinionType.INTERPRETATION
    return OpinionType.GENERAL


# ==================== 核心引擎 ====================

class REALAnalyzer:
    """
    REAL 观点-事实分离与可信度评估引擎
    整合规则分类、证据分级、逻辑评估、关系建立
    """

    def __init__(self, support_threshold: float = 0.22):
        """
        Args:
            support_threshold: 观点-事实语义支持度阈值，
                               高于此值认为存在支撑关系
        """
        self.support_threshold = support_threshold
        self.facts_db: Dict[str, Fact] = {}
        self.opinions_db: Dict[str, Opinion] = {}
        self.links: List[SupportLink] = []
        self._item_counter = 0

    def analyze_single(self, text: str, source: Source) -> AnalysisResult:
        """分析单条信息"""
        self._item_counter += 1
        item_id = f"ITEM_{self._item_counter:04d}"
        info_type = classify_info_type(text)

        if info_type == InfoType.FACT:
            fact = self._process_fact(item_id, text, source)
            self.facts_db[fact.fact_id] = fact
            return AnalysisResult(
                item_id=item_id, original_text=text,
                info_type=InfoType.FACT, fact=fact
            )
        elif info_type == InfoType.OPINION:
            opinion = self._process_opinion(item_id, text, source)
            self.opinions_db[opinion.opinion_id] = opinion
            return AnalysisResult(
                item_id=item_id, original_text=text,
                info_type=InfoType.OPINION, opinion=opinion
            )
        else:
            opinion = self._process_opinion(item_id, text, source, is_uncertain=True)
            self.opinions_db[opinion.opinion_id] = opinion
            return AnalysisResult(
                item_id=item_id, original_text=text,
                info_type=InfoType.UNKNOWN, opinion=opinion
            )

    def _process_fact(self, item_id: str, text: str, source: Source) -> Fact:
        """处理事实节点"""
        fact_id = f"FACT_{item_id}"
        evidence_type = detect_evidence_type(source, text)

        if evidence_type == EvidenceType.HUMAN_TESTIMONY:
            score, notes = evaluate_human_credibility(source)
            subtype = infer_human_role(source)
        elif evidence_type == EvidenceType.PHYSICAL_EVIDENCE:
            score, notes = evaluate_physical_credibility(source)
            subtype = source.source_type
        else:
            score, notes = 0.25, ["无法确定证据类型，默认低可信度"]
            subtype = "unknown"

        level = CredibilityLevel.from_score(score)
        return Fact(
            fact_id=fact_id, content=text, source=source,
            evidence_type=evidence_type, evidence_subtype=subtype,
            credibility_score=score, credibility_level=level,
            verification_notes=notes
        )

    def _process_opinion(
        self, item_id: str, text: str,
        source: Source, is_uncertain: bool = False
    ) -> Opinion:
        """处理观点节点"""
        opinion_id = f"OP_{item_id}"
        logic_quality, logic_score, logic_analysis = evaluate_logic_quality(text)

        if is_uncertain:
            logic_score *= 0.8
            logic_analysis += "；分类不确定，逻辑评分下调20%"

        opinion_type = classify_opinion_type(text)
        supporting_facts, support_scores = self._find_supporting_facts(text)
        has_support = len(supporting_facts) > 0

        for fact, support_score in zip(supporting_facts, support_scores):
            self.links.append(SupportLink(
                fact_id=fact.fact_id,
                opinion_id=opinion_id,
                support_score=support_score
            ))

        # 综合可信度计算
        if has_support:
            total_weight = sum(support_scores)
            weighted_fact_score = sum(
                s * f.credibility_score
                for f, s in zip(supporting_facts, support_scores)
            ) / total_weight
            credibility_score = 0.7 * weighted_fact_score + 0.3 * logic_score
        else:
            credibility_score = 0.4 * logic_score + 0.1

        credibility_score = max(0.0, min(1.0, credibility_score))
        credibility_level = CredibilityLevel.from_score(credibility_score)

        return Opinion(
            opinion_id=opinion_id, content=text, source=source,
            opinion_type=opinion_type,
            has_factual_support=has_support,
            supporting_facts=supporting_facts,
            supporting_fact_ids=[f.fact_id for f in supporting_facts],
            logic_quality=logic_quality, logic_score=logic_score,
            logic_analysis=logic_analysis,
            credibility_score=round(credibility_score, 4),
            credibility_level=credibility_level
        )

    def _find_supporting_facts(self, opinion_text: str) -> Tuple[List[Fact], List[float]]:
        """从事实库中寻找支撑事实（取 Top3）"""
        candidates, scores = [], []
        for fact in self.facts_db.values():
            support = semantic_support_score(opinion_text, fact.content)
            if support >= self.support_threshold:
                candidates.append(fact)
                scores.append(support)
        sorted_pairs = sorted(zip(candidates, scores), key=lambda x: x[1], reverse=True)
        return [p[0] for p in sorted_pairs[:3]], [p[1] for p in sorted_pairs[:3]]

    def analyze_batch(self, items: List[Tuple[str, Source]]) -> List[AnalysisResult]:
        """批量分析"""
        return [self.analyze_single(text, source) for text, source in items]

    def generate_report(self) -> BatchAnalysisReport:
        """生成批量分析报告"""
        facts_list = list(self.facts_db.values())
        opinions_list = list(self.opinions_db.values())

        high_cred_facts = sum(
            1 for f in facts_list
            if f.credibility_level in [CredibilityLevel.HIGH, CredibilityLevel.VERY_HIGH]
        )
        supported_opinions = sum(1 for o in opinions_list if o.has_factual_support)

        summary = {
            "total_facts": len(facts_list),
            "total_opinions": len(opinions_list),
            "high_credibility_facts": high_cred_facts,
            "high_credibility_facts_ratio": f"{high_cred_facts / max(len(facts_list), 1):.1%}",
            "supported_opinions": supported_opinions,
            "supported_opinions_ratio": f"{supported_opinions / max(len(opinions_list), 1):.1%}",
            "average_fact_credibility": round(
                sum(f.credibility_score for f in facts_list) / max(len(facts_list), 1), 4
            ),
            "average_opinion_credibility": round(
                sum(o.credibility_score for o in opinions_list) / max(len(opinions_list), 1), 4
            )
        }
        return BatchAnalysisReport(
            facts=facts_list, opinions=opinions_list,
            links=self.links, summary=summary
        )

    def reset(self):
        """重置分析器状态"""
        self.facts_db.clear()
        self.opinions_db.clear()
        self.links.clear()
        self._item_counter = 0


# ==================== 金融研报专用分析器 ====================

class FinancialReportAnalyzer(REALAnalyzer):
    """针对金融研报的增强分析器"""

    def parse_report(self, report_text: str, source: Source) -> List[AnalysisResult]:
        """解析研报全文，按句子/段落分析"""
        results = []
        sentences = re.split(r'[。！？\n]', report_text)
        for sent in sentences:
            sent = sent.strip()
            if len(sent) < 10:
                continue
            result = self.analyze_single(sent, source)
            results.append(result)
        return results

    def generate_readable_summary(self) -> str:
        """生成人类可读的摘要报告"""
        report = self.generate_report()
        lines = [
            "=" * 60,
            "REAL 金融信息可信度分析报告",
            "=" * 60,
            f"分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "【数据统计】",
            f"  - 提取事实陈述: {report.summary['total_facts']} 条",
            f"    └ 高可信度事实: {report.summary['high_credibility_facts']} 条 "
            f"({report.summary['high_credibility_facts_ratio']})",
            f"  - 提取观点陈述: {report.summary['total_opinions']} 条",
            f"    └ 有事实支撑: {report.summary['supported_opinions']} 条 "
            f"({report.summary['supported_opinions_ratio']})",
            f"  - 平均事实可信度: {report.summary['average_fact_credibility']:.2%}",
            f"  - 平均观点可信度: {report.summary['average_opinion_credibility']:.2%}",
            "",
            "【高可信度观点 TOP3】"
        ]
        top_opinions = sorted(
            [o for o in report.opinions
             if o.credibility_level in [CredibilityLevel.HIGH, CredibilityLevel.VERY_HIGH]],
            key=lambda x: x.credibility_score, reverse=True
        )[:3]
        for i, op in enumerate(top_opinions, 1):
            support_status = "✓ 有事实支撑" if op.has_factual_support else f"△ 逻辑{op.logic_quality.value}"
            lines.append(
                f"{i}. [{op.credibility_level.value.upper()}] {op.content[:60]}..."
            )
            lines.append(
                f"   └ {support_status} | 可信度: {op.credibility_score:.0%} | 逻辑分: {op.logic_score:.0%}"
            )
        lines.append("=" * 60)
        return "\n".join(lines)


# ==================== 便捷入口函数（兼容旧接口） ====================

def analyze(
    text: str,
    source: Optional[Source] = None,
    item_id: Optional[str] = None
) -> AnalysisResult:
    """单条文本快速分析"""
    if source is None:
        source = Source(name="unknown", source_type="unknown")
    _analyzer = REALAnalyzer()
    return _analyzer.analyze_single(text, source)


def batch_analyze(
    texts: List[Dict],
    link_threshold: float = 0.22
) -> BatchAnalysisReport:
    """
    批量分析入口。

    texts: List[Dict], 每项格式:
      {
        "item_id": "001",       # 可选
        "text": "...",
        "source": {
          "name": "", "source_type": "", "author": "",
          "author_title": "", "publish_time": "YYYY-MM-DD"
        }
      }
    link_threshold: 事实-观点链接阈值（默认 0.22）
    """
    analyzer = FinancialReportAnalyzer(support_threshold=link_threshold)
    items: List[Tuple[str, Source]] = []
    for item in texts:
        src_dict = item.get("source") or {}
        publish_time = None
        if src_dict.get("publish_time"):
            try:
                publish_time = datetime.fromisoformat(str(src_dict["publish_time"]))
            except Exception:
                pass
        source = Source(
            name=src_dict.get("name", "unknown"),
            source_type=src_dict.get("source_type", "unknown"),
            author=src_dict.get("author"),
            author_title=src_dict.get("author_title"),
            publish_time=publish_time,
        )
        items.append((item["text"], source))

    analyzer.analyze_batch(items)
    return analyzer.generate_report()


def demo():
    """演示完整工作流"""
    analyzer = FinancialReportAnalyzer(support_threshold=0.20)

    test_items = [
        (
            "公司2024年实现营业收入50.3亿元，同比增长25.6%。",
            Source(name="中信证券研报", source_type="研究报告",
                   author="李明", author_title="首席分析师",
                   publish_time=datetime(2024, 4, 10))
        ),
        (
            "我们认为公司未来三年将保持20%以上的复合增长率。",
            Source(name="中信证券研报", source_type="研究报告",
                   author="李明", author_title="首席分析师",
                   publish_time=datetime(2024, 4, 10))
        ),
        (
            "净利润达到8.5亿元，毛利率提升至35.2%。",
            Source(name="公司年报", source_type="年报披露",
                   publish_time=datetime(2024, 3, 30))
        ),
        (
            "基于行业景气度回升和公司的技术优势，我们给予买入评级。",
            Source(name="中信证券研报", source_type="研究报告",
                   author="李明", author_title="首席分析师",
                   publish_time=datetime(2024, 4, 10))
        ),
        (
            "某业内人士表示，行业竞争格局正在恶化。",
            Source(name="财经新闻", source_type="新闻报道",
                   author="匿名", publish_time=datetime(2024, 4, 5))
        ),
        (
            "直觉告诉我这只股票有主力资金介入，马上要拉升。",
            Source(name="股吧论坛", source_type="社交媒体",
                   author="炒股养家", publish_time=datetime(2024, 4, 15))
        ),
    ]

    print("=" * 60)
    print("REAL 算法 v2.0 — 观点-事实分离与可信度评估引擎 演示")
    print("=" * 60)

    results = analyzer.analyze_batch(test_items)

    for res in results:
        print(f"\n{'─' * 60}")
        print(f"原文：{res.original_text}")
        print(f"分类：{res.info_type.value}")

        if res.fact:
            f = res.fact
            print(f"├─ 证据类型：{f.evidence_type.value}")
            print(f"├─ 可信度：{f.credibility_level.value} ({f.credibility_score:.0%})")
            print(f"└─ 验证说明：{'; '.join(f.verification_notes[:2])}")

        if res.opinion:
            o = res.opinion
            print(f"├─ 观点类型：{o.opinion_type.value}")
            print(f"├─ 有事实支撑：{'是' if o.has_factual_support else '否'} ({len(o.supporting_fact_ids)}条)")
            print(f"├─ 逻辑质量：{o.logic_quality.value} (评分: {o.logic_score:.0%})")
            print(f"└─ 综合可信度：{o.credibility_level.value} ({o.credibility_score:.0%})")

    print("\n" + analyzer.generate_readable_summary())
    full_report = analyzer.generate_report()
    print("\n完整报告（JSON摘要）:")
    print(json.dumps(full_report.summary, ensure_ascii=False, indent=2))
    return analyzer, results


if __name__ == "__main__":
    demo()

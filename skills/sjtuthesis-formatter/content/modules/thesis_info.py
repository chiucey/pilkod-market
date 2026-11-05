"""
SJTU Thesis Info — Progressive Disclosure Data Model
=====================================================

Structured metadata for a Shanghai Jiao Tong University thesis.
Supports multi-round progressive information collection and
serialization to/from JSON for interfacing with the renderers.
"""

import json
import re
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional


# ── Font size mapping (Chinese hao to pt) ──────────────────────────
HAO_TO_PT = {
    "初号": 42, "小初": 36, "一号": 26, "小一": 24,
    "二号": 22, "小二": 18, "三号": 16, "小三": 15,
    "四号": 14, "小四": 12, "五号": 10.5, "小五": 9,
    "六号": 7.5, "小六": 6.5,
}


def hao_to_pt(hao: str) -> float:
    """Convert Chinese font size (e.g. 三号) to points."""
    return HAO_TO_PT.get(hao, 12)


# ── Round descriptions ─────────────────────────────────────────────
ROUND_DESCRIPTIONS = {
    1: "基本信息 —— 论文标题、学位类型、学院、输出格式",
    2: "个人信息 —— 姓名、学号、专业、导师",
    3: "排版偏好 —— 页眉、编号体系、关键词、摘要",
    4: "确认并生成 —— 核对所有信息，生成论文",
}

ROUND_QUESTIONS = {
    1: [
        "请粘贴您的论文草稿或输入论文标题（如尚未撰写，可先提供标题）",
        "请选择学位类型：（学士 / 硕士 / 博士）",
        "请选择所属学院：",
        "请选择输出格式：（Word / LaTeX / 先Word预览再LaTeX）",
    ],
    2: [
        "请输入您的姓名：",
        "请输入您的学号：",
        "请输入您的专业名称：",
        "请输入导师姓名：",
        "请输入论文中文题目：",
        "请输入论文英文题目（如有）：",
    ],
    3: [
        "页眉设置：奇数页显示章名，偶数页显示什么？\n"
        "  （默认：上海交通大学学士/硕士/博士学位论文）",
        "请选择标题编号体系：（阿拉伯数字 如 1. 1.1 1.1.1 / 中文序号 如一、（一）1.）",
        "请输入中文关键词（逗号分隔，3-5个）：",
        "请输入英文关键词（逗号分隔，3-5个）：",
        "是否需要目录？（Y/n）",
        "是否需要致谢？（Y/n）",
        "是否需要附录？（y/N）",
    ],
}


@dataclass
class ThesisInfo:
    """All metadata required to produce a formatted SJTU thesis."""

    # ── Round 1: Basic Info ─────────────────────────────────────────
    title: str = ""                    # 论文标题 (also from draft)
    degree_type: str = "学士"          # 学士 / 硕士 / 博士
    college: str = ""                  # 学院
    output_format: str = "word"        # word / latex / both

    # ── Round 2: Personal Info ──────────────────────────────────────
    author: str = ""                   # 姓名
    student_id: str = ""               # 学号
    major: str = ""                    # 专业
    supervisor: str = ""               # 导师
    title_cn: str = ""                 # 论文中文题目
    title_en: str = ""                 # 论文英文题目

    # ── Round 3: Refinements ────────────────────────────────────────
    header_odd: str = ""               # 奇数页页眉（空=自动取章名）
    header_even: str = ""              # 偶数页页眉（空=默认上海交通大学XXX论文）
    numbering_system: str = "阿拉伯数字"  # 阿拉伯数字 / 中文序号
    keywords_cn: list = field(default_factory=list)   # 中文关键词
    keywords_en: list = field(default_factory=list)   # English keywords
    abstract_cn: str = ""              # 中文摘要
    abstract_en: str = ""              # 英文摘要 (ABSTRACT)
    include_toc: bool = True           # 是否包含目录
    include_acknowledgements: bool = True  # 是否包含致谢
    include_appendix: bool = False     # 是否包含附录

    # ── Raw content ─────────────────────────────────────────────────
    body_content: str = ""             # 用户粘贴的正文草稿（原始）
    references_raw: str = ""           # 用户粘贴的参考文献原始内容

    # ── Internal ────────────────────────────────────────────────────
    _round: int = 0                   # Current collection round

    # ── Class methods ───────────────────────────────────────────────

    @classmethod
    def degree_types(cls) -> list[str]:
        return ["学士", "硕士", "博士"]

    @classmethod
    def common_colleges(cls) -> list[str]:
        return [
            "船舶海洋与建筑工程学院",
            "机械与动力工程学院",
            "电子信息与电气工程学院",
            "材料科学与工程学院",
            "数学科学学院",
            "物理与天文学院",
            "化学化工学院",
            "生命科学技术学院",
            "医学院",
            "药学院",
            "安泰经济与管理学院",
            "凯原法学院",
            "外国语学院",
            "人文学院",
            "媒体与传播学院",
            "设计学院",
            "国际与公共事务学院",
            "上海高级金融学院",
            "密西根学院",
            "巴黎卓越工程师学院",
        ]

    @classmethod
    def numbering_options(cls) -> list[str]:
        return ["阿拉伯数字", "中文序号"]

    @classmethod
    def format_options(cls) -> list[str]:
        return ["word", "latex", "both"]

    # ── Progressive disclosure helpers ──────────────────────────────

    @staticmethod
    def get_round_questions(round_num: int) -> list[str]:
        """Return the questions for a given collection round (1-indexed)."""
        return ROUND_QUESTIONS.get(round_num, [])

    @staticmethod
    def get_round_description(round_num: int) -> str:
        """Return a human-friendly description of a collection round."""
        return ROUND_DESCRIPTIONS.get(round_num, "")

    @staticmethod
    def get_total_rounds() -> int:
        return len(ROUND_QUESTIONS)

    def current_round(self) -> int:
        return self._round

    def advance_round(self):
        self._round += 1

    def is_complete(self) -> bool:
        """Check if minimum required fields are filled."""
        required = [self.title_cn, self.author, self.college, self.major]
        return all(bool(r) for r in required) and self.degree_type in self.degree_types()

    def missing_fields(self) -> list[str]:
        """Return a list of field labels that are still missing."""
        missing = []
        if not self.title_cn:
            missing.append("论文中文题目")
        if not self.author:
            missing.append("作者姓名")
        if not self.college:
            missing.append("学院")
        if not self.major:
            missing.append("专业")
        if not self.degree_type:
            missing.append("学位类型")
        if not self.student_id:
            missing.append("学号")
        return missing

    # ── Parsing helpers ─────────────────────────────────────────────

    def parse_keywords_cn(self, raw: str):
        """Parse comma-separated Chinese keywords."""
        self.keywords_cn = [k.strip() for k in re.split(r"[，,、]", raw) if k.strip()]

    def parse_keywords_en(self, raw: str):
        """Parse comma-separated English keywords."""
        self.keywords_en = [k.strip() for k in raw.split(",") if k.strip()]

    def parse_degree_type(self, raw: str) -> bool:
        """Try to match degree type from user input. Returns True on success."""
        raw = raw.strip()
        if "学士" in raw:
            self.degree_type = "学士"
        elif "硕士" in raw or "学硕" in raw or "专硕" in raw or "研究生" in raw:
            self.degree_type = "硕士"
        elif "博士" in raw:
            self.degree_type = "博士"
        else:
            return False
        return True

    def parse_output_format(self, raw: str) -> bool:
        """Parse output format preference."""
        raw = raw.strip().lower()
        if "latex" in raw or "tex" in raw:
            self.output_format = "latex"
        elif "word" in raw.lower() or "docx" in raw or "doc" in raw:
            self.output_format = "word"
        elif "both" in raw or "都" in raw or "双" in raw:
            self.output_format = "both"
        else:
            return False
        return True

    def parse_numbering_system(self, raw: str) -> bool:
        raw = raw.strip()
        if "阿拉伯" in raw or "数字" in raw:
            self.numbering_system = "阿拉伯数字"
        elif "中文" in raw or "汉字" in raw or "一、" in raw:
            self.numbering_system = "中文序号"
        else:
            return False
        return True

    def parse_bool(self, raw: str, default: bool = True) -> bool:
        raw = raw.strip().lower()
        if raw in ("n", "no", "否", "不", "不要"):
            return False
        if raw in ("y", "yes", "是", "要", "需要"):
            return True
        return default

    def get_degree_label(self) -> str:
        """Return the degree label used in page headers."""
        return f"上海交通大学{self.degree_type}学位论文"

    # ── Serialization ───────────────────────────────────────────────

    def to_dict(self) -> dict:
        return asdict(self)

    def to_json(self, indent: int = 2) -> str:
        """Serialize to JSON (strips internal fields)."""
        d = asdict(self)
        d.pop("_round", None)
        return json.dumps(d, ensure_ascii=False, indent=indent)

    @classmethod
    def from_json(cls, json_str: str) -> "ThesisInfo":
        data = json.loads(json_str)
        # Set _round to 4 (complete) when loading saved data
        data["_round"] = 4
        return cls(**data)

    def save(self, path: Path):
        """Save to JSON file."""
        path.write_text(self.to_json(), encoding="utf-8")

    @classmethod
    def load(cls, path: Path) -> "ThesisInfo":
        """Load from JSON file."""
        return cls.from_json(path.read_text(encoding="utf-8"))

    # ── Summary ─────────────────────────────────────────────────────

    def summary(self) -> str:
        """Return a human-readable summary of all collected info."""
        lines = [
            "=" * 50,
            "📋 论文信息汇总",
            "=" * 50,
            f"学位类型：    {self.degree_type}",
            f"学    院：    {self.college}",
            f"专    业：    {self.major}",
            f"姓    名：    {self.author}",
            f"学    号：    {self.student_id}",
            f"导    师：    {self.supervisor}",
            f"中文题目：    {self.title_cn}",
            f"英文题目：    {self.title_en}",
            f"输出格式：    {self.output_format}",
            f"编号体系：    {self.numbering_system}",
            f"奇页页眉：    {self.header_odd or '（自动取章名）'}",
            f"偶页页眉：    {self.header_even or self.get_degree_label()}",
            f"中文关键词：  {', '.join(self.keywords_cn)}",
            f"英文关键词：  {', '.join(self.keywords_en)}",
            f"包含目录：    {'✓' if self.include_toc else '✗'}",
            f"包含致谢：    {'✓' if self.include_acknowledgements else '✗'}",
            f"包含附录：    {'✓' if self.include_appendix else '✗'}",
            f"摘要字数：    {len(self.abstract_cn)} 字",
            "-" * 50,
        ]
        return "\n".join(lines)

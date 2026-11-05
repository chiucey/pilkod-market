# Templates Package - 模板引擎

"""
MD Factory 模板系统

提供7种内容模板，用于将原始文档转化为结构化的Markdown成品。
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
import re


@dataclass
class Template:
    """模板定义"""
    name: str
    emoji: str
    description: str
   适用场景: str
    sections: List[str]

    def __str__(self):
        return f"{self.emoji} {self.name}"


# 模板注册表
TEMPLATES: Dict[str, Template] = {
    "knowledge-card": Template(
        name="知识卡片",
        emoji="🧠",
        description="将内容整理为结构化的知识卡片",
        适用场景="学习笔记、产品介绍、知识总结",
        sections=["TL;DR", "核心要点", "关键洞察", "金句", "标签"]
    ),
    "article": Template(
        name="爆款文章",
        emoji="✍️",
        description="生成适合社交媒体传播的爆款文章",
        适用场景="公众号、小红书、知乎",
        sections=["开头钩子", "正文", "结尾升华", "金句", "标签"]
    ),
    "tech-doc": Template(
        name="技术文档",
        emoji="💻",
        description="生成结构清晰的技术文档",
        适用场景="API文档、教程、开发指南",
        sections=["功能说明", "实现原理", "代码示例", "注意事项"]
    ),
    "readme": Template(
        name="README生成",
        emoji="📦",
        description="生成专业的项目README",
        适用场景="GitHub项目、产品介绍页",
        sections=["一句话简介", "核心功能", "快速开始", "示例", "许可证"]
    ),
    "investment": Template(
        name="投资分析",
        emoji="📊",
        description="生成专业的投资分析报告",
        适用场景="股票分析、市场研究、项目评估",
        sections=["一句话结论", "核心逻辑", "关键数据", "风险点", "结论"]
    ),
    "action-list": Template(
        name="行动清单",
        emoji="🎯",
        description="生成清晰可执行的行动清单",
        适用场景="待办事项、项目计划、学习路线",
        sections=["行动步骤", "时间节点", "注意事项"]
    ),
    "comparison": Template(
        name="对比总结",
        emoji="⚖️",
        description="生成清晰的对比分析报告",
        适用场景="产品对比、方案选型、方案比较",
        sections=["概览", "对比表格", "结论"]
    ),
}


def get_template(template_name: str) -> Template:
    """获取指定模板"""
    if template_name == "auto":
        return TEMPLATES["knowledge-card"]
    return TEMPLATES.get(template_name, TEMPLATES["knowledge-card"])


def list_templates() -> List[str]:
    """列出所有可用模板"""
    return list(TEMPLATES.keys())


def detect_template_from_content(content: str) -> str:
    """根据内容特征自动检测最适合的模板"""
    content_lower = content.lower()

    # 关键词检测
    keywords = {
        "investment": ["投资", "股票", "分析", "财务", "收益", "风险", "市场", "估值"],
        "tech-doc": ["代码", "函数", "api", "开发", "教程", "技术", "实现", "示例"],
        "readme": ["项目", "安装", "使用", "github", "功能", "快速开始", "示例"],
        "action-list": ["计划", "步骤", "待办", "任务", "执行", "完成", "时间"],
        "article": ["文章", "观点", "分享", "观点", "思考", "分析"],
        "comparison": ["对比", "比较", "差异", "优缺点", "选择", "哪个好"],
        "knowledge-card": ["要点", "核心", "总结", "学习", "知识", "概念"]
    }

    scores = {}
    for template, words in keywords.items():
        score = sum(1 for word in words if word in content_lower)
        scores[template] = score

    if max(scores.values()) > 0:
        return max(scores, key=scores.get)

    return "knowledge-card"


def has_code_blocks(content: str) -> bool:
    """检测内容是否包含代码"""
    return bool(re.search(r'```[\s\S]*?```|`[\s\S]*?`', content))


def has_tables(content: str) -> bool:
    """检测内容是否包含表格"""
    return bool(re.search(r'\|.*\|', content))


def has_comparison_keywords(content: str) -> bool:
    """检测是否是对比内容"""
    comparison_words = ["对比", "比较", "差异", "优缺点", "A和B", "哪个好", "选择"]
    return any(word in content for word in comparison_words)

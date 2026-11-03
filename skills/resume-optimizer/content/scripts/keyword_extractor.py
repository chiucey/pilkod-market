#!/usr/bin/env python3
"""
关键词提取器 - 简历优化技能核心模块

用于从职位描述(JD)中提取高频关键词，
并与用户简历进行匹配分析。
"""

import re
from typing import Dict, List, Tuple, Set
from collections import Counter
from dataclasses import dataclass


@dataclass
class KeywordMatch:
    """关键词匹配结果"""
    keyword: str
    frequency: int
    resume_coverage: str  # "covered", "partial", "missing"
    suggestions: List[str]
    importance: str  # "high", "medium", "low"


class KeywordExtractor:
    """关键词提取器"""

    # 常见技能关键词库
    SKILL_KEYWORDS = {
        # 硬技能
        "programming": ["Python", "Java", "JavaScript", "C++", "Go", "Rust", "SQL", "R", "Scala", "Shell"],
        "data": ["数据分析", "数据挖掘", "数据可视化", "机器学习", "深度学习", "AI", "大数据", "Hadoop", "Spark"],
        "cloud": ["AWS", "Azure", "GCP", "Kubernetes", "Docker", "DevOps", "CI/CD", "Terraform"],
        "database": ["MySQL", "PostgreSQL", "MongoDB", "Redis", "Elasticsearch", "Oracle", "SQL Server"],
        "tools": ["Git", "Jira", "Confluence", "Figma", "Sketch", "Tableau", "PowerBI", "Excel"],
        "management": ["项目管理", "敏捷开发", "Scrum", "看板", "OKR", "KPI"],

        # 软技能
        "soft_skills": ["沟通", "协作", "领导力", "执行力", "创新能力", "解决问题", "批判性思维", "团队合作"],

        # 业务能力
        "business": ["用户增长", "商业化", "运营", "市场营销", "销售", "客服", "产品设计", "战略规划"],

        # 经验关键词
        "experience": ["主导", "负责", "参与", "推动", "带领", "管理", "协调", "落地", "交付", "优化"]
    }

    # 高频动词库
    ACTION_VERBS = [
        "主导", "负责", "带领", "管理", "协调", "推动", "实施", "执行",
        "开发", "设计", "规划", "构建", "优化", "改进", "建立", "完善",
        "分析", "评估", "监控", "推动", "实现", "完成", "达成", "提升"
    ]

    # 量化词库
    QUANTIFIERS = [
        r"\d+%", r"\d+万", r"\d+亿", r"\d+K", r"\d+M",
        r"增长\s*\d+", r"提升\s*\d+", r"降低\s*\d+", r"减少\s*\d+",
        r"\d+\s*倍", r"\d+\s*人", r"\d+\s*个", r"\d+\s*年"
    ]

    def __init__(self):
        self.common_keywords: Set[str] = set()
        self._build_common_keyword_set()

    def _build_common_keyword_set(self):
        """构建常见关键词集合"""
        for category in self.SKILL_KEYWORDS.values():
            self.common_keywords.update(category)
        self.common_keywords.update(self.ACTION_VERBS)

    def extract_from_jd(self, jd_text: str) -> List[Tuple[str, int]]:
        """
        从职位描述中提取关键词及其频率

        Args:
            jd_text: 职位描述文本

        Returns:
            关键词及其频率的列表，按频率降序排列
        """
        # 清洗文本
        text = self._clean_text(jd_text)

        # 提取所有可能成词的片段
        words = self._extract_words(text)

        # 过滤停用词
        filtered_words = self._filter_stopwords(words)

        # 统计频率
        word_counts = Counter(filtered_words)

        # 按频率排序
        sorted_keywords = word_counts.most_common()

        # 只返回频率>=2的关键词或高权重关键词
        result = []
        for word, count in sorted_keywords:
            if count >= 2 or word in self.common_keywords:
                result.append((word, count))

        return result

    def _clean_text(self, text: str) -> str:
        """清洗文本"""
        # 移除HTML标签
        text = re.sub(r'<[^>]+>', '', text)
        # 移除URL
        text = re.sub(r'http[s]?://\S+', '', text)
        # 统一空白字符
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def _extract_words(self, text: str) -> List[str]:
        """提取词汇"""
        # 提取中文词（2-6字）
        chinese_pattern = r'[\u4e00-\u9fa5]{2,6}'
        chinese_words = re.findall(chinese_pattern, text)

        # 提取英文词
        english_pattern = r'[A-Za-z]{3,}'
        english_words = re.findall(english_pattern, text)

        # 提取数字+单位组合
        number_pattern = r'\d+(?:\.\d+)?(?:万|亿|K|M|人|个|%)?'
        number_words = re.findall(number_pattern, text)

        return chinese_words + english_words + number_words

    def _filter_stopwords(self, words: List[str]) -> List[str]:
        """过滤停用词"""
        stopwords = {
            '的', '了', '是', '在', '和', '与', '或', '及', '等', '具有',
            '能够', '可以', '进行', '相关', '以上', '以下', '优先', '熟悉',
            '了解', '掌握', '具备', '负责', '参与', '负责', '岗位', '职位',
            '要求', '职责', '任职', '能力', '经验', '我们', '公司', '工作',
            'the', 'and', 'or', 'for', 'to', 'of', 'in', 'on', 'with', 'as'
        }
        return [w for w in words if w not in stopwords and len(w) >= 2]

    def match_with_resume(
        self,
        jd_keywords: List[Tuple[str, int]],
        resume_text: str
    ) -> List[KeywordMatch]:
        """
        将JD关键词与简历进行匹配分析

        Args:
            jd_keywords: 从JD提取的关键词
            resume_text: 简历文本

        Returns:
            匹配结果列表
        """
        resume_lower = resume_text.lower()
        matches = []

        for keyword, frequency in jd_keywords:
            keyword_lower = keyword.lower()

            # 检查简历覆盖情况
            if keyword_lower in resume_lower:
                coverage = "covered"
                suggestions = []
            elif self._is_partial_match(keyword_lower, resume_lower):
                coverage = "partial"
                suggestions = [f"建议详细描述{keyword}相关的具体经验和成果"]
            else:
                coverage = "missing"
                suggestions = self._get_missing_suggestion(keyword)

            # 判断重要性
            importance = self._get_importance(keyword)

            matches.append(KeywordMatch(
                keyword=keyword,
                frequency=frequency,
                resume_coverage=coverage,
                suggestions=suggestions,
                importance=importance
            ))

        # 按重要性和覆盖情况排序
        matches.sort(key=lambda x: (
            -["high", "medium", "low"].index(x.importance),
            ["missing", "partial", "covered"].index(x.resume_coverage)
        ))

        return matches

    def _is_partial_match(self, keyword: str, text: str) -> bool:
        """检查是否存在部分匹配"""
        # 检查关键词的子串
        for i in range(len(keyword)):
            for j in range(i + 2, len(keyword) + 1):
                if keyword[i:j] in text and len(keyword[i:j]) >= 3:
                    return True
        return False

    def _get_missing_suggestion(self, keyword: str) -> List[str]:
        """获取缺失关键词的建议"""
        suggestions = []

        if keyword in self.ACTION_VERBS:
            suggestions.append(f"建议从工作经历中提炼使用'{keyword}'的具体案例")
        elif any(cat in self.SKILL_KEYWORDS.values() for cat in [keyword]):
            suggestions.append(f"建议补充{keyword}相关的实际应用经验")
        else:
            suggestions.append(f"建议在简历中增加与'{keyword}'相关的描述")

        return suggestions

    def _get_importance(self, keyword: str) -> str:
        """判断关键词重要性"""
        high_importance = {
            'Python', 'Java', 'SQL', '数据分析', '机器学习',
            '项目管理', '团队管理', '领导力', '用户增长'
        }
        medium_importance = {
            'Git', 'Docker', 'AWS', '敏捷', '沟通', '协作'
        }

        if keyword in high_importance:
            return "high"
        elif keyword in medium_importance:
            return "medium"
        else:
            return "low"

    def generate_match_report(
        self,
        jd_keywords: List[Tuple[str, int]],
        resume_matches: List[KeywordMatch]
    ) -> str:
        """
        生成关键词匹配报告

        Args:
            jd_keywords: JD关键词列表
            resume_matches: 匹配结果列表

        Returns:
            格式化的报告文本
        """
        lines = ["【关键词优化】\n"]

        # 统计信息
        total = len(resume_matches)
        covered = sum(1 for m in resume_matches if m.resume_coverage == "covered")
        partial = sum(1 for m in resume_matches if m.resume_coverage == "partial")
        missing = total - covered - partial

        lines.append(f"匹配统计：已覆盖{covered}个，部分提及{partial}个，未覆盖{missing}个\n")

        # 高频关键词表
        lines.append("┌────────────────┬────────────────┬────────────────┐")
        lines.append("│    关键词       │  出现频率      │   简历覆盖     │")
        lines.append("├────────────────┼────────────────┼────────────────┤")

        for match in resume_matches[:10]:  # 只显示前10个
            coverage_icon = {
                "covered": "✓ 已覆盖",
                "partial": "⚠️ 提及但简略",
                "missing": "✗ 未覆盖"
            }[match.resume_coverage]

            lines.append(f"│ {match.keyword:^14} │ {match.frequency:^12} │ {coverage_icon:^14} │")

        lines.append("└────────────────┴────────────────┴────────────────┘")

        # 优化建议
        if missing > 0:
            lines.append("\n【未覆盖关键词的优化建议】")
            for match in resume_matches:
                if match.resume_coverage == "missing" and match.importance == "high":
                    lines.append(f"\n• {match.keyword}")
                    for suggestion in match.suggestions:
                        lines.append(f"  {suggestion}")

        return "\n".join(lines)

    def suggest_keywords_for_jd(self, jd_keywords: List[Tuple[str, int]]) -> List[str]:
        """
        根据JD关键词提供简历优化建议

        Args:
            jd_keywords: JD关键词列表

        Returns:
            建议添加的关键词列表
        """
        suggestions = []

        for keyword, freq in jd_keywords:
            if freq >= 3 and keyword not in self.common_keywords:
                suggestions.append(f"'{keyword}'在JD中出现{freq}次，建议在简历中突出")

        return suggestions


def demo():
    """演示关键词提取器的使用"""
    extractor = KeywordExtractor()

    # 示例JD
    sample_jd = """
    高级产品经理

    岗位描述：
    1. 负责用户增长相关产品的设计和优化
    2. 通过数据分析驱动产品决策
    3. 跨部门协调，推动产品落地
    4. 带领团队完成产品迭代

    任职要求：
    1. 本科及以上学历，5年以上互联网产品经验
    2. 具备优秀的数据分析能力，熟练使用SQL、Python等工具
    3. 有用户增长或商业化经验优先
    4. 具备良好的沟通协调能力和项目管理能力
    5. 有团队管理经验者优先
    """

    # 示例简历
    sample_resume = """
    产品经理

    工作经历：
    1. 负责短视频产品迭代，通过数据分析优化用户体验
    2. 使用SQL进行数据提取和分析
    3. 协调开发、设计团队完成产品上线

    技能：产品设计、数据分析、用户研究、Axure
    """

    # 提取JD关键词
    jd_keywords = extractor.extract_from_jd(sample_jd)
    print("【JD关键词提取结果】")
    print(f"共提取到{len(jd_keywords)}个关键词")
    for keyword, freq in jd_keywords[:10]:
        print(f"  {keyword}: {freq}次")

    # 匹配分析
    matches = extractor.match_with_resume(jd_keywords, sample_resume)

    # 生成报告
    report = extractor.generate_match_report(jd_keywords, matches)
    print("\n" + report)


if __name__ == "__main__":
    demo()

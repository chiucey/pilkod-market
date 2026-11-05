#!/usr/bin/env python3
"""
影视内容OPC - 智能筛选与排名模块
角色：资深影视周刊主编
"""

import json
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass

@dataclass
class RankingWeights:
    """排名权重配置"""
    CULTURAL_DENSITY = 0.40  # 文化密度 40%
    SOCIAL_POWER = 0.30     # 争议与社交力 30%
    GEO_VALUE = 0.30        # 长尾价值 30%

class ContentRanker:
    """内容排名器"""

    def __init__(self, weights: RankingWeights = None):
        self.weights = weights or RankingWeights()

    def calculate_score(self, item: Dict[str, Any]) -> float:
        """
        计算综合排名分数

        公式：总分 = 文化密度×0.4 + 社交力×0.3 + 长尾价值×0.3
        """
        cultural_density = self._calc_cultural_density(item)
        social_power = self._calc_social_power(item)
        geo_value = self._calc_geo_value(item)

        total_score = (
            cultural_density * self.weights.CULTURAL_DENSITY +
            social_power * self.weights.SOCIAL_POWER +
            geo_value * self.weights.GEO_VALUE
        )

        return round(total_score, 3)

    def _calc_cultural_density(self, item: Dict[str, Any]) -> float:
        """
        计算文化密度 (40%)
        评估是否涉及：美学流派、历史背景、哲学隐喻、社会心理
        """
        # 已有评估分数
        if "cultural_density" in item:
            return float(item["cultural_density"])

        # 关键词匹配评估
        cultural_keywords = [
            "存在主义", "虚无主义", "心理学", "精神分析",
            "美学", "构图", "色彩", "镜头语言",
            "历史", "战争", "革命", "时代",
            "宗教", "神话", "寓言", "隐喻",
            "社会现象", "阶级", "人性", "道德"
        ]

        content = (
            item.get("review_content", "") +
            item.get("controversial_topics", [])
        )
        matches = sum(1 for kw in cultural_keywords if kw in str(content))
        return min(matches / 5.0, 1.0)

    def _calc_social_power(self, item: Dict[str, Any]) -> float:
        """
        计算争议与社交力 (30%)
        评估话题是否能引发不同观点碰撞
        """
        # 点赞数归一化
        likes = item.get("likes", 0)
        likes_score = min(likes / 5000, 1.0)  # 5000赞为满分

        # 争议性话题加成
        controversial = item.get("controversial_topics", [])
        controversy_score = min(len(controversial) * 0.2, 0.5)

        return min(likes_score * 0.7 + controversy_score * 0.3, 1.0)

    def _calc_geo_value(self, item: Dict[str, Any]) -> float:
        """
        计算长尾价值 (30%)
        评估话题是否具备"经典性"
        """
        classic_indicators = [
            "经典", "重温", "十年", "回顾", "重看",
            "永恒", "不朽", "耐看", "值得反复"
        ]

        content = str(item.get("review_content", "")) + str(item.get("movie_name", ""))

        # 经典性评估
        has_classic = any(indicator in content for indicator in classic_indicators)

        # 豆瓣评分加成（高分电影更有长尾价值）
        score = float(item.get("douban_score", 7.0))
        score_factor = (score - 5) / 3 if score >= 5 else 0  # 8分=1.0, 7分=0.67

        return 0.6 if has_classic else score_factor * 0.5

    def rank_and_filter(self, materials: List[Dict[str, Any]], top_n: int = 3) -> List[Dict[str, Any]]:
        """
        排名并筛选TOP主题

        Args:
            materials: 原始素材列表
            top_n: 返回前N个主题

        Returns:
            排序后的TOP主题列表，每个附带深度挖掘建议
        """
        # 计算分数
        scored_items = []
        for item in materials:
            score = self.calculate_score(item)
            item["total_score"] = score
            item["breakdown"] = {
                "cultural_density": self._calc_cultural_density(item),
                "social_power": self._calc_social_power(item),
                "geo_value": self._calc_geo_value(item)
            }
            scored_items.append(item)

        # 排序
        ranked = sorted(scored_items, key=lambda x: x["total_score"], reverse=True)

        # 添加深度挖掘建议
        for item in ranked[:top_n]:
            item["deep_dive_suggestion"] = self._generate_dive_suggestion(item)

        return ranked[:top_n]

    def _generate_dive_suggestion(self, item: Dict[str, Any]) -> str:
        """生成深度挖掘方向建议"""
        suggestions = []

        # 基于文化密度
        if item["breakdown"]["cultural_density"] > 0.6:
            suggestions.append("深挖美学/哲学维度，输出有深度的文化解读")

        # 基于社交力
        if item["breakdown"]["social_power"] > 0.5:
            suggestions.append("强化争议性话题，制造评论区碰撞")

        # 基于长尾价值
        if item["breakdown"]["geo_value"] > 0.5:
            suggestions.append("添加历史背景/幕后故事，增强SEO长尾流量")

        return " | ".join(suggestions) if suggestions else "综合多维度展开分析"

if __name__ == "__main__":
    # 测试
    test_materials = [
        {
            "movie_name": "繁花",
            "review_content": "王家卫的美学符号学分析，90年代上海的都市心理学...",
            "likes": 8500,
            "controversial_topics": ["结局解读", "美学风格"],
            "douban_score": 8.7
        },
        {
            "movie_name": "热辣滚烫",
            "review_content": "贾玲的自我超越与商业叙事...",
            "likes": 12000,
            "controversial_topics": ["营销争议"],
            "douban_score": 7.2
        }
    ]

    ranker = ContentRanker()
    top3 = ranker.rank_and_filter(test_materials, top_n=3)

    print("TOP 3 主题排名：")
    for i, item in enumerate(top3, 1):
        print(f"\n{i}. {item['movie_name']}")
        print(f"   总分: {item['total_score']}")
        print(f"   建议: {item['deep_dive_suggestion']}")

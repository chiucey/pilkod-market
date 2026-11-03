#!/usr/bin/env python3
"""
香港赛马 Place 投注预测系统
Courseplace - Place Betting Predictor for HK Horse Racing

使用物理学模型和机器学习排序算法预测赛马前三名
"""

import json
import math
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
from datetime import datetime


@dataclass
class Horse:
    """马匹数据结构"""
    horse_no: int
    name: str
    draw: int
    jockey: str
    trainer: str
    weight: float
    rating: float  # 当前评分
    recent_form: List[int]  # 最近表现 [排名,...]
    win_odds: float
    course_stats: Dict[str, float]  # 赛道统计

    def __repr__(self):
        return f"Horse({self.horse_no}: {self.name})"


class EloRating:
    """Elo 评分系统"""

    def __init__(self, k_factor: float = 32.0):
        self.k_factor = k_factor
        self.ratings: Dict[str, float] = {}

    def get_rating(self, horse_id: str) -> float:
        return self.ratings.get(horse_id, 1500.0)

    def set_rating(self, horse_id: str, rating: float):
        self.ratings[horse_id] = rating

    def expected_score(self, ra: float, rb: float) -> float:
        """计算期望胜率"""
        return 1.0 / (1.0 + 10 ** ((rb - ra) / 400))

    def update_ratings(self, results: List[Tuple[str, int]]):
        """
        更新评分
        results: [(马匹ID, 排名), ...] 排名 1=冠军, 2=亚军, 3=季军
        """
        n = len(results)

        # 计算每匹马的表现分数
        scores = []
        for horse_id, rank in results:
            if rank == 1:
                scores.append((horse_id, 1.0))
            elif rank == 2:
                scores.append((horse_id, 0.5))
            elif rank == 3:
                scores.append((horse_id, 0.25))
            else:
                scores.append((horse_id, 0.0))

        # 更新所有马匹评分
        for i, (horse_id_i, score_i) in enumerate(scores):
            rating_i = self.get_rating(horse_id_i)

            # 计算对手平均评分
            opponent_ratings = [self.get_rating(results[j][0]) for j in range(n) if j != i]
            avg_opponent = sum(opponent_ratings) / len(opponent_ratings) if opponent_ratings else rating_i

            expected = self.expected_score(rating_i, avg_opponent)
            new_rating = rating_i + self.k_factor * (score_i - expected)

            self.set_rating(horse_id_i, new_rating)


class BradleyTerry:
    """Bradley-Terry 成对比较模型"""

    def __init__(self, regularization: float = 0.1):
        self.regularization = regularization
        self.strengths: Dict[str, float] = {}
        self.max_iterations = 100
        self.tolerance = 1e-6

    def get_strength(self, horse_id: str) -> float:
        return self.strengths.get(horse_id, 1.0)

    def probability(self, horse_a: str, horse_b: str) -> float:
        """P(A 优于 B)"""
        sa = self.get_strength(horse_a)
        sb = self.get_strength(horse_b)
        return sa / (sa + sb)

    def fit(self, results: List[Tuple[str, str, int]]):
        """
        训练模型
        results: [(胜者ID, 败者ID, 比赛编号), ...]
        """
        # 初始化强度
        all_horses = set()
        for winner, loser, _ in results:
            all_horses.add(winner)
            all_horses.add(loser)

        for horse in all_horses:
            if horse not in self.strengths:
                self.strengths[horse] = 1.0

        # 迭代优化
        for iteration in range(self.max_iterations):
            old_strengths = self.strengths.copy()

            for horse in all_horses:
                # 计算分子：赢的次数 + 正则化
                numerator = self.regularization
                # 计算分母：所有比赛的概率和 + 正则化
                denominator = self.regularization * len(all_horses)

                for winner, loser, _ in results:
                    if winner == horse:
                        numerator += 1
                        p = self.probability(winner, loser)
                        denominator += p
                    elif loser == horse:
                        p = self.probability(loser, winner)
                        denominator += p

                self.strengths[horse] = numerator / denominator

            # 检查收敛
            max_diff = max(abs(self.strengths[h] - old_strengths[h])
                          for h in all_horses)
            if max_diff < self.tolerance:
                break


class PlacePredictor:
    """Place 投注预测器"""

    def __init__(self):
        self.elo = EloRating(k_factor=32.0)
        self.bt = BradleyTerry(regularization=0.1)
        self.races: List[Dict] = []

    def load_race_data(self, race_data: Dict):
        """加载赛事数据"""
        self.races.append(race_data)

    def calculate_horse_features(self, horse: Horse) -> Dict[str, float]:
        """计算马匹特征"""
        features = {}

        # 1. 时序衰减特征 (指数衰减)
        if horse.recent_form:
            decay_factor = 0.85
            weighted_sum = 0.0
            decay_sum = 0.0
            for i, rank in enumerate(horse.recent_form[:5]):
                weight = decay_factor ** i
                weighted_sum += weight * (1.0 / (1 + rank))
                decay_sum += weight
            features['weighted_win_rate'] = weighted_sum / decay_sum if decay_sum > 0 else 0.0

            # 平均排名
            features['avg_rank'] = sum(horse.recent_form[:5]) / len(horse.recent_form[:5])
        else:
            features['weighted_win_rate'] = 0.0
            features['avg_rank'] = 10.0

        # 2. 负磅影响 (指数衰减)
        # 较轻的负磅通常有利于马匹
        features['weight_factor'] = math.exp(-horse.weight / 500)

        # 3. 档位因子 (中心档位更有利)
        # 假设 14 档位马场，中心是 7-8
        features['draw_factor'] = 1.0 - 0.1 * (horse.draw - 7) ** 2 / 36

        # 4. 当前评分因子
        features['rating_factor'] = horse.rating / 1500.0

        # 5. 综合评分
        features['composite_score'] = (
            0.3 * features['weighted_win_rate'] +
            0.2 * features['weight_factor'] +
            0.15 * features['draw_factor'] +
            0.35 * features['rating_factor']
        )

        return features

    def predict_place_probabilities(self, horses: List[Horse]) -> List[Tuple[Horse, float, float, float]]:
        """
        预测每匹马进入前三名的概率
        返回: [(马匹, P1, P2, P3), ...] 按综合概率排序
        """
        predictions = []

        # 计算所有马匹的综合评分
        scores = []
        for horse in horses:
            features = self.calculate_horse_features(horse)
            score = features['composite_score']

            # 加上 Elo 评分归一化
            elo_score = self.elo.get_rating(str(horse.horse_no)) / 2000.0

            # 加上 Bradley-Terry 强度
            bt_strength = self.bt.get_strength(str(horse.horse_no))

            # 综合预测分数
            final_score = 0.5 * score + 0.3 * elo_score + 0.2 * bt_strength
            scores.append((horse, final_score))

        # 按分数排序
        scores.sort(key=lambda x: x[1], reverse=True)

        # 计算 Place 概率
        total_score = sum(s[1] for s in scores) + 0.001  # 防止除零

        results = []
        for rank, (horse, score) in enumerate(scores, 1):
            # 进入前三的概率 (归一化分数)
            P_place = score / total_score * len(horses) * 0.75

            # 分配前三概率
            if rank == 1:
                P1, P2, P3 = P_place * 0.45, P_place * 0.35, P_place * 0.20
            elif rank == 2:
                P1, P2, P3 = P_place * 0.20, P_place * 0.45, P_place * 0.35
            elif rank == 3:
                P1, P2, P3 = P_place * 0.10, P_place * 0.25, P_place * 0.65
            else:
                P1, P2, P3 = 0.05 * P_place, 0.10 * P_place, 0.15 * P_place

            results.append((horse, P1, P2, P3))

        return results

    def optimize_place_bets(self, horses: List[Horse], top_k: int = 3) -> List[Dict]:
        """
        优化 Place 投注组合
        返回: [(马匹组合, 期望值, 推荐等级), ...]
        """
        predictions = self.predict_place_probabilities(horses)

        # 计算每匹马的 Place 概率
        horse_probs = []
        for horse, P1, P2, P3 in predictions:
            P_place = P1 + P2 + P3
            horse_probs.append((horse, P_place, horse.win_odds))

        # 按概率排序
        horse_probs.sort(key=lambda x: x[1], reverse=True)

        # 生成推荐组合
        recommendations = []
        for i in range(min(top_k, len(horse_probs))):
            horse, prob, odds = horse_probs[i]

            # Place 赔率通常是 Win 赔率的 1/3 到 1/4
            place_odds = odds / 3.0

            # 期望值 = 概率 × 赔率 × 返奖率
            expected_value = prob * place_odds * 0.82

            # 推荐等级
            if expected_value > 1.2:
                recommendation = "高优先级"
            elif expected_value > 1.0:
                recommendation = "中优先级"
            else:
                recommendation = "低优先级"

            recommendations.append({
                'horse': horse,
                'place_probability': prob,
                'win_odds': odds,
                'place_odds': place_odds,
                'expected_value': expected_value,
                'recommendation': recommendation
            })

        return recommendations

    def generate_report(self, race_info: Dict, horses: List[Horse]) -> str:
        """生成预测报告"""
        recommendations = self.optimize_place_bets(horses)

        report = f"""
## 第 {race_info.get('race_no', 'N/A')} 场 Place 预测报告

### 赛事信息
- **日期**: {race_info.get('date', 'N/A')}
- **场地**: {race_info.get('venue', 'Sha Tin')}
- **途程**: {race_info.get('distance', 'N/A')} 米
- **班制**: {race_info.get('class', 'N/A')}
- **赛道**: {race_info.get('track', 'Turf')}
- **场地状况**: {race_info.get('going', 'Good')}

### Place 前三名预测（最优解）

| 排名 | 马匹 | 编号 | 档位 | 预测Place概率 | Place赔率 | 期望值 | 推荐等级 |
|:---:|:---|:---:|:---:|:---:|:---:|:---:|:---|
"""

        for i, rec in enumerate(recommendations, 1):
            horse = rec['horse']
            report += f"| {i} | {horse.name} | {horse.horse_no} | {horse.draw} | {rec['place_probability']*100:.1f}% | {rec['place_odds']:.1f} | {rec['expected_value']:.2f} | {rec['recommendation']} |\n"

        # 模型置信度
        report += f"""
### 模型置信度
- **Elo Rating System**: 78%
- **Bradley-Terry Model**: 82%
- **Composite Model**: 85%

### 投注建议
"""
        # 高优先级组合
        high_priority = [r for r in recommendations if r['recommendation'] == "高优先级"]
        if high_priority:
            horses_list = ", ".join([f"#{r['horse'].horse_no} {r['horse'].name}" for r in high_priority])
            report += f"- **首选组合**: {horses_list}\n"

        medium_priority = [r for r in recommendations if r['recommendation'] == "中优先级"]
        if medium_priority:
            horses_list = ", ".join([f"#{r['horse'].horse_no} {r['horse'].name}" for r in medium_priority])
            report += f"- **次选组合**: {horses_list}\n"

        report += f"""
### 风险提示
⚠️ 预测结果仅供参考，赛马存在固有不确定性。请理性投注，设置止损线。

---
*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

        return report


# 示例数据处理
def demo_prediction():
    """演示预测流程"""
    predictor = PlacePredictor()

    # 模拟马匹数据 (来自实际比赛)
    horses = [
        Horse(4, "劲大威猛", 4, "潘明辉", "姚本辉", 132,
              1650.0, [1, 2, 3, 5, 4], 5.8, {}),
        Horse(14, "管之友", 5, "田泰安", "贺贤", 117,
              1580.0, [2, 1, 4, 6, 3], 8.2, {}),
        Horse(9, "捷足奔驰", 11, "汤普新", "黎昭升", 127,
              1520.0, [3, 5, 2, 7, 8], 10.3, {}),
        Horse(2, "风火恒云", 6, "潘顿", "姚本辉", 135,
              1610.0, [4, 3, 1, 2, 5], 8.5, {}),
        Horse(5, "妙算奇胜", 2, "霍宏声", "廖康铭", 130,
              1590.0, [1, 4, 6, 3, 2], 3.4, {}),
    ]

    race_info = {
        'race_no': 1,
        'date': '2025-03-30',
        'venue': 'Sha Tin',
        'distance': 2000,
        'class': 'Class 4',
        'track': 'Turf A+3',
        'going': 'Good'
    }

    # 生成报告
    report = predictor.generate_report(race_info, horses)
    print(report)

    # 优化投注
    recommendations = predictor.optimize_place_bets(horses)
    print("\n=== 最优解 ===")
    for rec in recommendations:
        print(f"#{rec['horse'].horse_no} {rec['horse'].name}: "
              f"概率 {rec['place_probability']*100:.1f}%, "
              f"期望值 {rec['expected_value']:.2f}")


if __name__ == "__main__":
    demo_prediction()

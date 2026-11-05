#!/usr/bin/env python3
"""
香港赛马三重彩/四重彩预测系统
整合数据采集、特征工程、排序模型和投注建议生成
"""

import json
import math
import re
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from collections import defaultdict
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class RaceInfo:
    """赛事信息"""
    date: str
    venue: str
    race_number: int
    distance: int
    track_condition: str
    horses: List[Dict]


@dataclass
class HorseRecord:
    """马匹历史记录"""
    horse_id: str
    horse_name: str
    races: List[Dict]  # {date, position, distance, track, odds, time}


@dataclass
class PredictionResult:
    """预测结果"""
    model_type: str
    horse_strengths: Dict[str, float]
    top_k_trio: List[Tuple[str, float]]  # (排列, 概率)
    top_k_quartet: List[Tuple[str, float]]
    betting_advice: List[Dict]


class DataCollector:
    """数据采集器 - 支持多种数据源"""

    def __init__(self):
        self.hkjc_base_url = "https://www.hkjc.com"
        self.data_cache = {
            'races': [],
            'horses': {},
            'jockeys': {},
            'trainers': {}
        }

    def collect_race_data(self, start_date: str, end_date: str) -> List[Dict]:
        """
        从 HKJC 采集赛事数据
        注意：实际部署时需要配置官方 API 或网页爬取逻辑
        此处提供模拟数据结构作为参考
        """
        logger.info(f"采集 {start_date} 至 {end_date} 的赛事数据")

        # 模拟数据结构
        # 实际实现中需要根据 HKJC 的数据格式进行调整
        sample_race = {
            'date': start_date,
            'venue': '沙田',
            'race_number': 1,
            'distance': 1200,
            'track_condition': '好地',
            'horses': [
                {
                    'horse_id': 'H001',
                    'horse_name': 'XX之星',
                    'draw': 1,
                    'jockey': 'A',
                    'trainer': 'T1',
                    'weight': 123,
                    'gear': 'B',
                    'rating': 85
                }
            ],
            'results': {
                'H001': 1,
                'H002': 2,
                'H003': 3,
                'H004': 4
            }
        }

        return [sample_race]

    def load_from_csv(self, file_path: str) -> List[Dict]:
        """从 CSV 文件加载数据"""
        import csv

        logger.info(f"从 {file_path} 加载数据")
        races = []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                # 解析 CSV 数据
                # 返回格式化的赛事数据
                pass
        except Exception as e:
            logger.error(f"加载 CSV 失败: {e}")

        return races

    def validate_data(self, data: List[Dict]) -> bool:
        """验证数据完整性"""
        required_fields = ['date', 'race_number', 'horses', 'results']

        for race in data:
            for field in required_fields:
                if field not in race:
                    logger.warning(f"赛事数据缺少必要字段: {field}")
                    return False

            if len(race['horses']) < 4:
                logger.warning(f"赛事马匹数量不足: {len(race['horses'])}")
                return False

        return True


class FeatureEngineer:
    """特征工程模块"""

    def __init__(self, decay_factor: float = 0.9):
        self.decay_factor = decay_factor  # 时序衰减因子

    def compute_all_features(self, races: List[Dict]) -> Dict[str, Dict]:
        """
        计算所有马匹特征
        返回: {horse_id: {feature_name: value}}
        """
        logger.info(f"计算 {len(races)} 场赛事的特征")

        # 构建马匹历史记录
        horse_history = self._build_horse_history(races)

        # 计算各类特征
        features = {}
        for horse_id, history in horse_history.items():
            features[horse_id] = {
                **self._compute_recency_features(history),
                **self._compute_head_to_head_features(history, horse_history),
                **self._compute_track_adaptation_features(history),
                **self._compute_form_features(history)
            }

        return features

    def _build_horse_history(self, races: List[Dict]) -> Dict[str, List[Dict]]:
        """构建马匹历史记录"""
        history = defaultdict(list)

        for race in sorted(races, key=lambda x: x['date']):
            results = race.get('results', {})
            for horse_id, position in results.items():
                record = {
                    'date': race['date'],
                    'venue': race['venue'],
                    'distance': race['distance'],
                    'position': position,
                    'track_condition': race.get('track_condition', '未知'),
                    'horses_count': len(race['horses'])
                }
                history[horse_id].append(record)

        return dict(history)

    def _compute_recency_features(self, history: List[Dict]) -> Dict[str, float]:
        """计算时序衰减特征"""
        if not history:
            return {
                'recent_3_avg_position': 0.5,
                'recent_5_avg_position': 0.5,
                'decay_weighted_position': 0.5,
                'total_races': 0
            }

        # 最近 N 场平均排名
        recent_3 = [h['position'] / h['horses_count'] for h in history[:3]]
        recent_5 = [h['position'] / h['horses_count'] for h in history[:5]]

        # 指数加权平均
        weights = [self.decay_factor ** i for i in range(len(history))]
        weights.reverse()
        weighted_pos = sum(h['position'] / h['horses_count'] * w
                          for h, w in zip(history, weights))
        weighted_pos /= sum(weights)

        return {
            'recent_3_avg_position': sum(recent_3) / len(recent_3) if recent_3 else 0.5,
            'recent_5_avg_position': sum(recent_5) / len(recent_5) if recent_5 else 0.5,
            'decay_weighted_position': weighted_pos,
            'total_races': len(history)
        }

    def _compute_head_to_head_features(self, history: List[Dict],
                                       all_history: Dict) -> Dict[str, float]:
        """计算对比特征"""
        # 此处简化处理，实际需要更复杂的逻辑
        return {
            'win_rate': sum(1 for h in history if h['position'] == 1) / max(len(history), 1),
            'place_rate': sum(1 for h in history if h['position'] <= 3) / max(len(history), 1),
            'top4_rate': sum(1 for h in history if h['position'] <= 4) / max(len(history), 1)
        }

    def _compute_track_adaptation_features(self, history: List[Dict]) -> Dict[str, float]:
        """计算赛道适配特征"""
        # 按赛道分组统计
        track_stats = defaultdict(lambda: {'wins': 0, 'total': 0})

        for h in history:
            track = h['venue']
            track_stats[track]['total'] += 1
            if h['position'] == 1:
                track_stats[track]['wins'] += 1

        # 计算最佳赛道
        best_track_rate = 0
        for stats in track_stats.values():
            rate = stats['wins'] / stats['total']
            if rate > best_track_rate:
                best_track_rate = rate

        return {
            'best_track_win_rate': best_track_rate,
            'track_diversity': len(track_stats)
        }

    def _compute_form_features(self, history: List[Dict]) -> Dict[str, float]:
        """计算状态特征"""
        if len(history) < 3:
            return {'form_trend': 0, 'consistency': 0}

        # 趋势：最近表现 vs 历史平均
        recent = sum(h['position'] for h in history[:3]) / 3
        overall = sum(h['position'] for h in history) / len(history)
        trend = (overall - recent) / max(overall, 1)

        # 一致性：排名标准差
        positions = [h['position'] / h['horses_count'] for h in history[:5]]
        mean_pos = sum(positions) / len(positions)
        variance = sum((p - mean_pos) ** 2 for p in positions) / len(positions)
        consistency = 1 / (1 + math.sqrt(variance))

        return {
            'form_trend': trend,
            'consistency': consistency
        }


class BradleyTerryModel:
    """Bradley-Terry 排序模型"""

    def __init__(self, max_iterations: int = 100, tolerance: float = 1e-6):
        self.max_iterations = max_iterations
        self.tolerance = tolerance
        self.strengths = {}

    def train(self, races: List[Dict]) -> Dict[str, float]:
        """
        训练 Bradley-Terry 模型
        使用最大似然估计求解马匹强度参数
        """
        logger.info("训练 Bradley-Terry 模型")

        # 统计成对比较结果
        wins = defaultdict(lambda: defaultdict(int))
        total = defaultdict(lambda: defaultdict(int))

        for race in races:
            results = race.get('results', {})
            horse_positions = {v: k for k, v in results.items()}

            # 记录每对马匹的胜负
            for pos1 in range(1, len(horse_positions)):
                for pos2 in range(pos1 + 1, len(horse_positions) + 1):
                    horse1 = horse_positions.get(pos1)
                    horse2 = horse_positions.get(pos2)
                    if horse1 and horse2:
                        wins[horse1][horse2] += 1
                        total[horse1][horse2] += 1
                        total[horse2][horse1] += 1

        # 初始化强度参数
        all_horses = set(wins.keys()) | set(total.keys())
        strengths = {h: 1.0 for h in all_horses}

        # Newton-Raphson 迭代
        for iteration in range(self.max_iterations):
            new_strengths = {}
            max_change = 0

            for horse in all_horses:
                gradient = 0
                hessian = 0

                for opponent in all_horses:
                    if horse == opponent:
                        continue

                    w = wins[horse].get(opponent, 0) + wins[opponent].get(horse, 0)
                    t = total[horse].get(opponent, 0) + total[opponent].get(horse, 0)

                    if t > 0:
                        prob = strengths[horse] / (strengths[horse] + strengths[opponent])
                        gradient += w - t * prob
                        hessian -= t * strengths[opponent] / (strengths[horse] + strengths[opponent]) ** 2

                if abs(hessian) > 1e-10:
                    new_strength = strengths[horse] - gradient / hessian
                    new_strength = max(0.1, new_strength)  # 防止负值
                    new_strengths[horse] = new_strength
                    max_change = max(max_change, abs(new_strength - strengths[horse]))
                else:
                    new_strengths[horse] = strengths[horse]

            # 归一化
            sum_strengths = sum(new_strengths.values())
            for horse in new_strengths:
                new_strengths[horse] /= sum_strengths * len(new_strengths)

            strengths = new_strengths

            if max_change < self.tolerance:
                logger.info(f"模型收敛，迭代 {iteration + 1} 次")
                break

        self.strengths = strengths
        return strengths

    def predict_probabilities(self, horse_ids: List[str]) -> Dict[Tuple, float]:
        """
        预测排列概率分布
        返回: {(horse1, horse2, horse3): probability}
        """
        from itertools import permutations

        if not self.strengths:
            logger.warning("模型未训练，先调用 train()")
            return {}

        # 计算 Plackett-Luce 概率
        probabilities = {}

        for perm in permutations(horse_ids, 3):
            prob = 1.0
            remaining = list(perm)

            for i in range(3):
                horse = remaining[i]
                denominator = sum(self.strengths.get(h, 0.1) for h in remaining)
                numerator = self.strengths.get(horse, 0.1)
                prob *= numerator / denominator

            probabilities[perm] = prob

        # 归一化
        total = sum(probabilities.values())
        if total > 0:
            probabilities = {k: v / total for k, v in probabilities.items()}

        return probabilities

    def get_top_k(self, horse_ids: List[str], k: int = 10) -> List[Tuple[Tuple, float]]:
        """获取 Top-K 概率排列"""
        probs = self.predict_probabilities(horse_ids)
        sorted_probs = sorted(probs.items(), key=lambda x: x[1], reverse=True)
        return sorted_probs[:k]


class EloRatingSystem:
    """Elo 评分系统"""

    def __init__(self, k_factor: float = 32, initial_rating: float = 1500):
        self.k_factor = k_factor
        self.initial_rating = initial_rating
        self.ratings = {}
        self.rating_history = defaultdict(list)

    def train(self, races: List[Dict]) -> Dict[str, float]:
        """训练 Elo 评分系统"""
        logger.info("训练 Elo 评分系统")

        # 初始化
        all_horses = set()
        for race in races:
            all_horses.update(race.get('results', {}).keys())

        for horse in all_horses:
            self.ratings[horse] = self.initial_rating

        # 处理每场比赛
        for race in sorted(races, key=lambda x: x['date']):
            results = race.get('results', {})

            # 计算预期分数并更新评分
            new_ratings = self.ratings.copy()

            for horse, position in results.items():
                expected = 0
                actual = 0

                for opp, opp_pos in results.items():
                    if horse == opp:
                        continue

                    # 预期分数
                    diff = self.ratings[horse] - self.ratings[opp]
                    expected += 1 / (1 + 10 ** (diff / 400))

                    # 实际分数（第一名=1，后面递减）
                    if position < opp_pos:
                        actual += 1

                opponents = len(results) - 1
                if opponents > 0:
                    expected /= opponents
                    actual /= opponents

                    # 更新评分
                    new_ratings[horse] += self.k_factor * (actual - expected)

            self.ratings = new_ratings

            # 记录历史
            for horse in results.keys():
                self.rating_history[horse].append({
                    'date': race['date'],
                    'rating': self.ratings[horse]
                })

        return self.ratings

    def predict_win_probability(self, horse1: str, horse2: str) -> float:
        """预测马匹1战胜马匹2的概率"""
        r1 = self.ratings.get(horse1, self.initial_rating)
        r2 = self.ratings.get(horse2, self.initial_rating)

        return 1 / (1 + 10 ** ((r2 - r1) / 400))


class BettingAdvisor:
    """投注建议生成器"""

    def __init__(self, tax_rate: float = 0.18, min_ev_threshold: float = 0.8):
        self.tax_rate = tax_rate  # 香港马会抽水约18%
        self.min_ev_threshold = min_ev_threshold

    def generate_trio_advice(self, probabilities: Dict[Tuple, float],
                             odds: Optional[Dict[str, float]] = None) -> List[Dict]:
        """
        生成三重彩投注建议
        probabilities: {(h1, h2, h3): prob}
        odds: {排列: 赔率}
        """
        advice = []

        # 按概率排序
        sorted_probs = sorted(probabilities.items(),
                             key=lambda x: x[1], reverse=True)

        for i, (perm, prob) in enumerate(sorted_probs[:20], 1):
            # 计算期望值
            if odds and perm in odds:
                net_odds = odds[perm] * (1 - self.tax_rate) - 1
                expected_value = prob * net_odds - (1 - prob) * 1
            else:
                expected_value = None

            # 推荐等级
            if expected_value and expected_value > 0.5:
                recommendation = '高'
            elif expected_value and expected_value > 0:
                recommendation = '中'
            else:
                recommendation = '低'

            advice.append({
                'rank': i,
                'combination': f"{perm[0]}-{perm[1]}-{perm[2]}",
                'probability': f"{prob * 100:.2f}%",
                'expected_value': f"{expected_value:.3f}" if expected_value else 'N/A',
                'recommendation': recommendation
            })

        return advice

    def generate_quartet_advice(self, probabilities: Dict[Tuple, float],
                                odds: Optional[Dict[str, float]] = None) -> List[Dict]:
        """生成四重彩投注建议"""
        advice = []

        sorted_probs = sorted(probabilities.items(),
                             key=lambda x: x[1], reverse=True)

        for i, (perm, prob) in enumerate(sorted_probs[:20], 1):
            if odds and perm in odds:
                net_odds = odds[perm] * (1 - self.tax_rate) - 1
                expected_value = prob * net_odds - (1 - prob) * 1
            else:
                expected_value = None

            if expected_value and expected_value > 0.5:
                recommendation = '高'
            elif expected_value and expected_value > 0:
                recommendation = '中'
            else:
                recommendation = '低'

            advice.append({
                'rank': i,
                'combination': f"{perm[0]}-{perm[1]}-{perm[2]}-{perm[3]}",
                'probability': f"{prob * 100:.4f}%",
                'expected_value': f"{expected_value:.3f}" if expected_value else 'N/A',
                'recommendation': recommendation
            })

        return advice

    def generate_coverage_strategy(self, probabilities: Dict[Tuple, float],
                                   budget: float = 100,
                                   coverage_rate: float = 0.5) -> Dict:
        """
        生成覆盖策略
        覆盖概率总和达到 coverage_rate 的最少组合
        """
        sorted_probs = sorted(probabilities.items(),
                             key=lambda x: x[1], reverse=True)

        total_prob = 0
        selected = []
        remaining_budget = budget

        for perm, prob in sorted_probs:
            if total_prob >= coverage_rate:
                break

            # 每注10港币
            bet_amount = 10
            if remaining_budget >= bet_amount:
                selected.append({
                    'combination': perm,
                    'probability': prob,
                    'bet': bet_amount
                })
                total_prob += prob
                remaining_budget -= bet_amount

        return {
            'total_coverage': f"{total_prob * 100:.1f}%",
            'total_bet': budget - remaining_budget,
            'combinations': selected
        }


class HKRacingPredictor:
    """主预测类 - 整合所有模块"""

    def __init__(self, model_type: str = 'bt'):
        self.model_type = model_type
        self.data_collector = DataCollector()
        self.feature_engineer = FeatureEngineer()

        if model_type == 'bt':
            self.model = BradleyTerryModel()
        elif model_type == 'elo':
            self.model = EloRatingSystem()
        else:
            raise ValueError(f"不支持的模型类型: {model_type}")

        self.betting_advisor = BettingAdvisor()
        self.features = {}

    def full_pipeline(self, races: List[Dict],
                     target_horses: List[str],
                     top_k: int = 10) -> PredictionResult:
        """
        完整预测流程
        1. 数据验证
        2. 特征工程
        3. 模型训练
        4. 预测生成
        5. 投注建议
        """
        logger.info("开始完整预测流程")

        # 1. 数据验证
        if not self.data_collector.validate_data(races):
            logger.warning("数据验证未完全通过，继续处理...")

        # 2. 特征工程
        self.features = self.feature_engineer.compute_all_features(races)
        logger.info(f"特征计算完成，共 {len(self.features)} 匹马")

        # 3. 模型训练
        self.model.train(races)
        logger.info(f"模型训练完成，使用模型: {self.model_type}")

        # 4. 预测生成
        if self.model_type == 'bt':
            top_trio = self.model.get_top_k(target_horses, top_k)
            # 生成四重彩预测
            from itertools import permutations
            top_quartet = []
            for perm in permutations(target_horses, 4):
                probs = self.model.predict_probabilities(list(perm)[:3])
                top_quartet.append((perm, probs.get(tuple(list(perm)[:3]), 0)))
            top_quartet.sort(key=lambda x: x[1], reverse=True)
            top_quartet = top_quartet[:top_k]
        else:
            top_trio = []
            top_quartet = []

        # 5. 投注建议
        trio_advice = self.betting_advisor.generate_trio_advice(
            dict(top_trio) if isinstance(top_trio[0], tuple) else
            {k: v for k, v in [(t[0], t[1]) for t in top_trio]}
        )
        quartet_advice = self.betting_advisor.generate_quartet_advice(
            dict(top_quartet) if top_quartet else {}
        )

        return PredictionResult(
            model_type=self.model_type,
            horse_strengths=self.model.strengths,
            top_k_trio=top_trio,
            top_k_quartet=top_quartet,
            betting_advice=trio_advice + quartet_advice
        )

    def predict(self, race: Dict, history_races: List[Dict],
               top_k: int = 10) -> Dict:
        """
        单一赛事预测接口
        race: 当前赛事信息
        history_races: 历史赛事数据
        """
        # 获取参赛马匹列表
        target_horses = [h['horse_id'] for h in race['horses']]

        # 合并历史数据
        all_races = history_races + [race]

        # 执行完整流程
        result = self.full_pipeline(all_races, target_horses, top_k)

        return {
            'model_type': result.model_type,
            'horse_strengths': result.horse_strengths,
            'trio_predictions': result.top_k_trio[:top_k],
            'quartet_predictions': result.top_k_quartet[:top_k],
            'betting_advice': result.betting_advice
        }


def create_predictor(model_type: str = 'bt') -> HKRacingPredictor:
    """工厂函数 - 创建预测器实例"""
    return HKRacingPredictor(model_type=model_type)


# CLI 入口
if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='香港赛马预测系统')
    parser.add_argument('--model', choices=['bt', 'elo'], default='bt',
                       help='选择预测模型')
    parser.add_argument('--data', type=str, help='历史数据文件路径')
    parser.add_argument('--output', type=str, default='prediction_result.json',
                       help='输出文件路径')

    args = parser.parse_args()

    # 创建预测器
    predictor = create_predictor(args.model)

    # 示例：使用模拟数据
    sample_race = {
        'date': '2024-01-01',
        'venue': '沙田',
        'race_number': 1,
        'distance': 1200,
        'track_condition': '好地',
        'horses': [
            {'horse_id': 'H001', 'horse_name': 'XX之星'},
            {'horse_id': 'H002', 'horse_name': 'YY飞鹰'},
            {'horse_id': 'H003', 'horse_name': 'ZZ闪电'},
            {'horse_id': 'H004', 'horse_name': 'AA旋风'}
        ],
        'results': {
            'H001': 1,
            'H002': 2,
            'H003': 3,
            'H004': 4
        }
    }

    # 生成预测结果
    result = predictor.predict(sample_race, [])
    print(json.dumps(result, indent=2, ensure_ascii=False))

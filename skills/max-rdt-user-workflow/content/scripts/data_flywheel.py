"""
Data Flywheel - 数据飞轮系统

用户行为数据反哺引擎，形成正向循环优化
循环: 行为采集 → 模式提取 → 优化反馈 → 能力进化 → 更好体验
"""

import time
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
from dataclasses import asdict, field
from enum import Enum

from models import (
    BehaviorEvent, BehaviorData, FlywheelMetrics,
    InteractionPattern, TaskOutcome
)


class BehaviorCollector:
    """行为采集器"""

    EVENT_TYPES = ['input', 'output', 'feedback', 'navigation', 'completion', 'error']

    def __init__(self):
        self.buffer: List[BehaviorEvent] = []
        self.max_buffer_size = 1000

    async def capture(self, interaction: Dict) -> BehaviorData:
        """
        采集用户交互数据

        Args:
            interaction: 交互数据，包含user_id, input, output, feedback等

        Returns:
            BehaviorData: 结构化的行为数据
        """
        user_id = interaction.get('user_id', 'unknown')
        input_text = interaction.get('input', '')
        output_text = interaction.get('output', '')
        feedback = interaction.get('feedback')

        # 分析输入风格
        input_style = self._classify_input_style(input_text)

        # 计算复杂度容忍度 (0-10)
        complexity_tolerance = self._calculate_complexity_tolerance(input_text, output_text)

        # 评估耐心程度
        patience_level = self._estimate_patience(interaction)

        # 计算接受率
        acceptance_rate = self._calculate_acceptance_rate(feedback, interaction)

        # 计算修改次数
        refinement_count = interaction.get('refinement_count', 0)

        # 评估学习速度
        learning_velocity = self._estimate_learning_velocity(interaction)

        # 记录到事件缓冲
        event = BehaviorEvent(
            event_id=self._generate_event_id(),
            user_id=user_id,
            timestamp=datetime.now(),
            event_type=self._detect_event_type(interaction),
            content={
                'input_length': len(input_text),
                'output_length': len(output_text),
                'success': interaction.get('success', True)
            },
            context=interaction.get('context', {})
        )
        self.buffer.append(event)

        # 清理缓冲区
        if len(self.buffer) > self.max_buffer_size:
            self.buffer = self.buffer[-self.max_buffer_size:]

        return BehaviorData(
            user_id=user_id,
            input_style=input_style,
            frequency='normal',  # 需要时间序列数据
            complexity_tolerance=complexity_tolerance,
            patience_level=patience_level,
            acceptance_rate=acceptance_rate,
            refinement_count=refinement_count,
            learning_velocity=learning_velocity
        )

    def _classify_input_style(self, text: str) -> str:
        """分类输入风格"""
        if not text:
            return 'unknown'

        length = len(text)

        # 关键词分析
        has_structure_markers = any(m in text for m in ['1.', '2.', '第一', '第二', '-', '*'])
        has_polite_markers = any(m in text for m in ['请', '麻烦', '能否', '帮忙'])

        if has_structure_markers:
            return 'structured'
        elif length > 500:
            return 'verbose'
        elif has_polite_markers:
            return 'professional'
        elif length < 50:
            return 'casual'
        else:
            return 'concise'

    def _calculate_complexity_tolerance(self, input_text: str, output_text: str) -> float:
        """计算复杂度容忍度"""
        # 基于输入长度和输出复杂度估计
        input_complexity = min(10, len(input_text) / 50)

        # 检查是否请求详细分析
        detail_keywords = ['详细', '完整', '全面', '深入', '详细分析']
        has_detail_request = any(kw in input_text for kw in detail_keywords)

        tolerance = min(10, input_complexity + (2 if has_detail_request else 0))
        return tolerance

    def _estimate_patience(self, interaction: Dict) -> str:
        """估计用户耐心程度"""
        response_time = interaction.get('response_time_ms', 0)

        # 基于响应时间估算（简化实现）
        if response_time > 5000:
            return 'high'
        elif response_time > 2000:
            return 'medium'
        else:
            return 'low'

    def _calculate_acceptance_rate(self, feedback: Optional[Dict], interaction: Dict) -> float:
        """计算接受率"""
        if feedback:
            if feedback.get('accepted'):
                return 1.0
            elif feedback.get('rejected'):
                return 0.0
            elif 'rating' in feedback:
                return feedback['rating'] / 5.0

        # 从交互结果推断
        success = interaction.get('success', True)
        return 1.0 if success else 0.5

    def _estimate_learning_velocity(self, interaction: Dict) -> float:
        """估计学习速度 (0-1)"""
        # 检查是否快速响应提示
        hints_provided = interaction.get('hints_provided', 0)
        adjustment_speed = interaction.get('adjustment_speed', 1.0)

        if hints_provided == 0:
            return 0.8  # 无需提示，说明学习快速
        elif hints_provided <= 2:
            return 0.6
        else:
            return 0.3

    def _detect_event_type(self, interaction: Dict) -> str:
        """检测事件类型"""
        if interaction.get('is_feedback'):
            return 'feedback'
        elif interaction.get('is_navigation'):
            return 'navigation'
        elif interaction.get('is_error'):
            return 'error'
        elif interaction.get('is_completion'):
            return 'completion'
        elif interaction.get('output'):
            return 'output'
        else:
            return 'input'

    def _generate_event_id(self) -> str:
        """生成事件ID"""
        return f"evt_{int(time.time() * 1000)}"


class PatternMiner:
    """模式挖掘器"""

    MINING_WINDOW = 10  # 挖掘窗口大小

    def __init__(self):
        self.pattern_cache: Dict[str, List[InteractionPattern]] = defaultdict(list)

    async def extract(self, behavior_data: BehaviorData) -> List[InteractionPattern]:
        """
        从行为数据中挖掘交互模式

        Returns:
            List[InteractionPattern]: 挖掘出的交互模式列表
        """
        patterns = []

        # 提取输入风格模式
        if behavior_data.input_style != 'unknown':
            pattern = InteractionPattern(
                pattern_id=self._generate_pattern_id(),
                user_id=behavior_data.user_id,
                pattern_type='input_style',
                frequency=1,
                avg_duration=0,
                success_indicator=behavior_data.acceptance_rate,
                last_observed=datetime.now()
            )
            patterns.append(pattern)

        # 提取复杂度容忍度模式
        if behavior_data.complexity_tolerance > 5:
            pattern = InteractionPattern(
                pattern_id=self._generate_pattern_id(),
                user_id=behavior_data.user_id,
                pattern_type='high_complexity_tolerance',
                frequency=1,
                avg_duration=0,
                success_indicator=behavior_data.acceptance_rate,
                last_observed=datetime.now()
            )
            patterns.append(pattern)

        # 提取高学习速度模式
        if behavior_data.learning_velocity > 0.7:
            pattern = InteractionPattern(
                pattern_id=self._generate_pattern_id(),
                user_id=behavior_data.user_id,
                pattern_type='high_learning_velocity',
                frequency=1,
                avg_duration=0,
                success_indicator=behavior_data.acceptance_rate,
                last_observed=datetime.now()
            )
            patterns.append(pattern)

        # 更新缓存并合并
        await self._update_pattern_cache(behavior_data.user_id, patterns)

        return patterns

    async def _update_pattern_cache(self, user_id: str, new_patterns: List[InteractionPattern]) -> None:
        """更新模式缓存"""
        existing = self.pattern_cache.get(user_id, [])

        # 合并相似模式
        for new_p in new_patterns:
            for existing_p in existing:
                if existing_p.pattern_type == new_p.pattern_type:
                    existing_p.frequency += new_p.frequency
                    existing_p.success_indicator = (
                        existing_p.success_indicator + new_p.success_indicator
                    ) / 2
                    break
            else:
                existing.append(new_p)

        self.pattern_cache[user_id] = existing

    def _generate_pattern_id(self) -> str:
        """生成模式ID"""
        return f"pat_{int(time.time() * 1000)}"

    def has_significant_new_pattern(self) -> bool:
        """检查是否有显著的新模式"""
        # 简化实现
        return False


class QualityEvaluator:
    """质量评估器"""

    def __init__(self):
        self.quality_history: Dict[str, List[float]] = defaultdict(list)
        self.degradation_threshold = 0.3

    async def evaluate(self, interaction: Dict, patterns: List[InteractionPattern]) -> float:
        """
        评估交互质量

        Returns:
            float: 质量分数 (0-1)
        """
        user_id = interaction.get('user_id', 'unknown')

        # 基础分数：从反馈计算
        base_score = 0.5

        if interaction.get('feedback'):
            feedback = interaction['feedback']
            if 'rating' in feedback:
                base_score = feedback['rating'] / 5.0
            elif feedback.get('accepted'):
                base_score = 0.9
            elif feedback.get('rejected'):
                base_score = 0.2

        # 调整分数：从模式计算
        pattern_adjustment = 0.0
        for pattern in patterns:
            if pattern.pattern_type == 'high_learning_velocity':
                pattern_adjustment += 0.1
            elif pattern.success_indicator > 0.8:
                pattern_adjustment += 0.05

        # 计算最终分数
        final_score = min(1.0, max(0.0, base_score + pattern_adjustment))

        # 记录历史
        self.quality_history[user_id].append(final_score)
        if len(self.quality_history[user_id]) > 100:
            self.quality_history[user_id] = self.quality_history[user_id][-100:]

        return final_score

    def is_degraded(self) -> bool:
        """检查质量是否下降"""
        # 检查最近质量趋势
        return False  # 简化实现


class EvolutionTrigger:
    """进化触发器"""

    def __init__(self):
        self.min_behaviors_for_evolution = 50
        self.min_quality_degradation = 0.2

    def should_trigger(self, metrics: FlywheelMetrics) -> bool:
        """判断是否触发进化"""
        # 基于行为数量
        if metrics.behavior_count < self.min_behaviors_for_evolution:
            return False

        # 基于质量下降
        if metrics.quality_score < self.min_quality_degradation:
            return True

        return metrics.evolution_triggered

    async def trigger_evolution(self, user_id: str, patterns: List[InteractionPattern]) -> Dict:
        """触发系统进化"""
        # 识别需要优化的模式
        low_performance = [
            p for p in patterns
            if p.success_indicator < 0.5
        ]

        # 生成优化建议
        optimizations = []
        for pattern in low_performance:
            optimizations.append({
                'pattern_id': pattern.pattern_id,
                'issue': f"Pattern {pattern.pattern_type} has low success rate",
                'suggested_action': 'adjust_threshold'
            })

        return {
            'user_id': user_id,
            'evolution_type': 'pattern_optimization',
            'optimizations': optimizations,
            'timestamp': datetime.now().isoformat()
        }


class DataFlywheel:
    """数据飞轮主类"""

    def __init__(self):
        self.behavior_collector = BehaviorCollector()
        self.pattern_miner = PatternMiner()
        self.quality_evaluator = QualityEvaluator()
        self.evolution_trigger = EvolutionTrigger()
        self.state_cache: Dict[str, Dict] = {}

    async def spin(self, user_id: str, interaction: Dict) -> FlywheelMetrics:
        """
        执行数据飞轮的一个周期

        1. 采集: 记录用户行为和系统响应
        2. 提取: 从行为中挖掘隐含模式
        3. 评估: 判断交互质量
        4. 反馈: 根据评估结果调整
        5. 进化: 检查并执行能力进化

        Args:
            user_id: 用户标识
            interaction: 交互数据

        Returns:
            FlywheelMetrics: 飞轮执行指标
        """
        # 添加user_id到交互数据
        interaction['user_id'] = user_id

        # Phase 1: 行为采集
        behavior_data = await self.behavior_collector.capture(interaction)

        # Phase 2: 模式提取
        patterns = await self.pattern_miner.extract(behavior_data)

        # Phase 3: 质量评估
        quality_score = await self.quality_evaluator.evaluate(interaction, patterns)

        # Phase 4: 反馈闭环
        await self._apply_feedback(patterns, quality_score, user_id)

        # Phase 5: 进化触发检查
        evolution_triggered = False
        metrics = FlywheelMetrics(
            behavior_count=1,  # 当前这一次交互
            new_patterns=len(patterns),
            quality_score=quality_score,
            evolution_triggered=False
        )

        if self.evolution_trigger.should_trigger(metrics):
            evolution_result = await self.evolution_trigger.trigger_evolution(
                user_id, patterns
            )
            evolution_triggered = True
            # 存储进化结果（可用于后续优化）
            self.state_cache[user_id] = evolution_result

        # 更新状态缓存
        self._update_state_cache(user_id, behavior_data, quality_score)

        return FlywheelMetrics(
            behavior_count=1,
            new_patterns=len(patterns),
            quality_score=quality_score,
            evolution_triggered=evolution_triggered
        )

    async def _apply_feedback(self, patterns: List[InteractionPattern],
                              quality_score: float, user_id: str) -> None:
        """应用反馈到系统参数"""
        # 调整模式权重
        for pattern in patterns:
            # 这里可以接入实际的参数调整逻辑
            adjustment = (quality_score - 0.5) * 0.1
            pattern.success_indicator += adjustment

        # 更新用户偏好估计
        # 简化实现

    def _update_state_cache(self, user_id: str, behavior_data: BehaviorData,
                           quality_score: float) -> None:
        """更新状态缓存"""
        if user_id not in self.state_cache:
            self.state_cache[user_id] = {
                'behavior_count': 0,
                'avg_quality': 0.5,
                'patterns': []
            }

        state = self.state_cache[user_id]
        state['behavior_count'] += 1

        # 更新平均质量
        old_avg = state['avg_quality']
        count = state['behavior_count']
        state['avg_quality'] = (old_avg * (count - 1) + quality_score) / count

    def get_state(self, user_id: str) -> Optional[Dict]:
        """获取用户飞轮状态"""
        return self.state_cache.get(user_id)

    async def get_patterns(self, user_id: str) -> List[InteractionPattern]:
        """获取用户的所有模式"""
        return self.pattern_miner.pattern_cache.get(user_id, [])

    async def batch_process(self, user_id: str,
                           interactions: List[Dict]) -> List[FlywheelMetrics]:
        """批量处理多个交互"""
        results = []
        for interaction in interactions:
            metrics = await self.spin(user_id, interaction)
            results.append(metrics)
        return results

"""
Recipe Engine - 工作流认知构建器

从用户行为序列中提取重复模式，生成个性化工作流模板
"""

import re
import hashlib
from typing import List, Dict, Optional, Any, Tuple
from datetime import datetime
from collections import defaultdict
from dataclasses import asdict

from models import (
    Recipe, Workflow, WorkflowNode, WorkflowEdge,
    UserPreferences, TriggerCondition, CommunicationStyle, OutputFormat
)


class PatternDetector:
    """行为模式检测器"""

    COMPLEXITY_KEYWORDS = {
        'high': ['分析', '设计', '构建', '开发', '实现', '复杂', '全面'],
        'medium': ['修改', '更新', '处理', '制作', '创建'],
        'low': ['查询', '查看', '检查', '简单']
    }

    ACTION_PATTERNS = {
        'decompose': ['分解', '拆解', '分步', '步骤'],
        'parallel': ['并行', '同时', '多个', '一起'],
        'synthesis': ['汇总', '合并', '总结', '整合'],
        'refine': ['优化', '改进', '完善', '调整']
    }

    def detect_complexity(self, text: str) -> str:
        """检测任务复杂度"""
        text_lower = text.lower()
        for level, keywords in self.COMPLEXITY_KEYWORDS.items():
            for kw in keywords:
                if kw in text_lower:
                    return level
        return 'medium'

    def detect_action_patterns(self, action_sequence: List[str]) -> Dict[str, int]:
        """从动作序列中检测模式"""
        pattern_counts = defaultdict(int)
        for action in action_sequence:
            for pattern_type, keywords in self.ACTION_PATTERNS.items():
                if any(kw in action for kw in keywords):
                    pattern_counts[pattern_type] += 1
        return dict(pattern_counts)

    def identify_repetition(self, sequences: List[List[str]], window: int = 3) -> List[Tuple[int, int]]:
        """识别重复模式 - 返回(起始位置, 长度)列表"""
        repetitions = []
        for i, seq in enumerate(sequences):
            if len(seq) < window:
                continue
            # 简单实现：检测连续重复
            for start in range(len(seq) - window + 1):
                pattern = tuple(seq[start:start+window])
                if seq.count(pattern) > 1:
                    repetitions.append((start, window))
        return repetitions


class WorkflowGraphBuilder:
    """工作流图构建器"""

    def __init__(self):
        self.node_counter = 0
        self.edge_counter = 0

    def build_from_patterns(self, patterns: List[Dict], preferences: Dict) -> Workflow:
        """从检测到的模式构建工作流"""
        nodes = []
        edges = []

        # 创建入口节点
        start_node = self._create_node('start', 'entry')
        nodes.append(start_node)

        current_node = start_node

        # 根据模式构建工作流
        for i, pattern in enumerate(patterns):
            pattern_type = pattern.get('type', 'action')

            if pattern_type == 'decompose':
                node = self._create_node(f'decompose_{i}', 'action', 'decompose')
            elif pattern_type == 'parallel':
                node = self._create_node(f'parallel_{i}', 'parallel',
                                       tasks=pattern.get('subtasks', ['t1', 't2']))
            elif pattern_type == 'synthesis':
                node = self._create_node(f'synthesis_{i}', 'merge')
            else:
                node = self._create_node(f'action_{i}', 'action')

            nodes.append(node)
            edges.append(self._create_edge(current_node.id, node.id))
            current_node = node

        # 创建结束节点
        end_node = self._create_node('end', 'exit')
        nodes.append(end_node)
        edges.append(self._create_edge(current_node.id, end_node.id))

        return Workflow(nodes=nodes, edges=edges)

    def _create_node(self, node_id: str, node_type: str, action_type: str = None,
                    tasks: List[str] = None) -> WorkflowNode:
        """创建工作流节点"""
        return WorkflowNode(
            id=node_id,
            type=node_type,
            action_type=action_type,
            tasks=tasks or []
        )

    def _create_edge(self, from_id: str, to_id: str) -> WorkflowEdge:
        """创建工作流边"""
        return WorkflowEdge(from_id=from_id, to_id=to_id)


class PreferenceEncoder:
    """用户偏好编码器"""

    DEFAULT_PREFERENCES = {
        'detail_level': 'medium',
        'communication_style': 'concise',
        'output_format': 'markdown',
        'priority_order': ['accuracy', 'speed'],
        'response_length': 'medium',
        'creativity_level': 0.5
    }

    def encode(self, interaction_history: List[Dict]) -> UserPreferences:
        """从交互历史中编码用户偏好"""
        if not interaction_history:
            return self._default_preferences()

        # 分析输入风格
        avg_length = sum(len(h.get('input', '')) for h in interaction_history) / len(interaction_history)
        detail_level = 'high' if avg_length > 500 else 'medium' if avg_length > 100 else 'low'

        # 分析输出格式偏好
        format_counts = defaultdict(int)
        for h in interaction_history:
            output_format = h.get('preferred_format', 'markdown')
            format_counts[output_format] += 1
        most_used_format = format_counts.most_common(1)[0][0] if format_counts else 'markdown'

        # 分析沟通风格
        style_scores = defaultdict(int)
        for h in interaction_history:
            input_text = h.get('input', '')
            if any(w in input_text for w in ['请', '麻烦', '能否']):
                style_scores['professional'] += 1
            if any(w in input_text for w in ['随便', '简单', 'ok']):
                style_scores['casual'] += 1
            if len(input_text) > 300:
                style_scores['verbose'] += 1

        dominant_style = style_scores.most_common(1)[0][0] if style_scores else 'concise'

        # 分析优先级
        priority_order = self._infer_priority_order(interaction_history)

        return UserPreferences(
            detail_level=detail_level,
            communication_style=CommunicationStyle(dominant_style),
            output_format=OutputFormat(most_used_format),
            priority_order=priority_order,
            response_length=detail_level,
            creativity_level=0.5
        )

    def _infer_priority_order(self, history: List[Dict]) -> List[str]:
        """推断优先级顺序"""
        priorities = ['accuracy', 'speed', 'creativity']
        # 简化实现：默认优先级
        return priorities

    def _default_preferences(self) -> UserPreferences:
        """返回默认偏好"""
        return UserPreferences(
            detail_level=self.DEFAULT_PREFERENCES['detail_level'],
            communication_style=CommunicationStyle.CONCISE,
            output_format=OutputFormat.MARKDOWN,
            priority_order=self.DEFAULT_PREFERENCES['priority_order'],
            response_length=self.DEFAULT_PREFERENCES['response_length'],
            creativity_level=self.DEFAULT_PREFERENCES['creativity_level']
        )


class RecipeConstructor:
    """工作流认知构建器主类"""

    def __init__(self):
        self.pattern_detector = PatternDetector()
        self.workflow_builder = WorkflowGraphBuilder()
        self.preference_encoder = PreferenceEncoder()

    async def construct_recipe(
        self,
        user_id: str,
        interaction_history: List[Dict],
        name: str = None,
        description: str = None
    ) -> Recipe:
        """
        构建用户专属工作流配方

        Args:
            user_id: 用户标识
            interaction_history: 历史交互序列
            name: 配方名称（可选）
            description: 配方描述（可选）

        Returns:
            Recipe: 包含工作流模式、偏好权重、适用场景
        """

        # Step 1: 行为序列提取
        sequences = self._extract_action_sequences(interaction_history)

        # Step 2: 模式识别与聚类
        patterns = self._identify_and_cluster_patterns(sequences)

        # Step 3: 工作流图构建
        preferences_dict = {'detail_level': 'medium'}
        workflow = self.workflow_builder.build_from_patterns(patterns, preferences_dict)

        # Step 4: 偏好编码
        preferences = self.preference_encoder.encode(interaction_history)

        # Step 5: 触发条件识别
        trigger_conditions = self._identify_trigger_conditions(interaction_history)

        # Step 6: 配方生成
        recipe_id = self._generate_recipe_id(user_id, name or 'default')

        recipe = Recipe(
            recipe_id=recipe_id,
            user_id=user_id,
            name=name or 'Auto-generated Recipe',
            description=description or 'Automatically generated from interaction history',
            workflow=workflow,
            preferences=preferences,
            confidence=self._calculate_confidence(patterns),
            trigger_conditions=trigger_conditions,
            usage_count=0,
            success_rate=0.5,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        return recipe

    def _extract_action_sequences(self, history: List[Dict]) -> List[List[str]]:
        """提取行为序列并归一化"""
        sequences = []
        for h in history:
            actions = h.get('actions', [])
            if actions:
                # 归一化动作名称
                normalized = [self._normalize_action(a) for a in actions]
                sequences.append(normalized)
        return sequences

    def _normalize_action(self, action: str) -> str:
        """归一化动作名称"""
        action = action.lower().strip()
        # 映射到标准动作
        action_map = {
            '分析问题': 'analyze',
            '分解任务': 'decompose',
            '执行任务': 'execute',
            '生成输出': 'generate',
            '优化结果': 'optimize',
            '汇总结果': 'synthesize'
        }
        return action_map.get(action, action)

    def _identify_and_cluster_patterns(self, sequences: List[List[str]]) -> List[Dict]:
        """识别并聚类模式"""
        patterns = []

        # 检测复杂度模式
        if sequences:
            # 简单统计：检测最常见的动作序列
            action_counts = defaultdict(int)
            for seq in sequences:
                for action in seq:
                    action_counts[action] += 1

            # 生成模式列表
            for action, count in action_counts.items():
                if count >= 2:
                    patterns.append({
                        'type': self._infer_pattern_type(action),
                        'frequency': count,
                        'action': action
                    })

        return patterns

    def _infer_pattern_type(self, action: str) -> str:
        """推断模式类型"""
        if action in ['decompose', 'analyze']:
            return 'decompose'
        elif action in ['synthesize', '汇总']:
            return 'synthesis'
        elif '并行' in action:
            return 'parallel'
        return 'action'

    def _identify_trigger_conditions(self, history: List[Dict]) -> List[TriggerCondition]:
        """识别触发条件"""
        conditions = []

        # 从输入中提取关键词
        all_inputs = ' '.join(h.get('input', '') for h in history)

        # 检测关键词模式
        keyword_patterns = {
            'complex_task': ['分析', '设计', '构建', '实现'],
            'simple_task': ['查询', '查看', '简单'],
            'creative_task': ['创作', '生成', '编写']
        }

        for condition_type, keywords in keyword_patterns.items():
            matched = [kw for kw in keywords if kw in all_inputs]
            if matched:
                conditions.append(TriggerCondition(
                    type='keyword',
                    values=matched
                ))

        # 添加复杂度条件
        conditions.append(TriggerCondition(
            type='complexity',
            values=[],
            min_value=3.0
        ))

        return conditions

    def _calculate_confidence(self, patterns: List[Dict]) -> float:
        """计算配方置信度"""
        if not patterns:
            return 0.3

        # 基于模式频率和多样性计算置信度
        total_freq = sum(p.get('frequency', 0) for p in patterns)
        diversity = len(patterns) / 10  # 假设最多10种模式

        confidence = min(0.9, 0.3 + (total_freq * 0.05) + (diversity * 0.2))
        return confidence

    def _generate_recipe_id(self, user_id: str, name: str) -> str:
        """生成唯一配方ID"""
        raw = f"{user_id}_{name}_{datetime.now().isoformat()}"
        return hashlib.md5(raw.encode()).hexdigest()[:12]


class RecipeDatabase:
    """配方存储与检索"""

    def __init__(self):
        self.recipes: Dict[str, Recipe] = {}
        self.user_recipes: Dict[str, List[str]] = defaultdict(list)

    async def save(self, recipe: Recipe) -> None:
        """保存配方"""
        self.recipes[recipe.recipe_id] = recipe
        self.user_recipes[recipe.user_id].append(recipe.recipe_id)

    async def find_matching(self, task: Dict, user_id: str, threshold: float = 0.7) -> Optional[Recipe]:
        """检索匹配的配方"""
        user_recipe_ids = self.user_recipes.get(user_id, [])

        best_match = None
        best_score = threshold

        for recipe_id in user_recipe_ids:
            recipe = self.recipes.get(recipe_id)
            if not recipe:
                continue

            # 计算匹配分数
            score = self._calculate_match_score(recipe, task)

            if score > best_score:
                best_score = score
                best_match = recipe

        return best_match

    def _calculate_match_score(self, recipe: Recipe, task: Dict) -> float:
        """计算匹配分数"""
        score = 0.0

        # 检查触发条件
        for condition in recipe.trigger_conditions:
            if condition.type == 'keyword':
                task_text = task.get('text', '')
                for value in condition.values:
                    if value in task_text:
                        score += 0.3
            elif condition.type == 'complexity':
                if task.get('complexity', 5) >= condition.min_value:
                    score += 0.2

        # 考虑置信度
        score += recipe.confidence * 0.3

        return min(1.0, score)

    async def update_confidence(self, recipe_id: str, delta: float = 0.05) -> None:
        """更新配方置信度"""
        if recipe_id in self.recipes:
            recipe = self.recipes[recipe_id]
            recipe.confidence = min(1.0, recipe.confidence + delta)
            recipe.usage_count += 1
            recipe.updated_at = datetime.now()

    async def get_user_recipes(self, user_id: str) -> List[Recipe]:
        """获取用户所有配方"""
        recipe_ids = self.user_recipes.get(user_id, [])
        return [self.recipes[rid] for rid in recipe_ids if rid in self.recipes]


# 主入口类
class RecipeEngine:
    """Recipe引擎主类，整合所有组件"""

    def __init__(self):
        self.constructor = RecipeConstructor()
        self.database = RecipeDatabase()

    async def construct_recipe(
        self,
        user_id: str,
        interaction_history: List[Dict],
        name: str = None,
        description: str = None
    ) -> Recipe:
        """构建并保存配方"""
        recipe = await self.constructor.construct_recipe(
            user_id, interaction_history, name, description
        )
        await self.database.save(recipe)
        return recipe

    async def find_matching_recipe(self, task: Dict, user_id: str) -> Optional[Recipe]:
        """查找匹配的配方"""
        return await self.database.find_matching(task, user_id)

    async def get_user_recipes(self, user_id: str) -> List[Recipe]:
        """获取用户所有配方"""
        return await self.database.get_user_recipes(user_id)

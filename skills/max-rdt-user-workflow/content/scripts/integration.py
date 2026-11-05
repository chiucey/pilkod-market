"""
Max-RDT 集成层 - 与 Max-HCD 复合体系统集成

将 Recipe、Data Flywheel、Taste Standard 整合为统一的感知增强层
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import asdict

from models import (
    Recipe, TasteProfile, FlywheelMetrics, EnhancedTaskContext,
    TaskOutcome, EvaluationResult
)
from recipe_engine import RecipeEngine, RecipeDatabase
from data_flywheel import DataFlywheel
from taste_engine import TasteStandard


class MaxRDTLayer:
    """
    Max-RDT 作为 Max-HCD 的增强层

    位置: 位于Hermes(通信层)和DeerFlow(流程层)之间
    作用: 在任务执行前注入用户个性化认知
    """

    def __init__(self, hcd_composite=None):
        """
        初始化 Max-RDT 层

        Args:
            hcd_composite: 现有的 Max-HCD 复合体实例（可选）
        """
        self.hcd = hcd_composite

        # 初始化核心组件
        self.recipe_engine = RecipeEngine()
        self.data_flywheel = DataFlywheel()
        self.taste_engine = TasteStandard()

        # 内部状态
        self._initialized = True

    async def enhance_task(
        self,
        task: Dict[str, Any],
        user_id: str
    ) -> EnhancedTaskContext:
        """
        用用户专属认知增强任务

        流程:
        1. 检索匹配Recipe
        2. 加载Taste Profile
        3. 注入到任务上下文

        Args:
            task: 原始任务描述
            user_id: 用户标识

        Returns:
            EnhancedTaskContext: 增强后的任务上下文
        """
        # Step 1: 检索 Recipe
        recipe = await self.recipe_engine.find_matching_recipe(task, user_id)

        # Step 2: 获取 Taste Profile
        taste_profile = self.taste_engine.get_taste_profile(user_id)

        # Step 3: 获取 Flywheel State
        flywheel_state = self.data_flywheel.get_state(user_id)

        # Step 4: 构建增强上下文
        recipe_dict = recipe.to_dict() if recipe else None

        taste_dict = None
        if taste_profile:
            taste_dict = {
                'domains': {
                    domain: {
                        'quality_standards': [
                            {'dimension': s.dimension, 'weight': s.weight}
                            for s in dt.quality_standards
                        ],
                        'style_preferences': asdict(dt.style_preferences),
                        'confidence': dt.confidence
                    }
                    for domain, dt in taste_profile.domains.items()
                },
                'cross_domain_consistency': taste_profile.cross_domain_consistency,
                'learning_confidence': taste_profile.learning_confidence
            }

        # 计算增强置信度
        enhancement_confidence = 0.0
        if recipe:
            enhancement_confidence += 0.4 * recipe.confidence
        if taste_profile:
            enhancement_confidence += 0.3 * taste_profile.cross_domain_consistency
        if flywheel_state:
            enhancement_confidence += 0.3 * flywheel_state.get('avg_quality', 0.5)

        return EnhancedTaskContext(
            original_task=task,
            user_recipe=recipe_dict,
            taste_standards=taste_dict,
            flywheel_state=flywheel_state,
            enhancement_confidence=enhancement_confidence
        )

    async def record_outcome(
        self,
        task: Dict,
        result: Any,
        user_feedback: Optional[Dict],
        user_id: str
    ) -> TaskOutcome:
        """
        记录任务执行结果到数据飞轮

        Args:
            task: 原始任务
            result: 执行结果
            user_feedback: 用户反馈
            user_id: 用户标识

        Returns:
            TaskOutcome: 任务执行结果记录
        """
        # 执行 Flywheel 周期
        metrics = await self.data_flywheel.spin(
            user_id=user_id,
            interaction={
                'task': task,
                'result': result,
                'feedback': user_feedback,
                'success': user_feedback.get('accepted', True) if user_feedback else True
            }
        )

        # 获取关联的 Recipe
        recipe = await self.recipe_engine.find_matching_recipe(task, user_id)
        recipe_id = recipe.recipe_id if recipe else None

        # 评估输出品味
        taste_evaluation = None
        if user_feedback:
            taste_evaluation = await self.taste_engine.evaluate_output(
                output=result,
                context={'task': task, 'user_id': user_id},
                user_id=user_id
            )

            # 更新品味标准
            await self.taste_engine.update_from_feedback(
                output=result,
                user_feedback=user_feedback,
                context={'task': task}
            )

        # 更新 Recipe 置信度
        if recipe and metrics.quality_score > 0.8:
            await self.recipe_engine.database.update_confidence(recipe_id, delta=0.05)
        elif recipe and metrics.quality_score < 0.5:
            await self.recipe_engine.database.update_confidence(recipe_id, delta=-0.1)

        # 构建结果记录
        success = user_feedback.get('accepted', True) if user_feedback else True

        return TaskOutcome(
            task_id=task.get('task_id', 'unknown'),
            user_id=user_id,
            recipe_id=recipe_id,
            execution_result=result,
            taste_evaluation=taste_evaluation,
            user_feedback=user_feedback,
            success=success,
            execution_time_ms=0.0  # 可从metrics获取
        )

    async def construct_recipe_from_interactions(
        self,
        user_id: str,
        interaction_history: List[Dict],
        name: str = None,
        description: str = None
    ) -> Recipe:
        """
        从交互历史构建 Recipe

        Args:
            user_id: 用户标识
            interaction_history: 历史交互数据
            name: 配方名称
            description: 配方描述

        Returns:
            Recipe: 构建的配方
        """
        return await self.recipe_engine.construct_recipe(
            user_id=user_id,
            interaction_history=interaction_history,
            name=name,
            description=description
        )

    async def establish_taste_profile(
        self,
        user_id: str,
        feedback_history: List[Dict]
    ) -> TasteProfile:
        """
        建立用户品味画像

        Args:
            user_id: 用户标识
            feedback_history: 历史反馈数据

        Returns:
            TasteProfile: 品味画像
        """
        return await self.taste_engine.establish_taste(user_id, feedback_history)

    def get_user_insights(self, user_id: str) -> Dict:
        """
        获取用户洞察摘要

        Args:
            user_id: 用户标识

        Returns:
            Dict: 用户洞察数据
        """
        # 获取 Recipe
        recipes = self.recipe_engine.database.user_recipes.get(user_id, [])
        recipe_list = [
            self.recipe_engine.database.recipes[rid]
            for rid in recipes
            if rid in self.recipe_engine.database.recipes
        ]

        # 获取 Taste Profile
        taste_profile = self.taste_engine.get_taste_profile(user_id)

        # 获取 Flywheel State
        flywheel_state = self.data_flywheel.get_state(user_id)

        return {
            'user_id': user_id,
            'recipe_count': len(recipe_list),
            'recipes': [
                {
                    'name': r.name,
                    'confidence': r.confidence,
                    'usage_count': r.usage_count,
                    'success_rate': r.success_rate
                }
                for r in recipe_list
            ],
            'taste_profile': {
                'domains': list(taste_profile.domains.keys()) if taste_profile else [],
                'cross_domain_consistency': taste_profile.cross_domain_consistency if taste_profile else 0,
                'learning_confidence': taste_profile.learning_confidence if taste_profile else 'low'
            } if taste_profile else None,
            'flywheel_state': flywheel_state
        }


class MaxRDTOrchestrator:
    """
    Max-RDT 编排器 - 简化版入口

    提供统一的接口来使用所有 Max-RDT 功能
    """

    def __init__(self):
        self.layer = MaxRDTLayer()

    async def initialize_user(self, user_id: str) -> Dict:
        """
        初始化用户环境

        Args:
            user_id: 用户标识

        Returns:
            Dict: 初始化状态
        """
        return {
            'user_id': user_id,
            'initialized': True,
            'timestamp': datetime.now().isoformat()
        }

    async def process_task(
        self,
        user_id: str,
        task: Dict,
        interaction_history: List[Dict] = None,
        feedback_history: List[Dict] = None
    ) -> Dict:
        """
        处理任务的完整流程

        Args:
            user_id: 用户标识
            task: 任务描述
            interaction_history: 交互历史（用于Recipe构建）
            feedback_history: 反馈历史（用于Taste构建）

        Returns:
            Dict: 处理结果
        """
        # Step 1: 增强任务上下文
        enhanced = await self.layer.enhance_task(task, user_id)

        # Step 2: 如果有足够的历史数据，构建或更新Recipe和Taste
        if interaction_history and len(interaction_history) >= 5:
            await self.layer.construct_recipe_from_interactions(
                user_id, interaction_history
            )

        if feedback_history and len(feedback_history) >= 3:
            await self.layer.establish_taste_profile(user_id, feedback_history)

        return {
            'enhanced_context': enhanced,
            'next_steps': [
                'Execute task with enhanced context',
                'Record outcome after execution'
            ]
        }

    async def record_and_learn(
        self,
        user_id: str,
        task: Dict,
        result: Any,
        feedback: Dict = None
    ) -> Dict:
        """
        记录结果并学习

        Args:
            user_id: 用户标识
            task: 原始任务
            result: 执行结果
            feedback: 用户反馈

        Returns:
            Dict: 学习结果
        """
        outcome = await self.layer.record_outcome(task, result, feedback, user_id)

        return {
            'outcome': {
                'task_id': outcome.task_id,
                'success': outcome.success,
                'taste_score': outcome.taste_evaluation.taste_score if outcome.taste_evaluation else None
            },
            'insights': self.layer.get_user_insights(user_id)
        }

    def get_capabilities(self) -> Dict:
        """获取系统能力"""
        return {
            'recipe_engine': {
                'features': [
                    'pattern_detection',
                    'workflow_construction',
                    'preference_encoding',
                    'recipe_matching'
                ]
            },
            'data_flywheel': {
                'features': [
                    'behavior_collection',
                    'pattern_mining',
                    'quality_evaluation',
                    'evolution_triggering'
                ]
            },
            'taste_engine': {
                'features': [
                    'domain_classification',
                    'quality_evaluation',
                    'style_matching',
                    'profile_calibration'
                ]
            }
        }


# 便捷函数
def create_rdt_layer(hcd_composite=None) -> MaxRDTLayer:
    """创建 Max-RDT 层的便捷函数"""
    return MaxRDTLayer(hcd_composite)


def create_orchestrator() -> MaxRDTOrchestrator:
    """创建编排器的便捷函数"""
    return MaxRDTOrchestrator()

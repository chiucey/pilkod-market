"""
MiniMax Agent 自进化系统 - 集成模块

整合 MaxHermes、MaxClaw、DeerFlow 和五层记忆体系统
"""

import time
import asyncio
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from memory_manager import FiveLayerMemory
from evolution_engine import EvolutionEngine


@dataclass
class SystemConfig:
    """系统配置"""
    max_session_memory: int = 100
    max_task_history: int = 50
    evolution_threshold: int = 20  # 触发进化的经验数
    auto_evolution_enabled: bool = True


class MiniMaxSelfEvolution:
    """
    MiniMax Agent 自进化系统 - 统一入口

    提供面向用户的统一接口，处理各类自进化相关请求
    """

    def __init__(self, config: Optional[SystemConfig] = None):
        self.config = config or SystemConfig()

        # 初始化核心组件
        self.memory = FiveLayerMemory()
        self.evolution = EvolutionEngine(self.memory)

        # 意图处理器
        self.intent_handlers = {
            'remember_preference': self._handle_remember_preference,
            'continue_task': self._handle_continue_task,
            'improve_response': self._handle_improve_response,
            'analyze_failure': self._handle_analyze_failure,
            'self_evolve': self._handle_self_evolve
        }

        # 对话状态
        self.dialogue_state: Dict[str, Any] = {}

    async def process(self, user_message: str, intent: str = None, context: Dict = None) -> Dict:
        """
        处理用户请求

        Args:
            user_message: 用户消息
            intent: 识别到的意图（可选）
            context: 额外上下文（可选）

        Returns:
            处理结果
        """
        # 1. 识别意图
        if not intent:
            intent = self._recognize_intent(user_message)

        # 2. 存储到 L1 会话记忆
        await self.memory.l1_session.set('last_message', user_message)
        await self.memory.l1_session.set('last_intent', intent)

        # 3. 调用对应处理器
        handler = self.intent_handlers.get(intent)
        if handler:
            result = await handler(user_message, context or {})
        else:
            result = {
                'action': 'general',
                'message': '收到您的请求，正在处理...'
            }

        # 4. 记录响应历史
        self.dialogue_state['last_result'] = result

        # 5. 检查是否需要触发自动进化
        if self.config.auto_evolution_enabled:
            await self._check_auto_evolution()

        return result

    def _recognize_intent(self, message: str) -> str:
        """识别用户意图"""
        message_lower = message.lower()

        # 优先级匹配
        patterns = {
            'remember_preference': ['记住', '保存偏好', '以后用', '下次记得'],
            'continue_task': ['继续', '从上次', '接着', '还没完成'],
            'improve_response': ['改进', '优化', '不满意', '重新回答'],
            'analyze_failure': ['失败', '错了', '不对', '为什么错'],
            'self_evolve': ['学习', '进化', '改进自己', '变得更好']
        }

        for intent, keywords in patterns.items():
            if any(kw in message_lower for kw in keywords):
                return intent

        return 'general'

    async def _handle_remember_preference(self, message: str, context: Dict) -> Dict:
        """处理记住偏好请求"""
        # 提取偏好
        preference = self._extract_preference(message)

        # 存储到 L5 进化记忆
        await self.memory.store(5, f'preference_{preference["type"]}', preference, metadata={
            'record_type': 'preference',
            'preference_type': preference['type'],
            'confidence': preference.get('confidence', 0.8),
            'source': 'user_explicit'
        })

        return {
            'action': 'preference_remembered',
            'preference': preference,
            'message': f'已记住您的偏好：{preference["description"]}',
            'impact': '后续响应将根据此偏好进行调整'
        }

    async def _handle_continue_task(self, message: str, context: Dict) -> Dict:
        """处理继续任务请求"""
        # 检查 L2 任务记忆
        task_state = self.memory.l2_task.get_state()

        if task_state.get('current_task'):
            return {
                'action': 'resume_task',
                'task': task_state['current_task'],
                'progress': task_state['progress'],
                'message': f'已找到未完成任务，进度：{task_state["progress"]*100:.0f}%'
            }

        # 检查检查点
        if task_state.get('checkpoint'):
            return {
                'action': 'restore_checkpoint',
                'checkpoint': task_state['checkpoint'],
                'message': '已恢复上次检查点'
            }

        # 检查 L3 项目记忆
        projects = await self.memory.l3_project.search('project', top_k=1)
        if projects:
            return {
                'action': 'resume_project',
                'project': projects[0],
                'message': '已找到项目上下文'
            }

        return {
            'action': 'no_checkpoint',
            'message': '未找到可恢复的任务或项目'
        }

    async def _handle_improve_response(self, message: str, context: Dict) -> Dict:
        """处理改进回答请求"""
        # 获取上次的响应
        last_result = self.dialogue_state.get('last_result')
        last_message = self.memory.l1_session.get('last_message')

        if not last_result:
            return {
                'action': 'no_previous_response',
                'message': '没有找到之前的响应可以改进'
            }

        # 分析改进点
        issues = self._analyze_improvement_points(message, last_result)

        # 生成改进建议
        improvements = []
        for issue in issues:
            improvements.append({
                'aspect': issue['aspect'],
                'suggestion': issue['suggestion']
            })

        # 存储改进经验
        await self.memory.store(5, 'response_improvement', {
            'original': last_result,
            'issues': issues,
            'improvements': improvements,
            'feedback': message
        }, metadata={'record_type': 'improvement'})

        return {
            'action': 'improvement_suggested',
            'improvements': improvements,
            'message': f'识别出 {len(improvements)} 个可改进点'
        }

    async def _handle_analyze_failure(self, message: str, context: Dict) -> Dict:
        """处理分析失败请求"""
        # 从 L5 获取最近的失败经验
        failure_lessons = await self.memory.l5_evolution.get_failure_lessons()

        if not failure_lessons:
            return {
                'action': 'no_failure_history',
                'message': '没有找到失败经验记录'
            }

        # 分类分析
        failure_analysis = {
            'total_failures': len(failure_lessons),
            'by_type': {},
            'common_causes': [],
            'lessons': []
        }

        for lesson in failure_lessons:
            cause = lesson.get('cause', 'unknown')
            failure_analysis['by_type'][cause] = \
                failure_analysis['by_type'].get(cause, 0) + 1

            if 'lesson' in lesson:
                failure_analysis['lessons'].append(lesson['lesson'])

        # 提取最常见原因
        sorted_causes = sorted(
            failure_analysis['by_type'].items(),
            key=lambda x: x[1],
            reverse=True
        )
        failure_analysis['common_causes'] = [
            {'cause': c, 'count': cnt}
            for c, cnt in sorted_causes[:3]
        ]

        return {
            'action': 'failure_analysis_complete',
            'analysis': failure_analysis,
            'message': '失败分析完成，发现主要问题模式'
        }

    async def _handle_self_evolve(self, message: str, context: Dict) -> Dict:
        """处理自我进化请求"""
        # 触发进化
        evolution_report = await self.evolution.trigger_self_evolution()

        # 生成摘要
        summary = {
            'total_improvements': len(evolution_report.get('improvements', [])),
            'new_capabilities': len(evolution_report.get('new_capabilities', [])),
            'evolution_timestamp': evolution_report.get('timestamp')
        }

        return {
            'action': 'evolution_complete',
            'summary': summary,
            'report': evolution_report,
            'message': f'自我进化完成：完成 {summary["total_improvements"]} 项改进'
        }

    async def _check_auto_evolution(self):
        """检查是否触发自动进化"""
        total = self.evolution.metrics.total_experiences

        if total > 0 and total % self.config.evolution_threshold == 0:
            await self.evolution.trigger_self_evolution()

    def _extract_preference(self, message: str) -> Dict:
        """提取偏好信息"""
        # 简单规则提取
        preference = {
            'type': 'general',
            'description': message,
            'confidence': 0.8
        }

        message_lower = message.lower()

        if any(k in message_lower for k in ['简洁', '简短', '简单', 'minimal', 'brief']):
            preference['type'] = 'response_length'
            preference['value'] = 'concise'
            preference['description'] = '偏好简洁的回答'

        elif any(k in message_lower for k in ['详细', '完整', '详细说明', 'detailed']):
            preference['type'] = 'response_length'
            preference['value'] = 'detailed'
            preference['description'] = '偏好详细的回答'

        elif any(k in message_lower for k in ['专业', '技术', '术语', 'technical']):
            preference['type'] = 'tone'
            preference['value'] = 'technical'
            preference['description'] = '偏好专业术语'

        elif any(k in message_lower for k in ['通俗', '简单', '易懂', 'simple']):
            preference['type'] = 'tone'
            preference['value'] = 'simple'
            preference['description'] = '偏好通俗易懂'

        return preference

    def _analyze_improvement_points(self, message: str, last_result: Dict) -> List[Dict]:
        """分析改进点"""
        issues = []
        message_lower = message.lower()

        if any(k in message_lower for k in ['太短', '不够详细', '详细']):
            issues.append({
                'aspect': 'length',
                'suggestion': '增加详细程度和解释深度'
            })

        if any(k in message_lower for k in ['太长', '简洁', '简短']):
            issues.append({
                'aspect': 'length',
                'suggestion': '精简回答，突出核心'
            })

        if any(k in message_lower for k in ['不清楚', '模糊', '不明白']):
            issues.append({
                'aspect': 'clarity',
                'suggestion': '提高表达清晰度'
            })

        if any(k in message_lower for k in ['不对', '错误', '不准']):
            issues.append({
                'aspect': 'accuracy',
                'suggestion': '核实信息准确性'
            })

        return issues

    def get_system_status(self) -> Dict:
        """获取系统状态"""
        memory_status = self.memory.get_system_status()
        evolution_metrics = self.evolution.get_metrics()

        return {
            'memory': memory_status,
            'evolution': {
                'total_experiences': evolution_metrics.total_experiences,
                'success_rate': evolution_metrics.current_success_rate,
                'improvement_count': len(evolution_metrics.most_common_errors)
            },
            'config': {
                'auto_evolution': self.config.auto_evolution_enabled,
                'evolution_threshold': self.config.evolution_threshold
            }
        }


# 便捷函数
async def create_system(config: Optional[SystemConfig] = None) -> MiniMaxSelfEvolution:
    """创建自进化系统实例"""
    return MiniMaxSelfEvolution(config)


async def quick_remember_preference(preference_text: str) -> Dict:
    """快速记住偏好"""
    system = await create_system()
    return await system.process(preference_text, intent='remember_preference')


async def quick_continue() -> Dict:
    """快速继续任务"""
    system = await create_system()
    return await system.process('继续任务', intent='continue_task')


async def quick_evolve() -> Dict:
    """快速触发进化"""
    system = await create_system()
    return await system.process('自我进化', intent='self_evolve')


# 导出
__all__ = [
    'MiniMaxSelfEvolution',
    'SystemConfig',
    'create_system',
    'quick_remember_preference',
    'quick_continue',
    'quick_evolve'
]

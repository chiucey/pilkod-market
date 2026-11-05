"""
进化引擎 - 自我优化核心实现

提供从经验中学习、提取模式、优化策略的完整能力
"""

import time
import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from collections import Counter


@dataclass
class EvolutionMetrics:
    """进化指标"""
    total_experiences: int = 0
    successful_experiences: int = 0
    failed_experiences: int = 0
    current_success_rate: float = 0.0
    avg_execution_time: float = 0.0
    most_common_errors: List[Tuple[str, int]] = field(default_factory=list)
    capability_score: float = 0.0


@dataclass
class ImprovementSuggestion:
    """改进建议"""
    type: str
    description: str
    priority: int  # 1-5, 1 是最高
    action_steps: List[str]
    expected_impact: str


class SuccessTracker:
    """成功追踪器 - 记录和分析成功案例"""

    def __init__(self):
        self.successful_approaches: Dict[str, List[Dict]] = {}
        self.task_success_count: Counter = Counter()

    async def record(self, experience: Dict):
        """记录成功经验"""
        task_type = experience.get('task_type', 'unknown')

        # 更新任务类型计数
        self.task_success_count[task_type] += 1

        # 存储成功方法
        if task_type not in self.successful_approaches:
            self.successful_approaches[task_type] = []

        self.successful_approaches[task_type].append({
            'approach': experience.get('approach'),
            'metrics': experience.get('metrics', {}),
            'timestamp': experience.get('timestamp', time.time())
        })

        # 保持最近 100 个
        if len(self.successful_approaches[task_type]) > 100:
            self.successful_approaches[task_type] = \
                self.successful_approaches[task_type][-100:]

    def get_best_approach(self, task_type: str) -> Optional[Dict]:
        """获取最佳方法"""
        approaches = self.successful_approaches.get(task_type, [])
        if not approaches:
            return None

        # 选择指标最优的方法
        best = max(approaches, key=lambda x:
            x.get('metrics', {}).get('score', 0) if x.get('metrics') else 0)

        return best

    def get_all_approaches(self, task_type: str) -> List[Dict]:
        """获取所有成功方法"""
        return self.successful_approaches.get(task_type, [])


class PatternExtractor:
    """模式提取器 - 从大量经验中识别重复模式"""

    def __init__(self):
        self.patterns: Dict[str, List[Dict]] = {}

    async def extract_from_success(self, experience: Dict) -> Dict:
        """从成功经验中提取模式"""
        patterns = {
            'task_type': experience.get('task_type'),
            'approach_structure': self._extract_structure(experience.get('approach')),
            'key_steps': self._extract_key_steps(experience.get('approach')),
            'success_factors': self._identify_success_factors(experience)
        }
        return patterns

    def _extract_structure(self, approach: Any) -> str:
        """提取方法结构"""
        if isinstance(approach, str):
            return 'simple'
        elif isinstance(approach, list):
            return 'sequential'
        elif isinstance(approach, dict):
            if 'subtasks' in approach:
                return 'hierarchical'
            return 'structured'
        return 'unknown'

    def _extract_key_steps(self, approach: Any) -> List[str]:
        """提取关键步骤"""
        steps = []

        if isinstance(approach, list):
            for item in approach:
                if isinstance(item, dict):
                    steps.append(item.get('action', str(item)))
                else:
                    steps.append(str(item))
        elif isinstance(approach, dict):
            if 'subtasks' in approach:
                steps = [s.get('action', s.get('id', 'unknown'))
                        for s in approach['subtasks']]
            else:
                steps = list(approach.keys())

        return steps

    def _identify_success_factors(self, experience: Dict) -> List[str]:
        """识别成功因素"""
        factors = []
        metrics = experience.get('metrics', {})

        if metrics.get('speed') == 'fast':
            factors.append('efficient_execution')
        if metrics.get('accuracy') == 'high':
            factors.append('high_accuracy')
        if metrics.get('simplicity') == 'high':
            factors.append('simple_approach')

        return factors

    async def extract_common_patterns(self, experiences: List[Dict]) -> List[Dict]:
        """从多个经验中提取共同模式"""
        if not experiences:
            return []

        # 统计任务类型
        task_types = [e.get('task_type') for e in experiences]
        task_counter = Counter(task_types)

        # 统计方法结构
        structures = [self._extract_structure(e.get('approach')) for e in experiences]
        structure_counter = Counter(structures)

        # 统计关键步骤
        all_steps = []
        for e in experiences:
            all_steps.extend(self._extract_key_steps(e.get('approach')))
        step_counter = Counter(all_steps)

        return [
            {
                'common_task_types': task_counter.most_common(5),
                'common_structures': structure_counter.most_common(3),
                'common_steps': step_counter.most_common(10)
            }
        ]


class StrategyOptimizer:
    """策略优化器 - 基于模式生成优化建议"""

    def __init__(self):
        self.optimization_rules: List[Dict] = []

    async def generate(self, patterns: List[Dict]) -> Dict:
        """生成优化策略"""
        strategy = {
            'recommended_approach': 'default',
            'key_steps': [],
            'avoid_steps': [],
            'optimization_notes': []
        }

        if not patterns:
            return strategy

        # 分析模式
        for pattern in patterns:
            if 'common_steps' in pattern:
                steps = pattern['common_steps']
                if steps:
                    # 推荐最常见的步骤
                    strategy['key_steps'] = [s[0] for s in steps[:5]]

            if 'common_structures' in pattern:
                structures = pattern['common_structures']
                if structures:
                    strategy['recommended_approach'] = structures[0][0]

        return strategy

    async def suggest_improvements(self, failure_analysis: Dict) -> List[ImprovementSuggestion]:
        """基于失败分析生成改进建议"""
        suggestions = []

        cause = failure_analysis.get('root_cause', '')

        if 'timeout' in cause.lower() or '时间' in cause:
            suggestions.append(ImprovementSuggestion(
                type='performance',
                description='执行超时问题优化',
                priority=2,
                action_steps=[
                    '添加进度检查点',
                    '实现增量执行',
                    '增加超时重试机制'
                ],
                expected_impact='减少 50% 超时风险'
            ))

        if 'error' in cause.lower() or '错误' in cause:
            suggestions.append(ImprovementSuggestion(
                type='reliability',
                description='错误处理优化',
                priority=1,
                action_steps=[
                    '增加输入验证',
                    '添加错误边界处理',
                    '实现降级策略'
                ],
                expected_impact='提高执行稳定性'
            ))

        return suggestions


class EvolutionEngine:
    """
    进化引擎 - 从经验中学习与优化

    核心能力：
    1. 任务结果记录
    2. 成功策略追踪
    3. 失败模式分析
    4. 优化建议生成
    5. 自我评估与进化
    """

    def __init__(self, memory_system):
        self.memory = memory_system
        self.success_tracker = SuccessTracker()
        self.pattern_extractor = PatternExtractor()
        self.strategy_optimizer = StrategyOptimizer()

        # 进化指标
        self.metrics = EvolutionMetrics()

        # 基准值
        self.baseline_success_rate = 0.7
        self.baseline_execution_time = 30.0  # 秒

    async def record_outcome(self, task: Any, approach: Any, success: bool,
                           metrics: Optional[Dict] = None) -> Dict:
        """记录任务执行结果"""
        record = {
            'task_type': self._classify_task(task),
            'approach': approach,
            'success': success,
            'metrics': metrics or {},
            'timestamp': time.time()
        }

        # 更新指标
        self.metrics.total_experiences += 1
        if success:
            self.metrics.successful_experiences += 1
            await self.success_tracker.record(record)
        else:
            self.metrics.failed_experiences += 1

        # 计算成功率
        if self.metrics.total_experiences > 0:
            self.metrics.current_success_rate = \
                self.metrics.successful_experiences / self.metrics.total_experiences

        # 存储到 L5 进化记忆
        await self.memory.store(5, 'experience', record, metadata={
            'success': success,
            'task_category': record['task_type']
        })

        # 处理失败经验
        if not success:
            await self._process_failure(record)

        return record

    async def _process_failure(self, record: Dict):
        """处理失败经验"""
        # 提取失败原因
        failure_analysis = await self._analyze_failure(record)

        # 存储失败教训
        await self.memory.store(5, 'failure_lesson', {
            'task': record['task_type'],
            'cause': failure_analysis.get('root_cause'),
            'lesson': failure_analysis.get('lesson'),
            'recovery': failure_analysis.get('recovery_action')
        }, metadata={
            'record_type': 'failure_lesson',
            'task_type': record['task_type']
        })

        # 更新错误统计
        cause = failure_analysis.get('root_cause', 'unknown')
        self.metrics.most_common_errors.append((cause, 1))

    async def _analyze_failure(self, record: Dict) -> Dict:
        """分析失败原因"""
        metrics = record.get('metrics', {})
        task = record.get('task_type', 'unknown')

        analysis = {
            'root_cause': 'unknown',
            'lesson': '',
            'recovery_action': '',
            'factors': []
        }

        # 基于指标分析
        if 'error' in metrics:
            error = metrics['error']
            analysis['root_cause'] = error

            if 'timeout' in str(error).lower():
                analysis['lesson'] = '执行时间过长，需要优化或分段执行'
                analysis['recovery_action'] = '添加检查点，实现增量执行'
            elif 'not found' in str(error).lower():
                analysis['lesson'] = '资源或上下文缺失'
                analysis['recovery_action'] = '先验证资源存在性'
            elif 'permission' in str(error).lower():
                analysis['lesson'] = '权限不足'
                analysis['recovery_action'] = '检查访问权限'

        # 存储到 L5
        await self.memory.store(5, 'failure_analysis', analysis)

        return analysis

    async def get_optimized_approach(self, task: Any) -> Dict:
        """获取针对任务的优化执行方案"""
        task_type = self._classify_task(task)

        # 1. 查询历史成功案例
        similar = await self.memory.retrieve(task, layers=[5], top_k=10)
        success_cases = [e for e in similar if e.get('metadata', {}).get('success')]

        if success_cases:
            # 从成功案例提取策略
            best = self.success_tracker.get_best_approach(task_type)
            if best:
                return {
                    'strategy': best['approach'],
                    'confidence': len(success_cases) / 10,
                    'source': 'learned'
                }

        # 2. 查询知识库
        practices = await self.memory.retrieve(task_type, layers=[4], top_k=3)
        if practices:
            return {
                'strategy': practices[0],
                'confidence': 0.6,
                'source': 'knowledge_base'
            }

        return {
            'strategy': 'default',
            'confidence': 0.3,
            'source': 'fallback'
        }

    async def trigger_self_evolution(self) -> Dict:
        """触发自我进化"""
        evolution_report = {
            'timestamp': time.time(),
            'improvements': [],
            'new_capabilities': [],
            'deprecated_patterns': []
        }

        # 1. 收集近期经验
        recent = await self._get_recent_experiences(100)

        # 2. 分析趋势
        trends = await self._analyze_trends(recent)

        # 3. 识别改进空间
        improvements = await self._identify_improvements(trends)

        # 4. 应用优化
        for improvement in improvements:
            applied = await self._apply_improvement(improvement)
            if applied:
                evolution_report['improvements'].append(applied)

        # 5. 检查能力边界扩展
        new_caps = await self._check_capability_expansion(recent)
        evolution_report['new_capabilities'] = new_caps

        # 6. 记录进化事件
        await self._record_evolution_event(evolution_report)

        return evolution_report

    async def _get_recent_experiences(self, count: int) -> List[Dict]:
        """获取近期经验"""
        # 从 L5 检索
        results = await self.memory.l5_evolution.query_experiences('', top_k=count)
        return results

    async def _analyze_trends(self, experiences: List[Dict]) -> Dict:
        """分析趋势"""
        if not experiences:
            return {}

        success_count = sum(1 for e in experiences if e.get('metadata', {}).get('success'))
        success_rate = success_count / len(experiences)

        return {
            'success_rate': success_rate,
            'total_experiences': len(experiences),
            'trend': 'improving' if success_rate > self.baseline_success_rate else 'declining'
        }

    async def _identify_improvements(self, trends: Dict) -> List[Dict]:
        """识别改进机会"""
        improvements = []

        success_rate = trends.get('success_rate', 0)

        # 成功率改进
        if success_rate < self.baseline_success_rate:
            gap = self.baseline_success_rate - success_rate
            improvements.append({
                'type': 'success_rate',
                'gap': gap,
                'action': 'analyze_failure_patterns',
                'priority': 1 if gap > 0.2 else 3
            })

        # 效率改进
        avg_time = trends.get('avg_execution_time', self.baseline_execution_time)
        if avg_time > self.baseline_execution_time:
            improvements.append({
                'type': 'efficiency',
                'gap': avg_time - self.baseline_execution_time,
                'action': 'optimize_execution_path',
                'priority': 2
            })

        return improvements

    async def _apply_improvement(self, improvement: Dict) -> Optional[Dict]:
        """应用改进"""
        improvement_type = improvement.get('type')

        applied = {
            'type': improvement_type,
            'applied': True,
            'timestamp': time.time()
        }

        if improvement_type == 'success_rate':
            # 分析失败模式
            failure_lessons = await self.memory.l5_evolution.get_failure_lessons()
            applied['lessons_count'] = len(failure_lessons)

        elif improvement_type == 'efficiency':
            # 优化执行路径
            applied['optimization'] = 'execution_path_updated'

        return applied

    async def _check_capability_expansion(self, experiences: List[Dict]) -> List[Dict]:
        """检查能力边界扩展"""
        new_capabilities = []

        # 分析是否有新任务类型成功
        task_types = set()
        for exp in experiences:
            if exp.get('metadata', {}).get('success'):
                task_types.add(exp.get('task_type'))

        # 检查是否是新任务类型
        known_tasks = set(self.success_tracker.task_success_count.keys())
        new_tasks = task_types - known_tasks

        for task in new_tasks:
            new_capabilities.append({
                'task_type': task,
                'first_success_time': time.time(),
                'confidence': 0.5  # 新能力置信度较低
            })

        return new_capabilities

    async def _record_evolution_event(self, report: Dict):
        """记录进化事件"""
        await self.memory.store(5, 'evolution_event', report, metadata={
            'record_type': 'evolution',
            'timestamp': report['timestamp']
        })

    def _classify_task(self, task: Any) -> str:
        """分类任务"""
        task_str = str(task).lower()

        # 简单规则分类
        if any(k in task_str for k in ['创建', '生成', '写', 'build', 'create', 'generate']):
            return 'creation'
        elif any(k in task_str for k in ['分析', '研究', 'analyze', 'research']):
            return 'analysis'
        elif any(k in task_str for k in ['搜索', '查询', 'search', 'find']):
            return 'search'
        elif any(k in task_str for k in ['修复', 'debug', 'fix']):
            return 'debugging'
        elif any(k in task_str for k in ['部署', 'deploy']):
            return 'deployment'
        else:
            return 'general'

    def get_metrics(self) -> EvolutionMetrics:
        """获取进化指标"""
        return self.metrics


# 导出
__all__ = [
    'EvolutionEngine',
    'SuccessTracker',
    'PatternExtractor',
    'StrategyOptimizer',
    'EvolutionMetrics',
    'ImprovementSuggestion'
]

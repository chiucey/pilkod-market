"""
Evolution Engine
进化引擎 - 从经验中学习与优化
"""

import time
from typing import Any, Dict, List, Optional


class SuccessTracker:
    """成功追踪器"""

    def __init__(self):
        self.successful_experiences: List[Dict] = []
        self.strategy_effectiveness: Dict[str, float] = {}

    async def record(self, experience: Dict) -> None:
        """记录成功经验"""
        self.successful_experiences.append({
            **experience,
            'recorded_at': time.time()
        })

        approach = experience.get('approach', 'unknown')
        if approach not in self.strategy_effectiveness:
            self.strategy_effectiveness[approach] = 0
        self.strategy_effectiveness[approach] += 1


class PatternExtractor:
    """模式提取器"""

    def __init__(self):
        self.patterns: Dict[str, List[Dict]] = {}

    async def extract_from_success(self, experience: Dict) -> List[str]:
        """从成功经验中提取模式"""
        patterns = []
        task_type = experience.get('task_type', '')

        if 'code' in task_type.lower():
            patterns.append('code_generation_pattern')
        if 'analysis' in task_type.lower():
            patterns.append('analysis_pattern')
        if 'creative' in task_type.lower():
            patterns.append('creative_pattern')

        return patterns

    async def is_known_pattern(self, pattern: str) -> bool:
        """检查是否为已知模式"""
        return pattern in self.patterns


class StrategyOptimizer:
    """策略优化器"""

    def __init__(self):
        self.optimization_history: List[Dict] = []

    async def generate_optimization(self, issue: Dict) -> Dict:
        """生成优化建议"""
        return {
            'issue': issue,
            'suggested_approach': 'optimized_strategy',
            'confidence': 0.8
        }


class EvolutionEngine:
    """
    进化引擎 - 从经验中学习与优化
    """

    def __init__(self, memory_system):
        self.memory = memory_system
        self.success_tracker = SuccessTracker()
        self.pattern_extractor = PatternExtractor()
        self.strategy_optimizer = StrategyOptimizer()

        # 进化指标
        self.evolution_metrics = {
            'total_experiences': 0,
            'successful_strategies': [],
            'failed_patterns': [],
            'capability_boundaries': [],
            'improvement_suggestions': []
        }

        # 基线指标
        self.baseline_time = 30.0  # 秒

    async def record_outcome(
        self,
        task: str,
        approach: str,
        success: bool,
        metrics: Optional[Dict] = None
    ) -> Dict:
        """记录任务执行结果"""
        record = {
            'task_type': self._classify_task(task),
            'approach': approach,
            'success': success,
            'metrics': metrics or {},
            'timestamp': time.time(),
            'context': await self._capture_context()
        }

        # 存储到 L5 进化记忆
        await self.memory.store(
            5,
            'experience',
            record,
            metadata={
                'success': success,
                'task_category': record['task_type']
            }
        )

        # 更新进化指标
        self.evolution_metrics['total_experiences'] += 1

        if success:
            await self._process_success(record)
        else:
            await self._process_failure(record)

        return record

    async def _process_success(self, record: Dict) -> None:
        """处理成功经验"""
        await self.success_tracker.record(record)
        patterns = await self.pattern_extractor.extract_from_success(record)

        if patterns:
            is_known = await self.pattern_extractor.is_known_pattern(patterns[0])
            if not is_known:
                await self.memory.store(4, 'success_pattern', patterns,
                                       metadata={'source': 'experience'})

    async def _process_failure(self, record: Dict) -> None:
        """处理失败经验"""
        failure_analysis = await self._analyze_failure(record)

        await self.memory.store(5, 'failure_lesson', {
            'task': record.get('task_type'),
            'cause': failure_analysis.get('root_cause'),
            'lesson': failure_analysis.get('lesson'),
            'recovery': failure_analysis.get('recovery_action')
        })

        self.evolution_metrics['failed_patterns'].append(failure_analysis)

        suggestion = await self._generate_improvement_suggestion(failure_analysis)
        if suggestion:
            self.evolution_metrics['improvement_suggestions'].append(suggestion)

    async def _analyze_failure(self, record: Dict) -> Dict:
        """分析失败原因"""
        return {
            'root_cause': 'insufficient_context',
            'lesson': 'need_more_background_info',
            'recovery_action': 'request_additional_context'
        }

    async def _generate_improvement_suggestion(self, failure_analysis: Dict) -> Optional[Dict]:
        """生成改进建议"""
        return {
            'type': 'context_enrichment',
            'action': 'gather_more_context_before_execution'
        }

    async def get_optimized_approach(self, task: str) -> Dict:
        """获取针对任务的优化执行方案"""
        task_type = self._classify_task(task)

        # 查询类似任务的历史经验
        similar_experiences = await self.memory.retrieve(task, layers=[5], top_k=10)
        success_patterns = [e for e in similar_experiences if e.get('success')]

        if success_patterns:
            best_strategy = self._extract_best_strategy(success_patterns)
            return {
                'strategy': best_strategy,
                'confidence': len(success_patterns) / 10,
                'source': 'learned'
            }

        # 查询知识库获取通用最佳实践
        general_practices = await self.memory.retrieve(task_type, layers=[4], top_k=3)
        if general_practices:
            return {
                'strategy': general_practices[0],
                'confidence': 0.6,
                'source': 'knowledge_base'
            }

        return {
            'strategy': 'default_approach',
            'confidence': 0.3,
            'source': 'fallback'
        }

    def _classify_task(self, task: str) -> str:
        """分类任务类型"""
        task_lower = task.lower()
        if any(kw in task_lower for kw in ['代码', 'code', '开发', '写']):
            return 'code_generation'
        elif any(kw in task_lower for kw in ['分析', 'analysis', '研究']):
            return 'analysis'
        elif any(kw in task_lower for kw in ['设计', 'design', '创建']):
            return 'design'
        return 'general'

    async def _capture_context(self) -> Dict:
        """捕获当前上下文"""
        return {
            'available_layers': [1, 2, 3, 4, 5],
            'timestamp': time.time()
        }

    def _extract_best_strategy(self, experiences: List[Dict]) -> str:
        """从成功经验中提取最优策略"""
        approach_counts = {}
        for exp in experiences:
            approach = exp.get('approach', 'unknown')
            approach_counts[approach] = approach_counts.get(approach, 0) + 1

        if approach_counts:
            return max(approach_counts, key=approach_counts.get)
        return 'default'

    async def trigger_self_evolution(self) -> Dict:
        """触发自我进化"""
        evolution_report = {
            'timestamp': time.time(),
            'improvements': [],
            'new_capabilities': [],
            'deprecated_patterns': []
        }

        # 分析近期经验趋势
        recent = await self._get_recent_experiences(100)

        # 识别改进空间
        improvements = await self._identify_improvements(recent)
        for improvement in improvements:
            applied = await self._apply_improvement(improvement)
            if applied:
                evolution_report['improvements'].append(applied)

        # 扩展能力边界
        new_capabilities = await self._expand_capabilities(recent)
        evolution_report['new_capabilities'] = new_capabilities

        # 记录进化事件
        await self._record_evolution_event(evolution_report)

        return evolution_report

    async def _get_recent_experiences(self, limit: int) -> List[Dict]:
        """获取近期经验"""
        experiences = await self.memory.retrieve('experience', layers=[5], top_k=limit)
        return experiences[:limit]

    async def _identify_improvements(self, experiences: List[Dict]) -> List[Dict]:
        """从经验中识别改进机会"""
        improvements = []

        if not experiences:
            return improvements

        success_count = sum(1 for e in experiences if e.get('success'))
        success_rate = success_count / len(experiences)

        if success_rate < 0.7:
            improvements.append({
                'type': 'success_rate',
                'current': success_rate,
                'target': 0.8,
                'action': 'analyze_failure_patterns'
            })

        return improvements

    async def _apply_improvement(self, improvement: Dict) -> Optional[Dict]:
        """应用改进"""
        return {
            'applied': True,
            'improvement': improvement
        }

    async def _expand_capabilities(self, experiences: List[Dict]) -> List[str]:
        """扩展能力边界"""
        return []

    async def _record_evolution_event(self, report: Dict) -> None:
        """记录进化事件"""
        await self.memory.store(5, 'evolution_event', report)

    def _get_baseline_time(self) -> float:
        """获取基线执行时间"""
        return self.baseline_time

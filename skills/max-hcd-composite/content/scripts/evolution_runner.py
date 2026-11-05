"""
Evolution Engine - 进化引擎
从历史经验中学习，自动优化任务执行策略
"""

import json
import time
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, asdict
from collections import Counter
import asyncio


@dataclass
class TaskOutcome:
    """任务执行结果"""
    task_type: str
    approach: str
    success: bool
    metrics: Dict[str, Any]
    timestamp: float
    duration: float = 0.0
    error: Optional[str] = None


@dataclass
class Strategy:
    """执行策略"""
    name: str
    description: str
    steps: List[str]
    success_rate: float
    avg_duration: float
   适用场景: List[str]


class SuccessTracker:
    """成功率追踪器"""

    def __init__(self):
        self.outcomes: List[TaskOutcome] = []
        self.task_type_stats: Dict[str, Dict] = {}

    async def update(self, record: Dict):
        """更新追踪数据"""
        outcome = TaskOutcome(
            task_type=record.get('task_type', 'unknown'),
            approach=record.get('approach', ''),
            success=record.get('success', False),
            metrics=record.get('metrics', {}),
            timestamp=record.get('timestamp', time.time()),
            duration=record.get('metrics', {}).get('duration', 0.0),
            error=record.get('error')
        )

        self.outcomes.append(outcome)

        # 更新统计
        task_type = outcome.task_type
        if task_type not in self.task_type_stats:
            self.task_type_stats[task_type] = {
                'total': 0,
                'successes': 0,
                'failures': 0,
                'total_duration': 0.0,
                'approaches': Counter()
            }

        stats = self.task_type_stats[task_type]
        stats['total'] += 1
        if outcome.success:
            stats['successes'] += 1
        else:
            stats['failures'] += 1
        stats['total_duration'] += outcome.duration
        stats['approaches'][outcome.approach] += 1

    def get_stats(self, task_type: Optional[str] = None) -> Dict:
        """获取统计信息"""
        if task_type:
            stats = self.task_type_stats.get(task_type, {})
            if stats:
                return {
                    **stats,
                    'success_rate': stats['successes'] / stats['total'] if stats['total'] > 0 else 0,
                    'avg_duration': stats['total_duration'] / stats['total'] if stats['total'] > 0 else 0
                }
            return {}

        # 返回总体统计
        total = sum(s['total'] for s in self.task_type_stats.values())
        successes = sum(s['successes'] for s in self.task_type_stats.values())
        return {
            'total_tasks': total,
            'total_successes': successes,
            'overall_success_rate': successes / total if total > 0 else 0,
            'task_types': len(self.task_type_stats)
        }

    def get_best_approach(self, task_type: str) -> Optional[str]:
        """获取最佳执行策略"""
        task_outcomes = [o for o in self.outcomes if o.task_type == task_type]
        if not task_outcomes:
            return None

        approach_stats = {}
        for o in task_outcomes:
            if o.approach not in approach_stats:
                approach_stats[o.approach] = {'successes': 0, 'total': 0}
            approach_stats[o.approach]['total'] += 1
            if o.success:
                approach_stats[o.approach]['successes'] += 1

        best = max(approach_stats.items(),
                  key=lambda x: x[1]['successes'] / x[1]['total'] if x[1]['total'] > 0 else 0)

        return best[0] if best[1]['successes'] > 0 else None


class PatternExtractor:
    """模式提取器"""

    def __init__(self):
        self.patterns: Dict[str, List[Dict]] = {}

    async def analyze(self, experiences: List[Dict]) -> List[Dict]:
        """分析成功经验，提取模式"""
        patterns = []

        successful = [e for e in experiences if e.get('metadata', {}).get('success', False)]

        if not successful:
            return []

        # 提取任务类型模式
        task_types = [e.get('metadata', {}).get('task_type') for e in successful]
        most_common_type = Counter(task_types).most_common(1)
        if most_common_type:
            patterns.append({
                'type': 'task_type',
                'pattern': most_common_type[0][0],
                'confidence': most_common_type[0][1] / len(successful)
            })

        # 提取步骤模式
        steps = []
        for e in successful:
            steps.extend(e.get('experience', {}).get('steps', []))

        if steps:
            common_steps = Counter(steps).most_common(5)
            patterns.append({
                'type': 'steps',
                'pattern': [s[0] for s in common_steps],
                'confidence': common_steps[0][1] / len(steps) if steps else 0
            })

        return patterns

    def extract_lessons(self, failed_experience: Dict) -> List[str]:
        """从失败经验中提取教训"""
        lessons = []

        error = failed_experience.get('error')
        if error:
            lessons.append(f"避免错误: {error}")

        approach = failed_experience.get('approach', '')
        if approach:
            lessons.append(f"重新考虑方法: {approach}")

        metrics = failed_experience.get('metrics', {})
        if 'duration' in metrics and metrics['duration'] > 60:
            lessons.append("执行超时，考虑分解任务")

        return lessons


class StrategyOptimizer:
    """策略优化器"""

    def __init__(self):
        self.strategies: Dict[str, Strategy] = {}

    async def generate(self, patterns: List[Dict]) -> Optional[Strategy]:
        """基于模式生成优化策略"""
        if not patterns:
            return None

        # 构建策略
        strategy = Strategy(
            name=f"optimized_{int(time.time())}",
            description="基于历史经验优化的策略",
            steps=[],
            success_rate=0.0,
            avg_duration=0.0,
            适用场景=[]
        )

        for p in patterns:
            if p['type'] == 'task_type':
                strategy.适用场景.append(p['pattern'])
            elif p['type'] == 'steps':
                strategy.steps = p['pattern']
            elif p['type'] == 'success_rate':
                strategy.success_rate = p.get('value', 0.0)

        # 计算平均成功率
        rates = [p.get('confidence', 0) for p in patterns]
        if rates:
            strategy.success_rate = sum(rates) / len(rates)

        self.strategies[strategy.name] = strategy
        return strategy

    def get_strategy(self, name: str) -> Optional[Strategy]:
        """获取指定策略"""
        return self.strategies.get(name)


class EvolutionEngine:
    """
    进化引擎 - 从历史经验中学习和优化

    核心能力:
    1. 任务成功率追踪
    2. 策略模式提取
    3. 自我优化建议
    4. 能力边界扩展
    """

    def __init__(self, memory_system):
        self.memory = memory_system
        self.success_tracker = SuccessTracker()
        self.pattern_extractor = PatternExtractor()
        self.optimizer = StrategyOptimizer()
        self.evolution_history: List[Dict] = []

    def classify_task(self, task: Any) -> str:
        """任务分类（简化版，实际可用LLM）"""
        task_str = str(task).lower()

        # 简单关键词分类
        if any(k in task_str for k in ['分析', 'research', '调研']):
            return 'research'
        elif any(k in task_str for k in ['开发', 'build', 'create', '实现']):
            return 'development'
        elif any(k in task_str for k in ['写作', 'write', '创作']):
            return 'creative'
        elif any(k in task_str for k in ['代码', 'code', 'debug', '修复']):
            return 'coding'
        elif any(k in task_str for k in ['设计', 'design', '架构']):
            return 'design'
        else:
            return 'general'

    async def record_outcome(self, task: Any, approach: Any,
                            success: bool, metrics: Optional[Dict] = None,
                            error: Optional[str] = None):
        """记录任务执行结果"""
        task_type = self.classify_task(task)

        record = {
            'task_type': task_type,
            'approach': str(approach),
            'success': success,
            'metrics': metrics or {},
            'timestamp': time.time(),
            'error': error
        }

        # 存储到L5进化记忆
        await self.memory.store(5, 'outcome', record, {
            'task_type': task_type,
            'success': success
        })

        # 更新成功追踪
        await self.success_tracker.update(record)

        # 如果失败，提取教训
        if not success:
            lessons = self.pattern_extractor.extract_lessons(record)
            for lesson in lessons:
                await self.memory.store(5, 'lesson', lesson, {
                    'task_type': task_type,
                    'timestamp': time.time()
                })

    async def get_optimized_approach(self, task: Any) -> Optional[Strategy]:
        """获取优化后的任务执行方法"""
        task_type = self.classify_task(task)

        # 1. 查询历史成功案例
        similar = await self.memory.l5_evolution.query(str(task), top_k=10)

        # 2. 获取该任务类型的最佳方法
        best_approach = self.success_tracker.get_best_approach(task_type)

        # 3. 分析成功模式
        patterns = await self.pattern_extractor.analyze(similar)

        # 4. 如果有最佳方法，添加到模式
        if best_approach:
            patterns.append({
                'type': 'best_approach',
                'pattern': best_approach,
                'confidence': self.success_tracker.get_stats(task_type).get('success_rate', 0)
            })

        # 5. 生成优化策略
        return await self.optimizer.generate(patterns)

    async def evolve_capabilities(self) -> Dict:
        """触发能力进化"""
        # 1. 收集近期经验
        recent = await self.memory.l5_evolution.get_recent(100)

        if len(recent) < 10:
            return {
                'evolved': False,
                'reason': 'insufficient_experience',
                'experience_count': len(recent)
            }

        # 2. 识别改进空间
        improvements = self.identify_improvements(recent)

        # 3. 应用优化
        applied = []
        for imp in improvements:
            result = await self.apply_optimization(imp)
            if result:
                applied.append(result)

        # 4. 记录进化事件
        evolution_event = {
            'timestamp': time.time(),
            'experience_count': len(recent),
            'improvements_identified': len(improvements),
            'improvements_applied': len(applied),
            'details': improvements
        }
        self.evolution_history.append(evolution_event)

        # 存储到记忆系统
        await self.memory.store(5, 'evolution_event', evolution_event)

        return {
            'evolved': len(applied) > 0,
            'experience_count': len(recent),
            'improvements_applied': applied
        }

    def identify_improvements(self, experiences: List[Dict]) -> List[Dict]:
        """识别改进空间"""
        improvements = []

        # 分析失败模式
        failures = [e for e in experiences
                   if not e.get('metadata', {}).get('success', True)]

        if failures:
            # 统计失败原因
            errors = Counter([f.get('metadata', {}).get('error') for f in failures])
            most_common_error = errors.most_common(1)

            if most_common_error:
                improvements.append({
                    'type': 'error_avoidance',
                    'pattern': most_common_error[0][0],
                    'frequency': most_common_error[0][1],
                    'suggestion': f"需要优化错误处理: {most_common_error[0][0]}"
                })

        # 分析耗时任务
        durations = [e.get('metadata', {}).get('metrics', {}).get('duration', 0)
                     for e in experiences if e.get('metadata', {}).get('metrics')]

        if durations:
            avg_duration = sum(durations) / len(durations)
            long_tasks = [e for e in experiences
                         if e.get('metadata', {}).get('metrics', {}).get('duration', 0) > avg_duration * 1.5]

            if long_tasks:
                improvements.append({
                    'type': 'performance',
                    'pattern': 'slow_execution',
                    'count': len(long_tasks),
                    'suggestion': f"有 {len(long_tasks)} 个任务执行时间过长，考虑任务分解"
                })

        # 分析重复尝试
        repeated = [e for e in experiences
                   if e.get('metadata', {}).get('retry_count', 0) > 0]

        if repeated:
            improvements.append({
                'type': 'efficiency',
                'pattern': 'retry_required',
                'count': len(repeated),
                'suggestion': "部分任务需要重试，优化初次执行策略"
            })

        return improvements

    async def apply_optimization(self, improvement: Dict) -> Optional[Dict]:
        """应用优化"""
        imp_type = improvement.get('type')

        if imp_type == 'error_avoidance':
            # 添加错误处理策略
            return {
                'applied': True,
                'type': 'error_handling',
                'description': f"优化错误处理: {improvement.get('pattern')}"
            }

        elif imp_type == 'performance':
            # 添加任务分解建议
            return {
                'applied': True,
                'type': 'task_decomposition',
                'description': "建议对复杂任务进行分解"
            }

        elif imp_type == 'efficiency':
            # 优化执行策略
            return {
                'applied': True,
                'type': 'strategy_optimization',
                'description': "优化初次执行以减少重试"
            }

        return None

    def get_evolution_stats(self) -> Dict:
        """获取进化统计"""
        return {
            'total_evolutions': len(self.evolution_history),
            'tracker_stats': self.success_tracker.get_stats(),
            'optimizer_strategies': len(self.optimizer.strategies),
            'recent_evolutions': self.evolution_history[-5:] if self.evolution_history else []
        }

    def summary(self) -> str:
        """获取进化引擎摘要"""
        stats = self.get_evolution_stats()
        tracker = self.success_tracker.get_stats()

        return f"""
╔═══════════════════════════════════════════════════╗
║             EVOLUTION ENGINE STATUS               ║
╠═══════════════════════════════════════════════════╣
║  Total Evolutions   │ {stats['total_evolutions']:<5d}                          ║
║  Strategies Learned │ {stats['optimizer_strategies']:<5d}                          ║
║  ───────────────────────────────────────────────  ║
║  Task Statistics                                     ║
║  ├─ Total Tasks    │ {tracker.get('total_tasks', 0):<5d}                          ║
║  ├─ Successes      │ {tracker.get('total_successes', 0):<5d}                          ║
║  └─ Success Rate   │ {tracker.get('overall_success_rate', 0)*100:5.1f}%                        ║
╚═══════════════════════════════════════════════════╝
        """


# 便捷函数
def create_evolution_engine(memory_system) -> EvolutionEngine:
    """创建进化引擎实例"""
    return EvolutionEngine(memory_system)


if __name__ == '__main__':
    # 测试
    from memory_manager import create_memory_system

    async def test():
        memory = create_memory_system('test')
        evolution = create_evolution_engine(memory)

        # 记录一些任务结果
        await evolution.record_outcome(
            "分析销售数据",
            approach="分解为子任务",
            success=True,
            metrics={'duration': 30, 'accuracy': 0.95}
        )

        await evolution.record_outcome(
            "构建Web应用",
            approach="一次性构建",
            success=False,
            error="内存溢出"
        )

        await evolution.record_outcome(
            "编写测试用例",
            approach="TDD方法",
            success=True,
            metrics={'duration': 45}
        )

        # 获取优化建议
        strategy = await evolution.get_optimized_approach("开发新功能")
        if strategy:
            print(f"Optimized Strategy: {strategy.description}")

        # 触发进化
        result = await evolution.evolve_capabilities()
        print(f"Evolution result: {result}")

        print(evolution.summary())

    asyncio.run(test())

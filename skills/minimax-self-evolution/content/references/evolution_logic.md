# 进化逻辑详解

## 1. 进化引擎概述

进化引擎是 MiniMax Agent 自进化系统的核心，负责从经验中学习、提取模式、优化策略，最终实现能力的持续提升。

### 1.1 进化循环

```
┌─────────────────────────────────────────────────────────────────┐
│                        进化循环                                  │
│                                                                 │
│   ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐       │
│   │ 记录    │───►│ 分析    │───►│ 提取    │───►│ 应用    │       │
│   │ 经验    │    │ 趋势    │    │ 模式    │    │ 优化    │       │
│   └─────────┘    └─────────┘    └─────────┘    └─────────┘       │
│       ▲                                                    │      │
│       │                                                    │      │
│       └────────────────────────────────────────────────────┘      │
│                          持续迭代                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 核心组件

| 组件 | 职责 | 输入 | 输出 |
|------|------|------|------|
| SuccessTracker | 追踪成功案例 | 经验记录 | 最佳策略 |
| PatternExtractor | 提取模式 | 经验列表 | 模式库 |
| StrategyOptimizer | 生成优化 | 模式 | 策略建议 |

## 2. 经验记录机制

### 2.1 记录触发

经验记录在以下时机触发：

```python
class RecordingTrigger:
    # 自动触发
    AUTO_TRIGGERS = {
        'task_completed': True,      # 任务完成
        'task_failed': True,         # 任务失败
        'user_feedback': True,       # 用户反馈
        'checkpoint_reached': True    # 检查点到达
    }

    # 手动触发
    MANUAL_TRIGGERS = [
        '用户要求记住偏好',
        '用户触发自我进化',
        '用户要求分析失败'
    ]
```

### 2.2 经验数据结构

```python
Experience = {
    # 基础信息
    'id': str,                      # UUID
    'timestamp': float,              # 时间戳

    # 任务信息
    'task_type': str,                # 任务类型
    'task_description': str,         # 任务描述
    'task_complexity': str,          # 复杂度: simple/complex/multi

    # 执行信息
    'approach': Any,                 # 采用的方法
    'execution_time': float,         # 执行时间(秒)

    # 结果信息
    'success': bool,                 # 是否成功
    'metrics': Dict,                # 指标数据
    'error': str | None,             # 错误信息(如有)

    # 上下文
    'context': {
        'layers_used': List[int],    # 使用的记忆层
        'intents': List[str],        # 识别的意图
        'tools_used': List[str]      # 使用的工具
    },

    # 元数据
    'metadata': {
        'source': str,               # 来源: auto/manual
        'confidence': float          # 置信度
    }
}
```

## 3. 模式提取算法

### 3.1 成功模式提取

```python
async def extract_success_pattern(experience: Dict) -> Pattern:
    """从单个成功经验提取模式"""

    pattern = {
        'task_type': experience['task_type'],

        # 结构模式
        'structure': classify_structure(experience['approach']),

        # 关键步骤
        'key_steps': extract_key_steps(experience['approach']),

        # 成功因素
        'success_factors': identify_success_factors(experience),

        # 时间特征
        'time_category': categorize_execution_time(
            experience.get('execution_time', 0)
        ),

        # 置信度
        'confidence': calculate_pattern_confidence(experience)
    }

    return pattern


def classify_structure(approach: Any) -> str:
    """分类方法结构"""
    if isinstance(approach, str):
        return 'simple'

    if isinstance(approach, list):
        if len(approach) <= 3:
            return 'sequential_simple'
        return 'sequential_complex'

    if isinstance(approach, dict):
        if 'subtasks' in approach:
            return 'hierarchical'
        return 'structured'

    return 'unknown'


def extract_key_steps(approach: Any) -> List[str]:
    """提取关键步骤"""
    steps = []

    if isinstance(approach, list):
        for item in approach:
            if isinstance(item, dict):
                action = item.get('action', item.get('id', 'step'))
                steps.append(action)

    elif isinstance(approach, dict):
        if 'subtasks' in approach:
            steps = [s.get('action') for s in approach['subtasks']]
        else:
            steps = list(approach.keys())

    return steps


def identify_success_factors(experience: Dict) -> List[str]:
    """识别成功因素"""
    factors = []
    metrics = experience.get('metrics', {})

    # 速度因素
    exec_time = experience.get('execution_time', float('inf'))
    if exec_time < 30:
        factors.append('fast_execution')

    # 准确性因素
    if metrics.get('accuracy', 0) > 0.9:
        factors.append('high_accuracy')

    # 简洁性因素
    steps = extract_key_steps(experience.get('approach', []))
    if len(steps) <= 3:
        factors.append('simple_approach')

    # 资源效率因素
    if metrics.get('resource_usage', 1) < 0.5:
        factors.append('resource_efficient')

    return factors
```

### 3.2 模式聚类

```python
async def cluster_patterns(experiences: List[Dict]) -> Dict:
    """模式聚类"""

    # 按任务类型分组
    by_type = defaultdict(list)
    for exp in experiences:
        by_type[exp['task_type']].append(exp)

    # 聚类结果
    clusters = {}

    for task_type, exps in by_type.items():
        # 提取共同特征
        common = {
            'task_type': task_type,
            'count': len(exps),

            # 共同结构
            'structures': Counter(
                classify_structure(e['approach']) for e in exps
            ).most_common(1)[0][0],

            # 共同步骤
            'all_steps': [],
            'step_frequency': Counter()
        }

        # 统计步骤频率
        for exp in exps:
            steps = extract_key_steps(exp.get('approach', []))
            common['all_steps'].extend(steps)

        for step in common['all_steps']:
            common['step_frequency'][step] += 1

        # 提取高频步骤
        common['key_steps'] = [
            step for step, count
            in common['step_frequency'].most_common(5)
        ]

        clusters[task_type] = common

    return clusters
```

## 4. 优化策略生成

### 4.1 优化规则

```python
OPTIMIZATION_RULES = {
    'response_length': {
        'condition': lambda p: 'concise' in p.get('preference', ''),
        'action': 'reduce_details',
        'weight': 1.5
    },

    'execution_speed': {
        'condition': lambda p: 'fast' in p.get('priority', ''),
        'action': 'parallel_execution',
        'weight': 1.3
    },

    'accuracy': {
        'condition': lambda p: 'accurate' in p.get('priority', ''),
        'action': 'add_verification',
        'weight': 1.4
    }
}


async def generate_optimized_strategy(task: str, patterns: List[Dict]) -> Strategy:
    """生成优化策略"""

    strategy = {
        'task': task,
        'recommended_approach': None,
        'steps': [],
        'avoid_steps': [],
        'optimizations': []
    }

    # 分析模式
    if patterns:
        # 选择最佳模式
        best_pattern = max(patterns,
                          key=lambda p: p.get('confidence', 0))

        strategy['recommended_approach'] = best_pattern.get('structure')
        strategy['steps'] = best_pattern.get('key_steps', [])

        # 应用优化规则
        for rule_name, rule in OPTIMIZATION_RULES.items():
            if rule['condition'](best_pattern):
                strategy['optimizations'].append({
                    'rule': rule_name,
                    'action': rule['action'],
                    'weight': rule['weight']
                })

    return strategy
```

### 4.2 失败预防

```python
async def generate_failure_prevention(failure_lessons: List[Dict]) -> List[str]:
    """基于失败教训生成预防措施"""

    preventions = []

    # 按原因分类
    by_cause = defaultdict(list)
    for lesson in failure_lessons:
        by_cause[lesson['cause']].append(lesson)

    # 生成预防规则
    for cause, lessons in by_cause.items():
        if len(lessons) >= 3:  # 多次出现的问题
            prevention = {
                'trigger': cause,
                'rule': lessons[0]['lesson'],
                'action': f'check_{cause}',
                'severity': 'high' if len(lessons) > 5 else 'medium'
            }
            preventions.append(prevention)

    return preventions
```

## 5. 自我进化流程

### 5.1 进化触发

```python
class EvolutionTrigger:
    """进化触发条件"""

    TRIGGERS = {
        'experience_threshold': {
            'condition': lambda m: m.total >= 20,
            'frequency': 'per_threshold'
        },

        'success_rate_drop': {
            'condition': lambda m: m.success_rate < 0.7,
            'frequency': 'immediate'
        },

        'manual': {
            'condition': lambda _: True,
            'frequency': 'on_demand'
        },

        'periodic': {
            'condition': lambda m: True,
            'frequency': 'daily'
        }
    }
```

### 5.2 进化流程

```python
async def trigger_self_evolution(self) -> EvolutionReport:
    """执行自我进化"""

    report = EvolutionReport()

    # 阶段 1: 数据收集
    report.data_collection = await self._collect_evolution_data()

    # 阶段 2: 趋势分析
    report.trends = await self._analyze_trends(report.data_collection)

    # 阶段 3: 模式识别
    report.patterns = await self._identify_patterns(report.trends)

    # 阶段 4: 优化应用
    report.applied_optimizations = await self._apply_optimizations(
        report.patterns
    )

    # 阶段 5: 能力扩展
    report.new_capabilities = await self._check_capability_expansion()

    # 阶段 6: 记录进化
    await self._record_evolution_event(report)

    return report


async def _collect_evolution_data(self) -> EvolutionData:
    """收集进化数据"""

    # 获取所有经验
    experiences = await self.memory.l5_evolution.query_experiences(
        '', top_k=1000
    )

    # 获取用户偏好
    preferences = await self.memory.l5_evolution.get_preferences()

    # 获取失败教训
    failure_lessons = await self.memory.l5_evolution.get_failure_lessons()

    return EvolutionData(
        experiences=experiences,
        preferences=preferences,
        failure_lessons=failure_lessons,
        timestamp=time.time()
    )
```

### 5.3 进化评估

```python
class EvolutionEvaluator:
    """进化效果评估"""

    METRICS = {
        'success_rate_improvement': {
            'before': 'old_success_rate',
            'after': 'new_success_rate',
            'target': 'improvement > 0.1'
        },

        'execution_time_reduction': {
            'before': 'avg_execution_time',
            'after': 'new_avg_time',
            'target': 'reduction > 20%'
        },

        'capability_expansion': {
            'before': 'known_task_types',
            'after': 'new_task_types',
            'target': 'new_types >= 1'
        }
    }

    def evaluate(self, report: EvolutionReport) -> EvaluationResult:
        """评估进化效果"""

        results = {}

        for metric_name, metric in self.METRICS.items():
            before = report.get(metric['before'])
            after = report.get(metric['after'])

            if before is not None and after is not None:
                improvement = (after - before) / before if before > 0 else 0
                results[metric_name] = {
                    'before': before,
                    'after': after,
                    'improvement': improvement,
                    'target_met': self._check_target(
                        improvement,
                        metric['target']
                    )
                }

        return EvaluationResult(results=results)
```

## 6. 持续学习机制

### 6.1 在线学习

```python
class OnlineLearning:
    """在线学习机制"""

    def __init__(self, evolution_engine):
        self.engine = evolution_engine
        self.learning_rate = 0.1

    async def learn_from_feedback(self, interaction: Dict):
        """从用户反馈中学习"""

        feedback = interaction.get('feedback')
        original_response = interaction.get('response')

        if not feedback:
            return

        # 提取反馈信号
        signal = self._extract_feedback_signal(feedback)

        # 更新经验置信度
        await self._update_confidence(
            original_response,
            signal
        )

        # 调整策略权重
        await self._adjust_strategy_weights(signal)

    def _extract_feedback_signal(self, feedback: str) -> float:
        """提取反馈信号 (-1 到 1)"""
        positive = ['好', '不错', '满意', '可以', '谢谢', 'good', 'great']
        negative = ['不好', '不对', '不满意', '差', 'bad', 'wrong']

        feedback_lower = feedback.lower()

        for p in positive:
            if p in feedback_lower:
                return 1.0

        for n in negative:
            if n in feedback_lower:
                return -1.0

        return 0.0
```

### 6.2 遗忘机制

```python
class MemoryDecay:
    """记忆衰减机制"""

    DECAY_FUNCTIONS = {
        'exponential': lambda t, rate: math.exp(-rate * t),
        'linear': lambda t, rate: max(0, 1 - rate * t),
        'step': lambda t, rate: 1 if t < rate else 0.5
    }

    def __init__(self, decay_type='exponential', rate=0.01):
        self.decay_func = self.DECAY_FUNCTIONS[decay_type]
        self.rate = rate

    def calculate_weight(self, timestamp: float) -> float:
        """计算记忆权重"""
        age = time.time() - timestamp
        return self.decay_func(age, self.rate)
```

## 7. 总结

进化引擎通过以上机制实现了智能体的持续学习和自我优化：

1. **经验记录**：自动记录所有任务执行结果
2. **模式提取**：从成功案例中提取可复用的模式
3. **策略优化**：基于模式生成优化策略
4. **预防机制**：基于失败教训生成预防措施
5. **持续学习**：在线学习用户反馈
6. **遗忘机制**：避免过时知识影响决策

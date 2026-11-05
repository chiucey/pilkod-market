---
name: minimax-self-evolution
description: MiniMax Agent 自进化系统，具备 5 层记忆体架构和持续学习能力。当用户要求"记住偏好"、"从上次继续"、"改进回答"、"分析失败"、"自我进化"时触发。支持用户偏好学习、跨会话上下文恢复、任务执行策略优化、失败模式分析与能力边界扩展。
---

# MiniMax Agent 自进化系统

## 系统概述

MiniMax Agent 自进化系统是一套完整的智能体自我优化框架，通过五层记忆体架构实现经验的积累与策略的进化。系统能够从每次交互中学习，不断优化响应质量，逐步扩展能力边界。

## 核心架构

本系统由三大核心组件构成：**MaxHermes** 负责用户交互与意图识别，**MaxClaw** 负责工具调用与执行，**DeerFlow** 负责任务编排与流程控制。三者协同工作，结合五层记忆体系统，实现智能体的持续进化。

```
┌─────────────────────────────────────────────────────────────────────┐
│                    MINIMAX 自进化系统架构                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│    ┌─────────────────────────────────────────────────────────┐      │
│    │                    MaxHermes (通信层)                    │      │
│    │              用户交互 · 意图识别 · 响应生成               │      │
│    └─────────────────────────┬───────────────────────────────┘      │
│                              │                                       │
│    ┌─────────────────────────▼───────────────────────────────┐      │
│    │                    DeerFlow (编排层)                      │      │
│    │              任务分解 · 流程控制 · 结果整合                │      │
│    └─────────────────────────┬───────────────────────────────┘      │
│                              │                                       │
│    ┌─────────────────────────▼───────────────────────────────┐      │
│    │                    MaxClaw (执行层)                      │      │
│    │              工具选择 · 代码执行 · 错误处理               │      │
│    └─────────────────────────┬───────────────────────────────┘      │
│                              │                                       │
│    ┌─────────────────────────▼───────────────────────────────┐      │
│    │                   进化引擎                              │      │
│    │           经验记录 · 模式提取 · 策略优化                 │      │
│    └─────────────────────────┬───────────────────────────────┘      │
│                              │                                       │
│    ┌─────────────────────────▼───────────────────────────────┐      │
│    │                  5层记忆体系统                           │      │
│    │      L1会话 · L2任务 · L3项目 · L4知识 · L5进化          │      │
│    └─────────────────────────────────────────────────────────┘      │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## 五层记忆体系统

五层记忆体系统是自进化能力的核心基础设施，每一层承担不同的存储职责，共同支持智能体的持续学习。

### 层级结构详解

| 层级 | 名称 | 存储内容 | 持久性 | 访问频率 | 容量 |
|------|------|---------|--------|---------|------|
| L1 | 会话记忆 | 当前对话上下文、用户即时输入 | 会话内 | 极高 | 100条 |
| L2 | 任务记忆 | 当前任务状态、子任务进度、中间结果 | 任务周期 | 高 | 50项 |
| L3 | 项目记忆 | 项目上下文、文件结构、历史决策 | 跨会话 | 中 | 20项目 |
| L4 | 知识库 | 技能定义、模式库、最佳实践 | 永久 | 低 | 无限制 |
| L5 | 进化记忆 | 经验总结、失败教训、优化策略 | 永久 | 低 | 无限制 |

### 记忆体实现

```python
class FiveLayerMemory:
    """MiniMax Agent 五层记忆体系统"""

    def __init__(self):
        # L1: 会话上下文 - Python 字典，最高速访问
        self.l1_session = {}

        # L2: 任务状态 - 任务生命周期管理
        self.l2_task = {
            'current_task': None,
            'subtasks': [],
            'progress': 0.0,
            'checkpoint': None
        }

        # L3: 项目上下文 - JSON 文件持久化
        self.l3_project = ProjectMemory()

        # L4: 知识库 - 向量化存储，支持语义检索
        self.l4_knowledge = VectorKnowledgeBase()

        # L5: 进化记忆 - 经验模式库
        self.l5_evolution = EvolutionMemory()

    async def store(self, layer, key, value, metadata=None):
        """存储到指定记忆层"""
        timestamp = time.time()

        if layer == 1:
            self.l1_session[key] = {
                'value': value,
                'timestamp': timestamp,
                'access_count': 0
            }

        elif layer == 2:
            await self._store_l2(key, value, metadata, timestamp)

        elif layer == 3:
            await self.l3_project.save(key, value, metadata)

        elif layer == 4:
            await self.l4_knowledge.upsert(value, metadata)

        elif layer == 5:
            await self.l5_evolution.record(value, metadata)

    async def retrieve(self, query, layers=None, top_k=5):
        """跨层语义检索"""
        layers = layers or [1, 2, 3, 4, 5]
        results = []

        for layer in layers:
            layer_results = await self._retrieve_layer(layer, query, top_k)
            results.extend(layer_results)

        return self._rank_results(results, query)

    async def _retrieve_layer(self, layer, query, top_k):
        """从指定层检索"""
        if layer == 1:
            return self._search_l1(query, top_k)
        elif layer == 2:
            return await self._search_l2(query, top_k)
        elif layer == 3:
            return await self.l3_project.search(query, top_k)
        elif layer == 4:
            return await self.l4_knowledge.similarity_search(query, top_k)
        elif layer == 5:
            return await self.l5_evolution.query_experiences(query, top_k)
```

## 三大核心组件

### MaxHermes（赫尔墨斯层）

MaxHermes 是用户与系统之间的桥梁，负责意图识别、上下文管理和响应生成。

```python
class MaxHermes:
    """
    赫尔墨斯层 - 用户交互与意图识别
    名称来源于希腊神话中的信使，象征信息的传递与解析
    """

    def __init__(self, memory_system, evolution_engine):
        self.memory = memory_system
        self.evolution = evolution_engine

        # 意图分类器
        self.intent_patterns = {
            'remember_preference': [
                '记住', '保存', '偏好', '以后用', '下次记得'
            ],
            'continue_task': [
                '继续', '从上次', '接着', '还没完成', '上次的'
            ],
            'improve_response': [
                '改进', '优化', '更好', '不满意', '重新回答'
            ],
            'analyze_failure': [
                '失败', '错了', '不对', '分析一下', '为什么'
            ],
            'self_evolve': [
                '学习', '进化', '成长', '改进自己', '变得更好'
            ],
            'complex_task': [
                '构建', '开发', '实现', '设计', '分析', '研究'
            ],
            'simple_query': [
                '什么是', '如何', '怎么', '查询', '告诉我'
            ]
        }

        self.dialogue_state = {}
        self.response_history = []

    async def process_input(self, user_message):
        """处理用户输入"""
        # 1. 意图识别
        intent = self.recognize_intent(user_message)

        # 2. 上下文检索
        context = await self._build_context(user_message, intent)

        # 3. 特殊处理：自进化相关意图
        if intent in ['remember_preference', 'continue_task', 'improve_response',
                      'analyze_failure', 'self_evolve']:
            return await self._handle_evolution_intent(intent, user_message, context)

        # 4. 构建响应
        return {
            'intent': intent,
            'context': context,
            'dialogue_state': self.dialogue_state
        }

    def recognize_intent(self, message):
        """识别用户意图"""
        message_lower = message.lower()

        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if pattern in message_lower:
                    return intent

        return 'general'

    async def _handle_evolution_intent(self, intent, message, context):
        """处理自进化相关意图"""
        handlers = {
            'remember_preference': self._remember_preference,
            'continue_task': self._continue_from_checkpoint,
            'improve_response': self._improve_response,
            'analyze_failure': self._analyze_failure,
            'self_evolve': self._trigger_evolution
        }

        handler = handlers.get(intent)
        if handler:
            return await handler(message, context)
        return {'error': 'Unknown evolution intent'}

    async def _remember_preference(self, message, context):
        """记住用户偏好"""
        # 提取偏好信息
        preference = self._extract_preference(message)

        # 存储到 L5 进化记忆
        await self.memory.store(5, f'preference_{preference["type"]}',
                                 preference,
                                 metadata={'source': 'user_explicit',
                                          'confidence': 0.9})

        return {
            'action': 'preference_saved',
            'preference': preference,
            'message': f'已记住您的偏好：{preference["description"]}'
        }

    async def _continue_from_checkpoint(self, message, context):
        """从检查点继续任务"""
        # 从 L2 检索上次任务状态
        task_state = await self.memory.retrieve('task_state', layers=[2])

        if task_state:
            return {
                'action': 'task_resumed',
                'checkpoint': task_state,
                'message': '已恢复上次任务状态'
            }

        # 尝试从 L3 项目记忆恢复
        project_state = await self.memory.retrieve('project_context', layers=[3])
        if project_state:
            return {
                'action': 'project_resumed',
                'context': project_state,
                'message': '已恢复项目上下文'
            }

        return {
            'action': 'no_checkpoint',
            'message': '未找到可恢复的任务状态'
        }
```

### MaxClaw（执行层）

MaxClaw 负责工具调用、代码执行和错误处理，是系统的执行引擎。

```python
class MaxClaw:
    """
    执行层 - 工具调用与代码执行
    名称来源于爪子，象征精准而有力的执行能力
    """

    def __init__(self, available_tools):
        self.tools = self._register_tools(available_tools)
        self.execution_history = []
        self.retry_policy = RetryPolicy(max_retries=3, backoff='exponential')

    async def execute(self, task_spec, context=None):
        """执行任务"""
        # 1. 任务分解
        atoms = self.decompose_task(task_spec)

        # 2. 依赖分析
        execution_plan = self._plan_execution(atoms)

        # 3. 执行
        results = []
        for step in execution_plan:
            result = await self._execute_step(step, context)
            results.append(result)

            if result.get('error') and not self.retry_policy.should_continue():
                break

        # 4. 结果聚合
        aggregated = self._aggregate_results(results)

        # 5. 记录执行历史
        await self._record_execution(task_spec, results, aggregated)

        return aggregated

    def decompose_task(self, task):
        """将复杂任务分解为原子操作"""
        if isinstance(task, str):
            # 使用模式识别进行分解
            return self._pattern_decompose(task)
        elif isinstance(task, dict) and 'subtasks' in task:
            return task['subtasks']
        return [{'type': 'atomic', 'action': task}]

    def _pattern_decompose(self, task_text):
        """基于模式的自动分解"""
        patterns = [
            (r'.*搜索.*并.*分析.*', ['search', 'analyze']),
            (r'.*创建.*并.*部署.*', ['create', 'test', 'deploy']),
            (r'.*读取.*修改.*保存.*', ['read', 'modify', 'write'])
        ]

        for pattern, actions in patterns:
            if re.match(pattern, task_text):
                return [{'type': 'composite', 'actions': actions, 'source': task_text}]

        return [{'type': 'atomic', 'action': task_text}]
```

### DeerFlow（编排层）

DeerFlow 负责任务编排、流程控制和状态管理，确保复杂任务的正确执行。

```python
class DeerFlow:
    """
    编排层 - 任务协调与流程控制
    名称来源于鹿与流水，象征灵动而有条理的协调能力
    """

    def __init__(self, hermes, claw, memory):
        self.hermes = hermes
        self.claw = claw
        self.memory = memory
        self.task_graph = TaskGraph()
        self.state_manager = StateManager()

    async def orchestrate(self, goal, constraints=None):
        """编排复杂任务"""
        # 1. 目标分析
        subtasks = await self.analyze_goal(goal)

        # 2. 构建任务图
        self.task_graph.build(subtasks)

        # 3. 拓扑排序确定执行顺序
        execution_order = self.task_graph.topological_sort()

        # 4. 创建检查点
        checkpoint_id = await self._create_checkpoint(subtasks)

        # 5. 迭代执行
        results = []
        for subtask_id in execution_order:
            subtask = self.task_graph.get_node(subtask_id)

            # 检查前置条件
            if not await self._check_prerequisites(subtask):
                await self._handle_prerequisite_failure(subtask)
                continue

            # 执行子任务
            result = await self.claw.execute(subtask)

            # 更新图节点状态
            self.task_graph.update_node(subtask_id, {'status': 'completed', 'result': result})
            results.append(result)

            # 更新检查点
            await self._update_checkpoint(checkpoint_id, subtask_id, result)

        # 6. 结果整合
        return await self.synthesize_results(results, goal)

    async def analyze_goal(self, goal):
        """使用 LLM 分析并分解目标"""
        # 构建分析提示
        prompt = f"""
        分析以下目标，将其分解为可执行的子任务：

        目标：{goal}

        要求：
        1. 每个子任务应该是独立的、可执行的
        2. 明确子任务之间的依赖关系
        3. 识别关键决策点
        4. 估计每个子任务的复杂度

        输出格式：JSON
        """

        # 查询 L5 进化记忆获取类似经验
        similar = await self.memory.retrieve(goal, layers=[5], top_k=3)

        # 生成任务分解
        decomposition = await self._generate_decomposition(prompt, similar)

        return decomposition

    async def _create_checkpoint(self, subtasks):
        """创建执行检查点"""
        checkpoint_id = f"cp_{int(time.time() * 1000)}"

        checkpoint_data = {
            'id': checkpoint_id,
            'subtasks': subtasks,
            'status': {st['id']: 'pending' for st in subtasks},
            'created_at': time.time()
        }

        # 存储到 L2 任务记忆
        await self.memory.store(2, 'checkpoint', checkpoint_data)

        return checkpoint_id
```

## 进化引擎

进化引擎是系统的核心学习模块，负责从经验中提取模式、优化策略、扩展能力边界。

```python
class EvolutionEngine:
    """
    进化引擎 - 从经验中学习与优化

    核心机制：
    1. 成功追踪 - 记录成功案例，提取有效策略
    2. 失败分析 - 分析失败原因，提取教训
    3. 模式提取 - 从大量经验中识别重复模式
    4. 策略优化 - 基于模式生成优化建议
    5. 能力扩展 - 识别能力边界，持续扩展
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

    async def record_outcome(self, task, approach, success, metrics=None):
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
        await self.memory.store(5, 'experience', record,
                               metadata={
                                   'success': success,
                                   'task_category': record['task_type']
                               })

        # 更新进化指标
        self.evolution_metrics['total_experiences'] += 1

        if success:
            await self._process_success(record)
        else:
            await self._process_failure(record)

        return record

    async def _process_success(self, record):
        """处理成功经验"""
        # 更新成功追踪器
        await self.success_tracker.record(record)

        # 提取成功模式
        patterns = await self.pattern_extractor.extract_from_success(record)

        # 如果是新模式，添加到模式库
        if patterns and not await self._is_known_pattern(patterns):
            await self.memory.store(4, 'success_pattern', patterns,
                                   metadata={'source': 'experience'})

    async def _process_failure(self, record):
        """处理失败经验"""
        # 提取失败原因
        failure_analysis = await self._analyze_failure(record)

        # 存储失败教训
        await self.memory.store(5, 'failure_lesson', {
            'task': record['task_type'],
            'cause': failure_analysis['root_cause'],
            'lesson': failure_analysis['lesson'],
            'recovery': failure_analysis['recovery_action']
        })

        # 更新失败模式库
        self.evolution_metrics['failed_patterns'].append(failure_analysis)

        # 生成改进建议
        suggestion = await self._generate_improvement_suggestion(failure_analysis)
        if suggestion:
            self.evolution_metrics['improvement_suggestions'].append(suggestion)

    async def get_optimized_approach(self, task):
        """获取针对任务的优化执行方案"""
        task_type = self._classify_task(task)

        # 1. 查询类似任务的历史经验
        similar_experiences = await self.memory.retrieve(task, layers=[5], top_k=10)

        # 2. 分析成功模式
        success_patterns = [e for e in similar_experiences if e.get('success')]

        if success_patterns:
            # 从成功经验中提取最优策略
            best_strategy = self._extract_best_strategy(success_patterns)
            return {
                'strategy': best_strategy,
                'confidence': len(success_patterns) / 10,
                'source': 'learned'
            }

        # 3. 查询知识库获取通用最佳实践
        general_practices = await self.memory.retrieve(task_type, layers=[4], top_k=3)

        if general_practices:
            return {
                'strategy': general_practices[0],
                'confidence': 0.6,
                'source': 'knowledge_base'
            }

        # 4. 返回默认策略
        return {
            'strategy': 'default_approach',
            'confidence': 0.3,
            'source': 'fallback'
        }

    async def trigger_self_evolution(self):
        """触发自我进化"""
        evolution_report = {
            'timestamp': time.time(),
            'improvements': [],
            'new_capabilities': [],
            'deprecated_patterns': []
        }

        # 1. 分析近期经验趋势
        recent = await self._get_recent_experiences(100)

        # 2. 识别改进空间
        improvements = await self._identify_improvements(recent)

        # 3. 应用优化
        for improvement in improvements:
            applied = await self._apply_improvement(improvement)
            if applied:
                evolution_report['improvements'].append(applied)

        # 4. 扩展能力边界
        new_capabilities = await self._expand_capabilities(recent)
        evolution_report['new_capabilities'] = new_capabilities

        # 5. 记录进化事件
        await self._record_evolution_event(evolution_report)

        return evolution_report

    async def _identify_improvements(self, experiences):
        """从经验中识别改进机会"""
        improvements = []

        # 分析成功率变化
        success_rate = sum(1 for e in experiences if e.get('success')) / len(experiences)

        if success_rate < 0.7:
            improvements.append({
                'type': 'success_rate',
                'current': success_rate,
                'target': 0.8,
                'action': 'analyze_failure_patterns'
            })

        # 分析执行时间趋势
        avg_time = self._calculate_avg_execution_time(experiences)
        if avg_time > self._get_baseline_time():
            improvements.append({
                'type': 'efficiency',
                'current': avg_time,
                'target': self._get_baseline_time() * 0.8,
                'action': 'optimize_execution_path'
            })

        # 分析错误类型
        error_types = self._analyze_error_types(experiences)
        for error_type, count in error_types.items():
            if count > 5:
                improvements.append({
                    'type': 'error_reduction',
                    'error_type': error_type,
                    'count': count,
                    'action': f'address_{error_type}'
                })

        return improvements
```

## 触发场景与响应

### 记住偏好（remember_preference）

当用户表达偏好时，系统将其存储到 L5 进化记忆，并在后续交互中自动应用。

```python
async def handle_remember_preference(self, preference_text):
    """处理记住偏好请求"""
    # 1. 解析偏好
    preference = self._parse_preference(preference_text)

    # 2. 存储到 L5
    await self.memory.store(5, f'preference_{preference.type}',
                           preference,
                           metadata={
                               'learned_at': time.time(),
                               'confidence': preference.confidence,
                               'context': preference.context
                           })

    # 3. 更新响应策略
    await self._update_response_strategy(preference)

    return {
        'action': 'preference_remembered',
        'description': preference.description,
        'impact': '已调整后续响应以匹配您的偏好'
    }
```

### 从上次继续（continue_task）

系统从 L2/L3 记忆恢复任务状态，实现无缝继续。

```python
async def handle_continue_task(self):
    """处理继续任务请求"""
    # 1. 检查 L2 任务记忆
    task_state = await self.memory.retrieve('current_task_state', layers=[2])

    if task_state:
        return {
            'action': 'resume_task',
            'checkpoint': task_state,
            'message': '已找到未完成任务，正在恢复...'
        }

    # 2. 检查 L3 项目记忆
    project_state = await self.memory.retrieve('project_context', layers=[3])

    if project_state:
        return {
            'action': 'resume_project',
            'context': project_state,
            'message': '已找到项目上下文，正在加载...'
        }

    return {
        'action': 'no_checkpoint_found',
        'message': '未找到可恢复的任务或项目'
    }
```

### 改进回答（improve_response）

系统分析之前的响应，识别改进点，并生成优化版本。

```python
async def handle_improve_response(self, original_response, feedback):
    """处理改进回答请求"""
    # 1. 分析反馈
    issues = self._analyze_issues(feedback, original_response)

    # 2. 检索类似成功案例
    successful = await self.memory.retrieve(original_response.topic,
                                           layers=[5], top_k=5)

    # 3. 生成改进版本
    improved = await self._generate_improved_response(
        original_response,
        issues,
        successful_examples=successful
    )

    # 4. 记录改进过程
    await self.memory.store(5, 'response_improvement', {
        'original': original_response,
        'issues': issues,
        'improved': improved,
        'feedback': feedback
    })

    return improved
```

### 分析失败（analyze_failure）

系统深入分析失败原因，提取教训并生成预防建议。

```python
async def handle_analyze_failure(self, failure_context):
    """处理分析失败请求"""
    # 1. 收集失败相关记忆
    related_experiences = await self.memory.retrieve(
        failure_context.description,
        layers=[2, 3, 5],
        top_k=10
    )

    # 2. 深度分析
    analysis = await self._deep_failure_analysis(
        failure_context,
        related_experiences
    )

    # 3. 生成报告
    report = {
        'root_cause': analysis.root_cause,
        'contributing_factors': analysis.factors,
        'lessons': analysis.lessons,
        'prevention': analysis.prevention_steps,
        'recovery': analysis.recovery_actions
    }

    # 4. 存储分析结果
    await self.memory.store(5, 'failure_analysis', report)

    return report
```

### 自我进化（self_evolve）

系统运行完整的自我评估和优化流程。

```python
async def handle_self_evolution(self):
    """处理自我进化请求"""
    # 1. 收集全量经验
    all_experiences = await self._collect_all_experiences()

    # 2. 生成进化报告
    evolution = await self.trigger_self_evolution()

    # 3. 应用可执行的改进
    applied = await self._apply_evolution_changes(evolution)

    # 4. 生成进化摘要
    summary = {
        'total_experiences_analyzed': len(all_experiences),
        'improvements_made': len(applied),
        'new_capabilities': evolution.get('new_capabilities', []),
        'next_steps': evolution.get('next_steps', [])
    }

    return summary
```

## 文件结构

```
minimax-self-evolution/
├── SKILL.md                     # 主技能文档
├── scripts/
│   ├── memory_manager.py        # 记忆体管理器
│   ├── evolution_engine.py      # 进化引擎实现
│   └── integration.py           # 系统集成脚本
├── references/
│   ├── architecture.md          # 详细架构设计
│   ├── memory_design.md         # 记忆体设计说明
│   └── evolution_logic.md       # 进化逻辑详解
└── assets/
    └── system_diagram.svg       # 系统架构图
```

## 集成使用

```python
from minimax_self_evolution import (
    MiniMaxSelfEvolution,
    FiveLayerMemory,
    EvolutionEngine
)

# 初始化系统
memory = FiveLayerMemory()
evolution = EvolutionEngine(memory)
system = MiniMaxSelfEvolution(memory, evolution)

# 处理用户请求
response = await system.process(
    "记住我喜欢简洁的回答",
    intent='remember_preference'
)

# 继续未完成任务
response = await system.process(
    "继续上次的任务",
    intent='continue_task'
)

# 触发自我进化
evolution_report = await system.evolve()
```

## 总结

MiniMax Agent 自进化系统通过五层记忆体架构和三大核心组件的协同工作，实现了智能体的持续学习和自我优化。系统能够从每次交互中积累经验，识别模式，优化策略，最终实现能力的不断提升。

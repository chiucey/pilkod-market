---
name: max-hcd-composite
description: MaxHermes+MaxClaw+DeerFlow 多智能体复合体系统。当用户要求处理复杂多步骤任务、构建多代理协作系统、设计记忆体架构、进行长程任务规划、需要自我进化能力的AI系统时使用此技能。触发场景：复杂任务分解、多代理协调、5层记忆体实现、进化学习系统、MaxHermes/MaxClaw/DeerFlow相关开发。
---

# MaxHermes + MaxClaw + DeerFlow 复合体系统

## 系统概览

```
┌─────────────────────────────────────────────────────────────────────┐
│                    MAX-HCD COMPOSITE SYSTEM                         │
├─────────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐              │
│  │   MAXHERMES │ + │   MAXCLAW   │ + │   DEERFLOW  │              │
│  │  (通信层)   │   │  (执行层)   │   │  (流程层)   │              │
│  └──────┬──────┘   └──────┬──────┘   └──────┬──────┘              │
│         │                 │                 │                      │
│         └─────────────────┼─────────────────┘                      │
│                           │                                          │
│                    ┌──────▼──────┐                                  │
│                    │  5-LAYER    │                                  │
│                    │  MEMORY     │                                  │
│                    │  SYSTEM     │                                  │
│                    └──────┬──────┘                                  │
│                           │                                          │
│                    ┌──────▼──────┐                                  │
│                    │ EVOLUTION   │                                  │
│                    │ ENGINE      │                                  │
│                    └─────────────┘                                  │
└─────────────────────────────────────────────────────────────────────┘
```

## 核心组件

### 1. MaxHermes (赫尔墨斯 - 信使层)

**职责**: 用户交互与消息路由

- 接收并解析用户输入
- 意图识别与任务分类
- 多轮对话状态管理
- 响应生成与格式化

**实现要点**:
```python
class MaxHermes:
    def __init__(self, memory_system, evolution_engine):
        self.memory = memory_system  # L1-L2 短中期记忆
        self.evolution = evolution_engine
        self.dialogue_state = {}

    async def process_input(self, user_message):
        # 1. 意图识别
        intent = self.recognize_intent(user_message)
        # 2. 记忆检索
        context = await self.memory.retrieve(user_message)
        # 3. 任务路由
        return self.route_task(intent, context)

    def recognize_intent(self, message):
        # 简单规则 + 模式匹配
        patterns = {
            'complex_task': ['分析', '构建', '实现', '设计', '开发'],
            'simple_query': ['什么是', '如何', '怎么', '查询'],
            'creative': ['创作', '写', '生成', '制作']
        }
```

### 2. MaxClaw (爪子 - 执行层)

**职责**: 工具调用与代码执行

- 工具选择与调用编排
- 代码生成与执行
- 文件系统操作
- 错误处理与重试

**实现要点**:
```python
class MaxClaw:
    def __init__(self, available_tools):
        self.tools = self.register_tools(available_tools)
        self.execution_history = []

    async def execute(self, task_spec):
        # 1. 分解为原子操作
        atoms = self.decompose(task_spec)
        # 2. 依赖分析
        plan = self.plan_execution(atoms)
        # 3. 并行/串行执行
        results = await self.run_plan(plan)
        # 4. 结果聚合
        return self.aggregate(results)

    def decompose(self, task):
        # 递归分解任务为可执行单元
        pass
```

### 3. DeerFlow (鹿流 - 流程层)

**职责**: 任务编排与状态管理

- 复杂任务分解
- 子任务依赖管理
- 执行流程控制
- 中间结果缓存

**实现要点**:
```python
class DeerFlow:
    def __init__(self, hermes, claw, memory):
        self.hermes = hermes
        self.claw = claw
        self.memory = memory
        self.task_graph = TaskGraph()

    async def orchestrate(self, goal):
        # 1. 目标分析
        subgoals = self.analyze_goal(goal)
        # 2. 构建任务图
        self.task_graph.build(subgoals)
        # 3. 拓扑排序执行
        execution_order = self.task_graph.topological_sort()
        # 4. 迭代执行
        results = await self.execute_ordered(execution_order)
        # 5. 结果整合
        return self.synthesize(results)

    def analyze_goal(self, goal):
        # 使用LLM进行目标分解
        pass
```

## 5层记忆体系统

```
┌────────────────────────────────────────────────────────────┐
│                      MEMORY HIERARCHY                       │
├────────────────────────────────────────────────────────────┤
│  L5 │ EVOLUTION MEMORY  │ 经验总结 │ 自我优化 │ 永久持久 │
├─────┼───────────────────┼──────────┼──────────┼───────────┤
│  L4 │ KNOWLEDGE BASE    │ 知识存储 │ 结构化   │ 永久持久 │
├─────┼───────────────────┼──────────┼──────────┼───────────┤
│  L3 │ PROJECT MEMORY    │ 项目上下文│ 会话持久 │ 跨会话   │
├─────┼───────────────────┼──────────┼──────────┼───────────┤
│  L2 │ TASK MEMORY       │ 任务状态 │ 任务周期 │ 任务内   │
├─────┼───────────────────┼──────────┼──────────┼───────────┤
│  L1 │ SESSION CONTEXT   │ 当前上下文│ 会话内存 │ 会话内   │
└────────────────────────────────────────────────────────────┘
```

### 记忆层实现

```python
class FiveLayerMemory:
    """5层记忆体系统"""

    def __init__(self):
        # L1: 短时会话 - 字典结构
        self.l1_session = {}

        # L2: 任务记忆 - 当前任务上下文
        self.l2_task = {
            'current_task': None,
            'subtasks': [],
            'progress': 0.0
        }

        # L3: 项目记忆 - 持久化存储
        self.l3_project = PersistentDict('project_memory.json')

        # L4: 知识库 - 向量化存储
        self.l4_knowledge = VectorStore('knowledge_base')

        # L5: 进化记忆 - 经验模式库
        self.l5_evolution = ExperienceStore('evolution_memory')

    async def store(self, layer, key, value, metadata=None):
        """存储到指定层"""
        if layer == 1:
            self.l1_session[key] = {'value': value, 'ts': time.time()}
        elif layer == 2:
            self.l2_task[key] = value
        elif layer == 3:
            await self.l3_project.set(key, value, metadata)
        elif layer == 4:
            await self.l4_knowledge.add(value, metadata)
        elif layer == 5:
            await self.l5_evolution.record(value, metadata)

    async def retrieve(self, query, layers=None, top_k=5):
        """跨层检索"""
        layers = layers or [1, 2, 3, 4, 5]
        results = []

        for layer in sorted(layers):
            if layer == 1:
                results.extend(self._retrieve_l1(query))
            elif layer == 2:
                results.extend(await self._retrieve_l2(query, top_k))
            elif layer == 3:
                results.extend(await self.l3_project.search(query, top_k))
            elif layer == 4:
                results.extend(await self.l4_knowledge.search(query, top_k))
            elif layer == 5:
                results.extend(await self.l5_evolution.query(query, top_k))

        return self._rank_and_merge(results)
```

## 进化引擎

```python
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

    async def record_outcome(self, task, approach, success, metrics):
        """记录任务执行结果"""
        record = {
            'task_type': self.classify_task(task),
            'approach': approach,
            'success': success,
            'metrics': metrics,
            'timestamp': time.time()
        }

        # 存储到L5进化记忆
        await self.memory.store(5, 'outcome', record)

        # 更新成功追踪
        await self.success_tracker.update(record)

        # 如果失败，提取教训
        if not success:
            await self.extract_lessons(record)

    async def get_optimized_approach(self, task):
        """获取优化后的任务执行方法"""
        task_type = self.classify_task(task)

        # 1. 查询历史成功案例
        similar = await self.memory.retrieve(task, layers=[5], top_k=10)

        # 2. 分析成功模式
        patterns = await self.pattern_extractor.analyze(similar)

        # 3. 生成优化建议
        return await self.optimizer.generate(patterns)

    async def evolve_capabilities(self):
        """触发能力进化"""
        # 1. 收集近期经验
        recent = await self.memory.l5_evolution.get_recent(100)

        # 2. 识别改进空间
        improvements = self.identify_improvements(recent)

        # 3. 应用优化
        for imp in improvements:
            await self.apply_optimization(imp)

        # 4. 记录进化事件
        await self.record_evolution_event(improvements)
```

## 协作流程

```
User Input
    │
    ▼
┌──────────────┐
│  MaxHermes   │ ◄── L1 Session Context
│  (意图识别)   │
└──────┬───────┘
       │ Intent + Context
       ▼
┌──────────────┐
│  DeerFlow    │ ◄── L2 Task Memory, L3 Project Memory
│  (任务编排)   │
└──────┬───────┘
       │ Subtask Graph
       ▼
┌──────────────┐
│  MaxClaw     │ ◄── L1-L5 All Memory Layers
│  (并行执行)   │
└──────┬───────┘
       │ Results
       ▼
┌──────────────┐
│  DeerFlow    │ ◄── 结果整合
│  (结果聚合)   │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Evolution   │ ◄── 记录到L5 Evolution Memory
│  (进化学习)   │
└──────┬───────┘
       │
       ▼
   Final Response
```

## 使用示例

### 场景1: 复杂项目开发

```python
# 用户请求: "帮我构建一个电商系统，包含用户、订单、商品模块"
async def handle_ecommerce_project(user_request):
    # 1. MaxHermes 处理输入
    intent = await hermes.process_input(user_request)

    # 2. DeerFlow 分解任务
    subtasks = await deerflow.analyze_goal(intent)

    # 3. MaxClaw 执行
    for subtask in subtasks:
        result = await claw.execute(subtask)

    # 4. 进化引擎记录
    await evolution.record_outcome(
        task=user_request,
        approach=subtasks,
        success=True,
        metrics={'time': '2h', 'modules': 3}
    )
```

### 场景2: 经验驱动优化

```python
# 当遇到类似任务时，查询L5进化记忆
optimized_approach = await evolution.get_optimized_approach(
    "构建REST API"
)

# 使用优化后的策略执行
result = await claw.execute(task, strategy=optimized_approach)
```

## 集成指南

将此复合体集成到现有系统:

```python
from max_hcd_composite import (
    MaxHCDComposite,
    FiveLayerMemory,
    EvolutionEngine
)

# 1. 初始化组件
memory = FiveLayerMemory()
evolution = EvolutionEngine(memory)
composite = MaxHCDComposite(memory, evolution)

# 2. 注册工具
composite.register_tools([...your_tools...])

# 3. 处理请求
response = await composite.process("帮我分析这个数据集")
```

## 文件结构

```
max-hcd-composite/
├── SKILL.md                 # 本文件
├── _meta.json               # 元数据
├── scripts/
│   ├── init_composite.py    # 初始化脚本
│   ├── memory_manager.py    # 记忆体管理
│   └── evolution_runner.py  # 进化引擎
├── references/
│   ├── architecture.md      # 详细架构文档
│   ├── memory_design.md     # 记忆体设计说明
│   └── evolution_logic.md   # 进化逻辑详解
└── assets/
    └── system_diagram.svg   # 系统架构图
```

## 扩展点

1. **自定义组件**: 继承BaseAgent实现自己的MaxHermes/MaxClaw/DeerFlow
2. **记忆体后端**: 支持Redis/PostgreSQL/Pinecone等
3. **进化策略**: 自定义进化算法和评估标准
4. **工具集**: 扩展MaxClaw的工具库

---

*此技能遵循模块化设计，支持独立升级各组件*

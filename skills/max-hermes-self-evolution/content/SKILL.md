---
name: max-hermes-self-evolution
description: MiniMax Agent 自进化核心技能。当用户要求"记住偏好"、"从上次继续"、"改进回答"、"分析失败原因"、"自我进化"时使用此技能。实现五层记忆体架构、经验模式提取、策略优化和能力边界扩展。
---

# MaxHermes Self-Evolution System

## 系统概述

MiniMax Agent 自进化系统是一套完整的智能体自我优化框架，通过五层记忆体架构实现经验的积累与策略的进化。系统能够从每次交互中学习，不断优化响应质量，逐步扩展能力边界。

## 五层记忆体架构

| 层级 | 名称 | 存储内容 | 持久性 | 访问频率 |
|------|------|---------|--------|----------|
| L1 | 会话记忆 | 当前对话上下文、用户即时输入 | 会话内 | 极高 |
| L2 | 任务记忆 | 当前任务状态、子任务进度、中间结果 | 任务周期 | 高 |
| L3 | 项目记忆 | 项目上下文、文件结构、历史决策 | 跨会话 | 中 |
| L4 | 知识库 | 技能定义、模式库、最佳实践 | 永久 | 低 |
| L5 | 进化记忆 | 经验总结、失败教训、优化策略 | 永久 | 低 |

## 核心组件

### MaxHermes（通信层）

负责用户交互、意图识别、上下文管理和响应生成。

**意图分类器**：
- `remember_preference`: 记住偏好（"记住"、"保存"、"偏好"）
- `continue_task`: 从上次继续（"继续"、"从上次"、"接着"）
- `improve_response`: 改进回答（"改进"、"优化"、"重新回答"）
- `analyze_failure`: 分析失败（"失败"、"错了"、"分析"）
- `self_evolve`: 自我进化（"学习"、"进化"、"成长"）

### MaxClaw（执行层）

负责工具调用、代码执行和错误处理。

- 任务分解：将复杂任务分解为原子操作
- 依赖分析：规划执行顺序
- 执行与重试：指数退避重试策略
- 结果聚合：整合多步执行结果

### DeerFlow（编排层）

负责任务编排、流程控制和状态管理。

- 目标分析：使用 LLM 分析并分解目标
- 任务图构建：建立依赖关系图
- 拓扑排序：确定最优执行顺序
- 检查点管理：支持任务恢复

## 进化引擎

### 核心机制

1. **成功追踪**：记录成功案例，提取有效策略
2. **失败分析**：分析失败原因，提取教训
3. **模式提取**：从大量经验中识别重复模式
4. **策略优化**：基于模式生成优化建议
5. **能力扩展**：识别能力边界，持续扩展

### 进化指标

```python
evolution_metrics = {
    'total_experiences': 0,
    'successful_strategies': [],
    'failed_patterns': [],
    'capability_boundaries': [],
    'improvement_suggestions': []
}
```

## 触发场景与响应

### 记住偏好

```python
async def handle_remember_preference(self, preference_text):
    # 1. 解析偏好
    preference = self._parse_preference(preference_text)
    # 2. 存储到 L5
    await self.memory.store(5, f'preference_{preference.type}', preference)
    # 3. 更新响应策略
    await self._update_response_strategy(preference)
    return {'action': 'preference_remembered', 'impact': '已调整后续响应'}
```

### 从上次继续

```python
async def handle_continue_task(self):
    # 1. 检查 L2 任务记忆
    task_state = await self.memory.retrieve('current_task_state', layers=[2])
    if task_state:
        return {'action': 'resume_task', 'checkpoint': task_state}
    # 2. 检查 L3 项目记忆
    project_state = await self.memory.retrieve('project_context', layers=[3])
    if project_state:
        return {'action': 'resume_project', 'context': project_state}
    return {'action': 'no_checkpoint_found'}
```

### 分析失败

```python
async def handle_analyze_failure(self, failure_context):
    # 1. 收集失败相关记忆
    related_experiences = await self.memory.retrieve(failure_context.description, layers=[2,3,5])
    # 2. 深度分析
    analysis = await self._deep_failure_analysis(failure_context, related_experiences)
    # 3. 生成报告
    return {
        'root_cause': analysis.root_cause,
        'lessons': analysis.lessons,
        'prevention': analysis.prevention_steps
    }
```

### 自我进化

```python
async def handle_self_evolution(self):
    # 1. 收集全量经验
    all_experiences = await self._collect_all_experiences()
    # 2. 触发进化
    evolution = await self.evolution_engine.trigger_self_evolution()
    # 3. 应用改进
    applied = await self._apply_evolution_changes(evolution)
    return {
        'experiences_analyzed': len(all_experiences),
        'improvements_made': len(applied),
        'new_capabilities': evolution.get('new_capabilities', [])
    }
```

## 记忆体实现

```python
class FiveLayerMemory:
    def __init__(self):
        self.l1_session = {}          # 会话上下文
        self.l2_task = {}             # 任务状态
        self.l3_project = ProjectMemory()      # 项目上下文
        self.l4_knowledge = VectorKnowledgeBase()  # 向量知识库
        self.l5_evolution = EvolutionMemory()  # 进化记忆

    async def store(self, layer, key, value, metadata=None):
        if layer == 1:
            self.l1_session[key] = {'value': value, 'timestamp': time.time()}
        elif layer == 2:
            await self._store_l2(key, value, metadata)
        elif layer == 3:
            await self.l3_project.save(key, value, metadata)
        elif layer == 4:
            await self.l4_knowledge.upsert(value, metadata)
        elif layer == 5:
            await self.l5_evolution.record(value, metadata)

    async def retrieve(self, query, layers=None, top_k=5):
        layers = layers or [1, 2, 3, 4, 5]
        results = [await self._retrieve_layer(l, query, top_k) for l in layers]
        return self._rank_results(results, query)
```

## 使用方式

```python
from minimax_self_evolution import MiniMaxSelfEvolution

# 初始化
system = MiniMaxSelfEvolution()

# 记住偏好
await system.process("记住我喜欢简洁的回答", intent='remember_preference')

# 继续任务
await system.process("继续上次的任务", intent='continue_task')

# 自我进化
evolution_report = await system.evolve()
```

## 总结

MaxHermes 自进化系统通过五层记忆体架构和三大核心组件（MaxHermes、MaxClaw、DeerFlow）的协同工作，实现了智能体的持续学习和自我优化。系统从每次交互中积累经验，识别模式，优化策略，最终实现能力的不断提升。

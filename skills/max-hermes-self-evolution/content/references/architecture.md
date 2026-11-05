# MaxHermes Self-Evolution Architecture

## Architecture Overview

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
│    │                   进化引擎                                │      │
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

## Component Responsibilities

### MaxHermes (Communication Layer)
- User intent recognition
- Context management
- Response generation
- Dialogue state tracking

### MaxClaw (Execution Layer)
- Task decomposition
- Tool selection and execution
- Error handling and retry
- Result aggregation

### DeerFlow (Orchestration Layer)
- Goal analysis
- Task graph construction
- Dependency management
- Checkpoint creation and recovery

### Evolution Engine
- Experience recording
- Pattern extraction
- Strategy optimization
- Capability expansion

## Data Flow

1. **Input**: User message arrives at MaxHermes
2. **Recognition**: Intent is classified using pattern matching
3. **Retrieval**: Relevant memories are fetched from 5-layer system
4. **Execution**: DeerFlow orchestrates task execution via MaxClaw
5. **Recording**: Results are stored and analyzed by Evolution Engine
6. **Output**: Response is generated and returned to user

## State Management

Each component maintains its own state:

- **MaxHermes**: `dialogue_state`, `response_history`
- **MaxClaw**: `execution_history`, `retry_policy`
- **DeerFlow**: `task_graph`, `state_manager`
- **Evolution**: `evolution_metrics`, `success_tracker`

# Max-RDT 架构设计文档

## 一、系统概述

Max-RDT (Max-Recursive Deployment Theory) 是一种用户专属工作流认知系统，通过持续学习用户行为来构建个性化AI交互模型。

### 1.1 设计目标

- **Recipe（工作流认知）**: 从用户行为中提取重复模式，生成个性化工作流模板
- **Data Flywheel（数据飞轮）**: 用户行为数据反哺，形成正向循环优化
- **Taste Standard（品味标准）**: 构建用户主观评价体系，让输出更符合审美

### 1.2 核心价值

```
传统方式: 用户 → AI → 固定响应 → 用户适应AI
Max-RDT:  用户 → AI → 学习用户 → 适应用户
```

## 二、系统架构

```
┌─────────────────────────────────────────────────────────────────┐
│                        Max-RDT Core                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐      │
│  │   Recipe      │  │  Data        │  │  Taste       │      │
│  │   Engine      │  │  Flywheel    │  │  Standard    │      │
│  │               │  │               │  │               │      │
│  │ - Pattern     │  │ - Behavior   │  │ - Domain     │      │
│  │   Detector    │  │   Collector   │  │   Classifier │      │
│  │ - Workflow    │  │ - Pattern     │  │ - Quality    │      │
│  │   Builder     │  │   Miner       │  │   Evaluator  │      │
│  │ - Preference  │  │ - Quality     │  │ - Style      │      │
│  │   Encoder     │  │   Evaluator   │  │   Matcher    │      │
│  │ - Recipe      │  │ - Evolution   │  │ - Standard   │      │
│  │   Database    │  │   Trigger     │  │   Calibrator │      │
│  └───────┬───────┘  └───────┬───────┘  └───────┬───────┘      │
│          │                  │                  │               │
│          └──────────────────┼──────────────────┘               │
│                             │                                    │
│                    ┌────────▼────────┐                           │
│                    │   Max-RDT       │                           │
│                    │   Layer         │                           │
│                    │   (集成层)      │                           │
│                    └────────┬────────┘                           │
│                             │                                    │
└─────────────────────────────┼─────────────────────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │   Max-HCD       │
                    │   Composite     │
                    │   System        │
                    └─────────────────┘
```

## 三、模块详细设计

### 3.1 Recipe Engine（工作流认知引擎）

#### 3.1.1 核心组件

| 组件 | 职责 | 输入 | 输出 |
|------|------|------|------|
| PatternDetector | 行为模式检测 | 交互历史 | 模式列表 |
| WorkflowGraphBuilder | 工作流图构建 | 模式 | Workflow对象 |
| PreferenceEncoder | 偏好编码 | 交互历史 | UserPreferences |
| RecipeDatabase | 配方存储检索 | Recipe对象 | 检索结果 |

#### 3.1.2 Recipe数据结构

```python
@dataclass
class Recipe:
    recipe_id: str           # 唯一标识
    user_id: str            # 所属用户
    name: str               # 配方名称
    workflow: Workflow      # 工作流结构
    preferences: UserPreferences  # 偏好配置
    confidence: float       # 置信度 0-1
    trigger_conditions: List[TriggerCondition]  # 触发条件
    usage_count: int        # 使用次数
    success_rate: float     # 成功率
```

#### 3.1.3 工作流图结构

```
Entry → Decompose → Parallel Exec → Synthesis → Exit
         ↓              ↓              ↓
      [Task 1]      [Task 2]       [Merge]
```

### 3.2 Data Flywheel（数据飞轮）

#### 3.2.1 循环机制

```
┌─────────────────────────────────────────────────────────┐
│                   DATA FLYWHEEL CYCLE                    │
├─────────────────────────────────────────────────────────┤
│                                                          │
│    ┌──────────┐                                         │
│    │  行为    │                                         │
│    │  采集    │ ◄────────────────────────────────┐     │
│    └────┬─────┘                                  │     │
│         │                                        │     │
│         ▼                                        │     │
│    ┌──────────┐                                 │     │
│    │  模式    │                                 │     │
│    │  提取    │                                 │     │
│    └────┬─────┘                                 │     │
│         │                                        │     │
│         ▼                                        │     │
│    ┌──────────┐                                 │     │
│    │  质量    │                                 │     │
│    │  评估    │                                 │     │
│    └────┬─────┘                                 │     │
│         │                                        │     │
│         ▼                                        │     │
│    ┌──────────┐                                 │     │
│    │  进化    │ ───────────────────────────────►│     │
│    │  触发    │                                 │     │
│    └──────────┘                                 │     │
│         │                                        │     │
│         ▼                                        │     │
│    ┌──────────┐                                 │     │
│    │  优化    │────────────────────────────────┘     │
│    │  反馈    │                                       │
│    └──────────┘                                       │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

#### 3.2.2 行为采集维度

| 维度 | 指标 | 说明 |
|------|------|------|
| 输入风格 | verbose/concise/structured | 文本长度和结构化程度 |
| 复杂度容忍 | 0-10 | 用户能接受的复杂度 |
| 耐心程度 | high/medium/low | 响应时间容忍 |
| 接受率 | 0-1 | 首次接受比例 |
| 学习速度 | 0-1 | 响应提示的能力 |

### 3.3 Taste Standard（品味标准）

#### 3.3.1 领域分类

```
general ─────────┬── code_generation
                  ├── writing
                  ├── analysis
                  ├── creative
                  └── data_processing
```

#### 3.3.2 评估维度

| 维度 | 说明 | 权重示例 |
|------|------|---------|
| relevance | 与请求的相关性 | 0.3 |
| style_match | 风格匹配度 | 0.2 |
| quality_perception | 质量感知 | 0.5 |

## 四、与Max-HCD集成

### 4.1 集成位置

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
│  Max-RDT     │ ◄── 感知增强层 (NEW)
│  (用户认知)   │
└──────┬───────┘
       │ Enhanced Context
       ▼
┌──────────────┐
│  DeerFlow    │ ◄── L2 Task Memory, L3 Project Memory
│  (任务编排)   │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  MaxClaw     │ ◄── 执行层
│  (并行执行)   │
└──────┬───────┘
       │
       ▼
   Response → Max-RDT (更新学习)
```

### 4.2 集成接口

```python
class MaxRDTLayer:
    async def enhance_task(self, task, user_id) -> EnhancedTaskContext:
        """任务增强"""

    async def record_outcome(self, task, result, feedback, user_id) -> TaskOutcome:
        """结果记录"""
```

## 五、数据存储

### 5.1 存储方案

| 数据类型 | 存储方案 | 说明 |
|---------|---------|------|
| Recipe | SQLite/JSON | 结构化存储 |
| Taste Profile | JSON | 领域品味序列化 |
| 行为数据 | SQLite | 时序数据 |
| 模式缓存 | 内存/Redis | 热数据 |

### 5.2 数据生命周期

```
采集 → 处理 → 存储 → 检索 → 清理
  │       │       │       │       │
  └───────┴───────┴───────┴───────┘
         (实时或批处理)
```

## 六、扩展设计

### 6.1 多用户支持

```python
# 每个用户独立的数据空间
user_data = {
    'recipes': List[Recipe],
    'taste_profile': TasteProfile,
    'behavior_history': List[BehaviorEvent],
    'patterns': List[InteractionPattern]
}
```

### 6.2 领域扩展

```python
# 支持自定义领域
class CustomDomain(DomainClassifier):
    DOMAIN_PATTERNS = {
        'legal': {...},
        'medical': {...},
        'financial': {...}
    }
```

### 6.3 存储后端扩展

```python
# 支持多种存储后端
class StorageBackend:
    async def save(self, key, value): pass
    async def load(self, key): pass
    async def search(self, query): pass

# 实现示例
- SQLiteBackend
- RedisBackend
- PineconeBackend (向量存储)
```

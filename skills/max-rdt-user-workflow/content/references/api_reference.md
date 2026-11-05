# Max-RDT API 参考文档

## 模块结构

```
max_rdt/
├── __init__.py          # 统一入口
├── models.py            # 数据模型
├── recipe_engine.py     # Recipe引擎
├── data_flywheel.py     # Data Flywheel引擎
├── taste_engine.py      # Taste Standard引擎
└── integration.py      # Max-RDT Layer集成
```

## RecipeEngine

### 构造配方

```python
async def construct_recipe(
    user_id: str,
    interaction_history: List[Dict],
    name: str = None,
    description: str = None
) -> Recipe
```

**参数:**
- `user_id` (str): 用户唯一标识
- `interaction_history` (List[Dict]): 历史交互数据
- `name` (str, optional): 配方名称
- `description` (str, optional): 配方描述

**返回:**
- `Recipe`: 构建的配方对象

**示例:**
```python
history = [
    {"input": "分析销售数据", "actions": ["分解任务", "执行分析"]},
    {"input": "生成报告", "actions": ["汇总结果"]}
]
recipe = await engine.construct_recipe("user_123", history)
```

### 查找匹配配方

```python
async def find_matching_recipe(
    task: Dict,
    user_id: str
) -> Optional[Recipe]
```

**参数:**
- `task` (Dict): 任务描述
- `user_id` (str): 用户标识

**返回:**
- `Optional[Recipe]`: 匹配的配方，未找到返回None

### 获取用户配方

```python
async def get_user_recipes(
    user_id: str
) -> List[Recipe]
```

## DataFlywheel

### 执行飞轮周期

```python
async def spin(
    user_id: str,
    interaction: Dict
) -> FlywheelMetrics
```

**参数:**
- `user_id` (str): 用户唯一标识
- `interaction` (Dict): 交互数据

**交互数据格式:**
```python
{
    "input": str,           # 用户输入
    "output": str,          # 系统输出
    "feedback": {           # 用户反馈（可选）
        "accepted": bool,
        "rating": int,      # 1-5
        "reasons": List[str]
    },
    "success": bool,        # 是否成功
    "response_time_ms": int # 响应时间
}
```

**返回:**
- `FlywheelMetrics`: 飞轮执行指标

**FlywheelMetrics字段:**
```python
{
    "behavior_count": int,      # 行为数量
    "new_patterns": int,        # 新模式数
    "quality_score": float,     # 质量分数 0-1
    "evolution_triggered": bool # 是否触发进化
}
```

### 批量处理

```python
async def batch_process(
    user_id: str,
    interactions: List[Dict]
) -> List[FlywheelMetrics]
```

## TasteStandard

### 建立品味画像

```python
async def establish_taste(
    user_id: str,
    feedback_history: List[Dict]
) -> TasteProfile
```

**参数:**
- `user_id` (str): 用户标识
- `feedback_history` (List[Dict]): 历史反馈数据

**反馈数据格式:**
```python
{
    "domain": str,              # 领域 (code_generation, writing等)
    "accepted": bool,           # 是否接受
    "content": str,             # 反馈内容
    "confidence": float         # 置信度
}
```

### 评估输出

```python
async def evaluate_output(
    output: Any,
    context: Dict,
    taste_profile: Optional[TasteProfile] = None,
    user_id: Optional[str] = None
) -> EvaluationResult
```

**参数:**
- `output` (Any): 待评估输出
- `context` (Dict): 上下文信息
- `taste_profile` (TasteProfile, optional): 品味画像
- `user_id` (str, optional): 如果profile未提供

**返回:**
- `EvaluationResult`: 评估结果

**EvaluationResult字段:**
```python
{
    "taste_score": float,        # 综合品味分数 0-1
    "dimension_scores": {        # 各维度分数
        "relevance": float,
        "style_match": float,
        "quality_perception": float
    },
    "suggestions": List[str],   # 改进建议
    "confidence": float         # 评估置信度
}
```

### 更新品味标准

```python
async def update_from_feedback(
    output: Any,
    user_feedback: Dict,
    context: Dict
) -> None
```

## MaxRDTLayer

### 任务增强

```python
async def enhance_task(
    task: Dict[str, Any],
    user_id: str
) -> EnhancedTaskContext
```

**参数:**
- `task` (Dict): 原始任务
- `user_id` (str): 用户标识

**返回:**
- `EnhancedTaskContext`: 增强后的上下文

**EnhancedTaskContext字段:**
```python
{
    "original_task": Dict,           # 原始任务
    "user_recipe": Dict,            # 用户配方
    "taste_standards": Dict,         # 品味标准
    "flywheel_state": Dict,          # 飞轮状态
    "enhancement_confidence": float  # 增强置信度
}
```

### 记录结果

```python
async def record_outcome(
    task: Dict,
    result: Any,
    user_feedback: Optional[Dict],
    user_id: str
) -> TaskOutcome
```

**参数:**
- `task` (Dict): 原始任务
- `result` (Any): 执行结果
- `user_feedback` (Dict, optional): 用户反馈
- `user_id` (str): 用户标识

**返回:**
- `TaskOutcome`: 任务执行结果记录

### 获取用户洞察

```python
def get_user_insights(
    user_id: str
) -> Dict
```

**返回:**
```python
{
    "user_id": str,
    "recipe_count": int,
    "recipes": [{
        "name": str,
        "confidence": float,
        "usage_count": int,
        "success_rate": float
    }],
    "taste_profile": {
        "domains": List[str],
        "cross_domain_consistency": float,
        "learning_confidence": str
    },
    "flywheel_state": Dict
}
```

## MaxRDTOrchestrator

### 初始化用户

```python
async def initialize_user(
    user_id: str
) -> Dict
```

### 处理任务

```python
async def process_task(
    user_id: str,
    task: Dict,
    interaction_history: List[Dict] = None,
    feedback_history: List[Dict] = None
) -> Dict
```

### 记录并学习

```python
async def record_and_learn(
    user_id: str,
    task: Dict,
    result: Any,
    feedback: Dict = None
) -> Dict
```

## 数据模型

### Recipe
```python
{
    "recipe_id": str,
    "user_id": str,
    "name": str,
    "description": str,
    "workflow": {
        "nodes": [...],
        "edges": [...]
    },
    "preferences": {
        "detail_level": str,
        "communication_style": str,
        "output_format": str,
        "priority_order": List[str]
    },
    "confidence": float,
    "trigger_conditions": [...],
    "usage_count": int,
    "success_rate": float
}
```

### TasteProfile
```python
{
    "user_id": str,
    "domains": {
        "code_generation": {
            "quality_standards": [
                {"dimension": str, "weight": float, "target": str}
            ],
            "style_preferences": {
                "naming_convention": str,
                "comment_style": str,
                "structure": str
            },
            "confidence": float
        }
    },
    "cross_domain_consistency": float,
    "learning_confidence": str
}
```

## 错误处理

所有异步方法可能抛出以下异常:

- `ValueError`: 参数无效
- `KeyError`: 用户不存在
- `RuntimeError`: 内部错误

建议使用try-catch处理:

```python
try:
    recipe = await engine.construct_recipe(...)
except ValueError as e:
    print(f"Invalid input: {e}")
except RuntimeError as e:
    print(f"Internal error: {e}")
```

---
name: max-rdt-user-workflow
description: 用户专属工作流认知系统。构建用户行为驱动的智能助手，包含Recipe工作流认知、Data Flywheel数据反哺、Taste Standard品味标准三大核心。当用户询问如何构建个性化AI系统、如何让AI学习用户偏好、如何建立用户专属工作流、如何实现数据飞轮循环、如何定义专业品味标准时使用。
---

# Max-RDT: 用户专属工作流认知系统

Max-RDT (Max-Recursive Deployment Theory) 是一种让AI通过持续学习用户行为构建专属认知模型的理论框架。

## 核心组件

| 模块 | 功能 | 核心能力 |
|------|------|---------|
| **Recipe** | 工作流认知 | 从用户行为中提取重复模式，生成个性化工作流模板 |
| **Data Flywheel** | 数据飞轮 | 用户行为数据反哺，形成正向循环优化 |
| **Taste Standard** | 品味标准 | 构建用户主观评价体系，让输出更符合审美 |

## 工作流程

```
用户输入 → 意图识别 → Recipe匹配 → 任务增强 → 执行
                              ↓
                        结果评估(Taste)
                              ↓
                        数据记录(Flywheel)
                              ↓
                        Recipe更新/进化
```

## 使用方法

### 1. Recipe构建
```python
from max_rdt import RecipeEngine
engine = RecipeEngine()
recipe = await engine.construct_recipe(user_id, interaction_history)
```

### 2. Data Flywheel运行
```python
from max_rdt import DataFlywheel
flywheel = DataFlywheel()
metrics = await flywheel.spin(user_id, interaction)
```

### 3. Taste Standard评估
```python
from max_rdt import TasteStandard
taste = TasteStandard()
result = await taste.evaluate_output(output, context, taste_profile)
```

## 集成Max-HCD

将Max-RDT作为Max-HCD的感知增强层，位于Hermes和DeerFlow之间。

```python
from max_rdt import MaxRDTLayer
rdt_layer = MaxRDTLayer(hcd_composite)
enhanced = await rdt_layer.enhance_task(task, user_id)
```

## 详细文档

- [架构设计](references/architecture.md)
- [实现路线图](references/roadmap.md)
- [API参考](references/api_reference.md)

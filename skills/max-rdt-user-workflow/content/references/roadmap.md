# Max-RDT 实现路线图

## Phase 1: Recipe 基础能力 (Week 1-2)

### 目标
建立工作流认知的核心框架，实现基本的模式提取和工作流构建。

### 任务清单

| 任务 | 描述 | 优先级 | 状态 |
|------|------|--------|------|
| T1.1 | 行为序列提取器 | P0 | ✅ 完成 |
| T1.2 | 模式识别算法 | P0 | ✅ 完成 |
| T1.3 | 工作流图构建器 | P0 | ✅ 完成 |
| T1.4 | 配方存储与检索 | P1 | ✅ 完成 |
| T1.5 | 偏好编码器 | P1 | ✅ 完成 |

### 交付物
```python
from max_rdt import RecipeEngine

engine = RecipeEngine()
recipe = await engine.construct_recipe(
    user_id="user_123",
    interaction_history=[
        {"input": "分析销售数据", "actions": ["分析问题", "分解任务"]},
        {"input": "设计数据库", "actions": ["设计", "实现"]}
    ]
)
```

---

## Phase 2: Data Flywheel (Week 2-4)

### 目标
构建用户行为数据反哺引擎，形成闭环优化。

### 任务清单

| 任务 | 描述 | 优先级 | 状态 |
|------|------|--------|------|
| T2.1 | 行为采集框架 | P0 | ✅ 完成 |
| T2.2 | 模式挖掘算法 | P0 | ✅ 完成 |
| T2.3 | 质量评估模型 | P1 | ✅ 完成 |
| T2.4 | 反馈闭环系统 | P1 | ✅ 完成 |
| T2.5 | 进化触发器 | P2 | 🔄 进行中 |

### 交付物
```python
from max_rdt import DataFlywheel

flywheel = DataFlywheel()
metrics = await flywheel.spin(
    user_id="user_123",
    interaction={
        "input": "帮我写一个排序算法",
        "output": "代码实现",
        "feedback": {"accepted": True, "rating": 5}
    }
)
print(f"Quality Score: {metrics.quality_score}")
```

---

## Phase 3: Taste Standard (Week 3-5)

### 目标
构建用户的主观评价体系，让输出更符合审美。

### 任务清单

| 任务 | 描述 | 优先级 | 状态 |
|------|------|--------|------|
| T3.1 | 领域分类器 | P0 | ✅ 完成 |
| T3.2 | 品味画像构建 | P0 | ✅ 完成 |
| T3.3 | 评估引擎 | P1 | ✅ 完成 |
| T3.4 | 风格匹配器 | P1 | ✅ 完成 |
| T3.5 | 标准校准器 | P2 | 🔄 进行中 |

### 交付物
```python
from max_rdt import TasteStandard

taste = TasteStandard()
profile = await taste.establish_taste(
    user_id="user_123",
    feedback_history=[
        {"domain": "code_generation", "accepted": True, "content": "代码清晰简洁"}
    ]
)

result = await taste.evaluate_output(
    output="def hello(): print('hi')",
    context={"domain": "code_generation"}
)
print(f"Taste Score: {result.taste_score}")
```

---

## Phase 4: 系统集成 (Week 5-6)

### 目标
将所有模块整合为统一的Max-RDT层，与Max-HCD系统集成。

### 任务清单

| 任务 | 描述 | 优先级 | 状态 |
|------|------|--------|------|
| T4.1 | MaxRDTLayer实现 | P0 | ✅ 完成 |
| T4.2 | 任务增强接口 | P0 | ✅ 完成 |
| T4.3 | 结果记录接口 | P1 | ✅ 完成 |
| T4.4 | 用户洞察API | P1 | 🔄 进行中 |

### 交付物
```python
from max_rdt import MaxRDTLayer

layer = MaxRDTLayer()

# 任务增强
enhanced = await layer.enhance_task(
    task={"text": "帮我分析销售数据"},
    user_id="user_123"
)

# 结果记录
outcome = await layer.record_outcome(
    task={"text": "帮我分析销售数据"},
    result="分析报告",
    user_feedback={"accepted": True},
    user_id="user_123"
)
```

---

## Phase 5: 优化与扩展 (Week 7-8)

### 任务清单

| 任务 | 描述 | 优先级 | 状态 |
|------|------|--------|------|
| T5.1 | 向量存储集成 | P1 | ⏳ 待开始 |
| T5.2 | 分布式支持 | P2 | ⏳ 待开始 |
| T5.3 | 实时学习 | P1 | ⏳ 待开始 |
| T5.4 | 自定义领域 | P2 | ⏳ 待开始 |

---

## 技术债务与优化项

### 当前限制
1. **存储**: 使用内存存储，重启后数据丢失
2. **模式识别**: 基于规则的简单实现，非ML
3. **规模**: 单用户设计，多用户需扩展

### 优化计划
- [ ] 添加持久化存储（SQLite/PostgreSQL）
- [ ] 集成向量数据库（用于Recipe相似度匹配）
- [ ] ML模型替代规则引擎
- [ ] 添加缓存层（Redis）
- [ ] 实现多租户隔离

---

## 测试计划

### 单元测试
```bash
python -m pytest tests/test_recipe_engine.py
python -m pytest tests/test_data_flywheel.py
python -m pytest tests/test_taste_engine.py
```

### 集成测试
```python
async def test_full_cycle():
    # 1. 构建Recipe
    recipe = await engine.construct_recipe(...)

    # 2. 运行Flywheel
    metrics = await flywheel.spin(...)

    # 3. 建立Taste
    profile = await taste.establish_taste(...)

    # 4. 验证集成
    enhanced = await layer.enhance_task(...)
    assert enhanced.enhancement_confidence > 0
```

---

## 里程碑

| 阶段 | 里程碑 | 日期 | 状态 |
|------|--------|------|------|
| Phase 1 | Recipe基础能力上线 | Week 2 | ✅ 完成 |
| Phase 2 | Data Flywheel上线 | Week 4 | 🔄 进行中 |
| Phase 3 | Taste Standard上线 | Week 5 | 🔄 进行中 |
| Phase 4 | 系统集成完成 | Week 6 | 🔄 进行中 |
| Phase 5 | 优化与扩展 | Week 8 | ⏳ 待开始 |

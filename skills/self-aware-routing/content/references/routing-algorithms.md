# Self-Aware Routing 参考文档

## 核心概念

### 什么是 LLM 路由？

LLM 路由（Routing）是指在多个大语言模型之间智能分配查询请求的系统。其核心目标是：
- 将简单查询路由到廉价模型
- 将复杂查询路由到高性能模型
- 在保证质量的前提下最大化成本效益

### 成本对比数据（2024）

| 模型 | 输入价格 ($/1M tokens) | 输出价格 ($/1M tokens) | 相对成本 |
|------|----------------------|----------------------|---------|
| GPT-4o | $5.00 | $15.00 | 基准 |
| GPT-3.5-turbo | $0.50 | $1.50 | 10% |
| Claude 3.5 Sonnet | $3.00 | $15.00 | 60% |
| Claude 3 Haiku | $0.25 | $1.25 | 5% |
| Gemini 1.5 Flash | $0.075 | $0.30 | 1.5% |
| Llama 3 8B | ~$0.20 (自托管) | ~$0.20 | 可忽略 |

### 典型节省效果

根据实际部署数据：
- **简单查询为主 (70%简单 + 30%复杂)**：节省 45-55%
- **混合查询 (50%简单 + 50%复杂)**：节省 30-40%
- **复杂查询为主 (30%简单 + 70%复杂)**：节省 15-25%

## 路由算法详解

### 1. 相似度加权方法

```
原理：利用嵌入向量计算查询与已知偏好的相似度

步骤：
1. 使用 OpenAI ada-002 或类似嵌入模型
2. 将查询转为 1536 维向量
3. 计算与训练集中 (查询, 模型偏好) 对的余弦相似度
4. 加权聚合多个相似度得分
5. 选择得分最高的模型

优点：无需训练新模型，可快速部署
缺点：依赖嵌入质量，泛化能力有限
```

### 2. 矩阵分解方法

```
原理：将人类偏好数据分解为潜在特征

步骤：
1. 构建用户-模型-查询三元组矩阵
2. 使用 SVD 或 ALS 分解
3. 学习每个模型在各维度的能力
4. 预测新查询最合适的模型

优点：可捕获复杂交互模式
缺点：需要大量训练数据
```

### 3. BERT/LLM 分类器

```
原理：训练分类器直接预测最优模型

架构：
- 输入层：query tokens
- 编码层：BERT/RoBERTa
- 输出层：softmax (每个模型一个类别)

训练数据：人类偏好对比数据集
评估指标：准确率、后悔值、成本节省率

优点：准确率高，可捕获语义差异
缺点：需要额外训练，部署复杂
```

### 4. 级联方法 (Cascade)

```
原理：逐步尝试从便宜到贵的模型

伪代码：
function cascade_route(query):
    models = [cheap, medium, expensive]
    for model in models:
        response = call(model, query)
        if quality_score(response) >= threshold:
            return response
    return response  # 最后一定返回
```

## RouteLLM 框架详解

### 架构

```
┌─────────────┐
│   Query     │
└──────┬──────┘
       │
       v
┌──────────────────┐
│  Router (多种策略) │
└──────┬───────────┘
       │
       ├────────────┬────────────┐
       v            v            v
   ┌───────┐   ┌───────┐   ┌───────┐
   │ Cheap │   │ Medium│   │Expensive│
   │ Model │   │ Model │   │  Model  │
   └───────┘   └───────┘   └─────────┘
```

### 部署方式

```bash
# 安装
pip install route-llm

# 快速启动
from route_llm import Router

router = Router(
    model_mapping={
        "strong": "gpt-4",
        "weak": "gpt-3.5-turbo"
    },
    router_type="similarity"  # or "bert-rank", "llm-judge"
)

response = router.chat(
    query="Explain quantum computing",
    budget_multiplier=0.5  # 成本容忍度
)
```

## FrugalGPT 策略

### 三层优化框架

1. **Prompt Adaptation（提示优化）**
   - 压缩提示长度
   - 减少示例数量
   - 使用更简洁的指令

2. **LLM Approximation（模型近似）**
   - 模型蒸馏
   - 量化压缩
   - 缓存复用

3. **LLM Cascade（模型级联）**
   - 智能回退策略
   - 早期终止
   - 成本感知的路由

### 成本节省公式

```
总成本 = Σ(cost_per_model × request_count)

节省率 = (基准成本 - 实际成本) / 基准成本

质量保证：路由后质量分数 ≥ (1 - ε) × 基准质量
```

## CARROT 算法

### Minimax 最优路由

核心思想：同时预测成本和准确率

```python
def carrot_route(query, models, budget):
    costs = []
    accuracies = []

    for model in models:
        cost = predict_cost(query, model)
        acc = predict_accuracy(query, model)
        costs.append(cost)
        accuracies.append(acc)

    # 最小化最大后悔值
    best_idx = argmin(max(accuracies - accuracies[best]))

    return models[best_idx]
```

### SPROUT 数据集

用于训练和评估路由模型的标准数据集：
- 覆盖多种查询类型
- 包含最新 SOTA 模型评估
- 公开可用

## 最佳实践

### 1. 查询分类

```python
def classify_query_complexity(query: str) -> str:
    """简单 heuristic 分类器"""

    # 复杂度指标
    length = len(query.split())
    has_technical_terms = any(t in query for t in technical_keywords)
    is_multi_turn = "?" in query and length > 50

    if length < 15 and not has_technical_terms:
        return "simple"  # → cheap model
    elif length > 100 or is_multi_turn:
        return "complex"  # → expensive model
    else:
        return "moderate"
```

### 2. 缓存策略

```
缓存键：hash(query + model + temperature)
TTL：根据查询类型设置不同过期时间
  - 简单问答：24小时
  - 复杂推理：1小时
  - 实时对话：不缓存
```

### 3. 质量监控

```python
# 自动回退机制
def monitor_quality(response, query):
    score = evaluate_response(response, query)

    if score < QUALITY_THRESHOLD:
        # 重新路由到更高级模型
        reroute(query, tier="high")
        log_incident(query, "low_quality")
```

### 4. A/B 测试框架

```yaml
# 路由实验配置
experiment:
  name: "routing_strategy_comparison"
  variants:
    - name: "random"
      weight: 0.2
    - name: "similarity"
      weight: 0.4
    - name: "cascade"
      weight: 0.4
  metrics:
    - cost_per_request
    - quality_score
    - user_satisfaction
```

## 常见问题

### Q: 如何确定路由阈值？

A: 建议通过实验确定：
1. 从宽松阈值开始（80% 质量保留）
2. 逐步收紧，观察投诉率
3. 找到成本与质量的平衡点

### Q: 哪些查询不适合路由？

A: 以下场景建议直接使用高级模型：
- 首次交互的关键任务
- 包含敏感信息的查询
- 需要高一致性的场景
- 用户明确要求高质量

### Q: 如何处理路由失败？

A: 实现降级策略：
1. 记录失败日志
2. 自动回退到默认高级模型
3. 触发告警
4. 人工审查模式选择

### Q: 多语言支持如何处理？

A:
- 非英语查询优先考虑多语言能力强的模型
- 小语种查询建议使用专用模型
- 检测语言并选择对应优化模型

## 资源链接

- RouteLLM GitHub: https://github.com/lm-sys/RouteLLM
- FrugalGPT Paper: https://arxiv.org/abs/2305.07176
- CARROT Paper: https://arxiv.org/abs/2402.03261
- LM-SYS Arena: https://lmarena.ai
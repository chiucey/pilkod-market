# 负样本生成策略

## 负样本的重要性

在NLP模型训练中，告诉机器人"什么不是"比"什么才是"更重要。负样本帮助模型：
- 区分相似但不同的意图
- 识别边界模糊的情况
- 过滤噪音和无意义输入
- 提升整体识别准确率

## 负样本类型分类

### 类型一：意图混淆负样本

**定义**：同一业务域内的其他意图，容易与目标意图混淆

**示例**（目标意图：提前还款）：
| 负样本 | 混淆原因 | 正确意图 |
|-------|---------|---------|
| 还款计算器在哪 | 查询类混淆操作类 | 查询还款计算器 |
| 我要延期还款 | 展期与还款混淆 | 延期还款 |
| 怎么调整还款日期 | 日期调整与还款混淆 | 修改还款日期 |

### 类型二：跨域混淆负样本

**定义**：其他业务域的相似表达，与目标意图无直接关联

**示例**（目标意图：贷款还款）：
| 负样本 | 混淆原因 | 正确意图 |
|-------|---------|---------|
| 我想申请贷款 | 贷款咨询vs还款 | 贷款申请 |
| 怎么提升额度 | 额度管理vs还款 | 额度提升 |
| 贷款产品有哪些 | 产品咨询vs还款 | 产品查询 |

### 类型三：部分特征负样本

**定义**：只包含部分关键词，但意图完全不同

**示例**（目标意图：提前还款）：
| 负样本 | 特征词 | 问题 |
|-------|-------|------|
| 提前还款利息太高了 | 提前、还款 | 只有抱怨，无操作意图 |
| 不想提前还款 | 提前、还款 | 表达否定态度 |
| 问下提前还款的事 | 提前、还款 | 只是询问，非实际操作 |

### 类型四：噪音负样本

**定义**：无意义输入、测试语句、错误格式

**示例**：
| 噪音类型 | 示例 |
|---------|------|
| 乱码输入 | asdfgh、？？？、!!! |
| 无意义语句 | 还款还款还款 |
| 测试语句 | test、测试、123456 |
| 非自然语言 | @#$%、。？！ |

### 类型五：边界模糊负样本

**定义**：涉及多个意图的边界情况

**示例**（目标意图：提前还款）：
| 边界样本 | 边界原因 | 建议处理 |
|---------|---------|---------|
| 提前还款违约金怎么算 | 涉及还款和费用计算 | 标注双意图 |
| 提前还款和延期还款哪个好 | 比较类问题 | 单独意图 |
| 还了一期想提前还款 | 部分还款后提前还 | 明确前置条件 |

## 负样本生成规则

### 规则一：数量要求

每个意图至少生成5-10条负样本：
- 意图混淆：2-3条
- 跨域混淆：1-2条
- 部分特征：1-2条
- 噪音样本：1-2条
- 边界模糊：1-2条

### 规则二：质量要求

1. **自然性**：负样本应看起来像真实用户输入
2. **相关性**：负样本应与目标意图有一定关联性
3. **区分性**：负样本应能被明显区分不是目标意图
4. **多样性**：覆盖不同类型的混淆情况

### 规则三：标注要求

每个负样本应标注：
```json
{
  "text": "负样本文本",
  "is_negative": true,
  "negative_type": "意图混淆|跨域混淆|部分特征|噪音|边界",
  "reason": "为什么不是目标意图",
  "should_match_intent": "正确匹配的意图（如适用）",
  "is_boundary": false,
  "boundary_reason": null
}
```

## 边界样本特殊标注

边界样本需要额外标注：

```json
{
  "text": "提前还款违约金怎么算",
  "is_negative": true,
  "negative_type": "边界模糊",
  "reason": "涉及还款和费用计算两个意图",
  "is_boundary": true,
  "boundary_reason": "双意图样本，需要联合预测",
  "primary_intent": "提前还款",
  "secondary_intent": "费用计算",
  "training_notes": "建议同时训练两个意图的联合识别"
}
```

## 自动化生成逻辑

```python
def generate_negative_samples(target_intent, count=10):
    negatives = []

    # 意图混淆
    similar_intents = get_similar_intents(target_intent)
    for intent in similar_intents[:3]:
        negatives.append(generate_confusion_sample(intent))

    # 跨域混淆
    cross_domain_intents = get_cross_domain_intents(target_intent)
    for intent in cross_domain_intents[:2]:
        negatives.append(generate_cross_domain_sample(intent))

    # 部分特征
    keywords = extract_keywords(target_intent)
    for _ in range(2):
        negatives.append(generate_partial_feature_sample(keywords))

    # 噪音样本
    for _ in range(2):
        negatives.append(generate_noise_sample())

    # 边界样本
    boundary_intents = get_boundary_intents(target_intent)
    for intent in boundary_intents[:1]:
        negatives.append(generate_boundary_sample(intent, target_intent))

    return negatives[:count]
```

## 负样本使用建议

### 训练比例
- 正样本：负样本 ≈ 1:0.3 ~ 1:0.5
- 避免负样本过多导致模型过于保守
- 根据实际误识别情况调整比例

### 训练策略
1. **分阶段训练**：先训练正样本，再加入负样本
2. **难例挖掘**：重点关注容易混淆的负样本
3. **在线学习**：根据实际误识别补充负样本

### 效果评估
- 监控负样本的召回率
- 检查是否有新发现的混淆情况
- 定期更新负样本库
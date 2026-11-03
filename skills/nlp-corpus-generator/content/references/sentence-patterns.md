# 句式变换规则

## 句式类型分类

### 1. 肯定句

**定义**：直接陈述某种事实或表达某种需求

**变换规则**：
- 主语 + 谓语 + 宾语（标准结构）
- 添加程度副词（一定、必须、肯定）
- 添加时间状语（现在、马上、立刻）

**示例**：
| 原始 | 变体1 | 变体2 | 变体3 |
|------|-------|-------|-------|
| 我要提前还款 | 我必须提前还款 | 我现在要提前还款 | 我想提前还款 |

### 2. 否定句

**定义**：表达否定意义的句子

**变换规则**：
- 添加否定词（不、没、未、非、别）
- 双重否定表肯定
- 疑问否定（能不能/会不会）

**示例**：
| 原始 | 变体1 | 变体2 | 变体3 |
|------|-------|-------|-------|
| 提前还款 | 能不能不提前还款 | 不提前还款可以吗 | 还没到还款日 |

### 3. 疑问句

**定义**：提出问题的句子

**变换规则**：
- 使用疑问词（怎么、如何、什么、多少、为什么）
- 使用疑问语气助词（吗、呢、吧）
- 使用疑问格式（能不能、可不可以）

**示例**：
| 原始 | 变体1 | 变体2 | 变体3 |
|------|-------|-------|-------|
| 提前还款 | 怎么提前还款 | 提前还款怎么操作 | 提前还款可以吗 |

### 4. 祈使句

**定义**：表达请求、命令、建议的句子

**变换规则**：
- 使用祈使语气（请、帮我、麻烦）
- 省略主语
- 添加礼貌用语

**示例**：
| 原始 | 变体1 | 变体2 | 变体3 |
|------|-------|-------|-------|
| 提前还款 | 请帮我提前还款 | 麻烦办理提前还款 | 帮我处理一下提前还款 |

### 5. 陈述句

**定义**：陈述事实或计划的句子

**变换规则**：
- 添加计划性词语（打算、准备、计划）
- 添加时间条件（以后、等、到了）
- 添加原因说明

**示例**：
| 原始 | 变体1 | 变体2 | 变体3 |
|------|-------|-------|-------|
| 提前还款 | 我打算提前还款 | 准备提前还款了 | 等资金到位就提前还款 |

## 句式变换矩阵

```
输入: [核心意图] + [实体]
输出: [句式前缀] + [核心意图] + [句式后缀]
```

### 句式前缀库

| 句式类型 | 前缀示例 |
|---------|---------|
| 肯定句 | 我要、我想、我要、我想 |
| 否定句 | 能不能、不想、不是、不想 |
| 疑问句 | 怎么、如何、能不能、可不可以 |
| 祈使句 | 请帮我、麻烦、帮我、麻烦 |
| 陈述句 | 我打算、准备、计划、预计 |

### 句式后缀库

| 句式类型 | 后缀示例 |
|---------|---------|
| 肯定句 | - | - | 呢 |
| 否定句 | 吗、可以吗、行不行 | 吗 |
| 疑问句 | 呢、吧、吗、怎么操作 | 呢 |
| 祈使句 | - | - | 一下 |
| 陈述句 | 了、的、的、的 | 了 |

## 组合变换示例

### 输入
```
核心意图: 提前还款
实体: 车贷
```

### 输出
| 句式 | 变换结果 |
|------|---------|
| 肯定句 | 我要提前还车贷、我想提前还款 |
| 否定句 | 不提前还款行不行、能不能不提前还 |
| 疑问句 | 怎么提前还款、车贷提前还款怎么操作 |
| 祈使句 | 请帮我办理提前还款、帮我提前还车贷 |
| 陈述句 | 我打算提前还款、准备把车贷提前还了 |

## 自动化变换脚本逻辑

```python
def generate_sentence_variants(intent, entities, count_per_type=3):
    variants = []

    # 肯定句变换
    for _ in range(count_per_type):
        prefix = random.choice(affirmative_prefixes)
        variants.append(f"{prefix}{intent}")

    # 否定句变换
    for _ in range(count_per_type):
        neg_prefix = random.choice(negative_prefixes)
        variants.append(f"{neg_prefix}{intent}")

    # 疑问句变换
    for _ in range(count_per_type):
        que_prefix = random.choice(question_prefixes)
        suffix = random.choice(question_suffixes)
        variants.append(f"{que_prefix}{intent}{suffix}")

    # 祈使句变换
    for _ in range(count_per_type):
        imp_prefix = random.choice(imperative_prefixes)
        suffix = random.choice(imperative_suffixes)
        variants.append(f"{imp_prefix}{intent}{suffix}")

    # 陈述句变换
    for _ in range(count_per_type):
        stat_prefix = random.choice(statement_prefixes)
        suffix = random.choice(statement_suffixes)
        variants.append(f"{stat_prefix}{intent}{suffix}")

    return variants
```
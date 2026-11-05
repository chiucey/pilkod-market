---
name: llm-agent-jpaf-personality-mbti
description: 你有没有想过：为什么 龙虾、豆包、gemini 这些 AI 说话总是千篇一律？不管你问多少次，它们都是用同一种方式回答你？JPAF 就是解决这个问题的 —— 让 AI 也能有"性格"。触发场景：Agent人格建模、MBTI人格控制、人格演化，游戏NPC设计。开发者-给你的AI产品和Skills加入性格系统！游戏玩家-创造独一无二的游戏角色。创作者-打造有性格的内容团队。职场人-私人定制的工作AI助手。玩家-和不同性格的AI聊天、玩角色扮演。研究者-研究AI人格演化、心理学实验。JPAF就是给你的AI加一个"性格芯片"，让AI不再是千篇一律的回复机器，而是可以根据你的需求，变成理性分析型、热情活泼型、温柔倾听型等各种性格的虚拟角色！一句话总结：JPAF = 给 AI 装上一个会成长的"性格系统"，让 AI 不再是冷冰冰的机器，而是有血有肉、有性格会变化的虚拟角色。LLM Agent人格建模工具。
---

# JPAF - 荣格人格适应框架 (Jungian Personality Adaptation Framework)

## 核心概述

JPAF是一个基于荣格八种认知功能理论的LLM人格建模框架，通过权重分配实现人格的细粒度表达，支持动态人格演化。

## 核心机制（三重自适应机制）

### 1. 主导-辅助协调 (Dominant-Auxiliary Coordination)
- 保持核心人格一致性
- 主导功能权重范围：0.31-1.00
- 辅助功能权重范围：0.06-0.30
- 权重交换阈值检测

### 2. 强化-补偿机制 (Reinforcement-Compensation)
- 短期情境适应
- 每次使用功能增加0.06权重
- 当主导功能权重>=0.5时触发归一化
- 支持补偿性功能激活

### 3. 反思机制 (Reflection Mechanism)
- 驱动长期人格演化
- reflection1(): 主导-辅助互换检测
- reflection2(): 仅主导功能变化
- reflection3(): 仅辅助功能变化
- reflection4(): 主辅功能同时变化

## 八种认知功能映射

| 功能 | 类型 | 描述 |
|------|------|------|
| Ti | 内向思考 | 内部逻辑分析，理论体系构建 |
| Te | 外向思考 | 外部组织优化，效率驱动决策 |
| Fi | 内向情感 | 个人价值体系维护，道德情感判断 |
| Fe | 外向情感 | 群体情感协调，社会规范适应 |
| Ni | 内向直觉 | 深度模式洞察，未来趋势预见 |
| Ne | 外向直觉 | 多种可能性探索，创意想法生成 |
| Si | 内向感觉 | 具体记忆回忆，细节事实专注 |
| Se | 外向感觉 | 即时感官体验，实时动作响应 |

## MBTI权重配置

每种MBTI类型有独特的八维权重配置，总和为1.0：

```
INTP: Ti=0.47, Ne=0.23, Si=0.05, Fe=0.05, Te=0.05, Ni=0.05, Se=0.05, Fi=0.05
INTJ: Ni=0.48, Te=0.22, ...
ENFP: Ne=0.41, Fi=0.29, ...
(详见 references/mbti_weights.md)
```

## 工作流程

### 流程1：人格初始化
```
1. 选择目标MBTI类型 (如INTJ)
2. 加载对应权重配置
3. 设置主导功能(main)和辅助功能(aux)
4. 初始化change_history全为零
```

### 流程2：场景问答处理
```
1. 输入场景(scene) + 问题(problem)
2. 获取系统提示词(sys_prompt)
3. 调用LLM获取响应
4. 提取使用的认知功能
5. 更新change_history
6. 执行status_check检测权重变化
```

### 流程3：权重状态检测 (status_check)
```
IF 使用的功能 == 辅助功能:
    IF 辅助临时权重 >= 主导基础权重:
        触发 reflection1() → 主导-辅助互换

ELIF 使用的功能 == 主导功能:
    IF 主导临时权重 >= 0.5:
        触发 norm_weight() 归一化

ELIF 使用的功能 in [主导,辅助]:
    IF 临时权重 >= 基础权重:
        根据功能关系触发 reflection2/3/4()
```

### 流程4：归一化处理 (norm_weight)
```
1. 计算所有功能总权重(含change_history)
2. 重新分配权重比例
3. 重置change_history为零
4. 清空history记录
```

## 使用场景

### 场景A：游戏NPC人格设计
```python
# 为策略游戏NPC设置INTJ人格
agent = Agent("INTJ")
agent.weight = WEIGHT["INTJ"]
agent.model = "OPENAI"

# NPC在特定场景下人格演化
rsp, change_log = agent.get_one_problem(
    scene="面对敌军包围，你需要制定突围计划",
    problem="你将优先考虑什么因素？"
)
```

### 场景B：个性化AI助手
```python
# 创建ENFJ类型的情感支持助手
agent = Agent("ENFJ")
# 长期对话中人格可能演化
```

### 场景C：多智能体差异化
```python
agents = {
    "分析师": Agent("INTP"),  # Ti主导，逻辑严谨
    "推销员": Agent("ESFP"),  # Se主导，活力四射
    "策划师": Agent("ENFP"),  # Ne主导，创意无限
}
```

## Prompt工程要点

### 心理类型描述
```
主导功能: {main_func}, 高度分化, 高权重
辅助功能: {aux_func}, 一般分化, 中等权重
未分化功能池: {miss_func}, 潜意识状态, 极低权重
```

### 补偿机制提示词
```
当主导和辅助功能无法有效应对当前情况时，
从不分化功能池中选择最合适的功能进行补偿。
```

## 演化边界条件

| 条件 | 动作 |
|------|------|
| 辅助功能权重 > 主导基础权重 | 检测是否互换 |
| 主导功能权重 > 0.5 | 归一化处理 |
| 对立功能频繁使用 | 检测人格重组 |
| 其他功能达到主导阈值 | 检测功能升级 |

## 验证实验

框架支持通过MBTI测试验证人格一致性：
- 93题完整测试集
- 70题精简测试集
- 支持GPT/Qwen/Llama多模型对比

## 注意事项

1. 权重必须在[0,1]范围内
2. 归一化后change_history必须清零
3. reflection触发后会执行norm_weight2()
4. MBTI变化需同步更新function_to_mbti映射

## 相关文件

- `references/mbti_weights.md` - 16种MBTI完整权重配置
- `references/jungian_functions.md` - 荣格八功能详细说明
- `scripts/validate_weights.py` - 权重验证脚本

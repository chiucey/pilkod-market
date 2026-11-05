---
name: auto-research
description: 自动多轮研究迭代技能。改编自 Karpathy AutoResearch（karpathy/autoresearch）的"循环验证"框架：定义目标→执行→评分→保留/丢弃→深化→重复。对复杂课题进行多轮渐进式研究，每轮输出研究进展快照，最终输出有来源、有置信度标注的研究报告。触发：用户说"研究一下"、"深度分析"、"做个调研"、"研究迭代"、"auto research"。
---

# AutoResearch Skill

改编自 [karpathy/autoresearch](https://github.com/karpathy/autoresearch)，核心思想：**不给结论，给迭代过程**。

## 核心概念

AutoResearch 的本质是"循环自我改进"：

```
假设 → 验证 → 评分 → 保留/丢弃 → 深化 → …
```

对应到研究场景：
- `train.py`（可编辑文件）→ 搜索策略和发现积累
- `program.md`（代理指令）→ 本 skill 的 agent prompt template
- `val_bpb`（评估指标）→ 研究置信度分数
- `results.tsv`（实验日志）→ 核心发现记录

## 快速开始

用户给出课题后：

```
研究课题：XXXXXXXX
轮次：4（可选）
重点：（可选）
```

直接启动，默认4轮迭代。

## 迭代流程

### 1. 读取参考文档

加载以下文件了解完整协议：
- `references/research_protocol.md` — 评分标准与保留规则
- `references/agent_prompt_template.md` — 每轮给代理的指令模板

### 2. 执行每轮迭代

每轮用 `batch_web_search` 搜索 3-5 个不同角度 query → 用 `extract_content_from_websites` 补充重点页面 → 按标准评分 → 更新研究状态

### 3. 每轮输出进展快照

格式见 `references/agent_prompt_template.md` 的输出格式节。

### 4. 全部轮次完成后输出最终报告

结构：
1. 核心结论（≤3条）
2. 关键发现（按重要性+置信度排序，附来源）
3. 争议与不确定性
4. 建议深化方向
5. 研究局限性说明

## 评分与保留规则

| 分数区间 | 动作 |
|---------|------|
| 综合分 ≥ 6 且相关性 ≥ 0.6 | 标记"核心发现"，积累 |
| 4 ≤ 综合分 < 6 | 标记"待验证"，保留 |
| 综合分 < 4 | 直接丢弃 |

每轮最多保留 **5个核心发现**。

## 质量标准

- **有来源**：每条核心发现必须附来源 URL
- **有置信度**：用⭐标注（1-5个）
- **有争议标注**：矛盾数据单独标注
- **有边界**：明确研究局限性

## 禁止事项

- 不在单轮内给最终结论，多轮迭代是核心价值
- 不保留未经评分的信息
- 不忽略矛盾数据，矛盾是洞察的入口
- 不安装依赖、不修改外部系统

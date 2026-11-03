---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7
    PropagateID: b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7
    ReservedCode1: 30450220712f58e532066532ba823ecca175bc20b7cfa2d968189fdb98dc8f2bd2bc9b55022100f2e0b88490d8ae18e6dbff9288ceb424ca61b13cf84eae56d12941a3d19a4982
    ReservedCode2: 304502201a341a1899871c909b4c6738f70e7cc0ef890b57414e85e8bf2c740d668b2f40022100950d259dc783092e6b1029cde19d9e8a35feb205349a16b8c3338b27878549fb
---

# 大模型算法工程师面试准备示例

## 大模型第一面：基础理论

### 面试题示例（30题）

| 题号 | 模块 | 题目 | 考察点 |
|------|------|------|--------|
| 001 | Transformer | Transformer 的整体架构？ | 架构 |
| 002 | Transformer | Self-Attention 的计算过程？QKV 是什么？ | 注意力 |
| 003 | Transformer | Multi-Head Attention 的作用？ | 多头 |
| 004 | Transformer | 为什么要用 Scaled Dot-Product Attention？ | 归一化 |
| 005 | Transformer | Positional Encoding 为什么用正弦余弦？ | 位置编码 |
| 006 | Transformer | Layer Normalization vs Batch Normalization？ | 归一化 |
| 007 | Transformer | Feed Forward 层的作用？激活函数？ | 前馈网络 |
| 008 | Transformer | Transformer 的残差连接？为什么要残差？ | 梯度 |
| 009 | GPT | GPT 系列的发展？GPT-1/2/3/4 的区别？ | GPT |
| 010 | GPT | GPT 的预训练任务？Next Token Prediction？ | 预训练 |
| 011 | GPT | Causal Mask 的作用？ | 自回归 |
| 012 | BERT | BERT 的架构？和 GPT 的区别？ | 架构 |
| 013 | BERT | BERT 的预训练任务？MLM 和 NSP？ | 预训练 |
| 014 | BERT | BERT 的输入表示？Token、Segment、Position？ | 输入 |
| 015 | LLM | 大模型参数规模？10B、100B、1T 参数什么概念？ | 规模 |
| 016 | LLM | 涌现能力（Emergent Abilities）是什么？ | 能力 |
| 017 | LLM | 模型的 Scaling Law？ | 缩放 |
| 018 | LLM | GPT-4 的主要技术改进？ | 模型 |
| 019 | LLM | MoE（Mixture of Experts）架构？ | 架构 |
| 020 | LLM | Flash Attention 的原理？ | 加速 |
| 021 | RLHF | 什么是 RLHF？为什么需要？ | 对齐 |
| 022 | RLHF | PPO 算法的核心步骤？ | 强化学习 |
| 023 | RLHF | Reward Model 如何训练？ | 奖励模型 |
| 024 | Prompt | Zero-shot、Few-shot、CoT 的区别？ | Prompt |
| 025 | Prompt | 如何设计有效的 Prompt？ | 工程 |
| 026 | RAG | RAG 的架构？检索和生成的结合？ | 检索增强 |
| 027 | RAG | 向量数据库的原理？ANN 算法？ | 检索 |
| 028 | Fine-tuning | LoRA 的原理？为什么高效？ | 微调 |
| 029 | Fine-tuning | Prefix Tuning 和 Adapter 的区别？ | 微调 |
| 030 | Fine-tuning | 全参数微调和 LoRA 的对比？ | 微调 |

---

## 大模型第二面：系统设计与工程

### 设计题示例

**题目：设计一个企业级 RAG 系统**

考察维度：
1. 文档处理（切分、embedding）
2. 向量检索优化（召回率、延迟）
3. Rerank 与精排
4. 多模态文档处理（PDF、表格）
5. 幻觉问题的缓解方案

---

## 大模型强化训练示例

### 强化训练 001：Transformer 深入理解

**目标**：从 ⚠️ 模糊 → 💪 熟练

**训练题**：
1. 推导 Self-Attention 的时间和空间复杂度？
2. 为什么 Attention 可以捕获长距离依赖？
3. Transformer 的位置编码有什么问题？如何改进？
4. Flash Attention 的核心思想是什么？
5. 如何用 CUDA 实现一个简化的 Attention？

---

## 大模型晋级评估标准

| 模块 | 精通要求 | 熟练要求 |
|------|---------|---------|
| Transformer | 源码、CUDA实现 | 架构原理 |
| 预训练 | 分布式训练 | 数据处理 |
| 对齐 | RLHF原理 | SFT/Lora |
| 应用 | RAG/Agent | Prompt工程 |
| 工程 | 推理优化 | vLLM/TGI |

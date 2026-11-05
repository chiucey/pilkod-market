# Research Map
更新时间：2026-03-26

## 1. Hindsight

**论文：**
- Hindsight is 20/20: Building Agent Memory that Retains, Recalls, and Reflects
- arXiv:2512.12818
- 提交日期：2025-12-14

**为什么重要：**
- 把 agent memory 从"外挂检索片段"提升为"推理底座"
- 明确区分 world facts、agent experiences、entity summaries、beliefs
- 给出 `retain / recall / reflect` 三个核心操作
- 在 LongMemEval 和 LoCoMo 这类长程记忆 benchmark 上给出大幅提升

**对 OpenClaw 的直接启发：**
- `memory/YYYY-MM-DD.md` 不是最终形态，只是 retain 输入
- `bank/world.md`、`bank/experience.md`、`bank/opinions.md`、`bank/entities/*.md` 更接近可持续结构
- 反思层不是可选装饰，而是解决冲突、偏好演化、关系总结的关键层

## 2. Mem0

**论文：**
- Mem0: Building Production-Ready AI Agents with Scalable Long-Term Memory
- arXiv:2504.19413
- 提交日期：2025-04-28

**为什么重要：**
- 聚焦生产环境，不只是论文概念
- 强调动态提取、巩固、召回 salient information
- 提出 graph-based memory variant
- 在 LoCoMo 上对现有 memory baselines、RAG、full-context 做系统比较
- 论文报告更低延迟和更低 token 成本

**对 OpenClaw 的直接启发：**
- 不能只靠把更多历史塞回 prompt
- 要做 selective memory extraction
- 实体关系一旦变复杂，应把 entity link / graph-ish structure 作为增强项

## 3. SuCo / Subspace Collision

**论文：**
- Subspace Collision: An Efficient and Accurate Framework for High-dimensional Approximate Nearest Neighbor Search
- arXiv:2411.14754
- SIGMOD 2025

**为什么重要：**
- 它不是"记忆架构"论文，而是"高维 ANN 检索"论文
- 对大规模语义检索后端有价值

**对 OpenClaw 的直接启发：**
- 官方研究文档已经明确说：不要一开始就上 SuCo
- 小规模工作区先用 SQLite FTS 或小型 embedding 检索即可
- 只有在 chunk 规模大、暴力搜索开始拖慢时，才考虑 HNSW / SuCo 级方案

## 4. 研究结论如何落地到 OpenClaw

**优先级顺序：**
1. 先解决 durable write
2. 再补 `Retain` 结构
3. 再补 typed bank / entity pages
4. 再补 reflection
5. 最后再补 heavy retrieval backend

**不要倒过来：**
- 先上向量库，写入协议却还是混乱
- 先做复杂 graph，长期记忆却没有分层
- 先堆 embedding provider，`MEMORY.md` 却已经臃肿到失效

## 5. 适合直接借鉴的研究要点

- 事实和推断分开存
- 给意见/偏好保留 confidence 和 evidence
- 实体化组织比平铺长文更可维护
- 反思是必要的 consolidation 操作
- 检索返回必须带 source citation

## Sources

- Hindsight: https://arxiv.org/abs/2512.12818
- Mem0: https://arxiv.org/abs/2504.19413
- SuCo: https://arxiv.org/abs/2411.14754
- OpenClaw research note: https://docs.openclaw.ai/experiments/research/memory

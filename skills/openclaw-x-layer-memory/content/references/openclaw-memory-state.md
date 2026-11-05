# OpenClaw Memory State (2026-03-26)

## 1. Official Stable State

截至 2026-03-26，OpenClaw 官方文档定义默认记忆为"两层 Markdown 源事实 + 检索插件"：

- `memory/YYYY-MM-DD.md`
  - 每日日志，追加式
  - 会话开始时读取今天和昨天
- `MEMORY.md`
  - 精选长期记忆
  - 主私有会话才会加载

**官方提供工具：**
- `memory_search`
- `memory_get`

**官方支持特性：**
- 小型向量索引
- Hybrid Search（BM25 + vector）
- 多种 embedding provider
- 可选 QMD sidecar backend
- MMR diversity re-ranking
- Temporal decay
- Compaction 前的 `memoryFlush`

**结论：**
- OpenClaw 的"稳定产品层"还不是原生三层
- 但已具备把三层或多层记忆跑起来的必要基础设施

## 2. Official Research Direction

OpenClaw 的 `Workspace Memory Research` 已明确提出 Memory v2 方向：

- 保持 Markdown 为 canonical store
- 增加 `bank/` 作为 reviewable typed memory pages
- 增加 `.memory/index.sqlite` 作为 derived store
- 采用 `Retain / Recall / Reflect` 框架
- 支持实体、时间、意见置信度、证据链

**建议布局：**
```
memory.md
memory/YYYY-MM-DD.md
bank/world.md
bank/experience.md
bank/opinions.md
bank/entities/*.md
.memory/index.sqlite
```

**结论：**
- 官方研究方向已超出"简单三层"
- 准确地说，OpenClaw 正在向"2 层事实源 + 1 层 typed bank + 1 层 derived index + 1 层 reflection loop"演进

## 3. Community Best Practices

OpenClaw 官方博客（2026-02-25）最佳实践三层：

1. **MEMORY.md**
   - 永久偏好、长期规律、硬约束
   - 建议控制在 3000 tokens 以内

2. **memory/YYYY-MM-DD.md**
   - 当日事件、决定、待办、时间敏感上下文

3. **实体文件层**
   - 人、项目、公司等长期对象
   - 用 `summary.md + items.json` 或等价结构

**博客建议：**
- 用 heartbeat/cron 自动提取 durable facts
- 纠正模型时立即回写 `MEMORY.md`
- 每晚产出当天 memory summary

## 4. Design Principles

- 源事实永远写 Markdown，不把向量库当真相
- 先解决写入协议，再解决搜索协议
- 先解决核心记忆过载，再解决 ANN 性能
- 能用简单结构解决的问题，不先上重型图谱或复杂数据库

## 5. Sources

- OpenClaw docs, Memory: https://docs.openclaw.ai/concepts/memory
- OpenClaw docs, Workspace Memory Research: https://docs.openclaw.ai/experiments/research/memory
- OpenClaw blog, permanent memory guide, 2026-02-25: https://www.getopenclaw.ai/en/blog/openclaw-permanent-memory

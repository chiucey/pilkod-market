# Troubleshooting Playbook

## 症状：这次说过，下次又忘了

**常见原因：**
- 只在聊天里说了，没有写入磁盘
- 写进了日记层，但没有进入核心层或实体层

**修法：**
- 先确认 `MEMORY.md` / `memory/YYYY-MM-DD.md` 是否真的更新
- 对稳定偏好写入 `MEMORY.md`
- 对实体相关长期信息写入 `bank/entities/*.md`

---

## 症状：MEMORY.md 越来越长，但效果越来越差

**常见原因：**
- 核心层混入了短期事项、原始聊天、重复事实

**修法：**
- 删除已过期、重复、被覆盖内容
- 只保留高稳定、高复用、高约束信息
- 把时间敏感内容退回日记层

---

## 症状：知道零碎事实，但说不清人和项目之间的关系

**常见原因：**
- 只有平铺日志，没有实体层

**修法：**
- 建 `bank/entities/`
- 让每个关键实体保留 current state、recent changes、evidence pointers

---

## 症状：能搜到相近内容，但经常返回旧信息或重复信息

**常见原因：**
- 检索只有基础向量召回，没有 hybrid/MMR/temporal decay

**修法：**
- 优先启用 hybrid search
- 再加 MMR 降重复
- 对时间敏感任务加 temporal decay

---

## 症状：事实互相冲突

**常见原因：**
- 没有 reflection/consolidation
- 新事实写进去了，旧事实没被标记 superseded

**修法：**
- 增加 `bank/reflections.md`
- 每次 consolidation 都显式处理冲突项
- 让"最新有效事实"赢，但保留证据链

---

## 症状：索引很好，但人工审查时看不懂真实来源

**常见原因：**
- 把向量层当成事实源

**修法：**
- 所有 recall 结果都必须能指回 Markdown 文件和位置
- 保持"Markdown 是源事实，索引可重建"

---

## 症状：记忆写入时好时坏

**常见原因：**
- 工作区不可写
- 自动 flush / compaction 触发了，但写入条件不满足
- 代理根本没被提醒要写 memory

**修法：**
- 检查 workspace 是否可写
- 检查 OpenClaw memory flush 与 compaction 配置
- 在 `AGENTS.md` 或 `MEMORY.md` 中明确加入 memory protocol

---

## Practical Checklist

1. 先跑 `scripts/audit_openclaw_memory.js`
2. 如果缺层，跑 `scripts/init_x_layer_memory.js`
3. 再根据审计结论手工迁移高价值内容
4. 最后再决定是否增加 QMD、ANN 或更复杂的检索后端

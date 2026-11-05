---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: "00000000000000000000000000000000"
    PropagateID: "00000000000000000000000000000000"
    ReservedCode1: 304402201f199182bcd4a01f303c22d37332206c0d859bb3636116265ab94d5f2b4e65e802205430841913ab947dc303723da0f2eb0287ceabaf40533103880bac622646d8f1
    ReservedCode2: 3046022100ab25b54a68533d3f3d8ed22701202146e2501dfb1653ec45a1f6a54db78808fe022100ebcaf11f8636e42d21cc62ed1186bdd733800e13d5075cff77f7e1bb7f689330
---

# Knowledge Hygiene Skill — Dorian 记忆有效期机制

> 两层架构：记忆文件（存储层）+ knowledge-hygiene（执行引擎）
> 解决：记忆膨胀 / 逻辑打架 / 过时信息干扰判断

---

## 核心机制

### 存储层 — `memory/KNOWLEDGE_REGISTRY.md`

结构化表格，每条记忆携带：
- `LastUpdated`：有效期的起点
- `ExpiryMonths`：有效期（月数，永久=不设过期）
- `Status`：当前状态（ACTIVE / STALE / ARCHIVED）

### 执行层 — `knowledge-hygiene` Skill

每次会话启动时自动运行，维护存储层的健康度。

---

## Skill 执行时机

| 时机 | 触发条件 | 动作 |
|------|---------|------|
| **每次会话启动** | 读取 MEMORY.md 前 | 自动扫描 Registry，计算每条状态 |
| **主动提醒** | 用户问"你记得..."时 | 先扫描，再回答 |
| **每月定期** | cron 每月 1 日 | 全量审查 STALE 条目 |

---

## 状态流转规则

```
ACTIVE ──(到期)──→ STALE ──(超期1个月/人工确认)──→ ARCHIVED
                        │
                        └──(重新验证/更新)──→ ACTIVE（重置LastUpdated）
```

| 状态 | 含义 | 被加载进上下文 |
|------|------|--------------|
| ACTIVE | 有效，正常使用 | ✅ 是 |
| STALE | 到期，需人工复核 | ⚠️ 提示后可用 |
| ARCHIVED | 归档，可彻底删除 | ❌ 不加载 |

---

## 过期判定逻辑

```
当前日期 > LastUpdated + ExpiryMonths → STALE
STALE 超过 1 个月 → 可选自动 ARCHIVED
永久条目 → 永不过期
```

---

## Skill 工作流

### 1. 启动时扫描（自动）

```
读取 KNOWLEDGE_REGISTRY.md
  ↓
解析每行 ID / LastUpdated / ExpiryMonths / Status
  ↓
计算：(当前日期 - LastUpdated) >= ExpiryMonths?
  ↓
更新 Status：ACTIVE → STALE（发现变化时）
  ↓
输出变化摘要（哪些变 STALE，哪些刚被复核）
  ↓
写回文件
```

### 2. 查询单条（按需）

```
接收要查询的 Topic / KR ID
  ↓
在 Registry 中定位
  ↓
返回：状态 + LastUpdated + 过期剩余时间
```

### 3. 更新单条（按需）

```
接收 Topic / 新 Status / 新 Notes
  ↓
定位该条，更新对应字段
  ↓
重置 LastUpdated 为今天
  ↓
写回文件
```

### 4. 月度归档报告（cron）

```
扫描所有 STALE 条目
  ↓
生成报告：过期的lesson/数据/skill变化
  ↓
推送给用户（飞书/当前会话）
```

---

## Skill 命令清单

| 命令 | 触发词 | 说明 |
|------|--------|------|
| 扫描 | "启动记忆 hygiene" | 全量扫描，更新状态 |
| 查询 | "查一下记忆里的XXX" | 单条查询 |
| 更新 | "更新记忆：KR-XXX..." | 更新单条 |
| 报告 | "生成记忆月报" | cron触发，输出STALE清单 |

---

## 写入文件格式规范

写入 `memory/KNOWLEDGE_REGISTRY.md` 时，必须保留原有格式：
- Markdown 表格结构不变
- 仅更新 `LastUpdated`、`Status`、`Notes` 字段
- 禁止删除其他列

---

*Skill 建立：2026-04-09 | 管理目标：memory/KNOWLEDGE_REGISTRY.md*
